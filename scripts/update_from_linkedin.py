#!/usr/bin/env python3
"""
Update Lektor CV content from LinkedIn data.

There are two modes:

  A) LinkedIn Data Export (recommended, no partner access needed)
     ─────────────────────────────────────────────────────────────
     1. linkedin.com → Me → Settings & Privacy → Data Privacy
        → Get a copy of your data → select "Connections, Contacts,
        Account, Profile" (or "All") → Request archive.
     2. LinkedIn emails you a download link (may take up to 24 h).
     3. Download the ZIP and run:
          python update_from_linkedin.py --from-export ~/Downloads/Basic_LinkedInDataExport_*.zip

  B) LinkedIn API (OAuth — limited to basic identity only)
     ──────────────────────────────────────────────────────
     As of 2023, the LinkedIn public API no longer exposes work history,
     education or skills without partner-level access. The OAuth flow is
     still useful to verify credentials or as a hook for future endpoints.

     Setup:
       1. linkedin.com/developers/apps → create or open your app.
       2. Auth tab → add  http://localhost:8001/callback  as Redirect URL.
       3. Products tab → enable "Sign In with LinkedIn using OpenID Connect".
       4. Copy .env.example → .env and fill in LINKEDIN_CLIENT_ID /
          LINKEDIN_CLIENT_SECRET.

     Usage:
       python update_from_linkedin.py            # API run (basic profile only)
       python update_from_linkedin.py --auth     # (re-)authorize only
       python update_from_linkedin.py --dry-run  # preview without writing

What gets updated in content/cv/contents.lr:
    experience   ← Positions.csv  (or API positions)
    education    ← Education.csv  (or API educations)
    volunteering ← Volunteer Experiences.csv
    skills       ← Skills.csv     (or API skills)

What is preserved untouched:
    _model, title, summary_es, contact, languages, interests, talks,
    plus all logo_color / logo_initials for entries that already exist
    (matched by company / school name).
"""

import csv
import io
import json
import os
import re
import secrets
import sys
import threading
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from dotenv import load_dotenv

# ── Config ─────────────────────────────────────────────────────────────────

SCRIPT_DIR   = Path(__file__).parent
ENV_FILE     = SCRIPT_DIR / ".env"
TOKEN_CACHE  = SCRIPT_DIR / ".linkedin_token.json"
CV_FILE      = SCRIPT_DIR / "lektor" / "content" / "cv" / "contents.lr"

REDIRECT_URI = "http://localhost:8001/callback"
REDIRECT_PORT = 8001

AUTH_URL     = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL    = "https://www.linkedin.com/oauth/v2/accessToken"
API_BASE     = "https://api.linkedin.com/v2"

# Scopes — only the current (v2/OpenID Connect) scopes; the v1 scopes
# (r_liteprofile, r_emailaddress, r_basicprofile, r_fullprofile) were
# removed by LinkedIn in 2022 and now cause invalid_scope errors.
SCOPES = [
    "openid",
    "profile",
    "email",
]

LOGO_COLORS = [
    "linear-gradient(135deg,#1F4F6C,#0d2a3d)",
    "linear-gradient(135deg,#2D749F,#1F4F6C)",
    "linear-gradient(135deg,#B37C57,#60412B)",
    "linear-gradient(135deg,#fb866a,#c8523a)",
    "linear-gradient(135deg,#545E6C,#2c333d)",
    "linear-gradient(135deg,#124191,#0a2960)",
    "linear-gradient(135deg,#FFD43B,#FF9F1C)",
    "linear-gradient(135deg,#092e20,#2a6f4b)",
]


# ── OAuth 2.0 ──────────────────────────────────────────────────────────────

