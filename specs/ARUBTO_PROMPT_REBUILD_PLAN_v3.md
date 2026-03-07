# ARUBTO Prompt 개선 기획서 v3

## 0) 목적
- `arubto-prompt`를 전면 재개발하지 않고, 현재 운영 이슈를 우선순위대로 해결한다.
- 한 번에 다 하지 않고, 단계별로 품질을 안정화한다.

---

## 1) 고정 원칙 (SPEC_v1 — 이 원칙 없이 개발 시작 금지)

1. **우선순위 고정**: Prompt > Narration > Audio > (topic/keywords/category는 메타데이터 only)
2. **길이 제한**: 숏폼 ≤30초, 롱폼 ≤120초
3. **저작권 원칙**: 자동 외부 BGM/SFX 수집 금지, 사용자 업로드 파일만 사용
4. **실패 기준**: 위 원칙 위반 시 결과 폐기
5. **엔진 분리**: 캐릭터서사 / 핵심전달 / 홍보 / 밈 / 액션스포츠 5개
6. **메타데이터 격리**: topic/keywords/category는 생성 로직에서 참조 금지. 저장/검색 전용
7. **strict_mode 기준**:
   - strict_mode=true: target_duration ±1초
   - strict_mode=false: target_duration -3초 이상 (예: 30초 → 최소 27초)
8. **하드코딩**: 정말 불가피한 경우만 허용. 기본은 설정값/동적 처리

> ⚠️ 이 원칙을 SPEC_v1.md로 먼저 파일 생성 후 Phase 1 진행

---

## 2) 단계별 실행 계획

### Phase 0. SPEC_v1.md 작성 (개발 시작 전 필수)
목표:
- 고정 원칙을 문서 1장으로 확정한다.
- 이후 모든 작업의 기준점이 된다.

작업 범위:
- 위 1) 고정 원칙을 SPEC_v1.md 파일로 생성
- 입력 payload 스키마 고정:
  - 필수: `prompt_p1`
  - 선택: `narration_text`, `narration_style`, `narration_tone`, `duration_sec`, `engine_type`, `strict_mode`
  - 메타데이터 전용: `topic`, `keywords`, `category` (생성 로직 참조 금지)

완료 기준:
- SPEC_v1.md 파일 생성 + 커밋
- payload 스키마 docs/05-input-schema.md 반영

---

### Phase 1. 길이 안정화 + Prompt Lock (지금 진행중)
목표:
- `30초 선택인데 19.1초 종료` 문제 해결
- Prompt Lock 재생성 플로우 연결 (현재 P0-2 작업과 병행)

작업 범위:
- Length Gate 보정 로직 점검 및 수정
- clip_count 재계산 로직 검증
- 나레이션 길이 부족 시 보정 규칙 정리 (재생성 1회 시도 → 그래도 짧으면 그대로 진행 + job_logs 기록)
- Prompt Lock 재생성 플로우: prompt_lock_valid=false → IF 노드 분기 → 재생성 브랜치 연결
- 렌더 직전 prompt_hash 재확인 체크포인트 추가
- 30초/60초 재테스트

완료 기준:
- 30초 케이스: strict_mode=false → 최소 27초 이상
- 60초 케이스: 목표 길이 근접 유지
- strict_mode=true: target_duration ±1초 통과
- Prompt Lock 재생성 동작 로그 증빙
- 테스트 결과를 HANDOFF/PROGRESS에 기록

제외:
- verify_mode 10회 동일성 최종 검증 (Phase 3에서)

---

### Phase 2. 웹앱 연동 뼈대
목표:
- 사용자 입력과 백엔드 계약을 안정적으로 맞춘다.

작업 범위:
- 프론트 입력 필드 정리:
  - `prompt_p1` (필수)
  - `narration_text` + `narration_style` + `narration_tone` (분리 입력칸)
  - duration 드롭다운 고정 (30/40/50/60/90/120초)
  - strict_mode 토글
  - BGM/효과음 업로드 칸 (사용자 직접 업로드만)
  - 엔진 선택 (5개)
- 백엔드 입력 검증과 에러 메시지 정리
- topic/keywords/category → 생성 로직 영향 경로 완전 제거 확인

완료 기준:
- 프론트/백 payload 계약 일치
- 허용값 외 duration 거부
- 기본 생성 경로 정상 동작
- topic/keywords/category 영향 경로 0건

---

### Phase 3. 프롬프트 고도화
목표:
- 프롬프트 변경/일관성/검증 품질을 강화한다.

