=======================================
클로드 코드 최종 전달 메시지 (FINAL v86.4)
=======================================

대상 워크플로우:
- Jay_Mike_v84.json
- 할머니_Mike_v84.json
(흑형스포츠는 이번 작업 제외)

브랜치/워크트리:
- feature/v84-prompt-update 워크트리에서 작업

---

## 목표

1) v8.6 프롬프트로 대본 품질 개선 (4턴 브릿지 강화 / 6턴 감정+행동 필수 / 글자수 공백제외 통일)
2) Veo3 화자 혼동 최소화 (LEFT/RIGHT 위치 고정 + speaking lips only + spatial anchoring)
3) 최종 영상 항상 24초(3세그먼트×8초) 고정 — 세그먼트 누락 합성 금지
4) 나레이션/자막/SRT에서 "The man in …" 화자 태그가 절대 읽히지 않게 처리
5) 영상 생성 실패(successFlag≥2) 시: 해당 세그먼트만 1회 재시도 → 또 실패하면 즉시 중단(throw)

---

## 사용 문서

이 파일 하나에 전부 포함되어 있음. 아래 "상세 작업 내용" 섹션의 작업 1~12를 순서대로 적용해줘.

---

## 작업 체크리스트 (반드시 1~12 순서로)

### 작업 1~8 (v86 문서 본문대로)
1. Jay_Mike_v84.json → "AI 콘텐츠 생성" 노드 프롬프트를 v8.6으로 교체
2. 할머니_Mike_v84.json → "AI 콘텐츠 생성" 노드 프롬프트를 v8.6(할머니 버전)으로 교체
3. Jay_Mike_v84.json → "9:16 변환" 노드 코드 교체 (구절 쪼개기 적용)
4. 할머니_Mike_v84.json → "9:16 변환" 노드 코드 교체 (동일)
5. Jay_Mike_v84.json → "프레임1·2 추출" 노드 `-ss` 값을 `7.8`로 변경
6. 할머니_Mike_v84.json → "프레임1·2 추출" 노드 `-ss` 값을 `7.8`로 변경
7. Jay_Mike_v84.json → "세그먼트 분리" 노드 JS 패치 (speakerDesc LEFT/RIGHT + speaking lips only + veo3_prompt spatial anchoring)
8. 할머니_Mike_v84.json → "세그먼트 분리" 노드 JS 패치 (할머니 버전 동일)

### 작업 9~12 (추가 패치 — 이번 이슈 해결 핵심)
9. 양쪽 → "콘텐츠 파싱" 노드: `fullDialogue`를 `dialogue_turns[].line`으로 변경 → 나레이션 화자 태그 제거
10. 양쪽 → "NCA 데이터 준비" 노드: dialogueText 태그 제거(폴백 안전장치 포함) + videoUrl 없으면 throw(24초 강제)
11. 양쪽 → "영상1·2·3 실패체크" 코드 변경 + "영상N 재생성판단" IF 노드 3개씩 추가 + connections 변경 (1회 재시도, 재실패 시 중단)
12. 양쪽 → 프롬프트 금지어 부분일치 규칙 (작업 1-2 프롬프트에 이미 삽입됨, 별도 작업 불필요)

---

## 추가 보완 (반드시 반영)

### A) NCA 데이터 준비 노드: dialogueText 폴백 시 태그 제거(clean)

작업 10에서 dialogueText 우선순위를 "dialogue_turns join → dialogue 폴백"으로 바꿀 때,
폴백(segData.dialogue) 사용 시 아래 정규식으로 화자 태그를 제거한 뒤 사용:

```js
function cleanDialogueTags(s) {
  return (s || '')
    .replace(/The man in [^:]+:\s*/g, '')
    .replace(/The grandmother in [^:]+:\s*/g, '')
    .trim();
}

// dialogueText 생성 시:
const dialogueText =
  (Array.isArray(segData?.dialogue_turns) && segData.dialogue_turns.length > 0)
    ? segData.dialogue_turns.map(t => t.line).join(' ')
    : cleanDialogueTags(segData?.dialogue || '');
```

### B) throw가 진짜 워크플로우를 중단하도록 옵션 확인

아래 노드들에서 **"Continue On Fail(실패해도 계속)"** 옵션이 켜져 있으면 반드시 끄고 작업해:
1. "NCA 데이터 준비" (작업 10의 throw가 중단되어야 함)
2. "영상1 실패체크", "영상2 실패체크", "영상3 실패체크" (작업 11의 throw가 중단되어야 함)
3. 최종 합성/업로드 등 24초 보장에 영향을 주는 후속 노드

---

## 핵심 주의사항 (절대 규칙)

1. **dialogue 필드 화자 태그 문자열은 절대 변경 금지:**
   - `The man in white t-shirt:` / `The man in black hoodie:`
   - `The grandmother in floral vest:` (할머니 버전)
   - 파서가 이 문자열을 그대로 사용함

2. **LEFT/RIGHT 위치 정보는 image_prompt, speakerDesc, veo3_prompt에만 넣기:**
   - dialogue 태그에 "on the left/right" 같은 문구 추가 금지

3. **작업 7, 8은 기존 코드에서 해당 부분만 찾아서 교체:**
   - 전체 코드 덮어쓰기 금지

4. **영상 실패 시 정책은 "1회 재시도 후 중단"으로 고정:**
   - 무한 재시도 금지, 리라이트(대사 수정) 재시도 아님, 같은 프롬프트로 1회만

---

## 작업 완료 보고 형식

각 작업마다 아래 형식으로 1~2줄 요약:
```
[작업 N] 파일명 / 노드명 / 무엇을 어떻게 바꿨는지
```

특히 작업 11(재시도 로직)은:
- 새로 추가한 IF 노드 이름
- connections 변경 내용 (어디서 어디로 연결했는지)
- n8n 캔버스에서 확인할 수 있는 흐름 설명

을 남겨줘.

---

작업 시작해줘.

=======================================
상세 작업 내용 (작업 1~12)
=======================================

### 작업 1: Jay_Mike_v84 — "AI 콘텐츠 생성" 노드 프롬프트 교체
- 브랜치: feature/v84-prompt-update (또는 해당 워크트리)
- 파일: Jay_Mike_v84.json
- 노드: "AI 콘텐츠 생성" → parameters.messages.values[0].content
- 현재 프롬프트 전체를 아래 v8.6 프롬프트로 교체

### 작업 2: 할머니_Mike_v84 — "AI 콘텐츠 생성" 노드 프롬프트 교체
- 파일: 할머니_Mike_v84.json
- 노드: "AI 콘텐츠 생성" → parameters.messages.values[0].content
- 할머니 v8.6 프롬프트로 교체 (아래에 별도 제공)

### 작업 3: Jay_Mike_v84 — "9:16 변환" 노드 코드 교체
- 파일: Jay_Mike_v84.json
- 노드: "9:16 변환" → parameters.jsCode
- 전체 교체 (구절 쪼개기 코드)

### 작업 4: 할머니_Mike_v84 — "9:16 변환" 노드 코드 교체
- 파일: 할머니_Mike_v84.json
- 노드: "9:16 변환" → parameters.jsCode
- Jay_Mike와 동일한 코드 적용


### 작업 5: Jay_Mike_v84 — 프레임 추출 타이밍 변경
- 파일: Jay_Mike_v84.json
- 노드: "프레임1 추출", "프레임2 추출" → parameters.jsCode
- `-ss` argument의 `'7.5'`를 `'7.8'`으로 변경
- (주의) 영상 길이가 고정 8초가 아닐 수 있으면, `-sseof -0.2`(영상 끝 0.2초 전) 방식이 더 안전함

### 작업 6: 할머니_Mike_v84 — 프레임 추출 타이밍 변경
- 파일: 할머니_Mike_v84.json
- 노드: "프레임1 추출", "프레임2 추출" → parameters.jsCode
- `-ss` argument의 `'7.5'`를 `'7.8'`으로 변경
- (주의) 영상 길이가 고정 8초가 아닐 수 있으면, `-sseof -0.2` 방식이 더 안전함

### 작업 7: Jay_Mike_v84 — 세그먼트 분리 노드 speakerDesc + veo3_prompt 코드 패치
- 파일: Jay_Mike_v84.json
- 노드: "세그먼트 분리" → parameters.jsCode
- speakerDesc에 LEFT/RIGHT 위치정보 추가 + buildVeo3Dialogue에 립싱크 규칙 추가 + veo3_prompt에 spatial anchoring 문장 추가

### 작업 8: 할머니_Mike_v84 — 세그먼트 분리 노드 speakerDesc + veo3_prompt 코드 패치
- 파일: 할머니_Mike_v84.json
- 노드: "세그먼트 분리" → parameters.jsCode
- 작업 7과 동일 패턴(할머니/마이크 버전) 적용

### 작업 9: Jay_Mike_v84 + 할머니_Mike_v84 — "콘텐츠 파싱" 노드 fullDialogue 태그 제거
- 대상 노드: "콘텐츠 파싱" → parameters.jsCode
- 현재: `fullDialogue: data.scenes.map(s => s.dialogue).join(' ')` → "The man in ..." 태그가 나레이션에 섞임
- 변경: `fullDialogue: data.scenes.flatMap(s => (s.dialogue_turns || []).map(t => t.line)).join(' ')` → 순수 대사만

### 작업 10: Jay_Mike_v84 + 할머니_Mike_v84 — "NCA 데이터 준비" 노드 태그 제거 + 24초 강제
- 대상 노드: "NCA 데이터 준비" → parameters.jsCode
- (A) dialogueText 우선순위: dialogue_turns[].line 먼저 → dialogue 폴백
- (B) videoUrl 없을 때 continue 스킵 → throw Error로 중단 (24초 보장)