class _CallbackHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler that captures the ?code= from LinkedIn."""
    code = None
    error = None
    error_description = None

    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        _CallbackHandler.code = qs.get("code", [None])[0]
        _CallbackHandler.error = qs.get("error", [None])[0]
        _CallbackHandler.error_description = qs.get(
            "error_description", [None]
        )[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        if _CallbackHandler.code:
            self.wfile.write(
                b"<h2>Authorized! You can close this tab.</h2>"
                b"<script>window.close()</script>"
            )
        else:
            err = (_CallbackHandler.error or "unknown_error").encode()
            desc = (_CallbackHandler.error_description or "").encode()
            self.wfile.write(
                b"<h2 style='color:red'>Authorization failed</h2>"
                b"<p><b>Error:</b> " + err + b"</p>"
                b"<p>" + desc + b"</p>"
                b"<p>Check the terminal for details. You can close this tab.</p>"
            )

    def log_message(self, *_):
        pass  # silence server log


def _authorize(client_id: str, client_secret: str) -> dict:
    """Run the browser-based OAuth 2.0 flow and return token data."""
    state = secrets.token_urlsafe(16)
    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "scope": " ".join(SCOPES),
    }
    url = f"{AUTH_URL}?{urlencode(auth_params)}"

    # Start a local server to receive the callback
    server = HTTPServer(("localhost", REDIRECT_PORT), _CallbackHandler)
    t = threading.Thread(target=server.handle_request)
    t.start()

    print(f"\nOpening browser for LinkedIn authorization…\n  {url}\n")
    webbrowser.open(url)
    t.join(timeout=120)
    server.server_close()

    code = _CallbackHandler.code
    if not code:
        if _CallbackHandler.error:
            sys.exit(
                f"LinkedIn authorization failed.\n"
                f"  error:             {_CallbackHandler.error}\n"
                f"  error_description: {_CallbackHandler.error_description}\n\n"
                f"Common causes:\n"
                f"  invalid_scope      → scopes not granted for this app\n"
                f"  access_denied      → user cancelled or app not approved\n"
                f"  redirect_uri_mismatch → add {REDIRECT_URI} in your app's Auth tab"
            )
        sys.exit("Authorization timed out or was cancelled.")

    # Exchange code for access token
    resp = requests.post(TOKEN_URL, data={
        "grant_type":    "authorization_code",
        "code":          code,
        "redirect_uri":  REDIRECT_URI,
        "client_id":     client_id,
        "client_secret": client_secret,
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_token(client_id: str, client_secret: str, force: bool = False) -> str:
    """Return a valid access token, running OAuth if needed."""
    # 1. Env var override (CI / manual supply)
    token = os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip()
    if token:
        return token

    # 2. Cached token from previous run
    if not force and TOKEN_CACHE.exists():
        data = json.loads(TOKEN_CACHE.read_text())
        cached = data.get("access_token", "")
        if cached:
            print("Using cached access token (delete .linkedin_token.json to re-auth).")
            return cached

    # 3. Full browser-based OAuth flow
    token_data = _authorize(client_id, client_secret)
    TOKEN_CACHE.write_text(json.dumps(token_data, indent=2))
    TOKEN_CACHE.chmod(0o600)
    print("Access token obtained and cached.")
    return token_data["access_token"]


# ── LinkedIn API helpers ───────────────────────────────────────────────────

def _get(token: str, path: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """GET from the LinkedIn API; returns None on 403/404."""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    resp = requests.get(f"{API_BASE}/{path.lstrip('/')}",
                        headers=headers, params=params, timeout=15)
    if resp.status_code in (401, 403):
        print(f"  ⚠ {path}: access denied (scope not granted for this app)")
        return None
    if resp.status_code == 404:
        print(f"  ⚠ {path}: endpoint not found")
        return None
    resp.raise_for_status()
    return resp.json()


def _localized(field: dict) -> str:
    """Extract a human-readable string from LinkedIn's localized value."""
    if not field:
        return ""
    if "localized" in field:
        vals = field["localized"]
        # Prefer the user's preferredLocale if present
        locale = field.get("preferredLocale", {})
        key = f"{locale.get('language', '')}_{locale.get('country', '')}"
        return vals.get(key) or next(iter(vals.values()), "")
    return str(field)


def _fmt_date(d: Optional[Dict]) -> str:
    """{'month': 3, 'year': 2019} → 'Mar 2019'; None → 'Present'."""
    if not d:
        return "Present"
    months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m = d.get("month")
    y = d.get("year", "")
    return f"{months[m]} {y}" if m else str(y)


