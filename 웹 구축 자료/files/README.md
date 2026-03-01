# Phase 2 적용 가이드

## 방법 1: Git Patch (추천)
```bash
cd ~/n8n-project
git checkout feature/web-app
git am 0001-feat-Phase-2.patch
```

## 방법 2: 파일 직접 복사
phase2-files/ 폴더 안의 packages/ 폴더를 프로젝트 루트에 덮어쓰기

```bash
cp -r phase2-files/packages ~/n8n-project/
```

## 파일 목록 (8개)

### 🆕 신규 파일 (3개)
| 파일 | 경로 | 설명 |
|------|------|------|
| production-progress.tsx | components/ | 7단계 진행 스텝퍼 |
| video-player.tsx | components/ | 9:16 숏폼 영상 플레이어 |
| page.tsx | productions/[id]/ | 제작 상세 페이지 |

### ✏️ 수정 파일 (5개)  
| 파일 | 경로 | 변경 내용 |
|------|------|----------|
| use-dashboard.ts | hooks/ | useProduction 훅 추가 (3초 자동 리프레시) |
| page.tsx | productions/ | 행 클릭→상세 이동 |
| page.tsx | productions/new/ | 제작 후 상세 페이지로 리다이렉트 |
| page.tsx | (dashboard)/ | 퀵 버튼 + 최근 제작 행 클릭 |
| productions.ts | backend/routes/ | callback에 videoUrl/thumbnailUrl/script 지원 |
