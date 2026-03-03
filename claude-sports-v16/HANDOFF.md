# 인수인계 문서 — 아럽토 유튜브 숏츠 프로젝트

> 최종 업데이트: 2026-03-03 (scoredata.org 마이그레이션 + TTS batching 수정 완료)
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
| 이미지 소스 | 라이브365 캡처 + Pexels + MinIO 밈 |
| CTA | 모든 영상 "라이브365" 언급 귀결 |
| 카테고리 | 7개 (프로토배당/경기분석/결과속보/적중인증/초보가이드/멀티종목/기능소개) |

---

## 2. 완료 단계 요약

| 단계 | 내용 | 산출물 | 상태 |
|------|------|--------|------|
| 1단계 | 콘텐츠 기획서 작성 | 콘텐츠기획서.md | 완료 |
| 2단계 | AI 프롬프트 설계 (7개 카테고리) | prompts_v1.md | 완료 |
| 3단계 | 캡처 서비스 구축 | capture-service/ (8파일) | ✅ 서버 배포 완료 |
| 3.5단계 | 캡처 서비스 v1.2 확장 | capturer/server/uploader/image-processor | 완료 (테스트 필요) |
| 4단계 | 워크플로우 구축 + 프롬프트 연동 + 배당 소싱 | arupto_shortform_v1.json | 완료 (테스트 필요) |
| 4.5단계 | n8n 코드노드 준비 + NCA 템플릿 A/B/C 변환 | sfx/timeline JS + nca_template_{A,B,C}_converted.json | 완료 |
| 4.6단계 | Gemini 시스템 프롬프트 v1.2 확정 | gemini_system_prompt_v1.2_final.txt | 완료 |
| 5단계 | v2 워크플로우 조립 | arupto_shortform_v2.json (29노드) | 완료 (테스트 필요) |
| 5.1단계 | TTS 3-segment concat | NCA 템플릿 A/B/C + v2 코드노드 | 완료 |

---

## 3. 파일 구조

```
claude-sports-v16/
├── HANDOFF.md                    # ★ 이 파일
├── 콘텐츠기획서.md                 # 1단계: 전체 기획
├── prompts_v1.md                 # 2단계: 7개 카테고리 프롬프트 설계
├── arupto_shortform_v1.json      # ★ 아럽토 전용 워크플로우 (32노드)
├── sports_shortform_v16.json     # 기존 흑형스포츠 워크플로우 (수정 안 함)
├── capture-service/              # ★ 3단계: Puppeteer 캡처 서비스
│   ├── package.json
│   ├── .env.example
│   ├── Dockerfile                # Docker 빌드 (node:20-slim + Chromium + dumb-init)
│   ├── docker-compose.yml        # docker compose up -d 로 실행
│   ├── .dockerignore
│   └── src/
│       ├── server.js             # POST /capture, /health (포트 3100) — v1.2: v1/v2 분기 라우팅
│       ├── config.js             # 환경변수 로딩
│       ├── browser.js            # Puppeteer 싱글턴
│       ├── capturer.js           # v1.2: capturePreset + captureAdvanced + style_mode + capture_mode
│       ├── uploader.js           # MinIO 업로드 — v1.2: jobId/filename 경로 지원
│       ├── image-processor.js    # Sharp — v1.2: skipResize 옵션 추가
│       └── presets.js            # 20개 프리셋 (변경 없음)
├── n8n_code_sfx_safety_mapping.js # ★ 4.5단계: SFX 폴백 매핑 (MinIO 경로 수정본)
├── n8n_code_timeline_assemble.js # ★ 4.5단계: TTS 기반 타임라인 조립
├── nca_template_A_converted.json # ★ 4.5단계: VS분할 템플릿 (NCA 서버 포맷)
├── nca_template_B_converted.json # ★ 4.5단계: 스크롤/줌인 템플릿 (NCA 서버 포맷)
├── nca_template_C_converted.json # ★ 4.5단계: 뉴스 티커 템플릿 (NCA 서버 포맷)
├── gemini_system_prompt_v1.2_final.txt # ★ 4.6단계: Gemini 시스템 프롬프트 (최종)
├── arupto_shortform_v2.json     # ★ 5단계: v2 워크플로우 (29노드, 템플릿 기반)
├── oncastudy_memes/              # 밈 에셋 (8카테고리, 74개)
├── 주제별 영상/                    # 아웃트로 mp4
├── 짤/ 페페/ 효과음/               # 미디어 에셋
```

