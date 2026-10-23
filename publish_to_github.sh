#!/usr/bin/env bash
set -euo pipefail
REPO_NAME="${1:-PowerBI-Industry-Analytics-Portfolio}"
cd "$(dirname "${BASH_SOURCE[0]}")"

for program in git gh python3; do
  if ! command -v "$program" >/dev/null 2>&1; then
    echo "Missing $program. For gh on macOS, use: brew install gh" >&2
    exit 1
  fi
done

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI not authenticated. Run: gh auth login" >&2
  exit 1
fi

python3 validate_all.py
LOGIN="$(gh api user --jq '.login')"
TARGET="$LOGIN/$REPO_NAME"

if [[ ! -d .git ]]; then git init -b main; fi
if [[ "$(git branch --show-current)" != main ]]; then git branch -M main; fi

# Let the actual authenticated user's local Git identity supply commit attribution.
if ! git config user.name >/dev/null || ! git config user.email >/dev/null; then
  echo "Set your Git name/email with git config --global user.name and user.email, then retry." >&2
  exit 1
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "Add four original industry Power BI case studies"
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "Existing origin remote detected: $(git remote get-url origin)"
  git push -u origin main
elif gh repo view "$TARGET" --json name >/dev/null 2>&1; then
  echo "Repository already exists: $TARGET"
  git remote add origin "https://github.com/$TARGET.git"
  git push -u origin main
else
  gh repo create "$TARGET" --public --source=. --remote=origin --push \
    --description "Four original industry-level Power BI analytics projects with datasets, DAX, validation and interactive HTML previews"
fi

echo "Repository: https://github.com/$TARGET"
