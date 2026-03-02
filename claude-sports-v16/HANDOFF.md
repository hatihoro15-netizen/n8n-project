# 인수인계 문서 — 아럽토 유튜브 숏츠 프로젝트

> 최종 업데이트: 2026-03-03
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
| 3단계 | 캡처 서비스 구축 | capture-service/ (8파일) | 완료 (배포 필요) |
| 4단계 | 워크플로우 구축 + 프롬프트 연동 + 배당 소싱 | arupto_shortform_v1.json | 완료 (테스트 필요) |

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
│   ├── Dockerfile
│   └── src/
│       ├── server.js             # POST /capture, /health (포트 3100)
│       ├── config.js             # 환경변수 로딩
│       ├── browser.js            # Puppeteer 싱글턴
│       ├── capturer.js           # 캡처 → 처리 → 업로드
│       ├── uploader.js           # MinIO 업로드
│       ├── image-processor.js    # Sharp 1080x1920
│       └── presets.js            # 20개 프리셋
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

| 변수 | 용도 | 값 예시 |
|------|------|---------|
| ODDS_API_KEY | the-odds-api.com API 키 | 무료 가입 후 발급 |
| CAPTURE_HOST | 캡처 서비스 주소 | 172.17.0.1 (Docker) |
| CAPTURE_PORT | 캡처 서비스 포트 | 3100 |
| MINIO_ENDPOINT | MinIO 주소 | 172.17.0.1 |
| MINIO_ACCESS_KEY | MinIO 접근 키 | |
| MINIO_SECRET_KEY | MinIO 비밀 키 | |

---

## 6. 배포 순서

```bash
# 1. 캡처 서비스 배포
scp -r capture-service/ user@서버:/opt/capture-service/
cd /opt/capture-service && cp .env.example .env  # 환경변수 편집
docker build -t capture-service . && docker run -d -p 3100:3100 --env-file .env capture-service
curl http://localhost:3100/health  # {"status":"ok","presets":20}

# 2. MinIO 버킷 생성
mc mb myminio/captures && mc anonymous set download myminio/captures

# 3. n8n 환경변수 추가
# CAPTURE_HOST, ODDS_API_KEY

# 4. 워크플로우 임포트
# arupto_shortform_v1.json을 n8n에 임포트

# 5. Google Sheets 시트 생성 (아래 컬럼 구조 참고)
```

---

## 7. Google Sheets 시트 구조 (생성 필요)

시트명: `아럽토 콘텐츠` (시트 ID는 임포트 후 워크플로우에 반영)

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

## 8. 다음 할 일 (5단계~)

1. **배포**: 캡처 서비스 Docker + MinIO 버킷 + 환경변수
2. **the-odds-api.com 가입**: 무료 API 키 발급 (월 500회)
3. **Google Sheets 생성**: 위 컬럼 구조로 시트 생성 → 시트 ID를 워크플로우에 반영
4. **테스트**: 카테고리 7(기능소개, 외부 데이터 불필요) → 카테고리 1(프로토배당) 순서
5. **카테고리 로테이션**: 종목 결정 노드에서 category를 시트/랜덤으로 결정하도록 수정
6. **BGM 교체**: 스포츠/에너지틱 BGM 선정
7. **Phase 3~4**: 전체 카테고리 + 업로드 자동화
