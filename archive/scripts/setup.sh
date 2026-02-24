#!/bin/bash
# 집 맥북에서 처음 한 번만 실행하면 됩니다
# 사용법: bash setup.sh

MEMORY_DIR="$HOME/.claude/projects/-Users-$(whoami)/memory"

mkdir -p "$MEMORY_DIR"
cp MEMORY.md "$MEMORY_DIR/MEMORY.md"
cp n8n_project_memory.md "$MEMORY_DIR/n8n_project.md"

echo "메모리 파일 복사 완료!"
echo "이제 claude 를 실행하세요."
