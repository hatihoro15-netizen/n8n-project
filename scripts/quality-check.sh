#!/bin/bash
# n8n 워크플로우 프로젝트 - 품질 검사 스크립트
# 실행: ./scripts/quality-check.sh
# 자동 실행: PostToolUse 훅 (Bash 도구 사용 후)

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0

echo "========================================="
echo " Quality Check - n8n 워크플로우 프로젝트"
echo "========================================="

# 1. JSON 문법 검사
echo ""
echo "[1/5] JSON 문법 검사..."
JSON_ERRORS=0
for f in "$PROJECT_DIR"/*.json; do
    [ -f "$f" ] || continue
    if ! python3 -m json.tool "$f" > /dev/null 2>&1; then
        echo "  FAIL: $(basename "$f")"
        JSON_ERRORS=$((JSON_ERRORS + 1))
        ERRORS=$((ERRORS + 1))
    fi
done
if [ $JSON_ERRORS -eq 0 ]; then
    echo "  PASS: 모든 JSON 파일 정상"
fi

# 2. Python 문법 검사
echo ""
echo "[2/5] Python 문법 검사..."
PY_ERRORS=0
for f in "$PROJECT_DIR"/*.py; do
    [ -f "$f" ] || continue
    if ! python3 -c "import py_compile; py_compile.compile('$f', doraise=True)" 2>/dev/null; then
        echo "  FAIL: $(basename "$f")"
        PY_ERRORS=$((PY_ERRORS + 1))
        ERRORS=$((ERRORS + 1))
    fi
done
if [ $PY_ERRORS -eq 0 ]; then
    echo "  PASS: 모든 Python 파일 정상"
fi

# 3. 하드코딩 검사 (IP 주소, 비밀번호 패턴 - py/js 파일 대상)
echo ""
echo "[3/5] 하드코딩 검사..."
HC_ERRORS=0
for f in "$PROJECT_DIR"/*.py "$PROJECT_DIR"/*.js; do
    [ -f "$f" ] || continue
    # IP 하드코딩 검사 (127.0.0.1, 0.0.0.0, 172.17.0.1 제외)
    if grep -En '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' "$f" | grep -v '127.0.0.1\|0.0.0.0\|172.17.0.1\|localhost' | grep -v '^ *#' | grep -v '^ *//' > /dev/null 2>&1; then
        echo "  WARN: IP 하드코딩 의심 - $(basename "$f")"
        HC_ERRORS=$((HC_ERRORS + 1))
    fi
    # password= 하드코딩 검사
    if grep -En 'password *= *["'"'"'][^"'"'"']+["'"'"']' "$f" | grep -v '^ *#' | grep -v '^ *//' > /dev/null 2>&1; then
        echo "  WARN: 비밀번호 하드코딩 의심 - $(basename "$f")"
        HC_ERRORS=$((HC_ERRORS + 1))
    fi
done
if [ $HC_ERRORS -eq 0 ]; then
    echo "  PASS: 하드코딩 미발견"
fi

# 4. JavaScript 문법 검사 (n8n Code 노드용 .js 파일)
echo ""
echo "[4/5] JavaScript 문법 검사..."
JS_ERRORS=0
for f in "$PROJECT_DIR"/*.js; do
    [ -f "$f" ] || continue
    if ! node --check "$f" 2>/dev/null; then
        echo "  FAIL: $(basename "$f")"
        JS_ERRORS=$((JS_ERRORS + 1))
        ERRORS=$((ERRORS + 1))
    fi
done
if [ $JS_ERRORS -eq 0 ]; then
    echo "  PASS: 모든 JavaScript 파일 정상"
fi

# 5. 필수 파일 존재 검사
echo ""
echo "[5/5] 필수 파일 존재 검사..."
FILE_ERRORS=0
REQUIRED_FILES=(
    "CLAUDE.md"
    "PROGRESS.md"
    "docs/01-architecture.md"
    "docs/02-infra-rules.md"
    "docs/03-file-roles.md"
    "docs/04-workflow.md"
    "docs/05-quality-check.md"
    "docs/06-error-patterns.md"
    "docs/07-report-template.md"
)
for f in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$PROJECT_DIR/$f" ]; then
        echo "  FAIL: $f 누락"
        FILE_ERRORS=$((FILE_ERRORS + 1))
        ERRORS=$((ERRORS + 1))
    fi
done
if [ $FILE_ERRORS -eq 0 ]; then
    echo "  PASS: 필수 파일 모두 존재"
fi

# 결과 요약
echo ""
echo "========================================="
if [ $ERRORS -eq 0 ]; then
    echo " RESULT: ALL PASS"
else
    echo " RESULT: $ERRORS 건 실패"
fi
echo "========================================="

exit $ERRORS