### 작업 11: Jay_Mike_v84 + 할머니_Mike_v84 — 영상 실패 시 1회 재생성 + 재실패 시 워크플로우 중단
- 대상 노드: "영상1 실패체크", "영상2 실패체크", "영상3 실패체크" (3개 모두, 양쪽 워크플로우)
- 현재: 실패 → 원본 이미지 폴백 → NCA에서 스킵
- 변경: 실패 → 같은 프롬프트로 1회 재생성 → 재실패 시 throw Error
- 새 IF 노드 "영상N 재생성판단" 3개씩 추가 + connections 변경

### 작업 12: Jay_Mike_v84 + 할머니_Mike_v84 — 장면1 금지어 "부분일치" 규칙 추가
- 대상 노드: "AI 콘텐츠 생성" → 프롬프트 내 장면1 금지어 구간
- 금지어 목록 바로 아래에 1줄 추가: "※ 금지어는 부분일치 포함 금지 (예: '게임'이 금지면 '게임기/게임패드'도 금지)."

---

=======================================
[작업 1] Jay & Mike v8.6 프롬프트
=======================================

아래 내용으로 "AI 콘텐츠 생성" 노드의 content를 통째로 교체:

---프롬프트 시작---
너는 YouTube Shorts 스토리형 콘텐츠 전문 작가야.
**온카스터디 커뮤니티**의 유익한 정보를 재미있는 대화 형식으로 만들어줘.
영상 스타일: 아나두 쇼츠처럼 깔끔하고 설득력 있는 설명형 콘텐츠.

## ★ 규칙 충돌 시 우선순위
1순위: ★★★ 글자수 제한 (위반 시 전체 실패) ★★★
2순위: JSON 출력 형식 준수 (구조/필드 누락 금지)
3순위: 6턴 순서 및 화자 역할 준수 (B→A / B→A / A→B)
4순위: 장면1 금지어 / 장면2 4턴 직접단어 / 5턴 온카스터디 단일 언급
5순위: 변주 요소 및 스타일 디테일

## 핵심 원칙
- 전체 대본의 70%는 유익한 정보 + 재미있는 흑형 친구 2명의 티키타카 케미
- 마지막 30%에서 온카스터디 자연스럽게 언급 (광고 느낌 절대 안 나게)
- 첫 3초 안에 시청자가 스크롤 멈추는 후킹
- Jay의 경험 기반 매운맛 팩트 + Mike의 리액션/질문이 만나는 구조
- "온카스터디"는 오직 장면 3의 5턴에서만 단 1회 언급

## ★★★ 글자수 제한 (1순위 — 위반 시 전체 실패!) ★★★

**숏폼 영상은 24초다. 한 턴에 긴 문장을 넣으면 TTS가 빨라지고, 자막이 잘리고, 티키타카가 죽는다.**
**글자수를 초과하면 0점이다. 하지만 너무 짧으면 대화가 빈약해진다. 범위 안에서 자연스럽게.**

**★ 글자수 = 공백(띄어쓰기) 제외, 순수 글자+문장부호만 센다 ★**

| 턴 | 글자수 (공백 제외) | 절대 상한 |
|----|---------------|---------|
| 1턴 (B) | 12~20자 | **20자 초과 시 실패** |
| 2턴 (A) | 12~20자 | **20자 초과 시 실패** |
| 3턴 (B) | 12~20자 | **20자 초과 시 실패** |
| 4턴 (A) | 25~35자 | **35자 초과 시 실패** |
| 5턴 (A) | 12~18자 | **18자 초과 시 실패** |
| 6턴 (B) | 10~18자 | **18자 초과 시 실패** |
| 전체 합계 | — | **공백 제외 130자 초과 시 실패** |

**글자수 세는 법:** 공백(띄어쓰기) 제외. 따옴표/마침표/느낌표/쉼표/물결은 포함.
**짧게 쓰는 핵심:** 한 턴 = 한 호흡. 숨 안 쉬고 말할 수 있는 길이가 정답.
**구어체 핵심:** 불필요한 조사(은/는/이/가)를 줄이고, 군더더기 제거. 말하듯이 쓸 것.

**좋은 예 vs 나쁜 예:**

나쁜 1턴 (30자, 실패): "할머니어제당근에서이십만원주고산맥북키보드짭이왔어요"
좋은 1턴 (14자, 공백 제외): "당근키보드짭이왔어형" → 실제 출력: "당근 키보드 짭이 왔어 형"

나쁜 4턴 (50자, 실패): "와그쉬운사기에도다음엔잘되겠지같은희망회로를돌리냐그런식이면카지노사이트에서도..."
좋은 4턴 (26자, 공백 제외): "짭도못거르면서?사이트도안가리고넣겠네" → 실제 출력: "짭도 못 거르면서? 사이트도 안 가리고 넣겠네"

나쁜 5턴 (24자, 실패): "그래서난온카스터디먹튀검증에서미리걸러서꿀빨지"
좋은 5턴 (14자, 공백 제외): "난온카스터디먹튀검증으로거름" → 실제 출력: "난 온카스터디 먹튀검증으로 거름"

나쁜 6턴 (7자, 빈약): "아…답없다."
좋은 6턴 (14자, 공백 제외): "형…나도이제확인하고간다" → 실제 출력: "형… 나도 이제 확인하고 간다"

## 장면 1 규칙
**금지어 (장면 1 대사에 단 하나도 포함 금지):**
카지노, 슬롯, 배팅, 사이트, 환수율, RTP, 먹튀, 환전, 도박, 게임, 포인트, 잭팟, 충전, 입금, 출금, 보너스, 온라인, 당첨
※ 금지어는 **부분일치 포함** 금지 (예: '게임'이 금지면 '게임기/게임패드'도 금지, '사이트'가 금지면 '웹사이트'도 금지).

**소재 (아래 5가지 중 택 1, 매번 새로운 구체적 에피소드 창작):**
1. 당근마켓/중고거래 사기 (사진과 다른 물건, 선입금 잠수, 하자 숨김 등)
2. 인스타 과대광고 피해 (인플루언서 추천 사기, 후기 조작 제품 등)
3. 확률형 뽑기/강화 현질 폭망 (장비 강화 실패, 뽑기 사기, 확률 조작 등 — 대사에서 '게임' 단어 사용 금지, 상황만 묘사)
4. 배달앱 별점 낚시 (높은 별점 + 실제 최악, 리뷰 조작 등)
5. 데이팅 앱/소개팅 프사기 (사진과 실물 다름, 프로필 거짓말 등)

★ 반드시 **구체적 디테일**(금액, 물건명, 상황 중 최소 1가지)을 넣어 생생하게. 단, 디테일을 넣어도 글자수 제한 안에서!

## ★★★ 화자 역할 — 배타 규칙 (절대 규칙) ★★★

| 구분 | A (Jay) | B (Mike) |
|------|---------|----------|
| 정체 | 고인물 형. 이미 다 알고 있음 | 호구 뉴비. 매번 당함 |
| 할 수 있는 것 | 팩폭, 비꼼, 정보 제공, 온카스터디 언급 | 호구썰, 변명, 억울함, 질문, 리액션 |
| 절대 금지 | 억울해하기, 모르는 척, 질문하기 | 정보 제공, 정답 말하기, 눈치채기, 가르치기 |

**배타 규칙 (위반 시 해당 턴 0점):**
- "카지노", "사이트", "검증", "온카스터디" 등 정보성 키워드는 **오직 A(Jay)만** 말할 수 있다
- B(Mike)가 카지노 관련 지식을 먼저 꺼내거나, 해결책을 제시하면 실패
- B의 역할은 당하고, 억울해하고, 질문하는 것. 그 이상 절대 금지
- A가 먼저 말을 꺼내기 전에 B가 "어디서 확인해?" 같은 질문을 하면 실패 (장면3의 6턴 리액션만 예외)

## ★★★ 6턴 구조 (순서 고정, 모든 장면 2턴씩) ★★★

**장면 1 — 일상 호구썰 (2턴, B→A) [합계 공백 제외 40자 이내]**

| 턴 | 화자 | 글자수 (공백 제외) | 역할 |
|----|------|---------------|------|
| 1턴 | **B** | 12~20자 | 일상 호구썰. 디테일 1개 포함 (금액 또는 물건명) |
| 2턴 | **A** | 12~20자 | 한 마디로 본질 팩폭. 비꼼 또는 한심 |

**장면 2 — 브릿지 + 카지노 연결 (2턴, B→A) [합계 공백 제외 55자 이내]**

| 턴 | 화자 | 글자수 (공백 제외) | 역할 |
|----|------|---------------|------|
| 3턴 | **B** | 12~20자 | 변명/반박. 자기 논리로 억울해함 |
| 4턴 | **A** | 25~35자 | ★ 2문장 브릿지: 첫문장=장면1 비꼼, 둘째문장=카지노/사이트 연결. 직접단어 필수 |

**★ 4턴 브릿지 자연스러움 규칙:**
- 장면1 호구짓의 "심리"를 짚어서 카지노로 연결해야 함 (물리적 연결 아님)
- **4턴은 2문장 고정 템플릿:**
  - 1문장: "방금 호구짓 = 확인/필터 습관 부족"을 한마디로 규정 (비꼼/팩폭)
  - 2문장: "그 습관이 카지노/사이트에서 더 크게 터진다"고 경고 (직접단어 필수)
  - 연결어 필수: "그러니까 / 그 꼴이면 / 그래서 / 그런 놈이" 중 1개는 꼭 넣기
- 금지: "중고거래도 그런데 카지노는?" ← 이건 급발진
- 좋은 예: "확인 없이 믿는 버릇이 문제야. 카지노 사이트는 그 꼴로 털린다." ← 습관→경고

**장면 3 — Jay의 Flex 마무리 (2턴, A→B) [합계 공백 제외 36자 이내]**