---

## 4. arupto_shortform_v1.json 워크플로우 (32노드)

### 노드 흐름
```
수동실행 → 종목결정
  ├→ 오늘경기조회 → 경기목록파싱 → 순위표조회 → 부상자조회 → 상대전적조회
  ├→ 이전픽조회
  └→ 프로토배당조회 → 배당데이터파싱          ★ 신규 (the-odds-api.com)
→ 데이터병합 → AI경기선택 → 경기선택파싱
→ 스포츠프롬프트생성 (7개 카테고리 switch 분기)  ★ 4단계에서 교체
→ AI콘텐츠생성(Gemini) → 콘텐츠파싱 → 시트기록
→ [병렬] TTS요청 + 세그먼트분리
→ 세그먼트분리 → IF캡처분기                     ★ 3단계에서 추가
  ├→ [capture] 캡처요청 → 캡처URL정리
  └→ [else] 이미지검색(Pexels) → 이미지URL추출
→ Merge2 → Merge(TTS합류) → Aggregate
→ NCA데이터준비 (capture 스케일링 포함)
→ NCA영상제작 → NCA결과처리 → 상태업데이트
```

### 3단계에서 추가한 것 (sports_shortform_v16.json은 수정 안 함)
- IF캡처분기, 캡처요청, 캡처URL정리, Merge2 (4노드)
- 세그먼트분리에 capture_id/capture_params/description 필드
- NCA에서 capture 이미지는 크롭 없이 1080x1920 전체 표시
- 콘텐츠파싱에서 capture visual_type 검증

### 4단계에서 추가/수정한 것
- **프롬프트 생성 노드 전체 교체**: 7개 buildXxxPrompt 함수 + switch 분기
  - TONE_STYLES 4종 (hyung/angry/asmr/friendly)
  - CATEGORY_TONES 카테고리별 말투 제한
  - COMMON_RULES 공통 규칙 블록
- **프로토 배당 조회 노드 추가**: the-odds-api.com HTTP 호출
- **배당 데이터 파싱 노드 추가**: odds → matchesFormatted 변환
- **종목 결정 노드 수정**: ODDS_SPORT_MAP 매핑 추가
- **데이터 병합/경기선택파싱 수정**: matchesFormatted 필드 전달
- **CTA 전체 교체**: "온카스터디" → "라이브365" (0잔여 확인)

---

## 5. 필요한 환경변수

| 변수 | 용도 | 실제 값 |
|------|------|---------|
| ODDS_API_KEY | the-odds-api.com API 키 | `921688c663b829bbd79bab1d23c21440` |
| CAPTURE_HOST | 캡처 서비스 주소 | `76.13.182.180` |
| CAPTURE_PORT | 캡처 서비스 포트 | `3100` |
| MINIO_ENDPOINT | MinIO 주소 | `76.13.182.180` |
| MINIO_PORT | MinIO 포트 | `9000` |
| MINIO_ACCESS_KEY | MinIO 접근 키 | `admin` |
| MINIO_SECRET_KEY | MinIO 비밀 키 | `NcaMin10S3cure!` |
| MINIO_BUCKET | MinIO 버킷 | `arubto` |

---

## 6. 배포 순서

```bash
# 1. 캡처 서비스 — ✅ 배포 완료 (2026-03-03)
# 서버: 76.13.182.180 | 경로: /opt/capture-service/ | 포트: 3100
# 컨테이너명: capture-service | 이미지: capture-service-capture-service
ssh root@76.13.182.180
curl http://localhost:3100/health  # {"status":"ok","presets":20}

# 재배포 시:
# cd /opt/capture-service && docker compose up -d --build

# 2. MinIO 버킷 생성
mc mb myminio/captures && mc anonymous set download myminio/captures

# 3. n8n 환경변수 추가
# CAPTURE_HOST, ODDS_API_KEY

# 4. 워크플로우 임포트
# arupto_shortform_v1.json을 n8n에 임포트

# 5. Google Sheets — ✅ 생성 완료 (아래 참고)
```

---

## 7. Google Sheets — ✅ 생성 완료

