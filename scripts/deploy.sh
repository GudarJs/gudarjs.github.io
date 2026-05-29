#!/bin/bash
# Deploy the Lektor site to the main branch on GitHub.
# Run from the project root with the virtualenv activated:
#   source ../venv/bin/activate
#   bash scripts/deploy.sh

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY_BRANCH="main"
REMOTE="origin"

echo "→ Building Vite assets..."
cd "$REPO_ROOT/frontend" && npm run build

echo "→ Building Lektor site..."
cd "$REPO_ROOT" && lektor build --output-path dist/

echo "→ Preparing deploy..."
DEPLOY_DIR=$(mktemp -d)
cp -r "$REPO_ROOT/dist/." "$DEPLOY_DIR/"
rm -rf "$DEPLOY_DIR/.lektor"

cd "$DEPLOY_DIR"
git init
git config user.name "$(git -C "$REPO_ROOT" config user.name)"
git config user.email "$(git -C "$REPO_ROOT" config user.email)"
git checkout --orphan "$DEPLOY_BRANCH"
git remote add origin "$(git -C "$REPO_ROOT" remote get-url $REMOTE)"
git add -A
git commit -m "chore: deploy $(date '+%Y-%m-%d %H:%M')"
git push origin "$DEPLOY_BRANCH" --force

rm -rf "$DEPLOY_DIR"
echo "✓ Deploy completo → https://$(cat "$REPO_ROOT/assets/CNAME" 2>/dev/null || echo gudarjs.github.io)"