def _initials(name: str) -> str:
    words = name.split()
    if len(words) == 1:
        return name[:2].upper()
    return "".join(w[0].upper() for w in words[:3])


# ── Fetch profile sections ─────────────────────────────────────────────────

def fetch_profile(token: str) -> dict:
    """
    Fetch whatever the LinkedIn API will return with the current scopes.
    With the public OpenID Connect product (openid + profile + email),
    only basic identity is accessible. Work experience, education and skills
    require partner-level API access — use --from-export for those.
    """
    result: Dict = {}

    # OpenID Connect userinfo — most reliable endpoint with standard scopes
    userinfo = _get(token, "userinfo")
    if userinfo:
        first = userinfo.get("given_name", "")
        last  = userinfo.get("family_name", "")
        result["name"]  = f"{first} {last}".strip() or userinfo.get("name", "")
        result["email"] = userinfo.get("email", "")

    # v2/me fallback with localized fields (no profilePicture — that requires
    # additional permissions and has been removed from the public API)
    if not result.get("name"):
        me = _get(token, "me", params={
            "projection": "(id,localizedFirstName,localizedLastName)"
        })
        if me:
            result["name"] = (
                me.get("localizedFirstName", "") + " " +
                me.get("localizedLastName", "")
            ).strip()

    return result


# ── LinkedIn Data Export parser ────────────────────────────────────────────

def _parse_export_date(s: str) -> Optional[Dict]:
    """'Jan 2019' or '2019' → {month, year}; blank → None."""
    if not s or not s.strip():
        return None
    months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    parts = s.strip().split()
    if len(parts) == 2:
        m = months.get(parts[0].lower())
        try:
            return {"month": m, "year": int(parts[1])} if m else {"year": int(parts[1])}
        except ValueError:
            pass
    try:
        return {"year": int(parts[0])}
    except ValueError:
        return None


def fetch_from_export(zip_path: str) -> dict:
    """
    Parse a LinkedIn Data Export ZIP and return the same structure as
    fetch_profile so the existing builder functions work unchanged.

    Expected CSV files inside the ZIP (LinkedIn names them exactly like this):
        Positions.csv, Education.csv, Skills.csv, Volunteer Experiences.csv
    """
    result: Dict = {}

    with zipfile.ZipFile(zip_path) as zf:
        # Build a case-insensitive name → archive-path map
        name_map = {Path(n).name.lower(): n for n in zf.namelist()}

        def read_csv(filename: str) -> List[Dict]:
            key = filename.lower()
            if key not in name_map:
                print(f"  ⚠ {filename} not found in ZIP (skipping)")
                return []
            with zf.open(name_map[key]) as f:
                text = f.read().decode("utf-8-sig")  # strip BOM if present
            return list(csv.DictReader(io.StringIO(text)))

        # Positions → experience
        rows = read_csv("Positions.csv")
        if rows:
            result["positions"] = [
                {
                    "title":        r.get("Title", ""),
                    "companyName":  r.get("Company Name", ""),
                    "locationName": r.get("Location", ""),
                    "description":  r.get("Description", ""),
                    "startDate":    _parse_export_date(r.get("Started On", "")),
                    "endDate":      _parse_export_date(r.get("Finished On", "")),
                    "isCurrent":    not r.get("Finished On", "").strip(),
                }
                for r in rows
                if r.get("Company Name", "").strip()
            ]
            print(f"  ✓ Positions.csv — {len(result['positions'])} entries")

        # Education
        rows = read_csv("Education.csv")
        if rows:
            result["educations"] = [
                {
                    "schoolName":  r.get("School Name", ""),
                    "degreeName":  r.get("Degree Name", ""),
                    "fieldOfStudy": r.get("Notes", ""),
                    "startDate":   _parse_export_date(r.get("Start Date", "")),
                    "endDate":     _parse_export_date(r.get("End Date", "")),
                }
                for r in rows
                if r.get("School Name", "").strip()
            ]
            print(f"  ✓ Education.csv — {len(result['educations'])} entries")

        # Skills
        rows = read_csv("Skills.csv")
        if rows:
            result["skills"] = [
                {"name": r.get("Name", "")}
                for r in rows
                if r.get("Name", "").strip()
            ]
            print(f"  ✓ Skills.csv — {len(result['skills'])} entries")

        # Volunteering
        rows = read_csv("Volunteer Experiences.csv")
        if rows:
            result["volunteerExperiences"] = [
                {
                    "organizationName": r.get("Organization", ""),
                    "role":             r.get("Role", ""),
                    "description":      r.get("Description", ""),
                    "startDate":        _parse_export_date(r.get("Start Date", "")),
                    "endDate":          _parse_export_date(r.get("End Date", "")),
                }
                for r in rows
                if r.get("Organization", "").strip()
            ]
            print(f"  ✓ Volunteer Experiences.csv — {len(result['volunteerExperiences'])} entries")

    return result