**v2 시트 (아럽토 v2)**
- 시트 ID: `1SCzznS9eLMmyK_jQq0qFSx4zWKmwIK6dGesFEgm0brA`
- URL: https://docs.google.com/spreadsheets/d/1SCzznS9eLMmyK_jQq0qFSx4zWKmwIK6dGesFEgm0brA/edit
- 시트명(탭): `스포츠 픽` (기본 "아럽토 v2" → "스포츠 픽"으로 변경 완료)
- 컬럼 21개 (1행 헤더, 볼드, 고정):

| 컬럼 | 설명 |
|------|------|
| id | 자동증가 |
| created_at | 생성일시 |
| category_id | 카테고리 번호 (1~7) |
| template_id | NCA 템플릿 (A/B/C) |
| status | 대기/생성중/완료/실패 |
| match_title | 경기 제목 |
| match_date | 경기 날짜 |
| home_team | 홈팀 |
| away_team | 어웨이팀 |
| tts_total_dur_sec | TTS 총 길이 (초) |
| segments_dur_json | 세그먼트별 duration JSON |
| render_duration_sec | 렌더링 소요 시간 |
| video_url | 완성 영상 URL |
| thumbnail_url | 썸네일 URL |
| minio_path | MinIO 저장 경로 |
| error_message | 에러 메시지 |
| retry_count | 재시도 횟수 |
| script_json | Gemini 스크립트 원본 |
| capture_urls | 캡처 URL 목록 |
| odds_data | 배당 데이터 |
| upload_status | 업로드 상태 |

**기존 v1 시트 (스포츠 픽)** — 수정 안 함
- 시트 ID: `1gkRjLIcK3HxbnTbLCvG6oknMGVt2uz9pgboM3EF_VKg`

| 컬럼 | 설명 | 예시 |
|------|------|------|
| id | 자동증가 | 1 |
| category | 카테고리 번호 | 1 |
| categoryName | 카테고리명 | 프로토 배당 분석 |
| topic | 세부 주제 | 오늘 고배당 탑3 |
| sport | 종목 | soccer |
| league | 리그 | Premier League |
| matchup | 대진 | 맨시티 vs 리버풀 |
| featureFocus | 기능포커스 (Cat 7) | 실시간 스코어 |
| toneStyle | 사용 말투 | 형 |
| status | 대기/생성중/완료/실패 | 완료 |
| createdAt | 생성일 | 2026-03-03 |
| videoUrl | 영상 URL | http://... |
| pick | 최종 픽 | 맨시티 승 |
| pickResult | 적중/실패/미확인 | 적중 |
| hookTitle | 훅 제목 | 천 원으로 3만원? |
| confidence | 높음/보통/낮음 | 높음 |
| notes | 메모 | |

---

## 8. capture-service v1.2 변경사항 (3.5단계)

### 수정 파일 4개
| 파일 | 변경 | 핵심 |
|------|------|------|
| capturer.js | 59줄→309줄 | applyCommonCleanup, applyStyleMode, captureLongElement, captureWithMode, captureAdvanced 추가 |
| image-processor.js | processImage 시그니처 확장 | `{ skipResize: true }` → 리사이즈 건너뜀 (element/long용) |
| uploader.js | uploadCapture 시그니처 확장 | `{ job_id, filename }` → `{날짜}/{jobId}/{filename}` 경로 |
| server.js | POST /capture 분기 로직 | capture_id만 → capturePreset (v1), url/capture_mode/style_mode → captureAdvanced (v2) |

### style_mode 4종
| 모드 | 동작 |
|------|------|
| CLEAN | 배경 투명 + 타겟 카드형 (흰배경, 둥근모서리, 그림자) |
| FONT_UP | 폰트 1.15배 + 굵게 + 진한색 |
| ZOOM | transform scale (기본 1.2배, style_args.scale로 조절) |
| HIGHLIGHT | 전체 dim 오버레이 + 타겟만 밝게 (z-index) |

### capture_mode 3종
| 모드 | 동작 |
|------|------|
| full_page | 뷰포트 크기 캡처 (기본) |
| element | selector 필수 → 해당 엘리먼트만 캡처 |
| long | selector 있으면 scrollHeight 기반 확장 캡처 (상한 16000px), 없으면 fullPage |

### 하위 호환
- 기존 `POST /capture { "capture_id": "home_full_page" }` → capturePreset() 경로 그대로
- 새 파라미터 없으면 기존 동작 100% 동일

