# HANDOFF - 온카 캡처 v16

> 마지막 업데이트: 2026-03-04

## 브랜치 정보
- **브랜치**: feature/onca-capture (feature/onca-shortform-v16에서 분기)
- **작업 폴더**: ~/n8n-worktrees/onca-capture/
- **원본 폴더**: ~/n8n-worktrees/onca/ (수정 금지)

## 목표
온카 설명형 워크플로우(v16)에 웹사이트 캡처 기능 추가

## 파일 구조
| 파일 | 역할 |
|------|------|
| claude-tools/onca_shortform_v16.json | 원본 복사본 (이 폴더 내 참고용) |
| claude-tools/onca_shortform_v16_capture.json | 캡처 기능 추가 작업본 |

## 캡처 서비스
- **엔드포인트**: POST http://76.13.182.180:3100/capture
- **요청 형식**: `{ url, capture_mode, selector, style_mode, job_id, filename }`
- **응답 형식**: `{ url: "MinIO 이미지 URL" }`
- **헬스체크**: GET http://76.13.182.180:3100/health
- **참고 구현**: ~/n8n-worktrees/sports/claude-sports-v16/arupto_shortform_v2.json

## 작업 이력
| 날짜 | 작업 | 상태 |
|------|------|------|
| 2026-03-04 | 복사본 생성 + 워크플로우 이름 변경 | 완료 |
| 2026-03-04 | 아럽토 캡처 노드 분석 | 진행중 |
| 2026-03-04 | 삽입 계획 수립 | 대기 |

## 주의사항
- 원본 폴더(~/n8n-worktrees/onca/) 절대 수정 금지
- top-level nodes와 activeVersion.nodes 양쪽 다 수정 필요
- 직렬 삽입 시 $json 참조 깨짐 확인 필수