# ── .lr file parser / writer ───────────────────────────────────────────────

BLOCK_SEP = "\n----\n"


def parse_lr(text: str) -> List[Tuple[str, str]]:
    fields = []
    for part in re.split(r"\n---\n", text.replace("\r\n", "\n")):
        if not part.strip():
            continue
        m = re.match(r"^([^:\n]+):(.*)", part, re.DOTALL)
        if m:
            fields.append((m.group(1).strip(), m.group(2)))
        else:
            fields.append(("__raw__", part))
    return fields


def render_lr(fields: List[Tuple[str, str]]) -> str:
    parts = []
    for name, value in fields:
        parts.append(value if name == "__raw__" else f"{name}:{value}")
    return "\n---\n".join(parts)


# ── Logo preservation ──────────────────────────────────────────────────────

def _extract_logos(raw_value: str) -> dict[str, dict]:
    """Return {normalised_name: {logo_color, logo_initials}} from a flow field."""
    result = {}
    for block in re.split(r"(?=#### cv_)", raw_value):
        color_m  = re.search(r"^logo_color:\s*(.+)$",    block, re.MULTILINE)
        init_m   = re.search(r"^logo_initials:\s*(.+)$", block, re.MULTILINE)
        name_m   = (
            re.search(r"^company:\s*(.+)$", block, re.MULTILINE) or
            re.search(r"^meta:\s*(.+)$",    block, re.MULTILINE)
        )
        if name_m:
            key = name_m.group(1).strip().split("—")[0].strip().lower()
            result[key] = {
                "logo_color":    color_m.group(1).strip() if color_m else LOGO_COLORS[0],
                "logo_initials": init_m.group(1).strip()  if init_m  else "??",
            }
    return result


def _logo_for(name: str, existing: Dict, idx: int) -> Tuple[str, str, int]:
    key = name.lower().strip()
    if key in existing:
        d = existing[key]
        return d["logo_color"], d["logo_initials"], idx
    return LOGO_COLORS[idx % len(LOGO_COLORS)], _initials(name), idx + 1


# ── Flowblock builders ─────────────────────────────────────────────────────

def _experience_block(pos: dict, color: str, initials: str) -> str:
    title   = _localized(pos.get("title", {})) or pos.get("title", "")
    company = _localized(pos.get("companyName", {})) or pos.get("companyName", "")
    loc     = _localized(pos.get("locationName", {})) or pos.get("locationName", "")
    desc    = _localized(pos.get("description", {})) or pos.get("description", "")

    company_line = f"{company} — {loc}" if loc else company
    start = _fmt_date(pos.get("startDate") or pos.get("timePeriod", {}).get("startDate"))
    end   = _fmt_date(pos.get("endDate")   or pos.get("timePeriod", {}).get("endDate") or (None if pos.get("isCurrent") else {}))

    resp_lines = ""
    if desc:
        resp_lines = "\n".join(
            l.strip().rstrip(".")
            for l in re.split(r"\.\s+|\n+", desc)
            if l.strip()
        )

    return (
        "#### cv_experience_item ####\n"
        f"title: {title}\n"
        f"{BLOCK_SEP.lstrip()}time: {start} — {end}\n"
        f"{BLOCK_SEP.lstrip()}company: {company_line}\n"
        f"{BLOCK_SEP.lstrip()}logo_image:\n"
        f"{BLOCK_SEP.lstrip()}logo_initials: {initials}\n"
        f"{BLOCK_SEP.lstrip()}logo_color: {color}\n"
        f"{BLOCK_SEP.lstrip()}responsibilities:\n{resp_lines}\n"
        f"{BLOCK_SEP.lstrip()}tools:"
    )