### v2 요청 예시
```json
POST /capture
{
  "url": "https://scoredata.org/match/123",
  "capture_mode": "element",
  "selector": "#odds-table",
  "style_mode": "HIGHLIGHT",
  "style_args": { "scale": 1.2 },
  "omitBackground": true,
  "job_id": "arupto-001",
  "filename": "odds.png"
}
```

### 참고한 레퍼런스
- `arubto_FINAL_BUNDLE_v1.2.1/nextstep_pack/server.js` (applyCommonCleanup, applyStyleMode)
- `arubto_FINAL_BUNDLE_v1.2.1/patch_pack/puppeteer_long_capture_patch.js` (captureLongElement, captureWithMode)

---

## 9. n8n 코드노드 + NCA 템플릿 변환 (4.5단계)

### 9-A. SFX 안전 매핑 (`n8n_code_sfx_safety_mapping.js`)
- 원본: `arubto_FINAL_BUNDLE_v1.2.1/patch_pack/n8n_code_sfx_safety_mapping.js`
- 변경: SFX_KEY 경로를 실제 MinIO 파일로 교체

| 키 | 수정 전 | 수정 후 |
|---|---|---|
| whoosh | (없었음) | `audio/sfx_whoosh1.mp3` |
| swoosh | `audio/packs/sfx/swoosh.mp3` | `audio/sfx_whoosh1.mp3` |
| pop | `audio/packs/sfx/pop.mp3` | `audio/sfx_pop_user.mp3` |
| ding | `audio/packs/sfx/ding.mp3` | `audio/sfx_ding1.mp3` |
| ding2 | `audio/packs/sfx/ding2.mp3` | `audio/sfx_ding2.mp3` |
| ppook | `audio/packs/sfx/ppook.mp3` | `audio/sfx_ppook.wav` |
| wow | `audio/packs/sfx/wow.mp3` | `audio/sfx_wow.wav` |

- alias 유지: cash→ding, cheer→pop
- 최후 폴백: swoosh → whoosh로 변경
- MINIO_BASE_URL 폴백 IP 유지 (환경변수 미설정 시 안전)

### 9-B. 타임라인 조립 (`n8n_code_timeline_assemble.js`)
- 원본 그대로 복사 (변경 없음)
- TTS duration 기반으로 intro/body/outro 시간 계산
- 템플릿 B용 HOLD/SCROLL 파라미터 산출

### 9-C. NCA 템플릿 A 변환 (`nca_template_A_converted.json`)
- 원본: `arubto_FINAL_BUNDLE_v1.2.1/nextstep_pack/nca_template_A.json` (GPT filter_graph 형식)
- 변환: 실제 NCA 서버 `inputs/filters/outputs` 형식

**구조:**
- inputs 8개: bg(0) + team_a(1) + team_b(2) + vs_stats(3) + narr_intro(4) + narr_body(5) + narr_outro(6) + bgm(7)
- filters: 비디오 5단계 + 오디오(3-concat+BGM) `;`으로 연결한 단일 filter_complex
- outputs: `{ option, argument }` 형식 (v1 NCA 데이터 준비 노드와 동일)

**filter_complex 체인:**
```
[0:v]scale→crop→setsar→fps[base]
→ [base][1:v]overlay=y:260[v1]
→ [v1][2:v]overlay=y:980[v2]
→ [v2][3:v]overlay=y:700[v3]
→ [v3]drawtext×4[video_out]
→ [4:a]asetpts[nr1];[5:a]asetpts[nr2];[6:a]asetpts[nr3]
→ [nr1][nr2][nr3]concat=n=3:v=0:a=1[narr]
→ [7:a]atrim→afade→volume[bgm_d]
→ [narr][bgm_d]amix[audio_out]
```

**플레이스홀더 18개:** bg, team_a_card, team_b_card, vs_stats, narr_intro, narr_body, narr_outro, bgm_audio, duration_sec, fontfile, hook_text, key_point_text, conclusion_text, cta_text, reveal_t, bgm_volume, fade_out_start, output_filename

### 9-D. NCA 템플릿 B 변환 (`nca_template_B_converted.json`)
- 원본: `arubto_FINAL_BUNDLE_v1.2.1/nextstep_pack/nca_template_B.json` (스크롤/줌인)
- 변환: 실제 NCA 서버 `inputs/filters/outputs` 형식

**구조:**
- inputs 5개: long_capture(0) + narr_intro(1) + narr_body(2) + narr_outro(3) + bgm(4)
- 입력 0을 bg(블러)와 fg(전경) 양쪽에서 사용
- filters: 비디오 4단계 + 오디오(3-concat+BGM)

