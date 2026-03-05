# 01-architecture.md — AO Pipeline 시스템 구조

## 개요
프롬프트 100% 반영 기반 AI 영상 자동 제작 + 유튜브 업로드.
플랫폼: YouTube (쇼츠 9:16 + 일반 16:9) / 제작 빈도: 하루 1~3개 / 예산: $150~300/월

## 기술 스택
| 레이어 | 기술 | 역할 |
|--------|------|------|
| 프론트엔드 | Next.js + Tailwind + shadcn/ui | 관리자 웹 UI (다크모드, 데스크탑 전용) |
| DB | Supabase (PostgreSQL) | 소스/영상/설정/Job 상태 관리 |
| 파일 저장소 | Supabase Storage | 이미지, 오디오, 영상 파일 |
| 워크플로우 | n8n (셀프호스팅) | AI API 연결 + 영상 파이프라인 |
| 이미지 생성 | Replicate API | Flux Pro, SDXL, Ideogram, Playground v2.5 |
| 텍스트 AI | Claude API / GPT-4o | 스크립트, 나레이션 생성 |
| TTS | ElevenLabs API | 나레이션 음성 생성 |
| 영상 편집 | Creatomate API | 씬 합성, 자막, 렌더링 |
| 업로드 | YouTube API (OAuth 2.0) | 자동 업로드 |

## 이미지/영상 소스 (3가지)
1. **사용자 직접 업로드** — 이미지 1~4장, 레퍼런스 영상
2. **AI 이미지 생성** — 프롬프트로 이미지 생성 (Flux Pro/SDXL/Ideogram)
3. **인터넷/유튜브** — 관련 이미지/영상 검색해서 가져오기

## 아키텍처: Producer / Worker / Queue

```
[웹 UI / 웹훅] → Producer → [Queue] → Worker → [YouTube]
                    ↓                    ↓
                [Supabase]          [Replicate / ElevenLabs / Creatomate]
```

### Producer (작업 등록, 병렬 가능)
1. 입력 수신 (웹훅/폼)
2. 필수값 검사
3. Job 생성 (job_id, status=queued)
4. Queue에 Push
5. 응답 (job_id 반환)

### Worker (작업 처리, 1건씩)
1. Queue에서 Pop (1건)
2. AO 프롬프트 조립 → 최종 실행 프롬프트
3. AI 이미지 생성 (필요 시)
4. TTS 생성 (ElevenLabs)
5. Creatomate 영상 렌더링 (템플릿 적용)
6. AI 썸네일 생성 (선택)
7. YouTube 업로드 (OAuth)
8. 상태 업데이트 + 로그 기록

### Job 상태 흐름
```
queued → processing → generated → uploading → uploaded
                ↘ failed (3회 자동 재시도 → retrying → processing)
```

### n8n Webhook 엔드포인트
| 트리거 | URL | 데이터 |
|--------|-----|--------|
| 이미지 생성 | /webhook/generate-image | 모델, 프롬프트, 개수 |
| 나레이션 생성 | /webhook/generate-script | 주제, 유형, 톤, AI 모델 |
| 영상 제작 | /webhook/make-video | 이미지, 스크립트, 목소리, 템플릿 |
| 업로드 | /webhook/upload-video | 영상, 제목, 예약시간 |

## AO 프롬프트 조립기
P1을 재작성하지 않음. P1 100% 유지 + 변수 슬롯 주입:
- {TOPIC}, {KEYWORDS}, {CATEGORY}
- {IMG_1}~{IMG_4}, {REF_VIDEO}
- (선택) {LANG}, {TONE}, {DURATION}, {ASPECT_RATIO}

## use_media 모드
| 모드 | 동작 |
|------|------|
| auto | 이미지/영상 있으면 활용, 없으면 프롬프트만 |
| forced | 제공된 미디어 반드시 사용 |
| off | 프롬프트만 사용 (미디어 무시) |

## 웹 관리자 UI (9탭)
1. 대시보드 (제작/업로드 현황 + Cost Dashboard)
2. 이미지 생성 (AI 모델 선택 + 생성)
3. 나레이션 생성 (스크립트 + TTS)
4. 영상 제작 (소스 조합 + 템플릿 + 렌더링)
5. 소스 라이브러리 (이미지/오디오/영상 관리)
6. 업로드 관리 (YouTube 설정 + 예약)
7. 작업 큐 (진행/대기/완료/실패)
8. 채널/API 연결 (OAuth + API Key)
9. 영상 템플릿 관리 (Creatomate 매핑)

## 기존 인프라 (공유)
- n8n: https://n8n.srv1345711.hstgr.cloud
- VPS: root@76.13.182.180
- Postgres: n8n-postgres (docker, DB: n8ndb)

## 에이전트 팀 역할
| 역할 | 담당 |
|---|---|
| 인프라 에이전트 | 서버/배포/n8n 인스턴스/infra 파일 |
| 워크플로우 에이전트 | n8n 노드/연결/로직/*.json |
| 콘텐츠 에이전트 | 프롬프트/캐릭터/대사/콘텐츠 노드 |
| 검증 에이전트 | 테스트/lint/동작 확인 |

에이전트 규칙:
- 자기 역할 외 파일 수정 금지
- 작업 전 관련 docs/ 읽기
- 작업 완료 후 보고서 작성 (발견/수정/판단/파일/검증)

## 개발 우선순위
| 순위 | 기능 |
|------|------|
| 1순위 | 채널/API 연결, 이미지 생성, 영상 제작+큐 |
| 2순위 | 나레이션 생성, 업로드 관리, 영상 템플릿 |
| 3순위 | 소스 라이브러리, 대시보드+비용, AI 썸네일 |
