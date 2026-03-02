# 인수인계 문서 — 아럽토 유튜브 숏츠 프로젝트

> 작성: 2026-03-03
> 브랜치: feature/sports-pick-v16
> 워크트리: /Users/gimdongseog/n8n-worktrees/sports

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 채널명 | 아럽토 |
| 홍보 대상 | 라이브365 (scoredata.org) |
| 콘텐츠 형식 | 유튜브 숏츠 (1080x1920, 60초 이내) |
| 핵심 메시지 | "모든 스포츠 정보를 라이브365에서 확인 가능" |
| 제작 방식 | 이미지 + TTS + 자막 + BGM → NCA FFmpeg 합성 |
| 이미지 소스 | 라이브365 사이트 캡처 (자체 저작권) + Pexels 보조 + MinIO 밈 |
| CTA 규칙 | 모든 영상 마지막에 "라이브365" 언급으로 귀결 |
| 콘텐츠 카테고리 | 7개 (프로토배당/경기분석/결과속보/적중인증/초보가이드/멀티종목/기능소개) |

---

## 2. 완료된 작업

### 작업 1: 프로젝트 정리
- 불필요한 파일 삭제 (구버전 JSON 12개, 스크립트 5개, 백업 9개, archive 전체, assets)
- 미디어 에셋을 claude-sports-v16/ 으로 이동 보관
- 커밋: `4bdab08`

### 작업 2: 1단계 — 콘텐츠 기획서 작성
- **파일**: `claude-sports-v16/콘텐츠기획서.md`
- 내용: 사이트 분석, 카테고리 7개 정의, CTA 전략, 파이프라인, 우선순위, 기술스택

### 작업 3: 2단계 — AI 프롬프트 설계
- **파일**: `claude-sports-v16/prompts_v1.md`
- 내용: 카테고리별 Gemini 프롬프트 7개 + 공통 규칙 + 출력 JSON 스키마
- 콘텐츠 파싱/이미지 URL 추출 노드 변경사항 포함

---

## 3. 2단계 프롬프트 수정 반영 내역 (4가지)

### 수정 1: capture_id 프리셋 시스템
- 문제: area가 자연어("배당률 표 전체")라 Puppeteer 자동화 시 매핑 불가
- 해결: `capture_id` 필드 추가 → 사전 정의된 CSS 셀렉터 프리셋과 매칭
- 총 20개 프리셋 정의 (home 7, analysis 5, proto 5, community 3)
- 동적 파라미터 필요 시 `capture_params: { match_id: "xxx" }` 사용
- 프리셋 전체 목록: prompts_v1.md "1. 캡처 프리셋 정의" 섹션 참조

### 수정 2: 템플릿 변수 적용
- 문제: 프롬프트에 데이터가 하드코딩
- 해결: `${data.sport}`, `${data.matchesFormatted}` 등 n8n에서 동적 주입
- 각 카테고리별 `buildXxxPrompt(data, toneBlock)` 함수로 구조화

### 수정 3: 밈 소싱 명확화
- MinIO 기존 카탈로그 재활용 (76.13.182.180:9000/memes/)
- mood별 폴더: thinking(14), excited(6), shocked(12), sad(7), angry(8), cool(12), celebrating(7), money(8) = 총 74개
- 로직: `MEME_CATALOG[meme_mood]` 배열에서 랜덤 선택 → URL 반환

### 수정 4: 카테고리별 말투 차이
- `friendly` 말투 신규 추가 (존댓말, 친절)
- 카테고리별 허용 말투:
  - Cat 1~4,6: hyung/angry/asmr (기존)
  - Cat 5 초보자: **friendly/asmr만** (친절 전용)
  - Cat 7 기능소개: **friendly/hyung** (자연스러운 추천)

---

## 4. 3단계: 해야 할 것 — 이미지 캡처 자동화

### 4-1. Puppeteer 캡처 서비스 구축
- Node.js + Puppeteer로 HTTP API 서버 구축
- 엔드포인트: `POST /capture`
- 입력: `{ capture_id, capture_params?, viewport: {w:1080, h:1920} }`
- 출력: 캡처 이미지 URL (MinIO에 저장 후 반환)
- capture_id → CSS 셀렉터 매핑 테이블은 prompts_v1.md 섹션 1 참조
- **주의**: CSS 셀렉터는 실제 사이트(scoredata.org) DOM 확인 후 확정 필요

### 4-2. n8n 이미지 URL 추출 노드 수정
- visual_type별 분기 로직:
  - `capture` → Puppeteer 캡처 서비스 HTTP 호출
  - `pexels` → 기존 Pexels API 호출
  - `meme` → 기존 MinIO MEME_CATALOG 랜덤 선택
- 기존 코드: sports_shortform_v16.json의 "이미지 URL 추출" 노드 참조

### 4-3. 캡처 이미지 처리
- 저장: MinIO (76.13.182.180:9000/captures/날짜/capture_id_timestamp.png)
- 크롭/리사이즈: 1080x1920 세로 숏츠에 맞게
  - 전체 페이지 캡처 → 1080x1920 뷰포트로 캡처
  - 부분 영역 → 1080 폭 캡처 후 1080x1080 center crop → 1080x1920 pad(black)
  - NCA 데이터 준비 노드의 기존 스케일링 로직 활용 가능