def _entry_block(item: dict, role_key: str, org_key: str,
                 color: str, initials: str) -> str:
    role = _localized(item.get(role_key, {})) or item.get(role_key, "")
    org  = _localized(item.get(org_key, {}))  or item.get(org_key, "")

    # School / org may come as a nested object
    if isinstance(role, dict):
        role = _localized(role)
    if isinstance(org, dict):
        org = _localized(org)

    # Education extras
    degree = item.get("degreeName", "") or item.get("fieldOfStudy", "")
    if degree and degree != role:
        meta_line = f"{org} · {degree}"
    else:
        meta_line = org

    start = _fmt_date(item.get("startDate") or item.get("timePeriod", {}).get("startDate"))
    end   = _fmt_date(item.get("endDate")   or item.get("timePeriod", {}).get("endDate"))
    time_str = f"{start} - {end}" if start and start != "Present" else end

    return (
        "#### cv_entry_item ####\n"
        f"title: {role}\n"
        f"{BLOCK_SEP.lstrip()}meta: {meta_line}\n"
        f"{BLOCK_SEP.lstrip()}time: {time_str}\n"
        f"{BLOCK_SEP.lstrip()}logo_image:\n"
        f"{BLOCK_SEP.lstrip()}logo_initials: {initials}\n"
        f"{BLOCK_SEP.lstrip()}logo_color: {color}"
    )


def _skill_block(name: str, level: int) -> str:
    return (
        "#### cv_skill_item ####\n"
        f"label: {name}\n"
        f"{BLOCK_SEP.lstrip()}level: {level}"
    )


# ── Section builders ───────────────────────────────────────────────────────

def _join_blocks(blocks: list[str]) -> str:
    return "\n\n" + "\n\n".join(blocks) + "\n"


def build_experience(positions: list, existing: dict) -> str:
    blocks, idx = [], 0
    for pos in positions:
        company = (
            _localized(pos.get("companyName", {})) or
            pos.get("companyName", "") or ""
        )
        if not company:
            continue
        color, initials, idx = _logo_for(company, existing, idx)
        blocks.append(_experience_block(pos, color, initials))
    return _join_blocks(blocks) if blocks else "\n"


def build_education(educations: list, existing: dict) -> str:
    blocks, idx = [], 0
    for ed in educations:
        school = (
            _localized(ed.get("schoolName", {})) or
            ed.get("schoolName", "") or ""
        )
        if not school:
            continue
        color, initials, idx = _logo_for(school, existing, idx)
        blocks.append(_entry_block(ed, "degreeName", "schoolName", color, initials))
    return _join_blocks(blocks) if blocks else "\n"


def build_volunteering(volunteer: list, existing: dict) -> str:
    blocks, idx = [], 0
    for vol in volunteer:
        org = (
            _localized(vol.get("organizationName", {})) or
            vol.get("organizationName", "") or ""
        )
        if not org:
            continue
        color, initials, idx = _logo_for(org, existing, idx)
        blocks.append(_entry_block(vol, "role", "organizationName", color, initials))
    return _join_blocks(blocks) if blocks else "\n"


def build_skills(skills: list, existing_text: str) -> str:
    # Keep existing levels; default 80 for new skills
    levels: dict[str, int] = {}
    for m in re.finditer(r"label:\s*(.+?)\n----\nlevel:\s*(\d+)", existing_text):
        levels[m.group(1).strip().lower()] = int(m.group(2))

    blocks = []
    for skill in skills:
        name = (
            _localized(skill.get("name", {})) or
            skill.get("name", "") or
            skill.get("skillUrn", "")
        )
        if not name:
            continue
        level = levels.get(name.lower(), 80)
        blocks.append(_skill_block(name, level))
    return _join_blocks(blocks) if blocks else "\n"