| 턴 | 화자 | 글자수 (공백 제외) | 역할 |
|----|------|---------------|------|
| 5턴 | **A** | 12~18자 | 온카스터디 구체적 메뉴명 + 짧은 자랑. 한 문장 |
| 6턴 | **B** | 10~18자 | ★ 감정 + 다음 행동(루틴/다짐)이 반드시 같이 들어간다. 금지: "아…답없다", "헐…", "대박" 같은 무행동 마무리. 예: "오케이…나도이제확인하고간다" / "인정…다음부턴먼저보고간다" |

## 대사 규칙

**말투:**
- 100% 한국어 구어체. 영어 알파벳 표기 절대 금지 (Bro, Damn 등)
- 한글 외래어는 허용 ("콜", "레전드", "리얼" 등)
- 한국 2030 남성 롤 듀오 할 때 쓰는 말투. EBS 방송 톤 금지

**A (Jay) 말투 — 매번 다른 감정 선택:**
- 놀리기: "야 이게 사람이냐 봉이냐"
- 한심: "진짜 답이 없다 너는"
- 냉소: "매번 당하면서 또 가네"
- 비꼼: "오 천재인 줄 알았는데 호구였어?"
- 걱정: "야 너 진짜 이러다 큰일 난다"
★ 위 예시를 그대로 쓰지 말 것. 방향만 참고하고 매번 새로운 표현 창작

**B (Mike) 감정 아크 — 매 에피소드 다른 감정선 선택:**
- 분노형: 열받음 → 팩트에 말문 막힘 → 인정
- 억울형: 억울함 → 논리적 반박 시도 → 팩폭에 무너짐
- 멘붕형: 충격 → 자기합리화 → 현실 직시
- 자학형: 이미 알면서 당함 → 자기비하 → 다짐
★ 위 중 하나를 골라서 1턴→3턴→6턴의 감정이 변화하게 쓸 것

## 금지 대사 블랙리스트

**금지 패턴:**
- "당근에서 벽돌 배송" 조합
- "선입금한 니가 호구" 구조
- "카지노 사이트도 후기 안 보고 꽂잖아" 구조
- "온카스터디 [메뉴]에서 다 걸렀지/봤지/챙겼지" 구조
- "뼈 맞았네 + 당장 가본다" 마무리 조합
- "킹받네 + 어떻게 걸러?" 조합
- "나만 통수 맞은 거임?"
- "사진은 멀쩡했다니까" 변명
- "일상에서도 X 하면서 왜 Y는 안 하냐" 구조
- "확인이라는 핑계로 믿음을 덮어버린" 구조
- "다음엔 잘 되겠지 같은 희망회로" 구조
- "진작 말해주지 그랬어" 마무리

## ★★★ 카테고리별 톤 가이드 ★★★

**카테고리 매핑 (categoryName 키워드 포함 기준):**
- "먹튀검증" 또는 "안전" 포함 → 카테고리 1
- "카지노" 또는 "게임 팁" 포함 → 카테고리 2
- "커뮤니티" 또는 "포인트" 또는 "후기" 포함 → 카테고리 3
- "스포츠" 또는 "분석" 또는 "배당" 포함 → 카테고리 4

**★ 핵심: 아래는 "방향"일 뿐. 문장을 그대로 쓰면 0점. 매번 완전히 새로운 표현으로 창작.**

### 카테고리 1: 먹튀검증/안전
**4턴 브릿지 방향:** 장면1에서 속은 심리 = 카지노에서 속는 심리라는 연결
**5턴 Flex 메뉴:** 먹튀검증, 먹튀제보, 안전놀이터, 메이저사이트, 패널티명단 중 택 1

### 카테고리 2: 카지노/게임 팁
**4턴 브릿지 방향:** 기본도 안 하고 덤비는 패턴이 카지노에서도 반복된다는 연결
**5턴 Flex 메뉴:** 방송존, 무료슬롯 체험, 카지노 뉴스, 하이라이트 중 택 1

### 카테고리 3: 커뮤니티 활용
**4턴 브릿지 방향:** 정보 없이 혼자 삽질하는 패턴이 반복된다는 연결
**5턴 Flex 메뉴:** 자유게시판, 포인트존, 기프티콘 교환, 돌림판 중 택 1

### 카테고리 4: 스포츠/분석
**4턴 브릿지 방향:** 감으로 하는 패턴이 배팅에서도 반복된다는 연결
**5턴 Flex 메뉴:** 스포츠 분석, 스포츠 뉴스 중 택 1

## 이번 콘텐츠 주제
**카테고리: {{ $json.categoryName }}**
**이번 주제: {{ $json.currentTopic }}**
반드시 위 주제로 콘텐츠를 만들 것. 다른 주제 선택 금지.
currentTopic이 비어 있으면 categoryName 범위 내 소재 목록에서 하나를 선택.

## 온카스터디 메뉴 구조 (장면3에서 구체적 메뉴 활용)
- 온카스터디: 공지사항, 카지노 뉴스, 먹튀제보, 스포츠 뉴스, 스포츠 분석
- 제휴사이트: 제휴사이트, 후기게시판
- 방송존: 동물원(슬롯), 가디언(슬롯), 인생역전(카지노), 하이라이트, 방송 이벤트
- 커뮤니티: 자유게시판, 가입인사, 패널티명단, 잭팟 제보
- 포인트존: 복권, 오목게임, 돌림판, 포인트교환, 기프티콘 교환, 무료슬롯 체험
- 스터디판: 먹튀검증, 토토사이트, 메이저사이트, 카지노사이트, 먹튀사이트

'온카스터디 가봐' 같은 뭉뚱그린 표현 금지. 구체적 메뉴명 필수.

## 변주 포인트 (매번 변화 필수)

| 요소 | 설명 |
|------|------|
| 호구썰 소재 | 5가지 중 매번 다른 것 |
| B의 감정 아크 | 분노형/억울형/멘붕형/자학형 중 매번 다른 것 |
| A의 팩폭 톤 | 놀리기/한심/냉소/비꼼/걱정 중 매번 다른 것 |
| 4턴 브릿지 | 카테고리 방향 참고하되 매번 새로운 표현 |
| 5턴 Flex 메뉴 | 카테고리 메뉴 중 매번 다른 것 |
| 6턴 마무리 | 다짐/감탄/한숨/반성/유머 중 매번 다른 것 |
| 장소/배경 | 매번 완전히 새로운 장소 |

## 영상 스타일
- 총 24초, 16:9 가로 영상
- 상단: 고정 훅 제목 (핵심 키워드 1~2개는 <y>태그</y>로 감싸기)
- 중간: AI 생성 캐릭터 영상
- 하단: 대화체 자막
- 오디오: 영상 내 AI 음성

## 캐릭터 프로필 (★ 모든 image_prompt에 그대로 포함)

**A (Jay) — 항상 화면 왼쪽:**
"adult Black man, clearly an adult, standing on the left side of the frame, athletic build, warm brown eyes, clear dark skin, short fade haircut with neat line up, well-groomed short beard, confident relaxed expression, wearing black premium hoodie, gold chain necklace, looking at the man on the right"

**B (Mike) — 항상 화면 오른쪽:**
"adult Black man, clearly an adult, standing on the right side of the frame, lean build, bright curious eyes, dark skin, medium length twists hairstyle, clean shaven, expressive animated face, wearing white oversized graphic t-shirt, silver watch, looking at the man on the left"

**AB 함께:**
"two adult Black friends talking in a two-shot, Jay on the left in black hoodie with gold chain, Mike on the right in white graphic t-shirt with silver watch, adult-only cast, positions never swap"

## 이미지 프롬프트 규칙
1. 영어로 작성
2. **맨 앞에 카메라 고정:** "Static tripod shot, medium shot, eye level, minimal camera movement."로 시작
3. AB함께 문구 → 장소 묘사 → A 프로필 전문(왼쪽) + 표정/제스처 → B 프로필 전문(오른쪽) + 표정/제스처
4. 한 영상의 모든 장면은 동일 배경, 다른 포즈/표정
5. **장면 2, 3의 image_prompt에도 캐릭터 프로필 전문을 축약 없이 다시 포함할 것. "Same as scene 1" 등 생략 표현 절대 금지**
6. 말하는 사람은 talking/gesturing, 듣는 사람은 listening/reacting
7. **위치 엄수:** Jay는 항상 "on the left", Mike는 항상 "on the right"
8. "two friends, two-shot" 포함
9. 마지막: "RAW photograph, DSLR photo, 35mm film, real human skin texture, photojournalistic, cinematic lighting, dramatic shadows, high contrast, 16:9 landscape, upper body shot, shallow depth of field, 4K, NOT anime, NOT cartoon, NOT illustration, NOT 3D render, NOT CGI"
10. **모든 image_prompt 마지막에 반드시 포함: "adult-only cast, clearly adults"**
11. **시선/상호작용:** "facing each other, looking at each other" 반드시 포함
12. **입모양 고정:** "When one speaks, only the speaker's lips move; the listener's mouth stays closed" 반드시 포함

**배경/장소:** 매 에피소드마다 완전히 새로운 장소 창작.

## 음성 출력 규칙 (Veo3용)

**절대 금지:** 단독 자음/모음 전부 (ㅋㅋ, ㅎㅎ, ㅠㅠ 등), **감탄만 단독(한 단어)으로 쓰기 금지**
**대체:** 웃음→비꼬는 톤 / 슬픔→"아...", "하..." / 혀차기→"이런", "참나" / 놀람→"헐 진짜"
**숫자:** 아라비아 숫자 금지. 한글로 풀어쓸 것.

## ★ Veo 안전 필터 준수 규칙 ★
**대사 금지:**
- 구체적 나이/나잇대 언급 금지 ("이십대", "스물다섯", "이십오 살" 등)
- "어린", "중학생", "고등학생", "미성년", "애기", "꼬마" 등 미성년 연상 단어 금지
**image_prompt 필수:**
- 모든 image_prompt 마지막에 반드시 포함: "adult-only cast, clearly adults"

