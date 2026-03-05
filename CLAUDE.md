# CLAUDE.md — 운영 지침 (4파일 + docs/ 체계)

> ⚠️ 최상위 규칙. 임의 자동 수정 금지 — 변경 필요 시 이유/영향 먼저 보고.

---

## 0) 파일 역할 (절대 혼동 금지)

| 파일 | 역할 | 규칙 |
|---|---|---|
| **CLAUDE.md** | 운영 지침 / 우선순위 / 행동 규칙 | 고정 (수정 시 보고 필수) |
| **HANDOFF.md** | 다음 세션 즉시 실행 스냅샷 | 항상 전체 Overwrite |
| **process.md** | 정제된 지식베이스 (ADR + 트러블슈팅) | Append only |
| **PROGRESS.md** | 진행 일지 (날짜별 히스토리) | Append only |
| **docs/** | 정식 참조 문서 (아키텍처/규칙/에러패턴) | 수정 시 보고 필수 |

### "소스 오브 트루스" 규칙
- **Next Actions / Last Run / Blockers → HANDOFF.md가 유일한 정답**
- PROGRESS.md의 Next는 "방향/메모"만. 실행 커맨드/즉시 지시는 HANDOFF에만.
- docs/는 "참조용 정식 문서". 살아있는 지식은 process.md에.

---

## 1) 우선순위 (충돌 시)
1. 사용자 지시
2. CLAUDE.md
3. process.md
4. HANDOFF.md
5. PROGRESS.md / docs/

> 단, Next Actions / Last Run / Blockers 관련 충돌은 예외 없이 HANDOFF.md가 최우선이다.

---

## 2) 프로젝트 식별 (세션 시작 시 확정)

**이 레포 기본 정보:**
- 프로젝트: N8 Video Manager (AI 기반 유튜브 숏폼 자동 제작 플랫폼)
- VPS: 76.13.182.180 (Hostinger KVM1)
- n8n URL: https://n8n.srv1345711.hstgr.cloud
- 워크스페이스: 웹앱 / n8n 온카 / n8n 흑형·할머니·스포츠 / n8n 루믹스 / n8n 스포츠(아럽토)

**매 세션 확정할 항목:**
- 워크스페이스:
- 레포/경로:
- 브랜치:
- 환경(Local/VPS/Dev/Prod):

> ⚠️ 워크스페이스 확정 전에는 코드/서버 변경 작업 시작 금지.

---

## 3) 세션 시작 루틴 (INIT) — 답변/작업 전 반드시

읽는 순서:
1. **HANDOFF.md** → Next Actions / Last Run / Blockers 확인
2. **process.md** → 컨벤션 / ADR / 트러블슈팅 규칙 확인
3. **PROGRESS.md** → 매 세션 읽되, 상단 요약 + 최근 기록 1개만 본다
   - 전체 히스토리는 맥락 필요할 때만 (과거 시도/실패 이유 확인 등)
4. **docs/** → 해당 작업 유형의 참조 문서만 (아래 표 참고)

**작업 유형별 읽을 docs/ 파일:**
| 작업 유형 | 읽을 파일 |
|---|---|
| 아키텍처/흐름 | docs/01-architecture.md |
| 인프라/배포/VPS | docs/02-infra-rules.md |
| 파일 역할 확인 | docs/03-file-roles.md |
| 워크플로우/롤백 | docs/04-workflow.md |
| 품질/체크 | docs/05-quality-check.md |
| 에러 패턴 | docs/06-error-patterns.md |
| 보고서 작성 | docs/07-report-template.md |

**세션 첫 응답에 반드시 브리핑 포함:**
```
📝 현재 상태: (HANDOFF 기반 1줄)
🎯 이번 목표: (1개)
➡️ Next Actions Top 3: (HANDOFF 기준)
⚠️ Blockers: (HANDOFF 기준)
📌 주의 규칙 Top 3: (CLAUDE / docs 기준)
```
> ⚠️ 위 브리핑 + 수정 계획 출력 전에는 어떤 작업도 시작하지 마.

---

## 4) 작업 방식

### 4-1) 최소 변경 원칙
- 불필요한 리팩토링/추상화/새 의존성 금지
- 새 의존성/아키텍처 변경 시: 이유 1~2줄 → 대안 1개 → 영향/리스크 먼저 보고

### 4-2) 보안/비밀값 절대 규칙
- 토큰/키/계정/내부 URL → 출력/커밋/로그 금지
- 예시는 항상 더미값/환경변수로 대체
- CLAUDE.md의 "기본 정보"에 기재된 VPS/n8n URL은 예외

### 4-3) 수정 전 계획 먼저
- 어떤 파일을 어떻게 바꿀지 계획 보고 → 확인 후 작업
- 변경 전/후 명확히 구분해서 출력

### 4-4) 막히면 추측 금지
재현 단계 → 원인 후보 2~3개 → 최소 실험 1개 → 결론 순서로

---

## 5) 작업 완료 후 체크리스트

- [ ] scripts/quality-check.sh 통과 (해당 워크스페이스)
- [ ] 기능 실제 동작 확인 (최소 1회)
- [ ] git commit
- [ ] HANDOFF.md Overwrite (Next/LastRun/Blockers 최신화)
- [ ] PROGRESS.md Append (보고서 형식)
- [ ] 중요 트러블슈팅/결정 → process.md Append

**모든 응답 말미에 작업 요약 블록 포함:**
```
✅ 오늘 한 일
📁 변경 파일(경로) / 워크플로우(이름/ID)
🧪 실행/테스트(커맨드/결과)
⚠️ 이슈/주의사항
➡️ 다음 작업(우선순위 1~3)
```

---

## 6) 파일 업데이트 규칙

### HANDOFF.md (Overwrite)
아래 상황에서 스스로 업데이트 초안 제안:
- 큰 기능 1개 완료
- 중요 이슈 해결/중단/보류
- 서버/배포/환경 변경
- "다음 세션 즉시 할 일"이 바뀜

필수 포함 항목:
- Current Status / Goal
- Next Actions (우선순위 1~3, 커맨드 포함)
- Last Run Command + Result + 실행 위치
- Blockers / Known Issues
- 변경 파일 경로 또는 워크플로우 ID

### process.md (Append)
아래에 해당할 때만 추가:
- 환경/설정 변경 (버전, ENV, 브랜치, 새 의존성)
- 프로젝트 고유 버그의 근본 원인 + 해결 + 예방
- 반복 패턴/컨벤션 확정
- ADR: "왜 이 방식인지"가 재발할 것 같은 결정

오염 방지: 단순 문법/오타/일회성/누구나 아는 일반론 기록 금지

### PROGRESS.md (상단 요약 Overwrite / 보고서 Append)
- **상단 "현재 요약" 섹션만** 매 세션 overwrite 가능
- 날짜별 보고서는 append only. 기록 대상: Done / Tried / Result / Next(방향만) / Files
- 기록 금지: 실행 커맨드 정답 (그건 HANDOFF)

### docs/ (수정 시 보고)
정식 참조 문서. 내용 변경 시 이유/영향 먼저 보고.
새 패턴 발견 시 docs/06-error-patterns.md에 즉시 추가.

---

## 7) n8n / VPS 작업 추가 규칙

- n8n 워크플로우 수정 전 반드시 Export(JSON) 백업
- **top-level nodes와 activeVersion.nodes 양쪽 다 수정**
- **직렬 노드 삽입 시 이후 $json 참조 확인** (`$('노드명').first().json.xxx`)
- **Google Sheets update 노드: alwaysOutputData: true 필수**
- **n8n API 업로드 후 에디터 F5 새로고침 필수** (덮어쓰기 사고 방지)
- IP/호스트 하드코딩 금지 (환경변수 사용)
- VPS 작업 전 백업 여부 확인

---

## 8) 에이전트 역할 (멀티 Claude Code 운영 시)

| 역할 | 담당 |
|---|---|
| 인프라 | 서버/배포/n8n 인스턴스/infra 파일 |
| 워크플로우 | n8n 노드/연결/로직/*.json |
| 콘텐츠 | 프롬프트/캐릭터/대사 |
| 검증 | 테스트/lint/동작 확인 |

규칙: 자기 역할 외 파일 수정 금지. 작업 전 관련 docs/ 읽기.

---

## 9) 작업 중단 조건 (반드시 질문)

- 동작 중인 기능 수정 필요
- 파일 삭제 필요
- 방법 선택 불확실
- 요구사항 모호
- 예상치 못한 에러 발생
