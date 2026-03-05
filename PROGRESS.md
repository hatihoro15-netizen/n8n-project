# PROGRESS.md — 진행 일지 (히스토리)

> ❌ 이 파일은 "진행 일지(히스토리)"입니다. 날짜별 기록은 append만(삭제/overwrite 금지). (선택) 상단 요약 섹션이 있다면 그 부분만 최신으로 갱신 가능.

---

## 프로젝트 현재 상태
- **단계**: 캡처 파이프라인 추가 완료, 테스트 대기
- **마지막 업데이트**: 2026-03-05
- **활성 워크플로우**: [온카 스터디] 설명형 숏츠 - 캡처 v16 (ID: 9v1Qc84iI19lQCEx)

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
- 8/8 품질 이슈 API 적용 확인
- 프로젝트 관리 시스템(CLAUDE.md, docs/ 7개, quality-check.sh 등) 전체 재작성 완료

### 📁 Files / Links
- update_8fixes.py (n8n API로 5개 노드 업데이트)
- CLAUDE.md, docs/01~07, PROGRESS.md, scripts/quality-check.sh
- 활성 워크플로우: 설명형 숏츠 - 온카스터디 (ID: dEtWqwWQPJfwCWiIM0QYd)

---

## 2026-03-04
### ✅ Done
- [x] 복사본 생성 + 워크플로우 이름 변경
- [x] 아럽토 캡처 노드 분석
- [x] 삽입 계획 수립
- [x] 캡처 파이프라인 추가 (3개 노드 + 프롬프트/파싱/NCA 수정)
- [x] 캡처 결과 수집 → NCA 데이터 준비 connection 추가
- [x] capture_targets AI 생성 제거 → 고정 빈 배열로 변경
- [x] 캡처 타겟 분리 URL 테이블 추가 (13개 subtopic)
- [x] n8n 서버 업로드 (워크플로우 ID: 9v1Qc84iI19lQCEx)
- [x] 콘텐츠 파싱: 날린 금지어 카테고리1 전용으로 범위 축소

### 📌 Result
- 캡처 파이프라인 3노드 병렬 분기 추가 완료 (45노드)
- n8n 서버 업로드 성공, 비활성 상태

### ➡️ Next (방향만 / 실행 커맨드는 HANDOFF)
- 워크플로우 실제 테스트 실행
- 캡처 이미지 병합 검증
- 테스트 통과 후 활성화

### 📁 Files / Links
- claude-tools/onca_shortform_v16.json (원본)
- claude-tools/onca_shortform_v16_capture.json (작업본)
- 워크플로우 ID: 9v1Qc84iI19lQCEx

---

## 2026-03-05
### ✅ Done
- [x] 프로젝트 파일 체계 정비 (4파일 체계: CLAUDE/HANDOFF/process/PROGRESS)
- [x] 중요 클라우드코드 지식/ 폴더 → 루트로 통합 후 폴더 삭제
- [x] CLAUDE.md 업데이트 (새 운영 지침 적용)

### 📌 Result
- 4파일 체계 확립: CLAUDE.md(규칙) / HANDOFF.md(스냅샷) / process.md(지식베이스) / PROGRESS.md(일지)
- 모든 관리 파일이 프로젝트 루트에 통합됨