**filter_complex 체인:**
```
[0:v]scale→crop→boxblur→setsar→fps[bg]
→ [0:v]scale=980:-1,pad=1080[fg]
→ [bg][fg]overlay(스크롤 y 수식)[v0]
→ [v0]drawtext(cta)[video_out]
→ [1:a]asetpts[nr1];[2:a]asetpts[nr2];[3:a]asetpts[nr3]
→ [nr1][nr2][nr3]concat=n=3:v=0:a=1[narr]
→ [4:a]atrim→afade→volume[bgm_d]
→ [narr][bgm_d]amix[audio_out]
```

**스크롤 y 수식:** `if(lte(overlay_h,main_h), start, if(lt(t,HOLD), start, max(-(overlay_h-main_h), start-((t-HOLD)/SCROLL)*(overlay_h-main_h))))`

**플레이스홀더 14개:** long_capture, narr_intro, narr_body, narr_outro, bgm_audio, duration_sec, fontfile, overlay_x, overlay_y_start, HOLD, SCROLL, cta_text, bgm_volume, fade_out_start, output_filename

### 9-E. NCA 템플릿 C 변환 (`nca_template_C_converted.json`)
- 원본: `arubto_FINAL_BUNDLE_v1.2.1/nextstep_pack/nca_template_C.json` (뉴스 티커)
- 변환: 실제 NCA 서버 `inputs/filters/outputs` 형식

**구조:**
- inputs 7개: bg(0) + scoreboard(1) + frame_overlay(2) + narr_intro(3) + narr_body(4) + narr_outro(5) + bgm(6)
- filters: 비디오 4단계 + 오디오(3-concat+BGM)

**filter_complex 체인:**
```
[0:v]scale→crop→boxblur→setsar→fps[bg]
→ [bg][1:v]overlay=center,y:520[v1]
→ [v1][2:v]overlay=0,0[v2]
→ [v2]drawtext(headline)+drawtext(ticker scroll)+drawtext(cta)[video_out]
→ [3:a]asetpts[nr1];[4:a]asetpts[nr2];[5:a]asetpts[nr3]
→ [nr1][nr2][nr3]concat=n=3:v=0:a=1[narr]
→ [6:a]atrim→afade→volume[bgm_d]
→ [narr][bgm_d]amix[audio_out]
```

**티커 스크롤:** `x=w-mod(t*{{ticker_px_per_sec}},(text_w+w))` — 좌→우 무한 스크롤

**플레이스홀더 16개:** bg, scoreboard, frame_overlay, narr_intro, narr_body, narr_outro, bgm_audio, duration_sec, fontfile, headline_text, ticker_text, ticker_px_per_sec, cta_text, bgm_volume, fade_out_start, output_filename

### 9-F. Gemini 시스템 프롬프트 v1.2 (`gemini_system_prompt_v1.2_final.txt`)
- 원본 참고: `arubto_FINAL_BUNDLE_v1.2.1/nextstep_pack/gemini_system_prompt_v1.2.txt` (GPT 작성)
- 기존 참고: `prompts_v1.md` (카테고리별 7개 프롬프트 + 톤 스타일)
- 산출물: 346줄 / 16KB

**구조 (9개 섹션):**
1. ROLE + 채널 정보
2. HARD RULES (컴플라이언스)
3. TEMPLATE SELECTION (cat→template 매핑)
4. ALLOWED ENUMS
5. SCHEMA v1.2 (필수 키)
6. TONE STYLES — 가이드만 (JSON에 tone 필드 없음)
7. CATEGORY-SPECIFIC INSTRUCTIONS (7개)
8. COMMON RULES
9. CAPTURE TARGETS GUIDANCE + OUTPUT REQUIREMENTS

**v1에서 가져온 것:**
- 카테고리별 영상 구조 (16줄 → 3세그먼트 intro/body/outro로 재배치)
- 카테고리별 팩트 규칙 / 콘텐츠 규칙
- 4종 말투 스타일 + 카테고리별 허용 매핑
- 카테고리별 category_data 필드
- 공통 규칙 (한국어 구어체, 영어 금지, CTA)

**v1.2 GPT에서 가져온 것:**
- Script JSON v1.2 스키마 (capture_targets, segments, visual_plan, bgm, compliance)
- template_id 자동 매핑 (1,4,5→B / 2,6→A / 3,7→C)
- 허용 enum 정의
- 캡처 타겟 가이드, 템플릿 B 기본값

