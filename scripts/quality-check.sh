#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "== quality-check =="
echo "ROOT: $ROOT"
fail=0

EXCLUDE_DIRS=("$ROOT/.git" "$ROOT/node_modules" "$ROOT/.next" "$ROOT/dist" "$ROOT/build")
is_excluded() {
  local p="$1"
  for d in "${EXCLUDE_DIRS[@]}"; do [[ "$p" == "$d"* ]] && return 0; done
  return 1
}

# 1) Required files
req=(
  "$ROOT/CLAUDE.md" "$ROOT/HANDOFF.md" "$ROOT/PROGRESS.md"
  "$ROOT/docs/01-architecture.md" "$ROOT/docs/02-infra-rules.md"
  "$ROOT/docs/03-file-roles.md" "$ROOT/docs/04-workflow.md"
  "$ROOT/docs/05-quality-check.md" "$ROOT/docs/06-error-patterns.md"
  "$ROOT/docs/07-report-template.md" "$ROOT/scripts/quality-check.sh"
)
echo "-- required files --"
for f in "${req[@]}"; do
  [[ ! -f "$f" ]] && { echo "[FAIL] missing: $f"; fail=1; }
done

# 2) JSON syntax
echo "-- json syntax --"
while IFS= read -r -d '' f; do
  is_excluded "$f" && continue
  python3 -m json.tool "$f" > /dev/null 2>&1 || { echo "[FAIL] JSON: $f"; fail=1; }
done < <(find "$ROOT" -type f -name "*.json" -print0)

# 3) JS syntax
echo "-- js syntax --"
if command -v node >/dev/null 2>&1; then
  while IFS= read -r -d '' f; do
    is_excluded "$f" && continue
    node --check "$f" >/dev/null 2>&1 || { echo "[FAIL] JS: $f"; fail=1; }
  done < <(find "$ROOT" -type f \( -name "*.js" -o -name "*.mjs" -o -name "*.cjs" \) -print0)
else
  echo "[WARN] node not found; skip JS check"
fi

# 4) TS syntax (tsconfig 있을 때만)
echo "-- ts syntax --"
if command -v tsc >/dev/null 2>&1 && [[ -f "$ROOT/tsconfig.json" ]]; then
  tsc --noEmit --project "$ROOT/tsconfig.json" >/dev/null 2>&1 || { echo "[FAIL] TS"; fail=1; }
else
  echo "[SKIP] tsc or tsconfig.json not found"
fi

# 5) Python syntax
echo "-- python syntax --"
if command -v python3 >/dev/null 2>&1; then
  while IFS= read -r -d '' f; do
    is_excluded "$f" && continue
    python3 -m py_compile "$f" >/dev/null 2>&1 || { echo "[FAIL] PY: $f"; fail=1; }
  done < <(find "$ROOT" -type f -name "*.py" -print0)
else
  echo "[WARN] python3 not found; skip PY check"
fi

# 6) Hardcoding scan
echo "-- hardcoding scan --"
while IFS= read -r -d '' f; do
  is_excluded "$f" && continue
  [[ "$f" == "$ROOT/docs/"* ]] && continue
  if grep -nE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' "$f" >/dev/null 2>&1; then
    echo "[FAIL] IP hardcoding suspected: $f"
    grep -nE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' "$f" | head -n 3
    fail=1
  fi
  if grep -nE '(password\s*=|passwd\s*=|api[_-]?key\s*=|secret\s*=|token\s*=)' "$f" >/dev/null 2>&1; then
    echo "[FAIL] secret keyword suspected: $f"
    grep -nE '(password\s*=|passwd\s*=|api[_-]?key\s*=|secret\s*=|token\s*=)' "$f" | head -n 3
    fail=1
  fi
done < <(find "$ROOT" -type f \( -name "*.js" -o -name "*.mjs" -o -name "*.cjs" -o -name "*.ts" -o -name "*.json" -o -name "*.py" -o -name "*.sh" \) -print0)

[[ "$fail" -ne 0 ]] && { echo "== RESULT: FAIL =="; exit 1; }
echo "== RESULT: PASS =="
