#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./manual_update.sh [-m "Commit message"] path [path ...]

Examples:
  ./manual_update.sh _papers/my-edited-paper.md
  ./manual_update.sh -m "Update paper summary" _papers/my-edited-paper.md
  ./manual_update.sh -m "Update homepage copy" _layouts/home.html _data/site.json

What it does:
  1. Regenerates and validates source data.
  2. Stages only the paths you provide.
  3. Also stages _data/paper_index.json if validation regenerated it.
  4. Commits and pushes the staged manual update.
USAGE
}

commit_message="Manual website update"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--message)
      if [[ $# -lt 2 || -z "${2:-}" ]]; then
        echo "Error: $1 requires a commit message." >&2
        usage
        exit 2
      fi
      commit_message="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Error: unknown option $1" >&2
      usage
      exit 2
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -eq 0 ]]; then
  echo "Error: provide at least one file or directory to stage." >&2
  echo
  usage
  echo
  echo "Current changed files:"
  git status --short
  exit 2
fi

cd "$(dirname "$0")"

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "Error: repository is in detached HEAD state; refusing to push." >&2
  exit 1
fi

echo "Running source validation..."
python3 scripts/validate_sources.py --write-index
python3 scripts/validate_sources.py

echo "Staging manual paths..."
git add -- "$@"

if ! git diff --quiet -- _data/paper_index.json; then
  echo "Staging regenerated _data/paper_index.json..."
  git add -- _data/paper_index.json
fi

if git diff --cached --quiet; then
  echo "No staged changes to commit."
  exit 0
fi

echo "Staged changes:"
git diff --cached --name-status

git commit -m "$commit_message"
git push origin "$branch"

echo "Manual update pushed to origin/$branch."