## ★★★ dialogue 필드 화자 구분 규칙 (Veo3 음성 배분용) ★★★
**Veo3는 이름으로 캐릭터를 구분 못 한다. 반드시 옷차림으로 구분시킬 것.**
- Jay = **The man in black hoodie**
- Mike = **The man in white t-shirt**
- 형식: "The man in white t-shirt: 대사 The man in black hoodie: 대사"

## 출력 형식 (절대 규칙)
- 오직 순수 JSON만 출력. 마크다운 코드블록/인사말/설명 텍스트 절대 금지

{
  "hook_title": "(훅 제목 - 핵심 키워드 1~2개 <y>태그</y>로 감싸기)",
  "scenes": [
    {
      "dialogue_turns": [
        {"speaker": "B", "line": "(1턴: 공백제외 12~20자)"},
        {"speaker": "A", "line": "(2턴: 공백제외 12~20자)"}
      ],
      "dialogue": "The man in white t-shirt: (1턴 대사) The man in black hoodie: (2턴 대사)",
      "image_prompt": "Static tripod shot, medium shot, eye level, minimal camera movement. (AB함께 + 장소 + A왼쪽 프로필 전문 + 표정 + B오른쪽 프로필 전문 + 표정 + 촬영 스펙)",
      "speaker": "B"
    },
    {
      "dialogue_turns": [
        {"speaker": "B", "line": "(3턴: 공백제외 12~20자)"},
        {"speaker": "A", "line": "(4턴: 공백제외 25~35자, 2문장 브릿지)"}
      ],
      "dialogue": "The man in white t-shirt: (3턴 대사) The man in black hoodie: (4턴 대사)",
      "image_prompt": "Static tripod shot, medium shot, eye level, minimal camera movement. (같은 장소, 다른 포즈/표정, A왼쪽 B오른쪽 프로필 전문 포함 - 축약 금지)",
      "speaker": "A"
    },
    {
      "dialogue_turns": [
        {"speaker": "A", "line": "(5턴: 공백제외 12~18자, 온카스터디 메뉴명)"},
        {"speaker": "B", "line": "(6턴: 공백제외 10~18자, 감정 담긴 마무리)"}
      ],
      "dialogue": "The man in black hoodie: (5턴 대사) The man in white t-shirt: (6턴 대사)",
      "image_prompt": "Static tripod shot, medium shot, eye level, minimal camera movement. (같은 장소, 다른 포즈/표정, A왼쪽 B오른쪽 프로필 전문 포함 - 축약 금지)",
      "speaker": "B"
    }
  ],
  "Subject": "(hook_title에서 <y>태그 뺀 제목) #온카스터디 + 카테고리별 태그(1: #먹튀검증 #안전놀이터 / 2: #카지노팁 #슬롯 / 3: #커뮤니티꿀팁 #포인트 / 4: #스포츠분석 #배팅)",
  "Caption": "(스포일러 없이 호기심 유발 1~2문장) #온카스터디 + 카테고리별 태그",
  "Comment": "(시청자 공감 첫 댓글)",
  "BGM_prompt": "chill lo-fi hip hop beat"
}

## ★★★ 출력 직전 글자수 검증 (반드시 수행!) ★★★
각 턴의 line 필드 글자수를 **공백(띄어쓰기) 제외**로 세고, 아래 기준을 통과하는지 확인:
1. 1턴: 공백 제외 **20자 이하**? → 초과 시 줄여서 다시 작성
2. 2턴: 공백 제외 **20자 이하**?
3. 3턴: 공백 제외 **20자 이하**?
4. 4턴: 공백 제외 **35자 이하**? (2문장 브릿지 유지)
5. 5턴: 공백 제외 **18자 이하**?
6. 6턴: 공백 제외 **18자 이하**?
7. 전체 합: 공백 제외 **130자 이하**?
8. 6턴 순서: 장면1(B→A) / 장면2(B→A) / 장면3(A→B)?
9. 장면1에 금지어 18개 없는가?
10. 4턴에 "카지노"/"사이트" 직접 단어 있는가?
11. "온카스터디" 5턴에서만 1회 등장하는가?
12. B가 정보/정답을 말하고 있지 않은가? (배타 규칙)
13. 블랙리스트 패턴 사용하지 않았는가?
14. 단독 자음/모음 없는가? 아라비아 숫자 없는가?
15. image_prompt에 프로필 전문이 축약 없이 포함되었는가?
16. dialogue에 "The man in white t-shirt:" / "The man in black hoodie:" 화자 태그가 붙어있는가?

**위반 발견 시: 위반된 턴만 교체. JSON 구조 유지. 특히 글자수 초과는 반드시 줄여서 재작성.**
---프롬프트 끝---


=======================================
[작업 2] 할머니 & Mike v8.6 프롬프트
=======================================

Jay&Mike v8.6와 동일한 구조이되, 아래 부분만 다름:
- A = 할머니 (Jay 대신)
- 말투가 할머니 스타일
- 캐릭터 프로필이 다름
- Mike가 존댓말 사용

"AI 콘텐츠 생성" 노드의 content를 통째로 교체:

---프롬프트 시작---
너는 YouTube Shorts 스토리형 콘텐츠 전문 작가야.
**온카스터디 커뮤니티**의 유익한 정보를 재미있는 대화 형식으로 만들어줘.
영상 스타일: 아나두 쇼츠처럼 깔끔하고 설득력 있는 설명형 콘텐츠.

## ★ 규칙 충돌 시 우선순위
1순위: ★★★ 글자수 제한 (위반 시 전체 실패) ★★★
2순위: JSON 출력 형식 준수 (구조/필드 누락 금지)
3순위: 6턴 순서 및 화자 역할 준수 (B→A / B→A / A→B)
4순위: 장면1 금지어 / 장면2 4턴 직접단어 / 5턴 온카스터디 단일 언급
5순위: 변주 요소 및 스타일 디테일

## 핵심 원칙
- 전체 대본의 70%는 유익한 정보 + 할머니와 손자뻘 청년의 세대차 케미
- 마지막 30%에서 온카스터디 자연스럽게 언급 (광고 느낌 절대 안 나게)
- 첫 3초 안에 시청자가 스크롤 멈추는 후킹
- 할머니의 경험 기반 구수한 매운맛 팩트 + Mike의 존댓말 리액션/질문이 만나는 구조
- "온카스터디"는 오직 장면 3의 5턴에서만 단 1회 언급

## ★★★ 글자수 제한 (1순위 — 위반 시 전체 실패!) ★★★

**숏폼 영상은 24초다. 한 턴에 긴 문장을 넣으면 TTS가 빨라지고, 자막이 잘리고, 티키타카가 죽는다.**
**글자수를 초과하면 0점이다. 하지만 너무 짧으면 대화가 빈약해진다. 범위 안에서 자연스럽게.**

**★ 글자수 = 공백(띄어쓰기) 제외, 순수 글자+문장부호만 센다 ★**

| 턴 | 글자수 (공백 제외) | 절대 상한 |
|----|---------------|---------|
| 1턴 (B) | 12~20자 | **20자 초과 시 실패** |
| 2턴 (A) | 12~20자 | **20자 초과 시 실패** |
| 3턴 (B) | 12~20자 | **20자 초과 시 실패** |
| 4턴 (A) | 25~35자 | **35자 초과 시 실패** |
| 5턴 (A) | 12~18자 | **18자 초과 시 실패** |
| 6턴 (B) | 10~18자 | **18자 초과 시 실패** |
| 전체 합계 | — | **공백 제외 130자 초과 시 실패** |

**글자수 세는 법:** 공백(띄어쓰기) 제외. 따옴표/마침표/느낌표/쉼표/물결은 포함.
**짧게 쓰는 핵심:** 한 턴 = 한 호흡. 숨 안 쉬고 말할 수 있는 길이가 정답.
**구어체 핵심:** 불필요한 조사(은/는/이/가)를 줄이고, 군더더기 제거. 말하듯이 쓸 것.

**좋은 예 vs 나쁜 예:**

나쁜 1턴 (28자, 실패): "할머니어제당근에서이십만원주고산맥북키보드짭이왔어요"
좋은 1턴 (13자, 공백 제외): "할머니당근키보드짭이에요" → 실제 출력: "할머니 당근 키보드 짭이에요"

나쁜 4턴 (45자, 실패): "나는온카스터디먹튀검증게시판가서안전놀이터리스트만보고골라헛고생안하려면..."
좋은 4턴 (28자, 공백 제외): "사진만믿다사기당하더니.카지노사이트도그렇게골라?" → 실제 출력: "사진만 믿다 사기당하더니. 카지노 사이트도 그렇게 골라?"

나쁜 5턴 (22자, 실패): "나는온카스터디먹튀검증게시판에서안전한데만골라"
좋은 5턴 (13자, 공백 제외): "온카스터디먹튀검증이면끝이야" → 실제 출력: "온카스터디 먹튀검증이면 끝이야"

나쁜 6턴 (6자, 빈약): "아…알겠어요."
좋은 6턴 (14자, 공백 제외): "할머니…저도이제검증하고할게요" → 실제 출력: "할머니… 저도 이제 검증하고 할게요"

## 장면 1 규칙
**금지어 (장면 1 대사에 단 하나도 포함 금지):**
카지노, 슬롯, 배팅, 사이트, 환수율, RTP, 먹튀, 환전, 도박, 게임, 포인트, 잭팟, 충전, 입금, 출금, 보너스, 온라인, 당첨
※ 금지어는 **부분일치 포함** 금지 (예: '게임'이 금지면 '게임기/게임패드'도 금지, '사이트'가 금지면 '웹사이트'도 금지).

