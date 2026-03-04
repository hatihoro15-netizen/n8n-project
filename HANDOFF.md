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
| 2026-03-04 | 아럽토 캡처 노드 분석 | 완료 |
| 2026-03-04 | 삽입 계획 수립 | 완료 |
| 2026-03-04 | 캡처 파이프라인 추가 (3개 노드 + 프롬프트/파싱/NCA 수정) | 완료 |
| 2026-03-04 | 캡처 결과 수집 → NCA 데이터 준비 connection 추가 | 완료 |
| 2026-03-04 | capture_targets AI 생성 제거 → 고정 빈 배열로 변경 | 완료 |

## 수정 내역 (캡처 파이프라인)

### 추가된 노드 (3개, 총 45노드)
| 노드 | 타입 | 위치 | ID |
|------|------|------|-----|
| 캡처 타겟 분리 | Code v2 | [1904,1480] | capture-node-001-split |
| 캡처 요청 v2 | HTTP Request v4.3 | [2128,1480] | capture-node-002-request |
| 캡처 결과 수집 | Code v2 | [2352,1480] | capture-node-003-collect |

### 수정된 노드 (3개)
| 노드 | 수정 내용 |
|------|-----------|
| 프롬프트 생성 | ~~capture_targets 지시 제거~~ (AI 생성 → 고정값으로 변경) |
| 콘텐츠 파싱 | capture_targets 파싱 로직 + return에 필드 추가 |
| NCA 데이터 준비 | $('캡처 결과 수집') 간접 참조 + 이미지 슬롯 대체 로직 |

### 연결 구조
```
시트 기록 ─┬─ TTS 요청 → ... → Merge [input 0]
           ├─ 세그먼트 분리 → ... → Merge [input 1]
           └─ 캡처 타겟 분리 → 캡처 요청 v2 → 캡처 결과 수집 ─→ NCA 데이터 준비
                                                                  (connection + $() 참조)
```

### 캡처 이미지 병용 로직 (NCA 데이터 준비)
- `captureResults.length > 0`: 기존 image 타입 슬롯 마지막 N개를 캡처 이미지로 대체
- `captureResults.length === 0`: 기존 이미지 검색 결과만 사용 (변경 없음)
- try-catch로 캡처 노드 미실행/실패 시 빈 배열 폴백

## 주의사항
- 원본 폴더(~/n8n-worktrees/onca/) 절대 수정 금지
- top-level nodes(45개)와 activeVersion.nodes(43개) 양쪽 다 수정 완료
- 직렬 삽입 시 $json 참조 깨짐 확인 완료 (병렬 분기이므로 기존 경로 영향 없음)
