# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate virtualenv (required — Lektor must be installed inside it)
source ../venv/bin/activate

# Dev server with admin UI at /admin/
lektor server --admin            # → http://127.0.0.1:5000

# Production build
lektor build --output-path dist/

# Deploy to GitHub Pages
lektor deploy ghpages

# Update CV from LinkedIn
cd scripts
python update_from_linkedin.py            # full run
python update_from_linkedin.py --dry-run  # preview without writing
python update_from_linkedin.py --auth     # force re-authorization
```

The `scripts/.env` file (gitignored) must contain `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET`. See `scripts/.env.example`.

## Frontend (Vite) — run from `frontend/`

```bash
npm install          # first time only
npm run dev          # watch mode: rebuilds assets/static/ on save
npm run build        # production build (required before lektor build or deploy)
```

**Important:** `npm run build` must be run before `lektor build` or `lektor deploy ghpages` — Lektor serves from `assets/static/` which Vite writes to.

## Architecture

This is a **[Lektor](https://www.getlektor.com/) static site** — Python-based SSG with a file-based CMS. Content is stored as plain text (`.lr` files), schemas are defined in `.ini` files, and HTML is rendered via Jinja2 templates at build time. There is no database or server-side logic.

### Bilingual content (ES / EN)

The site is bilingual: `es` is primary (served at `/`), `en` at `/en/`. For every page:
- `contents.lr` — Spanish (primary, always present)
- `contents+en.lr` — English (only fields that differ; omitted fields inherit from ES)

UI strings (nav labels, buttons, section headings) live in `databags/i18n_es.json` and `databags/i18n_en.json`. Templates access them via:

```jinja
{% set lang = 'en' if this.alt == 'en' else 'es' %}
{% set t = bag('i18n_' + lang) %}
```

**Critical:** flowblock templates (`templates/blocks/*.html`) run in an isolated Jinja2 context — the `t` variable is **not available** inside them. Use literal text or block-specific fields for any translated copy in flowblocks.

### Models and flowblocks

Page types are defined in `models/*.ini`. Structured repeating sections (CV entries, skill cards, workshop cards, etc.) use Lektor's flow type — each flowblock has a schema in `flowblocks/*.ini` and a template in `templates/blocks/<name>.html`.

In `.lr` files, flowblocks are separated by `----` between fields and `\n---\n` between top-level page fields.

### CV LinkedIn sync

`scripts/update_from_linkedin.py` overwrites the `experience`, `education`, `volunteering`, and `skills` fields in `content/cv/contents.lr` via the LinkedIn REST API. It preserves `logo_color` and `logo_initials` for existing entries by matching on company/school name. Fields not managed by the script (`_model`, `title`, `summary_es`, `contact`, `languages`, `interests`, `talks`) are left untouched.

### Workshop content structure

Workshops live under `content/talleres/<slug>/`. Each step is a subfolder `<NN-slug>/contents.lr` with `_model: taller-paso`. The `orden` field must match the numeric prefix of the folder (`04-vistas/` → `orden: 4`) — this drives the sidebar prev/next navigation.

Available flowblocks for workshop steps: `texto`, `codigo`, `comando_os`, `imagen`, `analogia`, `advertencia`, `checkpoint`, `error_provocado`, `solucion_error`. Each `error_provocado` must be followed immediately by a `solucion_error`.

## Content conventions

- Content fields in Spanish; English overrides in `contents+en.lr`.
- Second person address ("vas a", "fíjate", "guarda el archivo").
- No em dash (—) in prose; use comma, colon, or period.
- `cover_image` on posts and workshops accepts a root-relative path (`/static/image.jpg`) or absolute URL; omit for gradient fallback.
- Post `theme` colors: `green`, `blue`, `red`, `coral`.