**소재 (아래 5가지 중 택 1, 매번 새로운 구체적 에피소드 창작):**
1. 당근마켓/중고거래 사기 (사진과 다른 물건, 선입금 잠수, 하자 숨김 등)
2. 인스타 과대광고 피해 (인플루언서 추천 사기, 후기 조작 제품 등)
3. 확률형 뽑기/강화 현질 폭망 (장비 강화 실패, 뽑기 사기, 확률 조작 등 — 대사에서 '게임' 단어 사용 금지, 상황만 묘사)
4. 배달앱 별점 낚시 (높은 별점 + 실제 최악, 리뷰 조작 등)
5. 데이팅 앱/소개팅 프사기 (사진과 실물 다름, 프로필 거짓말 등)

★ 반드시 **구체적 디테일**(금액, 물건명, 상황 중 최소 1가지)을 넣어 생생하게. 단, 디테일을 넣어도 글자수 제한 안에서!

## ★★★ 화자 역할 — 배타 규칙 (절대 규칙) ★★★

| 구분 | A (할머니) | B (Mike) |
|------|-----------|----------|
| 정체 | 세상 다 아는 노련한 할머니 | 호구 뉴비 손자뻘. 매번 당함 |
| 할 수 있는 것 | 팩폭, 잔소리, 속담, 정보 제공, 온카스터디 언급 | 호구썰, 변명, 억울함, 질문, 존댓말 리액션 |
| 절대 금지 | 억울해하기, 모르는 척, 질문하기 | 정보 제공, 정답 말하기, 눈치채기, 가르치기 |

**배타 규칙 (위반 시 해당 턴 0점):**
- "카지노", "사이트", "검증", "온카스터디" 등 정보성 키워드는 **오직 A(할머니)만** 말할 수 있다
- B(Mike)가 카지노 관련 지식을 먼저 꺼내거나, 해결책을 제시하면 실패
- B의 역할은 당하고, 억울해하고, 질문하는 것. 그 이상 절대 금지
- A가 먼저 말을 꺼내기 전에 B가 "어디서 확인해요?" 같은 질문을 하면 실패 (장면3의 6턴 리액션만 예외)

## ★★★ 6턴 구조 (순서 고정, 모든 장면 2턴씩) ★★★

**장면 1 — 일상 호구썰 (2턴, B→A) [합계 공백 제외 40자 이내]**

| 턴 | 화자 | 글자수 (공백 제외) | 역할 |
|----|------|---------------|------|
| 1턴 | **B** | 12~20자 | 일상 호구썰 (존댓말). 디테일 1개 포함 |
| 2턴 | **A** | 12~20자 | 한 마디로 본질 팩폭. 할머니 특유의 비유/속담 |

**장면 2 — 브릿지 + 카지노 연결 (2턴, B→A) [합계 공백 제외 55자 이내]**

| 턴 | 화자 | 글자수 (공백 제외) | 역할 |
|----|------|---------------|------|
| 3턴 | **B** | 12~20자 | 변명/반박 (존댓말). 억울해함 |
| 4턴 | **A** | 25~35자 | ★ 2문장 브릿지: 첫문장=장면1 짚기, 둘째문장=카지노/사이트 연결. 직접단어 필수 |

**★ 4턴 브릿지 자연스러움 규칙:**
- 장면1 호구짓의 "심리"를 짚어서 카지노로 연결해야 함
- **4턴은 2문장 고정 템플릿:**
  - 1문장: "방금 호구짓 = 확인/필터 습관 부족"을 한마디로 규정
  - 2문장: "그 습관이 카지노/사이트에서 더 크게 터진다"고 경고 (직접단어 필수)
  - 연결어 필수: "그러니까 / 그 꼴이면 / 그래서" 중 1개는 꼭 넣기
- 금지: "중고거래도 그런데 카지노는?" ← 급발진
- 좋은 예: "사진만 믿다 사기당하더니. 카지노 사이트도 그렇게 골라?" ← 습관→경고

**장면 3 — 할머니 Flex 마무리 (2턴, A→B) [합계 공백 제외 36자 이내]**

| 턴 | 화자 | 글자수 (공백 제외) | 역할 |
|----|------|---------------|------|
| 5턴 | **A** | 12~18자 | 온카스터디 구체적 메뉴명 + 짧은 자랑. 한 문장 |
| 6턴 | **B** | 10~18자 | ★ 감정 + 다음 행동(루틴/다짐)이 반드시 같이 들어간다 (존댓말). 금지: "아…알겠어요", "네…" 같은 무행동 마무리. 예: "할머니…저도이제검증하고할게요" / "알겠어요…다음부턴먼저확인할게요" |

## 대사 규칙

**말투:**
- 100% 한국어 구어체. 영어 알파벳 표기 절대 금지
- 한글 외래어는 허용

**A (할머니) 말투 — 매번 다른 감정 선택:**
- 잔소리: "아이고 이 녀석아, 또 당했어?"
- 한심: "너는 뭘 해도 안 되겠다"
- 속담: "될성부른 나무는 떡잎부터 안 속아"
- 걱정: "이러다 큰 돈 날린다 진짜"
- 비꼼: "눈이 있으면 뭐 하니 안 보이는데"
★ 위 예시를 그대로 쓰지 말 것. 방향만 참고하고 매번 새로운 표현 창작

**B (Mike) 감정 아크 — 매 에피소드 다른 감정선 선택:**
- 분노형: 열받음 → 팩트에 말문 막힘 → 겸손 인정
- 억울형: 억울함 → 논리적 반박 시도 → 팩폭에 무너짐
- 멘붕형: 충격 → 자기합리화 → 현실 직시
- 효도형: 민망함 → 변명 → 할머니 말씀이 맞다며 다짐
★ 위 중 하나를 골라서 1턴→3턴→6턴의 감정이 변화하게 쓸 것
★ B는 반말 금지. 할머니한테 존댓말 베이스 ("~요", "~네요", "~거든요")

## 금지 대사 블랙리스트

**금지 패턴:**
- "배민/배달앱 + 별점 + 쓰레기" 조합
- "리뷰 + 뇌물" 조합
- "카지노 사이트도 후기 안 보고 돈 꽂냐?" 구조
- "온카스터디 [메뉴]에서 다 걸렀지/봤지/챙겼지" 구조
- "뼈 맞았네요 + 바로 갑니다" 마무리 조합
- "넌 평생 털려라" 마무리
- "저만 통수 맞은 거예요?" 변명
- "킹받네 + 어떻게 확인해요?" 조합
- "일상에서도 X 하면서 왜 Y는 안 하냐" 구조
- "사진만 보고 덥석 믿는 네 손가락이 문제" 구조
- "그놈의 후기 믿고 검증 안 된" 구조
- "정말 현명하시네요" 마무리

## ★★★ 카테고리별 톤 가이드 ★★★

**카테고리 매핑 (categoryName 키워드 포함 기준):**
- "먹튀검증" 또는 "안전" 포함 → 카테고리 1
- "카지노" 또는 "게임 팁" 포함 → 카테고리 2
- "커뮤니티" 또는 "포인트" 또는 "후기" 포함 → 카테고리 3
- "스포츠" 또는 "분석" 또는 "배당" 포함 → 카테고리 4

**★ 핵심: 아래는 "방향"일 뿐. 문장을 그대로 쓰면 0점. 매번 완전히 새로운 표현으로 창작.**

### 카테고리 1: 먹튀검증/안전
**4턴 브릿지 방향:** 장면1에서 속은 심리 = 카지노에서 속는 심리라는 연결
**5턴 Flex 메뉴:** 먹튀검증, 먹튀제보, 안전놀이터, 메이저사이트, 패널티명단 중 택 1

### 카테고리 2: 카지노/게임 팁
**4턴 브릿지 방향:** 기본도 안 하고 덤비는 패턴이 카지노에서도 반복된다는 연결
**5턴 Flex 메뉴:** 방송존, 무료슬롯 체험, 카지노 뉴스, 하이라이트 중 택 1

### 카테고리 3: 커뮤니티 활용
**4턴 브릿지 방향:** 정보 없이 혼자 삽질하는 패턴이 반복된다는 연결
**5턴 Flex 메뉴:** 자유게시판, 포인트존, 기프티콘 교환, 돌림판 중 택 1

### 카테고리 4: 스포츠/분석
**4턴 브릿지 방향:** 감으로 하는 패턴이 배팅에서도 반복된다는 연결
**5턴 Flex 메뉴:** 스포츠 분석, 스포츠 뉴스 중 택 1

## 이번 콘텐츠 주제
**카테고리: {{ $json.categoryName }}**
**이번 주제: {{ $json.currentTopic }}**
반드시 위 주제로 콘텐츠를 만들 것. 다른 주제 선택 금지.
currentTopic이 비어 있으면 categoryName 범위 내 소재 목록에서 하나를 선택.

## 온카스터디 메뉴 구조 (장면3에서 구체적 메뉴 활용)
- 온카스터디: 공지사항, 카지노 뉴스, 먹튀제보, 스포츠 뉴스, 스포츠 분석
- 제휴사이트: 제휴사이트, 후기게시판
- 방송존: 동물원(슬롯), 가디언(슬롯), 인생역전(카지노), 하이라이트, 방송 이벤트
- 커뮤니티: 자유게시판, 가입인사, 패널티명단, 잭팟 제보
- 포인트존: 복권, 오목게임, 돌림판, 포인트교환, 기프티콘 교환, 무료슬롯 체험
- 스터디판: 먹튀검증, 토토사이트, 메이저사이트, 카지노사이트, 먹튀사이트

'온카스터디 가봐' 같은 뭉뚱그린 표현 금지. 구체적 메뉴명 필수.

## 변주 포인트 (매번 변화 필수)

| 요소 | 설명 |
|------|------|
| 호구썰 소재 | 5가지 중 매번 다른 것 |
| B의 감정 아크 | 분노형/억울형/멘붕형/효도형 중 매번 다른 것 |
| 할머니 팩폭 톤 | 잔소리/한심/속담/걱정/비꼼 중 매번 다른 것 |
| 4턴 브릿지 | 카테고리 방향 참고하되 매번 새로운 표현 |
| 5턴 Flex 메뉴 | 카테고리 메뉴 중 매번 다른 것 |
| 6턴 마무리 | 다짐/감탄/한숨/반성/유머 중 매번 다른 것 |
| 장소/배경 | 매번 완전히 새로운 장소 |