### 4-4. 이후 Phase 계획
- Phase 1: 캡처 서비스 + 워크플로우 수정 + 시트 생성
- Phase 2: 카테고리 1(프로토 배당) 영상 테스트 3개
- Phase 3: 카테고리 2~3 추가
- Phase 4: 전체 카테고리 + API/크롤링 + 업로드 자동화

---

## 5. 현재 파일 구조

```
/Users/gimdongseog/n8n-worktrees/sports/
├── .claude/                          # Claude Code 설정
├── .gitignore
├── CLAUDE.md                         # 프로젝트 작업 규칙
├── PROGRESS.md                       # 진행 상황 (온카스터디 시절, 업데이트 필요)
├── claude-sports-v16/
│   ├── HANDOFF.md                    # ★ 이 파일 (인수인계 문서)
│   ├── 콘텐츠기획서.md                 # 1단계: 전체 콘텐츠 기획
│   ├── prompts_v1.md                 # 2단계: AI 프롬프트 설계 (v1.1)
│   ├── sports_shortform_v16.json     # ★ 현재 n8n 워크플로우 (핵심 파일)
│   ├── oncastudy_memes/              # 밈 이미지 에셋 (8 카테고리)
│   │   ├── conclusion/  confident/  hook/  money/
│   │   ├── reaction/  smart/  victim/  warning/
│   ├── 주제별 영상/                    # 아웃트로/주제 영상 13개 (mp4)
│   ├── 짤/                            # 짤 에셋 1개
│   ├── 페페/                          # 페페 밈 12개
│   └── 효과음/                        # 효과음 8개 (bgm, 띠링, 뽀옥 등)
├── docs/                             # 프로젝트 문서 7개
│   ├── 01-architecture.md
│   ├── 02-infra-rules.md
│   ├── 03-file-roles.md
│   ├── 04-workflow.md
│   ├── 05-quality-check.md
│   ├── 06-error-patterns.md
│   └── 07-report-template.md
└── scripts/
    └── quality-check.sh              # 품질 검사 스크립트
```

---

## 6. 기술 스택 & 서버 정보

| 도구 | 용도 | 주소/버전 |
|------|------|-----------|
| n8n | 워크플로우 자동화 | 서버에서 실행 중 |
| Gemini | AI 콘텐츠 생성 | Google AI (n8n googleGemini 노드) |
| edge-tts | TTS 나레이션 | n8n HTTP 노출 |
| NCA (FFmpeg) | 영상 합성 | n8n httpRequest로 호출 |
| MinIO | 미디어 저장 | `http://76.13.182.180:9000` |
| Pexels API | 스톡 이미지 | n8n httpRequest (API 키 워크플로우 내) |
| Google Sheets | 주제/상태 관리 | 시트 ID: `1gkRjLIcK3HxbnTbLCvG6oknMGVt2uz9pgboM3EF_VKg` |
| Puppeteer | 사이트 캡처 (미구축) | 3단계에서 구축 예정 |

### MinIO 경로 규칙
- 밈: `http://76.13.182.180:9000/memes/{mood}/{filename}`
- 효과음: `http://76.13.182.180:9000/audio/{filename}`
- 아웃트로: `http://76.13.182.180:9000/outro/{filename}`
- 캡처 (예정): `http://76.13.182.180:9000/captures/{date}/{capture_id}_{timestamp}.png`

### 기존 워크플로우 노드 흐름 (sports_shortform_v16.json)
```
수동실행 → 종목결정 → [병렬] 오늘경기조회 + 이전픽조회
→ 경기목록파싱 → 순위표조회 → 부상자조회 → 상대전적조회
→ 데이터병합 → AI경기선택 → 경기선택파싱
→ 스포츠프롬프트생성 → AI콘텐츠생성(Gemini) → 콘텐츠파싱
→ [병렬] TTS요청 + 이미지검색
→ TTS결과처리 → 이미지URL추출 → Merge → Aggregate
→ NCA데이터준비 → NCA영상제작 → NCA결과처리 → 시트기록
```

---

## 7. Git 정보

| 항목 | 값 |
|------|-----|
| 브랜치 | `feature/sports-pick-v16` |
| 리모트 | `https://github.com/hatihoro15-netizen/n8n-project.git` |
| 메인 브랜치 | `main` |
| 최신 커밋 | `4bdab08` — 불필요한 파일 정리 |
| 워크트리 경로 | `/Users/gimdongseog/n8n-worktrees/sports` |
| 메인 저장소 | `/Users/gimdongseog/n8n-project` |

### 미커밋 변경사항
- `claude-sports-v16/콘텐츠기획서.md` (신규)
- `claude-sports-v16/prompts_v1.md` (신규)
- `claude-sports-v16/HANDOFF.md` (이 파일)

---

## 8. 새 세션에서 시작하기

```bash
cd /Users/gimdongseog/n8n-worktrees/sports
cat claude-sports-v16/HANDOFF.md       # 이 문서 읽기
cat claude-sports-v16/prompts_v1.md    # 프롬프트 설계 확인
cat claude-sports-v16/콘텐츠기획서.md    # 기획서 확인
```

**다음 작업**: 3단계 — 이미지 캡처 자동화 (위 섹션 4 참조)