**주의사항 반영:**
- tone: 프롬프트 가이드로만 남김 (스키마에 필드 추가 안 함)
- selector 경고: "ASSUMED EXAMPLES — verify against actual scoredata.org DOM"
- v1.3 optional (modules, audio_plan): 제외

---

## 10. arupto_shortform_v2.json 워크플로우 (5단계, 29노드)

### v1 대비 핵심 변경
| 항목 | v1 | v2 |
|------|----|----|
| Gemini 출력 | images[] + subtitles[] | Script JSON v1.2 (capture_targets, segments, template_id) |
| 프롬프트 | 7개 buildXxxPrompt 인라인 | gemini_system_prompt_v1.2 시스템 메시지 |
| 캡처 | preset 기반 (capture_id) | v1.2 API (url, selector, style_mode, capture_mode) |
| 이미지 소싱 | Pexels + 밈 카탈로그 + 캡처 | 캡처만 (capture_targets[]) |
| NCA | 인라인 filter_complex 400줄 | 템플릿 A/B/C JSON + 플레이스홀더 치환 |
| TTS | 전체 텍스트 1회 호출 | 세그먼트별 3회 호출 (정확한 duration) |
| SFX | NCA 노드 인라인 | 별도 코드노드 (sfx_safety_mapping) |
| 타이밍 | 글자수 비율 추정 | TTS duration + timeline_assemble 코드노드 |

### 노드 흐름
```
Phase 1: 데이터 수집 (scoredata.org 기반, 13노드)
수동실행/웹훅 → 종목결정 (category 1~7 랜덤, 말투 3종 랜덤)
  ├→ 이전픽조회 (Sheets)
  └→ 오늘경기조회 (scoredata.org/api/scores/live) → 경기목록파싱 (주요리그 필터→랜덤선택)
      ├→ 순위표조회 → 부상자조회 → 상대전적조회
      └→ 프로토배당조회 → 배당데이터파싱
→ 데이터병합 → AI경기선택(Gemini) → 경기선택파싱

Phase 2: AI 스크립트 생성 (4노드)
→ v1.2 프롬프트 조립
→ AI 스크립트 생성 (Gemini + v1.2 시스템 프롬프트)
→ 스크립트 파싱 (v1.2 스키마 검증)
→ 시트 기록

Phase 3: 에셋 수집 (6노드, 병렬)
→ [병렬A] TTS 세그먼트 분리 → TTS 요청(x3) → TTS 결과 처리
→ [병렬B] 캡처 타겟 분리 → 캡처 요청 v2 → 캡처 결과 수집

Phase 4: 조립 + 렌더 (6노드)
→ SFX 매핑
→ 타임라인 조립
→ NCA 데이터 준비 v2 (템플릿 선택 + 플레이스홀더 치환)
→ NCA 영상 제작
→ NCA 결과 처리
→ 상태 업데이트
```

### v1에서 제거된 노드 (7개)
스포츠 프롬프트 생성, 세그먼트 분리, IF캡처분기, 이미지 검색(Pexels), 이미지 URL 추출(밈 카탈로그), Merge2, Aggregate

### NCA 데이터 준비 v2 플레이스홀더 매핑
- 템플릿 A/B/C JSON이 코드 안에 인라인으로 포함됨 (3-segment narration 대응)
- `replacePlaceholders()` 함수로 `{{key}}` → 실제 값 일괄 치환
- capture_results[0..3] → 템플릿별 캡처 슬롯 자동 매핑
- TTS 3개 세그먼트 → narr_intro/narr_body/narr_outro 각각 NCA 입력으로 전달
- NCA filter_complex 안에서 `concat=n=3:v=0:a=1` 로 합침 (5.1단계에서 해결)

### 알려진 제한사항 / TODO
1. ~~**TTS 오디오 concat**~~ → 5.1단계에서 해결 (NCA filter에서 3-segment concat)
2. **BGM 다양화**: 현재 모든 pack이 bgm_new.mp3로 매핑. 실제 BGM 에셋 확보 후 매핑 수정
3. **capture_targets → 템플릿 슬롯 매핑**: Gemini가 올바른 순서로 capture_targets를 생성하는지 검증 필요
4. **template D/R**: 현재 A/B/C만 구현. D(랭킹), R(리비전) 템플릿 미구현
5. ~~**경기 없는 리그 처리**~~: → scoredata.org `/api/scores/live` 전환으로 해결 (라이브/예정 경기 있는 리그만 선택)