# ── Main ───────────────────────────────────────────────────────────────────

_NO_SECTIONS_MSG = """
No profile sections were returned.

LinkedIn's public API no longer exposes work experience, education or
skills without partner-level access (since mid-2023).

To sync your full profile, download a LinkedIn Data Export:
  1. linkedin.com → Me (top right) → Settings & Privacy
  2. Data Privacy → Get a copy of your data
  3. Choose "Connections, Contacts, Account, Profile" and click Request
  4. Wait for LinkedIn's email with the download link (up to 24 h)
  5. Download the ZIP and run:

       python update_from_linkedin.py --from-export ~/Downloads/Basic_LinkedInDataExport_*.zip
"""


def main():
    argv = sys.argv[1:]
    flags = set(argv)
    auth_only   = "--auth" in flags
    dry_run     = "--dry-run" in flags
    export_path = None

    if "--from-export" in argv:
        idx = argv.index("--from-export")
        if idx + 1 >= len(argv):
            sys.exit("Error: --from-export requires a path to the LinkedIn ZIP file.")
        export_path = argv[idx + 1]

    load_dotenv(ENV_FILE)

    # ── Data Export mode (no OAuth needed) ────────────────────────────────
    if export_path:
        p = Path(export_path).expanduser()
        if not p.exists():
            sys.exit(f"Error: file not found: {p}")
        print(f"\nReading LinkedIn Data Export: {p.name}")
        profile = fetch_from_export(str(p))

    # ── API mode ───────────────────────────────────────────────────────────
    else:
        client_id     = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
        client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip()
        if not client_id or not client_secret:
            sys.exit(
                "Error: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set.\n"
                "Copy .env.example → .env and fill in your credentials."
            )
        token = get_token(client_id, client_secret, force=auth_only)
        if auth_only:
            print("Authorization complete.")
            return
        print("\nFetching LinkedIn profile via API…")
        profile = fetch_profile(token)

    sections_found = [
        k for k in ("positions", "educations", "skills", "volunteerExperiences")
        if k in profile
    ]
    if not sections_found:
        print(_NO_SECTIONS_MSG)
        return

    if not export_path:
        print(f"Received: {', '.join(sections_found)}\n")

    # Read current CV and extract existing logo data
    original = CV_FILE.read_text(encoding="utf-8")
    fields   = parse_lr(original)

    existing_logos: dict[str, dict] = {}
    existing_skills_text = ""
    for name, value in fields:
        if name in ("experience", "education", "volunteering"):
            existing_logos[name] = _extract_logos(value)
        if name == "skills":
            existing_skills_text = value

    # Build updated section values
    updates: dict[str, str] = {}
    if "positions" in profile:
        updates["experience"] = build_experience(
            profile["positions"], existing_logos.get("experience", {}))
    if "educations" in profile:
        updates["education"] = build_education(
            profile["educations"], existing_logos.get("education", {}))
    if "volunteerExperiences" in profile:
        updates["volunteering"] = build_volunteering(
            profile["volunteerExperiences"], existing_logos.get("volunteering", {}))
    if "skills" in profile:
        updates["skills"] = build_skills(profile["skills"], existing_skills_text)

    if not updates:
        print("Nothing to update.")
        return

    # Apply updates
    new_fields = []
    for name, value in fields:
        if name in updates:
            new_fields.append((name, updates[name]))
            print(f"  ✓ {'[dry-run] ' if dry_run else ''}Updated: {name}")
        else:
            new_fields.append((name, value))

    output = render_lr(new_fields)

    if dry_run:
        print("\n── Dry-run output ──────────────────────────────────────────\n")
        print(output)
    else:
        CV_FILE.write_text(output, encoding="utf-8")
        print(f"\nWritten → {CV_FILE}")
        print("Next: cd lektor && lektor build --output-path /tmp/lektor-build")


if __name__ == "__main__":
    main()
