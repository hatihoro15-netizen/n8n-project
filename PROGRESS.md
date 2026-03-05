# PROGRESS.md — 진행 일지 (히스토리)

> ❌ 이 파일은 "진행 일지(히스토리)"입니다. 날짜별 기록은 append만(삭제/overwrite 금지). (선택) 상단 요약 섹션이 있다면 그 부분만 최신으로 갱신 가능.

## 프로젝트 현재 상태
- **단계**: 숏폼 v16 워크플로우 운영 + 웹앱 연동
- **마지막 업데이트**: 2026-03-05
- **활성 워크플로우**: 온카 숏폼 v16 (ID: x6xTzHJ9WbUc94ec, 42노드)

---

## 2026-02-25
### ✅ Done
- [x] 프로젝트 초기 설정 시스템 구축
- [x] 꿀팁 숏츠 + 밈 혼합 워크플로우 개편
- [x] MinIO 밈 라이브러리 구축 - Pepe 밈 21개
- [x] 8가지 영상 품질 이슈 수정
- [x] 프로젝트 매뉴얼 시스템 재구축

### 📌 Result
- 꿀팁 숏츠 + 밈 혼합 워크플로우 정상 실행, 영상 생성 성공
- MinIO에 밈 라이브러리 구축 (Pepe 밈 21개, 7카테고리)
- 프롬프트: 25-30초, 8-10장면, 12자 이내 대사
- NCA: 검은배경(#000000@1.0), fontsize=72, 자막 줄바꿈(14자), 밈 루프(-stream_loop)
- TTS: HyunsuNeural, rate +15%
- 이미지: per_page=3, 랜덤 선택

### 📁 Files / Links
- CLAUDE.md, docs/01~07, PROGRESS.md, scripts/quality-check.sh, .claude/commands/start.md
- update_8fixes.py (n8n API로 5개 노드 업데이트)

---

## 2026-03-02~03
### ✅ Done
- [x] Webhook + 콜백 시스템 구축 (`f1a620a`)
  - Webhook POST `/onca` (responseMode: onReceived)
  - 성공/실패 콜백, 수동 실행 시 콜백 스킵 (skipCallback 분기)
- [x] 중간 단계 콜백 4개 (`80b9965`)
  - `script_ready`, `tts_ready`, `images_ready`, `rendering` (병렬 분기)
- [x] v3 종합 패치 머지 (`d3c58d1`)
  - 프롬프트 앵커 시스템 + 콘텐츠 검증 강화 + 사투리 + 밈 mood 매칭
- [x] 에러 핸들링 7개 경로 완비 (`f6c9608`)
- [x] 콜백 executionId 추가 (`fff8f3b`)

---

## 2026-03-04
### ✅ Done
- [x] 웹앱 executionId 매핑 배포 — PM2 `n8n-web-backend` online, 실행 #1280에서 정상 저장 확인
- [x] 주제 파싱 금지어 조기 검증 추가 — NEGATIVE_BLOCKLIST + TOPIC_CONFLICT 2단계
- [x] 실패 시 카운터 고정 문제 수정 — "실패 시트 기록" Google Sheets append 노드 추가
- [x] AI 주제 생성 프롬프트 강화 + 리트라이 판단 노드 추가 (42노드)

### 🔁 Tried
- [ ] Gemini 프롬프트 강화 (subtopic 주입, 카테고리별 톤/금지어 조건부 표시) → 여전히 소재 무관 주제 생성
- [ ] 실행 #1286, #1287: 조기 검증 효과 확인 (주제 파싱에서 차단, AI 콘텐츠 비용 절감)
- [ ] 실행 #1292 (webhook): Gemini rate limit 에러 → 연속 webhook 호출이 원인

### 📌 Result
- 에러 핸들링/콜백/카운터 시스템 안정화 완료
- Gemini 주제 생성 품질은 미해결 (모델 한계 가능성)
- 에러 준비 노드 `input.error` 문자열 타입 미처리 발견 (미수정)

### ➡️ Next (방향만)
- Gemini 주제 생성 개선 또는 다른 모델 검토
- 에러 메시지 추출 개선
- 콜백 API status 검증 로직 추가

### 📁 Files / Links
- `onca.json` (42노드)
- 웹앱 백엔드: 콜백 API executionId 매핑

---

## 2026-03-05
### ✅ Done
- [x] CLAUDE.md 4파일 체계로 업그레이드 (HANDOFF/process/PROGRESS 역할 분리)
- [x] HANDOFF.md 새 형식 Overwrite
- [x] process.md 상단 경고 문구 추가
- [x] PROGRESS.md 루트로 이동 + 상단 경고 문구 추가