---

## 12. scoredata.org API 조사 결과 (경기 데이터 소싱 변경용)

### 발견된 API

| 엔드포인트 | 설명 | 인증 |
|-----------|------|------|
| `/api/scores/date?date=YYYY-MM-DD&sport=football` | 날짜별 경기 목록 | 불필요 |
| `/api/scores/live` | 라이브 경기 (스포츠별 분류) | 불필요 |
| `/api/scores/match/{id}` | 경기 상세 (이벤트, 하프타임) | 불필요 |
| `/api/search?q=keyword` | 팀/게시글 검색 | 불필요 |

### 경기 데이터 구조

```json
{
  "matches": [{
    "id": 1501582, "sport": "football",
    "league": { "id": 322, "name": "[RUS D1] 러시아 - 프리미어 리그", "logo": "..." },
    "home": { "id": 3447, "name": "Waterhouse", "logo": "..." },
    "away": { "id": 26495, "name": "Spanish Town Police", "logo": "..." },
    "score": { "home": 3, "away": 0 },
    "status": { "code": "LIVE", "short": "진행중", "isLive": true, "isFinished": false, "isScheduled": false },
    "date": "2026-03-03T00:30:00.000Z"
  }]
}
```

### 오늘(3/3) 경기 현황

| 스포츠 | 경기 수 | 리그 수 | 주요 리그 |
|--------|---------|---------|----------|
| football | 186 | 76 | 라 리가, 리그 1, 러시아PL, 친선경기 |
| basketball | 75 | 19 | NBA(4), NCAAB(17), FIBA |
| baseball | 16 | 2 | MLB 프리시즌(11), NCAA(5) |

### 주요 리그 ID (api-sports.io 기반)

| league_id | 리그 | scoredata.org 태그 |
|-----------|------|-------------------|
| 39 | EPL | `[ENG D1]` |
| 140 | 라 리가 | `[SPA D1]` |
| 135 | 세리에 A | `[ITA D1]` (브라질도 135 — 국가로 구분) |
| 78 | 분데스리가 | `[GER D1]` (오늘 경기 없어서 미확인) |
| 61 | 리그 1 | `[FRA D1]` (오늘 여러 ID: 378,386,424) |
| 292 | K리그 1 | `[KOR D1]` (미확인) |
| 12 | NBA | basketball |

### 마이그레이션 완료 (2026-03-03)

**수정된 노드 (3+4):**

| 노드 | 수정 내용 |
|------|----------|
| 종목 결정 | ESPN 멀티스포츠 → scoredata.org 설정만 출력 (apiType, today, category, tone, fdoKey) |
| 오늘 경기 조회 | ESPN HTTP → `https://scoredata.org/api/scores/live` HTTP Request |
| 경기 목록 파싱 | ESPN 파싱 → scoredata.org live 응답 파싱 (9개 주요 리그 패턴 매칭) |
| 순위표 조회 | 참조 변경: `$('종목 결정')` → `$('경기 목록 파싱')` (standingsUrl, useFdo) |
| 프로토 배당 조회 | 연결 변경: 종목 결정 → 경기 목록 파싱 (oddsApiSport 필드 의존) |
| 데이터 병합 | sport/league/useFdo를 `$('경기 목록 파싱')`에서 읽도록 변경 |
| 배당 데이터 파싱 | 미사용 `$('종목 결정')` 참조 제거 |

**연결 구조 변경:**
```
변경 전: 종목 결정 → [이전 픽 조회, 오늘 경기 조회, 프로토 배당 조회]
변경 후: 종목 결정 → [이전 픽 조회, 오늘 경기 조회]
         경기 목록 파싱 → [순위표 조회, 프로토 배당 조회]
```
이유: oddsApiSport는 경기 목록 파싱에서 결정되므로, 프로토 배당 조회를 경기 목록 파싱 이후로 이동.