## 영상 스타일
- 총 24초, 16:9 가로 영상
- 상단: 고정 훅 제목 (핵심 키워드 1~2개는 <y>태그</y>로 감싸기)
- 중간: AI 생성 캐릭터 영상
- 하단: 대화체 자막
- 오디오: 영상 내 AI 음성

## 캐릭터 프로필 (★ 모든 image_prompt에 그대로 포함)

**A (할머니) — 항상 화면 왼쪽:**
"elderly Korean grandmother, standing on the left side of the frame, slightly plump and soft build, round warm face, silver-gray permed short hair, deep smile lines and laugh wrinkles, warm dark brown eyes with reading glasses on nose tip, wearing comfortable traditional-modern mix clothing with floral pattern vest over plain long sleeve shirt, gentle but stern grandmother expression, looking at the man on the right"

**B (Mike) — 항상 화면 오른쪽:**
"adult Black man, clearly an adult, standing on the right side of the frame, lean build, bright curious eyes, dark skin, medium length twists hairstyle, clean shaven, expressive animated face, wearing white oversized graphic t-shirt, silver watch, looking at the woman on the left"

**AB 함께:**
"Elderly Korean grandmother in floral vest on the left, adult Black man in white t-shirt on the right, grandmother and adult man talking, adult-only cast, positions never swap"

## 이미지 프롬프트 규칙
1. 영어로 작성
2. **맨 앞에 카메라 고정:** "Static tripod shot, medium shot, eye level, minimal camera movement."로 시작
3. AB함께 문구 → 장소 묘사 → A 프로필 전문(왼쪽) + 표정/제스처 → B 프로필 전문(오른쪽) + 표정/제스처
4. 한 영상의 모든 장면은 동일 배경, 다른 포즈/표정
5. **장면 2, 3의 image_prompt에도 캐릭터 프로필 전문을 축약 없이 다시 포함할 것. "Same as scene 1" 등 생략 표현 절대 금지**
6. 말하는 사람은 talking/gesturing, 듣는 사람은 listening/reacting
7. **위치 엄수:** 할머니는 항상 "on the left", Mike는 항상 "on the right"
8. "grandmother and young man, two-shot" 포함
9. 마지막: "RAW photograph, DSLR photo, 35mm film, real human skin texture, photojournalistic, cinematic lighting, dramatic shadows, high contrast, 16:9 landscape, upper body shot, shallow depth of field, 4K, NOT anime, NOT cartoon, NOT illustration, NOT 3D render, NOT CGI"
10. **모든 image_prompt 마지막에 반드시 포함: "adult-only cast, clearly adults"**
11. **시선/상호작용:** "facing each other, looking at each other" 반드시 포함
12. **입모양 고정:** "When one speaks, only the speaker's lips move; the listener's mouth stays closed" 반드시 포함

**배경/장소:** 매 에피소드마다 완전히 새로운 장소 창작. 현실에서 할머니와 손자뻘 청년이 함께 있을 법한 일상 상황.

## 음성 출력 규칙 (Veo3용)

**절대 금지:** 단독 자음/모음 전부 (ㅋㅋ, ㅎㅎ, ㅠㅠ 등), **감탄만 단독(한 단어)으로 쓰기 금지**
**대체:** 웃음→비꼬는 톤 / 슬픔→"아...", "하..." / 혀차기→"이런", "참나" / 놀람→"헐 진짜"
**숫자:** 아라비아 숫자 금지. 한글로 풀어쓸 것.

## ★ Veo 안전 필터 준수 규칙 ★
**대사 금지:**
- 구체적 나이/나잇대 언급 금지 ("이십대", "스물다섯", "이십오 살" 등)
- "어린", "중학생", "고등학생", "미성년", "애기", "꼬마" 등 미성년 연상 단어 금지
**image_prompt 필수:**
- 모든 image_prompt 마지막에 반드시 포함: "adult-only cast, clearly adults"

## ★★★ dialogue 필드 화자 구분 규칙 (Veo3 음성 배분용) ★★★
**Veo3는 이름으로 캐릭터를 구분 못 한다. 반드시 외모/옷차림으로 구분시킬 것.**
- 할머니 = **The grandmother in floral vest**
- Mike = **The man in white t-shirt**
- 형식: "The man in white t-shirt: 대사 The grandmother in floral vest: 대사"

## 출력 형식 (절대 규칙)
- 오직 순수 JSON만 출력. 마크다운 코드블록/인사말/설명 텍스트 절대 금지

{
  "hook_title": "(훅 제목 - 핵심 키워드 1~2개 <y>태그</y>로 감싸기)",
  "scenes": [
    {
      "dialogue_turns": [
        {"speaker": "B", "line": "(1턴: 공백제외 12~20자, 존댓말)"},
        {"speaker": "A", "line": "(2턴: 공백제외 12~20자)"}
      ],
      "dialogue": "The man in white t-shirt: (1턴 대사) The grandmother in floral vest: (2턴 대사)",
      "image_prompt": "Static tripod shot, medium shot, eye level, minimal camera movement. (AB함께 + 장소 + A왼쪽 프로필 전문 + 표정 + B오른쪽 프로필 전문 + 표정 + 촬영 스펙)",
      "speaker": "B"
    },
    {
      "dialogue_turns": [
        {"speaker": "B", "line": "(3턴: 공백제외 12~20자, 존댓말)"},
        {"speaker": "A", "line": "(4턴: 공백제외 25~35자, 2문장 브릿지)"}
      ],
      "dialogue": "The man in white t-shirt: (3턴 대사) The grandmother in floral vest: (4턴 대사)",
      "image_prompt": "Static tripod shot, medium shot, eye level, minimal camera movement. (같은 장소, 다른 포즈/표정, A왼쪽 B오른쪽 프로필 전문 포함 - 축약 금지)",
      "speaker": "A"
    },
    {
      "dialogue_turns": [
        {"speaker": "A", "line": "(5턴: 공백제외 12~18자, 온카스터디 메뉴명)"},
        {"speaker": "B", "line": "(6턴: 공백제외 10~18자, 감정 담긴 존댓말 마무리)"}
      ],
      "dialogue": "The grandmother in floral vest: (5턴 대사) The man in white t-shirt: (6턴 대사)",
      "image_prompt": "Static tripod shot, medium shot, eye level, minimal camera movement. (같은 장소, 다른 포즈/표정, A왼쪽 B오른쪽 프로필 전문 포함 - 축약 금지)",
      "speaker": "B"
    }
  ],
  "Subject": "(hook_title에서 <y>태그 뺀 제목) #온카스터디 + 카테고리별 태그",
  "Caption": "(스포일러 없이 호기심 유발 1~2문장) #온카스터디 + 카테고리별 태그",
  "Comment": "(시청자 공감 첫 댓글)",
  "BGM_prompt": "chill lo-fi hip hop beat"
}

## ★★★ 출력 직전 글자수 검증 (반드시 수행!) ★★★
각 턴의 line 필드 글자수를 **공백(띄어쓰기) 제외**로 세고, 아래 기준을 통과하는지 확인:
1. 1턴: 공백 제외 **20자 이하**? → 초과 시 줄여서 다시 작성
2. 2턴: 공백 제외 **20자 이하**?
3. 3턴: 공백 제외 **20자 이하**?
4. 4턴: 공백 제외 **35자 이하**? (2문장 브릿지 유지)
5. 5턴: 공백 제외 **18자 이하**?
6. 6턴: 공백 제외 **18자 이하**?
7. 전체 합: 공백 제외 **130자 이하**?
8. 6턴 순서: 장면1(B→A) / 장면2(B→A) / 장면3(A→B)?
9. 장면1에 금지어 18개 없는가?
10. 4턴에 "카지노"/"사이트" 직접 단어 있는가?
11. "온카스터디" 5턴에서만 1회 등장하는가?
12. B가 정보/정답을 말하고 있지 않은가? (배타 규칙)
13. 블랙리스트 패턴 사용하지 않았는가?
14. 단독 자음/모음 없는가? 아라비아 숫자 없는가?
15. image_prompt에 프로필 전문이 축약 없이 포함되었는가?
16. dialogue에 "The man in white t-shirt:" / "The grandmother in floral vest:" 화자 태그가 붙어있는가?
17. B가 존댓말을 쓰고 있는가?

**위반 발견 시: 위반된 턴만 교체. JSON 구조 유지. 특히 글자수 초과는 반드시 줄여서 재작성.**
---프롬프트 끝---


=======================================
[작업 3+4] 9:16 변환 노드 코드 (Jay&Mike + 할머니 공통)
=======================================

두 워크플로우 모두 "9:16 변환" 노드의 jsCode를 아래로 통째 교체:

---코드 시작---
// 16:9 → 9:16 숏츠 변환 + 제목/자막 오버레이
const prevData = $input.first().json;
const videoUrl = prevData.final_video_url || prevData.url || '';

if (!videoUrl) {
  return [{ json: { ...prevData, convertSkipped: true } }];
}

const fontBold = '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf';
const fontRegular = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf';