작업 범위:
- Last-Edit Priority 고도화
- `prompt_hash` 저장/비교 안정화
- `verify_mode` 검증 흐름 정리

완료 기준:
- 로그 경로 통일 (`ao_job_logs.details.output_hash`)
- verify_mode 결과 리포트 구조 준비

---

### Phase 3.5. 테스트셋 30개 구축 (엔진 PoC 후)
목표:
- 동일 입력으로 엔진만 바꿔 A/B 비교 가능한 체계 구축

작업 범위:
- 엔진별 6개씩 테스트 케이스 작성 (5엔진 × 6개 = 30개)
- 자동 실행 스크립트 작성
- 평가 지표:
  - 프롬프트 충실도
  - 서사 일관성
  - 나레이션 자연스러움
  - 오디오 적합성
  - 완주율 (실패 없이 생성)

완료 기준:
- 30개 케이스 자동 실행 + 결과 비교 가능
- 엔진별 점수 기록

---

### Phase 4. 연출 자동화 + 알고리즘/시장 분석
목표:
- 결과물 품질과 노출 전략을 고도화한다.

작업 범위:
- 자동 연출(F) 고도화
- 알고리즘/시장 분석 리포트(G) 구축
- 엔진별 prompt 템플릿 / 샷 구성 규칙 / 자막 스타일 / 컷 전개 속도 별도 설정 파일 분리
- 장면/오디오/전환 품질 고도화

완료 기준:
- 리포트 기반 추천 포맷 운영 가능
- 엔진별 결과 차별성/안정성 확인

---

## 3) 성공 기준 (v3)
1. SPEC_v1.md 원칙 문서 생성 완료
2. 길이 이슈 해결: strict_mode=false → 목표 -3초 이상, strict_mode=true → ±1초
3. Prompt Lock 재생성 플로우 동작 증빙
4. 웹앱 연동 시 입력 계약 불일치 0건
5. topic/keywords/category 생성 영향 경로 0건
6. 문서 동기화 누락 0건 (HANDOFF 갱신 + PROGRESS append)

---

## 4) 체크리스트 (v3)

### 4-0. Phase 0 SPEC_v1.md 작성
- [ ] S-1 SPEC_v1.md 파일 생성 + 커밋
- [ ] S-2 payload 스키마 docs/05-input-schema.md 반영

### 4-1. Phase 1 길이 안정화 + Prompt Lock
- [ ] L-1 30초 19.1초 원인 분석 완료
- [ ] L-2 clip_count 재계산 로직 수정
- [ ] L-3 길이 보정 규칙 반영 (재생성 1회 + 짧으면 그대로 + job_logs 기록)
- [ ] L-4 Prompt Lock IF 노드 분기 연결
- [ ] L-5 렌더 직전 prompt_hash 재확인 체크포인트 추가
- [ ] L-6 30초/60초 재테스트 완료
- [ ] L-7 HANDOFF 갱신 + PROGRESS append

### 4-2. Phase 2 웹앱 연동
- [ ] W-1 프론트 입력 필드 정리 (narration 분리 + 엔진 선택 + BGM 업로드)
- [ ] W-2 duration 드롭다운 고정 반영
- [ ] W-3 strict_mode 토글 연동
- [ ] W-4 백엔드 입력 검증 정리
- [ ] W-5 topic/keywords/category 영향 경로 제거 확인
- [ ] W-6 연동 테스트 완료

### 4-3. Phase 3 프롬프트 고도화
- [ ] P-1 Last-Edit Priority 보강
- [ ] P-2 prompt_hash 저장/비교 안정화
- [ ] P-3 verify_mode 검증 흐름 정리

### 4-3.5. Phase 3.5 테스트셋
- [ ] T-1 엔진별 6개 케이스 작성 (30개)
- [ ] T-2 자동 실행 스크립트
- [ ] T-3 평가 지표 기록 양식

### 4-4. Phase 4 연출/시장 분석
- [ ] Q-1 자동 연출 전략 고도화
- [ ] Q-2 알고리즘/시장 리포트 구축
- [ ] Q-3 엔진별 설정 파일 분리
- [ ] Q-4 엔진별 품질 비교 지표 확정

---

## 5) 운영 메모
- Phase 경계를 넘는 작업 요청이 오면 범위 이탈로 보고 분리한다.
- 단계 완료 기준 충족 후 다음 단계로 넘어간다.
- 현재 P0-2 작업(Claude Code 진행중)은 Phase 1 체크리스트 L-1~L-5에 해당한다.