**주요 리그 매칭 패턴 (9개):**
| 패턴 | 스포츠 | 리그 | oddsSport |
|------|--------|------|-----------|
| `[ENG D1]` | soccer | Premier League | soccer_epl |
| `[SPA D1]` | soccer | La Liga | soccer_spain_la_liga |
| `[ITA D1]` | soccer | Serie A | soccer_italy_serie_a |
| `[GER D1]` | soccer | Bundesliga | soccer_germany_bundesliga |
| `[FRA D1]` | soccer | Ligue 1 | soccer_france_ligue_one |
| `[KOR D1]` | soccer | K League 1 | soccer_korea_kleague1 |
| NBA | basketball | NBA | basketball_nba |
| MLB | baseball | MLB | baseball_mlb |
| KBO | baseball | KBO | baseball_mlb |

**E2E 테스트 결과 (execution #1251):**
- 웹훅 트리거 → 종목 결정 → 오늘 경기 조회 → 경기 목록 파싱 → 순위표 조회 → 부상자/상대전적 → 데이터 병합 → AI 경기 선택 → 경기 선택 파싱 → v1.2 프롬프트 조립 → AI 스크립트 생성 → 스크립트 파싱 → **시트 기록 (성공!)** → TTS → **에러: Typecast 429 Rate Limit**
- scoredata.org 마이그레이션 자체는 완전 성공
- TTS Typecast rate limit은 별도 이슈 (외부 서비스 제한)

---

## 11. 다음 할 일

1. ~~**TTS concat 처리**~~ → 5.1단계 완료
2. ~~**캡처 서비스 Docker 준비**~~ → Dockerfile/docker-compose.yml/.dockerignore 완료
3. ~~**배포 실행**~~ → 76.13.182.180:/opt/capture-service/ 배포 완료 (컨테이너 healthy, presets:20)
4. ~~**ODDS API 키**~~ → `921688c663b829bbd79bab1d23c21440` 확보 완료
5. ~~**Google Sheets 생성**~~ → "아럽토 v2" 시트 생성 완료 (ID: `1SCzznS9eLMmyK_jQq0qFSx4zWKmwIK6dGesFEgm0brA`)
6. ~~**n8n 환경변수 설정**~~ → docker-compose.yml에 4개 추가 완료 (n8n + worker 양쪽)
7. ~~**v2 워크플로우 시트 ID 교체**~~ → 3곳 일괄 교체 완료 (이전 픽 조회, 시트 기록, 상태 업데이트)
8. ~~**v2 워크플로우 import**~~ → n8n CLI로 import 완료 (ID: `arupto_shortform_v2`, 30노드, 웹훅 트리거 추가)
9. ~~**ESPN URL 수정**~~ → 축구 fixtures/standings URL 경로 변경 (league=xxx → /league/scoreboard)
10. ~~**scoredata.org 전환**~~ → 완료 (종목 결정/경기 조회/경기 파싱 + 다운스트림 참조 수정, E2E 시트 기록까지 성공)
11. ~~**Google Sheets 탭 이름 수정**~~ → "아럽토 v2" → "스포츠 픽" 변경 완료
12. ~~**TTS Typecast 429 에러 해결**~~ → TTS 요청 노드에 batching 추가 (batchSize:1, interval:2초) — 3세그먼트 순차 호출
13. **BGM 교체**: sportsbeat/newsroom/chill 에셋 확보
14. **템플릿 D/R 구현**: 필요 시 추가
15. **E2E 완주 테스트**: TTS 이후 캡처→SFX→타임라인→NCA→상태업데이트 전체 확인

### n8n 환경변수 — ✅ 설정 완료 (`/docker/n8n/docker-compose.yml`)
| 변수 | 값 | 비고 |
|------|-----|------|
| ODDS_API_KEY | `921688c663b829bbd79bab1d23c21440` | 프로토 배당 조회 노드에서 `$env` 참조 |
| CAPTURE_HOST | `76.13.182.180` | 캡처 요청 v2 노드에서 `$env` 참조 |
| MINIO_BASE_URL | `http://76.13.182.180:9000` | SFX/NCA 노드에서 `$env` 참조 (없으면 하드코딩 폴백) |
| MINIO_BUCKET | `arubto` | SFX/NCA 노드에서 `$env` 참조 (없으면 하드코딩 폴백) |

### 하드코딩 IP (환경변수 불필요 — 서버 고정)
| 노드 | URL | 비고 |
|------|-----|------|
| TTS 요청 | `http://172.17.0.1:5100/tts` | Docker 내부 IP, n8n과 같은 호스트 |
| NCA 영상 제작 | `http://76.13.182.180:8080/v1/ffmpeg/compose` | NCA 서버 |
