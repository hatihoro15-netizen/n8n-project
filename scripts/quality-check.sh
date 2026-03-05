#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== quality-check =="
echo "ROOT: $ROOT"

fail=0

# Exclude dirs
EXCLUDE_DIRS=(
  "$ROOT/.git"
  "$ROOT/node_modules"
  "$ROOT/.next"
  "$ROOT/.vercel"
  "$ROOT/.claude"
  "$ROOT/dist"
  "$ROOT/build"
  "$ROOT/deploy"
)

EXCLUDE_PATTERNS=(".vercel" ".next" "dist")

is_excluded() {
  local p="$1"
  for d in "${EXCLUDE_DIRS[@]}"; do
    [[ "$p" == "$d"* ]] && return 0
  done
  for pat in "${EXCLUDE_PATTERNS[@]}"; do
    [[ "$p" == *"/$pat/"* || "$p" == *"/$pat" ]] && return 0
  done
  return 1
}

# 1) Required files
req=(
  "$ROOT/CLAUDE.md"
  "$ROOT/HANDOFF.md"
  "$ROOT/process.md"
  "$ROOT/PROGRESS.md"
  "$ROOT/docs/01-architecture.md"
  "$ROOT/docs/02-infra-rules.md"
  "$ROOT/docs/03-file-roles.md"
  "$ROOT/docs/04-workflow.md"
  "$ROOT/docs/05-quality-check.md"
  "$ROOT/docs/06-error-patterns.md"
  "$ROOT/docs/07-report-template.md"
  "$ROOT/scripts/quality-check.sh"
)

echo "-- required files --"
for f in "${req[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "[FAIL] missing: $f"
    fail=1
  fi
done

# 2) JSON syntax
echo "-- json syntax --"
while IFS= read -r -d '' f; do
  if is_excluded "$f"; then continue; fi
  python3 -m json.tool "$f" > /dev/null 2>&1 || { echo "[FAIL] JSON: $f"; fail=1; }
done < <(find "$ROOT" -type f -name "*.json" -print0)

# 3) JS syntax (node --check)
echo "-- js syntax --"
if command -v node >/dev/null 2>&1; then
  while IFS= read -r -d '' f; do
    if is_excluded "$f"; then continue; fi
    node --check "$f" >/dev/null 2>&1 || { echo "[FAIL] JS: $f"; fail=1; }
  done < <(find "$ROOT" -type f \( -name "*.js" -o -name "*.mjs" -o -name "*.cjs" \) -print0)
else
  echo "[WARN] node not found; skip JS check"
fi

# 4) Python syntax
echo "-- python syntax --"
if command -v python3 >/dev/null 2>&1; then
  while IFS= read -r -d '' f; do
    if is_excluded "$f"; then continue; fi
    python3 -m py_compile "$f" >/dev/null 2>&1 || { echo "[FAIL] PY: $f"; fail=1; }
  done < <(find "$ROOT" -type f -name "*.py" -print0)
else
  echo "[WARN] python3 not found; skip PY check"
fi

# 5) Hardcoding scan
echo "-- hardcoding scan --"
while IFS= read -r -d '' f; do
  if is_excluded "$f"; then continue; fi
  # docs/는 예시 포함 허용
  [[ "$f" == "$ROOT/docs/"* ]] && continue

  # IP check: 0.0.0.0(바인드 주소), 127.0.0.1(localhost) 제외
  if grep -nE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' "$f" | grep -vE '(0\.0\.0\.0|127\.0\.0\.1)' >/dev/null 2>&1; then
    echo "[FAIL] IP hardcoding suspected: $f"
    grep -nE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' "$f" | grep -vE '(0\.0\.0\.0|127\.0\.0\.1)' | head -n 3
    fail=1
  fi

  # Secret check: 변수 선언(const/let/var token =)은 제외, 설정값 할당만 탐지
  if grep -nE '(password\s*=\s*['\''"]|passwd\s*=\s*['\''"]|api[_-]?key\s*=\s*['\''"]|secret\s*=\s*['\''"])' "$f" >/dev/null 2>&1; then
    echo "[FAIL] secret keyword suspected: $f"
    grep -nE '(password\s*=\s*['\''"]|passwd\s*=\s*['\''"]|api[_-]?key\s*=\s*['\''"]|secret\s*=\s*['\''"])' "$f" | head -n 3
    fail=1
  fi
done < <(find "$ROOT" -type f \( -name "*.js" -o -name "*.mjs" -o -name "*.cjs" -o -name "*.ts" -o -name "*.json" -o -name "*.py" -o -name "*.sh" \) -print0)

if [[ "$fail" -ne 0 ]]; then
  echo "== RESULT: FAIL =="
  exit 1
fi

echo "== RESULT: PASS =="
