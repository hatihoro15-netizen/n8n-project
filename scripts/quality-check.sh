#!/bin/bash
# quality-check.sh - 프로젝트 품질 자동 검사 스크립트

set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

# 프로젝트 루트 디렉토리 (스크립트 위치 기준)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

print_result() {
    local status=$1
    local message=$2
    if [ "$status" = "PASS" ]; then
        echo -e "  ${GREEN}[PASS]${NC} $message"
        PASS=$((PASS + 1))
    elif [ "$status" = "FAIL" ]; then
        echo -e "  ${RED}[FAIL]${NC} $message"
        FAIL=$((FAIL + 1))
    elif [ "$status" = "WARN" ]; then
        echo -e "  ${YELLOW}[WARN]${NC} $message"
        WARN=$((WARN + 1))
    fi
}

echo "================================"
echo " 품질 검사 시작"
echo "================================"
echo ""

# 1. 필수 파일 존재 검사
echo "1. 필수 파일 존재 검사"
for file in CLAUDE.md PROGRESS.md; do
    if [ -f "$file" ]; then
        print_result "PASS" "$file 존재"
    else
        print_result "FAIL" "$file 없음"
    fi
done

if [ -d "docs" ]; then
    print_result "PASS" "docs/ 디렉토리 존재"
else
    print_result "FAIL" "docs/ 디렉토리 없음"
fi
echo ""

# 2. JSON 문법 검사
echo "2. JSON 문법 검사"
json_files=$(find . -name "*.json" -not -path "./.git/*" -not -path "./node_modules/*" 2>/dev/null || true)
if [ -z "$json_files" ]; then
    print_result "WARN" "JSON 파일 없음"
else
    while IFS= read -r file; do
        if python3 -m json.tool "$file" > /dev/null 2>&1; then
            print_result "PASS" "$file"
        else
            print_result "FAIL" "$file - JSON 문법 오류"
        fi
    done <<< "$json_files"
fi
echo ""

# 3. JavaScript 문법 검사
echo "3. JavaScript 문법 검사"
js_files=$(find . -name "*.js" -not -path "./.git/*" -not -path "./node_modules/*" 2>/dev/null || true)
if [ -z "$js_files" ]; then
    print_result "WARN" "JavaScript 파일 없음"
else
    while IFS= read -r file; do
        if node --check "$file" 2>/dev/null; then
            print_result "PASS" "$file"
        else
            print_result "FAIL" "$file - JS 문법 오류"
        fi
    done <<< "$js_files"
fi
echo ""

# 4. Python 문법 검사
echo "4. Python 문법 검사"
py_files=$(find . -name "*.py" -not -path "./.git/*" -not -path "./node_modules/*" 2>/dev/null || true)
if [ -z "$py_files" ]; then
    print_result "WARN" "Python 파일 없음"
else
    while IFS= read -r file; do
        if python3 -c "compile(open('$file').read(), '$file', 'exec')" 2>/dev/null; then
            print_result "PASS" "$file"
        else
            print_result "FAIL" "$file - Python 문법 오류"
        fi
    done <<< "$py_files"
fi
echo ""

# 5. 하드코딩 검사
echo "5. 하드코딩 검사"
# IP 주소 패턴 (설정 파일/문서 제외)
hardcoded_ip=$(grep -rn --include="*.js" --include="*.py" --include="*.sh" -E '\b[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\b' . 2>/dev/null | grep -v "127.0.0.1" | grep -v "0.0.0.0" | grep -v ".git/" || true)
if [ -z "$hardcoded_ip" ]; then
    print_result "PASS" "IP 하드코딩 없음"
else
    print_result "WARN" "IP 하드코딩 의심:"
    echo "$hardcoded_ip" | head -5
fi

# 비밀번호/API키 패턴
hardcoded_secret=$(grep -rn --include="*.js" --include="*.py" -iE '(password|secret|api_key|apikey)\s*[=:]\s*["\x27][^"\x27]+["\x27]' . 2>/dev/null | grep -v ".git/" || true)
if [ -z "$hardcoded_secret" ]; then
    print_result "PASS" "비밀번호/API키 하드코딩 없음"
else
    print_result "FAIL" "비밀번호/API키 하드코딩 발견:"
    echo "$hardcoded_secret" | head -5
fi
echo ""

# 결과 요약
echo "================================"
echo " 검사 결과 요약"
echo "================================"
echo -e "  ${GREEN}PASS${NC}: $PASS"
echo -e "  ${RED}FAIL${NC}: $FAIL"
echo -e "  ${YELLOW}WARN${NC}: $WARN"
echo ""

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}검사 실패 - 수정 후 재실행 필요${NC}"
    exit 1
else
    echo -e "${GREEN}검사 통과${NC}"
    exit 0
fi