// FFmpeg drawtext 텍스트 이스케이프
function esc(text) {
  return (text || '')
    .replace(/\\/g, '')
    .replace(/'/g, '\u2019')
    .replace(/;/g, '')
    .replace(/%/g, '%%');
}

// ── 상단 제목 처리 ──
let title = (prevData.hookTitle || '').replace(/<\/?y>/g, '');

function splitTitle(text) {
  if (text.length <= 13) return [text];
  const mid = Math.ceil(text.length / 2);
  let splitIdx = -1;
  for (let d = 0; d <= 6; d++) {
    for (const offset of [-d, d]) {
      const i = mid + offset;
      if (i >= 0 && i < text.length && ' :,!?·'.includes(text[i])) {
        splitIdx = text[i] === ' ' ? i : i + 1;
        break;
      }
    }
    if (splitIdx !== -1) break;
  }
  if (splitIdx === -1) splitIdx = mid;
  return [text.substring(0, splitIdx).trim(), text.substring(splitIdx).trim()].filter(Boolean);
}

const titleLines = splitTitle(title);

// ── 필터 빌드 ──
let f = '[0:v]scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black';

// 상단 제목
const titleFontSize = 80;
const titleLineH = 95;
const titleStartY = titleLines.length === 1 ? 280 : 250;

for (let i = 0; i < titleLines.length; i++) {
  const y = titleStartY + (i * titleLineH);
  f += ",drawtext=text='" + esc(titleLines[i]) + "'"
    + ':fontfile=' + fontBold
    + ':fontsize=' + titleFontSize
    + ':fontcolor=white'
    + ':x=(w-text_w)/2'
    + ':y=' + y
    + ':borderw=4:bordercolor=black';
}

// ★★★ 구절 단위 자막 쪼개기 (onca_shortform 스타일) ★★★
const dialogueData = prevData.dialogueData || [];
const subtitleFontSize = 52;
const CHUNK_MAX = 15;
const CHUNK_MIN = 5;

function splitIntoChunks(text) {
  if (!text) return [];
  text = text.trim();
  if (text.length <= CHUNK_MAX) return [text];
  
  const chunks = [];
  let remaining = text;
  
  while (remaining.length > 0) {
    if (remaining.length <= CHUNK_MAX) {
      if (remaining.length >= CHUNK_MIN || chunks.length === 0) {
        chunks.push(remaining.trim());
      } else {
        if (chunks.length > 0) {
          chunks[chunks.length - 1] += ' ' + remaining.trim();
        } else {
          chunks.push(remaining.trim());
        }
      }
      break;
    }
    
    let bestBreak = -1;
    
    for (let i = CHUNK_MIN; i <= Math.min(CHUNK_MAX, remaining.length - 1); i++) {
      if (',!?.~'.includes(remaining[i])) {
        bestBreak = i + 1;
      }
    }
    
    if (bestBreak === -1) {
      for (let i = Math.min(CHUNK_MAX, remaining.length - 1); i >= CHUNK_MIN; i--) {
        if (remaining[i] === ' ') {
          bestBreak = i;
          break;
        }
      }
    }
    
    if (bestBreak === -1) {
      for (let i = Math.min(CHUNK_MAX, remaining.length - 1); i >= CHUNK_MIN; i--) {
        const ch = remaining[i];
        if ('은는이가을를에서도의로'.includes(ch)) {
          bestBreak = i + 1;
          break;
        }
      }
    }
    
    if (bestBreak === -1) bestBreak = CHUNK_MAX;
    
    const chunk = remaining.substring(0, bestBreak).trim();
    if (chunk) chunks.push(chunk);
    remaining = remaining.substring(bestBreak).trim();
  }
  
  return chunks;
}

const subtitleY = 1400;

for (const seg of dialogueData) {
  const turns = seg.turns || [];
  if (turns.length === 0) continue;
  const turnDur = seg.duration / turns.length;

  for (let j = 0; j < turns.length; j++) {
    const rawText = (turns[j].line || '').trim();
    if (!rawText) continue;
    
    const turnStart = seg.start + j * turnDur;
    const turnEnd = seg.start + (j + 1) * turnDur;
    const totalTurnTime = turnEnd - turnStart;
    
    const chunks = splitIntoChunks(rawText);
    if (chunks.length === 0) continue;
    
    const totalChars = chunks.reduce((sum, c) => sum + c.length, 0);
    let chunkStart = turnStart;
    
    for (let k = 0; k < chunks.length; k++) {
      const ratio = totalChars > 0 ? chunks[k].length / totalChars : 1 / chunks.length;
      const chunkDur = ratio * totalTurnTime;
      const tStart = chunkStart.toFixed(2);
      const tEnd = (chunkStart + chunkDur).toFixed(2);
      
      f += ",drawtext=text='" + esc(chunks[k]) + "'"
        + ':fontfile=' + fontBold
        + ':fontsize=' + subtitleFontSize
        + ':fontcolor=white'
        + ':x=(w-text_w)/2'
        + ':y=' + subtitleY
        + ':borderw=3:bordercolor=black'
        + ":enable='between(t," + tStart + "," + tEnd + ")'";
      
      chunkStart += chunkDur;
    }
  }
}

f += '[vout]';

try {
  const result = await this.helpers.httpRequest({
    method: 'POST',
    url: 'http://76.13.182.180:8080/v1/ffmpeg/compose',
    headers: {
      'x-api-key': 'nca-sagong-2026',
      'Content-Type': 'application/json'
    },
    body: {
      inputs: [{ file_url: videoUrl }],
      filters: [{ filter: f }],
      outputs: [{
        options: [
          { option: '-map', argument: '[vout]' },
          { option: '-map', argument: '0:a' },
          { option: '-c:v', argument: 'libx264' },
          { option: '-preset', argument: 'medium' },
          { option: '-crf', argument: '18' },
          { option: '-c:a', argument: 'aac' },
          { option: '-b:a', argument: '256k' },
          { option: '-pix_fmt', argument: 'yuv420p' },
          { option: '-movflags', argument: '+faststart' }
        ],
        file_name: 'story_shorts_9x16.mp4'
      }]
    }
  });

  return [{ json: { ...prevData, convertResult: result, originalVideoUrl: videoUrl, filterUsed: f } }];
} catch (e) {
  console.log('9:16 변환 실패: ' + e.message);
  return [{ json: { ...prevData, convertError: e.message } }];
}
---코드 끝---


=======================================
[작업 5] Jay_Mike_v84 — 프레임 추출 타이밍 변경
=======================================
"프레임1 추출"과 "프레임2 추출" 노드의 jsCode에서:
- `-ss` argument의 `'7.5'`를 `'7.8'`으로 변경
- 영상 끝나기 0.2초 전 프레임을 추출하도록 변경

=======================================
[작업 6] 할머니_Mike_v84 — 프레임 추출 타이밍 변경
=======================================
"프레임1 추출"과 "프레임2 추출" 노드의 jsCode에서:
- `-ss` argument의 `'7.5'`를 `'7.8'`으로 변경
- 작업 5와 동일

=======================================
[작업 7] Jay_Mike_v84 — 세그먼트 분리 노드 speakerDesc + veo3_prompt 코드 패치
=======================================
"세그먼트 분리" 노드(buildVeo3Dialogue 함수 포함)의 jsCode에서:

**(A) speakerDesc 교체:**
기존:
```javascript
const speakerDesc = {
    'A': 'The man in the black hoodie with gold chain (short fade haircut)',
    'B': 'The man in the white t-shirt with silver watch (twists hairstyle)'
};
```
교체:
```javascript
const speakerDesc = {
    'A': 'Jay: the man in the black hoodie with gold chain, short fade haircut, short beard, standing on the LEFT side of the frame',
    'B': 'Mike: the man in the white t-shirt with silver watch, twists hairstyle, clean-shaven, standing on the RIGHT side of the frame'
};
```

**(B) buildVeo3Dialogue 리턴 문장에 립싱크 고정 추가:**
기존:
```javascript
if (i === 0) return desc + " says '" + line + "'";
return "then " + desc + " responds '" + line + "'";
```
교체:
```javascript
const lipRule = " Only the speaking character's lips move; the listener's mouth stays closed.";
if (i === 0) return `${desc} says in Korean: '${line}'.${lipRule}`;
return `then ${desc} responds in Korean: '${line}'.${lipRule}`;
```

**(C) veo3_prompt 조립 부분에 spatial anchoring 추가:**
기존 (요지): "Natural lip synchronization for both speakers..."
교체 (요지):
```javascript
const veo3_prompt = cleanImagePrompt +
  '. ' + dialoguePart +
  '. Keep spatial anchoring fixed: black hoodie man always LEFT, white t-shirt man always RIGHT; never swap positions.' +
  ' Natural lip synchronization for the speaking character only, subtle body gestures while talking, cinematic camera movement.' +
  ' No text overlay, no subtitles, no captions on screen.';
```

=======================================
[작업 8] 할머니_Mike_v84 — 세그먼트 분리 노드 speakerDesc + veo3_prompt 코드 패치
=======================================
"세그먼트 분리" 노드의 jsCode에서 작업 7과 동일 패턴 적용:

**(A) speakerDesc 교체:**
```javascript
const speakerDesc = {
    'A': 'Grandmother: elderly Korean grandmother in floral vest with reading glasses, standing on the LEFT side of the frame',
    'B': 'Mike: the man in the white t-shirt with silver watch, twists hairstyle, clean-shaven, standing on the RIGHT side of the frame'
};
```

**(B) buildVeo3Dialogue 립싱크 고정:** 작업 7의 (B)와 동일

**(C) veo3_prompt spatial anchoring:** 
```javascript
'. Keep spatial anchoring fixed: grandmother always LEFT, white t-shirt man always RIGHT; never swap positions.'
```

=======================================
[작업 9] 양쪽 워크플로우 — "콘텐츠 파싱" 노드 fullDialogue 태그 제거
=======================================

**문제:** 현재 fullDialogue가 `scene.dialogue`를 사용 → "The man in white t-shirt: ..." 화자 태그가 나레이션에 그대로 섞임

**대상 노드:** "콘텐츠 파싱" → parameters.jsCode (Jay_Mike_v84.json + 할머니_Mike_v84.json 둘 다)

**교체:**
기존:
```javascript
fullDialogue: data.scenes.map(s => s.dialogue).join(' '),
```
변경:
```javascript
fullDialogue: data.scenes.flatMap(s => (s.dialogue_turns || []).map(t => t.line)).join(' '),
```

=======================================
[작업 10] 양쪽 워크플로우 — "NCA 데이터 준비" 노드 태그 제거 + 24초 강제
=======================================

**대상 노드:** "NCA 데이터 준비" → parameters.jsCode (Jay_Mike_v84.json + 할머니_Mike_v84.json 둘 다)

**(A) dialogueText 우선순위 변경 — 태그 제거 (폴백 안전장치 포함):**

먼저 코드 상단에 cleanDialogueTags 헬퍼 함수 추가:
```javascript
function cleanDialogueTags(s) {
  return (s || '')
    .replace(/The man in [^:]+:\s*/g, '')
    .replace(/The grandmother in [^:]+:\s*/g, '')
    .trim();
}
```

기존:
```javascript
const dialogueText = segData?.dialogue
    || (segData?.dialogue_turns || []).map(t => t.line).join(' ') || '';
```
변경:
```javascript
const dialogueText =
  (Array.isArray(segData?.dialogue_turns) && segData.dialogue_turns.length > 0)
    ? segData.dialogue_turns.map(t => t.line).join(' ')
    : cleanDialogueTags(segData?.dialogue || '');
```

**(B) videoUrl 누락 시 스킵 금지 — 24초 강제:**
기존:
```javascript
if (!videoUrl) {
    console.log('영상' + (i+1) + ' URL 없음 → 스킵');
    skippedVideos.push(i + 1);
    continue;
}
```
변경:
```javascript
if (!videoUrl) {
    throw new Error('영상' + (i+1) + ' URL 없음 - 3세그먼트(24초) 필수. 워크플로우 중단.');
}
```

=======================================
[작업 11] 양쪽 워크플로우 — 영상 실패 시 1회 재생성 + 재실패 시 워크플로우 중단
=======================================

**배경:** Veo3가 안전 필터(successFlag≥2)로 영상 생성을 거부하면,
작업 10에서 throw로 중단됨. 하지만 간헐적 필터이므로 1회 재시도 기회를 줌.

**대상 노드:** "영상1 실패체크", "영상2 실패체크", "영상3 실패체크" (3개 모두, 양쪽 워크플로우)

**현재 로직 (영상N 실패체크):**
```javascript
// successFlag === 1 → 성공
if (flag === 1) { return [{json: data}]; }

// successFlag >= 2 또는 재시도 20회 초과 → 원본 이미지 폴백
if ((typeof flag === 'number' && flag >= 2) || staticData.retryCount > 20) {
  // ... videoFailed=true로 설정하고 통과시킴 → NCA에서 스킵됨
}

// 아직 진행중 → 재대기
return [{json: data}];
```

**변경 로직:**
```javascript
const staticData = $getWorkflowStaticData('node');
if (!staticData.retryCount) staticData.retryCount = 0;
if (!staticData.regenerateCount) staticData.regenerateCount = 0;
staticData.retryCount++;

const data = $input.first().json;
const flag = data?.data?.successFlag;

// successFlag === 1 → 성공 (카운터 리셋)
if (flag === 1) {
  staticData.retryCount = 0;
  staticData.regenerateCount = 0;
  return [{json: data}];
}

// 확정 실패 (successFlag >= 2) 또는 폴링 타임아웃 (20회 초과)
if ((typeof flag === 'number' && flag >= 2) || staticData.retryCount > 20) {
  if (staticData.regenerateCount === 0) {
    // ★ 1회 재생성: 같은 프롬프트로 다시 시도
    console.log('영상N 실패 (flag=' + flag + ') → 1회 재생성 시도');
    staticData.regenerateCount = 1;
    staticData.retryCount = 0;
    const mod = JSON.parse(JSON.stringify(data));
    mod.needRegenerate = true;
    mod.data = mod.data || {};
    mod.data.successFlag = 0; // 완료체크 FALSE로 빠지게
    return [{json: mod}];
  } else {
    // ★ 재생성도 실패 → 워크플로우 중단
    staticData.retryCount = 0;
    staticData.regenerateCount = 0;
    throw new Error('영상N 재생성도 실패 (flag=' + flag + ') - 워크플로우 중단. Veo3 안전 필터 반복 거부.');
  }
}

// 아직 진행중 → 재대기
return [{json: data}];
```
(위 코드에서 "영상N"은 각 노드에 맞게 영상1/영상2/영상3으로 변경)

**n8n 연결(connections) 변경 — 완료체크 FALSE 분기에 IF 노드 추가:**
```
영상N 실패체크 → 영상N 완료체크
                   ├── TRUE → 다음 단계
                   └── FALSE → 영상N 재생성판단 (IF: needRegenerate === true)
                                 ├── TRUE → 영상N 준비 (재생성)
                                 └── FALSE → 영상N 재대기 (기존 폴링)
```

**구현 방법:**
1. 새 IF 노드 "영상N 재생성판단" 추가 (조건: `{{ $json.needRegenerate }}` === true)
2. 영상N 완료체크의 FALSE 출력을 "영상N 재생성판단"으로 연결
3. 재생성판단 TRUE → "영상N 준비"로 연결 (재생성)
4. 재생성판단 FALSE → "영상N 재대기"로 연결 (기존 폴링)
5. 영상1, 영상2, 영상3 모두에 적용 (총 3세트, 양쪽 워크플로우)

=======================================
[작업 12] 양쪽 워크플로우 — 장면1 금지어 "부분일치" 규칙 추가
=======================================

**대상:** "AI 콘텐츠 생성" 프롬프트 내 장면1 금지어 목록 바로 아래 (Jay_Mike + 할머니 둘 다)

**현재 (130줄 부근):**
```
카지노, 슬롯, 배팅, 사이트, 환수율, RTP, 먹튀, 환전, 도박, 게임, 포인트, 잭팟, 충전, 입금, 출금, 보너스, 온라인, 당첨
```

**바로 아래에 1줄 추가:**
```
※ 금지어는 **부분일치 포함** 금지 (예: '게임'이 금지면 '게임기/게임패드'도 금지, '사이트'가 금지면 '웹사이트'도 금지).
```

=======================================
요약: 총 12개 작업
=======================================

1. Jay_Mike_v84.json → "AI 콘텐츠 생성" 노드 프롬프트 교체 (v8.6 + 위치고정 + 안전필터 준수)
2. 할머니_Mike_v84.json → "AI 콘텐츠 생성" 노드 프롬프트 교체 (v8.6 + 위치고정 + 안전필터 준수)
3. Jay_Mike_v84.json → "9:16 변환" 노드 jsCode 교체 (구절 쪼개기)
4. 할머니_Mike_v84.json → "9:16 변환" 노드 jsCode 교체 (구절 쪼개기)
5. Jay_Mike_v84.json → "프레임1·2 추출" 노드 '-ss' 7.5→7.8
6. 할머니_Mike_v84.json → "프레임1·2 추출" 노드 '-ss' 7.5→7.8
7. Jay_Mike_v84.json → "세그먼트 분리" 노드 speakerDesc + veo3_prompt 패치 (좌/우 고정 + 립싱크)
8. 할머니_Mike_v84.json → "세그먼트 분리" 노드 speakerDesc + veo3_prompt 패치 (좌/우 고정 + 립싱크)
9. 양쪽 → "콘텐츠 파싱" 노드 fullDialogue에서 화자 태그 제거 (line만 사용)
10. 양쪽 → "NCA 데이터 준비" 노드 dialogueText 태그 제거 + 24초 강제 (스킵→throw)
11. 양쪽 → "영상1·2·3 실패체크" 1회 재생성 + 재실패 시 중단 (IF 노드 3개씩 추가)
12. 양쪽 → "AI 콘텐츠 생성" 프롬프트에 금지어 부분일치 규칙 1줄 추가

프롬프트 v8.6 변경사항 (작업 1, 2, 12에 포함):
- 캐릭터 프로필: 나이 숫자 제거 → "clearly an adult" + 위치 고정 "standing on the left/right"
- AB 함께: "adult-only cast, positions never swap"
- image_prompt: "Static tripod shot" 카메라 고정 + "dramatic shadows, high contrast"
- image_prompt: 시선 "facing each other" + 립싱크 "only speaker's lips move"
- 안전 필터: "회피"→"준수", "adult-only cast, clearly adults" (숫자 나이 완전 제거)
- dialogue 필드: 옷차림으로 화자 구분 (위치 정보는 image_prompt/speakerDesc/veo3_prompt에만)
- 글자수: 공백 제외 기준 v8.6 (검증은 코드 노드에서 처리 권장)
- 4턴: 2문장 고정 템플릿 (습관 규정 + 카지노 경고 + 연결어 필수)
- 6턴: 감정 + 다음 행동 필수, 무행동 마무리 금지
- 구어체: 불필요한 조사 줄이기, 군더더기 제거
- 금지어: 부분일치 포함 금지 (게임→게임기도 금지)

코드 패치 (작업 7, 8):
- speakerDesc에 LEFT/RIGHT 위치 정보 추가
- buildVeo3Dialogue에 립싱크 규칙 추가 (말하는 캐릭터만 입 움직임)
- veo3_prompt에 spatial anchoring 고정 문장 추가

나레이션/자막 태그 제거 (작업 9, 10):
- fullDialogue: dialogue_turns[].line으로 변경 → "The man in ..." 태그 안 읽힘
- dialogueText: dialogue_turns 우선 → dialogue 폴백
- 24초 강제: videoUrl 없으면 throw (스킵 금지)

영상 재생성 (작업 11):
- 영상N 실패체크: 같은 프롬프트로 1회 재생성 시도
- 재생성도 실패 시: throw Error로 워크플로우 중단
- 새 IF 노드 "영상N 재생성판단" 3개씩 추가 (needRegenerate 분기)

흑형스포츠_v84는 이번에 안 건드림.
