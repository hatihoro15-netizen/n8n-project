# 2단계: AI 프롬프트 설계 (라이브365 홍보용) v1.1

> 기존 onca_shortform 프롬프트 구조 기반, 라이브365 홍보에 맞게 재설계
> v1.1 수정: capture_id 프리셋, 템플릿 변수, 밈 소싱, 카테고리별 말투

---

## 1. 캡처 프리셋 정의 (capture_id)

Puppeteer가 참조하는 사전 정의 프리셋. AI는 capture_id만 지정하면 됨.

### 홈 페이지 (/)

| capture_id | CSS 셀렉터 / 영역 | 설명 |
|------------|-------------------|------|
| `home_scoreboard` | `.scoreboard-container` | 전체 스코어보드 |
| `home_match_row` | `.match-row[data-match-id="{{match_id}}"]` | 특정 경기 스코어 행 |
| `home_sport_tab_soccer` | `.sport-tab[data-sport="soccer"]` + `.match-list` | 축구탭 경기목록 |
| `home_sport_tab_baseball` | `.sport-tab[data-sport="baseball"]` + `.match-list` | 야구탭 경기목록 |
| `home_sport_tab_basketball` | `.sport-tab[data-sport="basketball"]` + `.match-list` | 농구탭 경기목록 |
| `home_finished_filter` | `.filter-btn[data-status="finished"]` 클릭 후 `.match-list` | 경기종료 필터 |
| `home_full_page` | `body` (뷰포트 전체) | 홈 전체 화면 |

### 분석 페이지 (/analysis)

| capture_id | CSS 셀렉터 / 영역 | 설명 |
|------------|-------------------|------|
| `analysis_popup` | `.analysis-modal` 또는 `.analysis-detail` | 경기 분석 팝업 전체 |
| `analysis_standings` | `.standings-table` | 리그 순위표 |
| `analysis_h2h` | `.h2h-section` | 상대전적 섹션 |
| `analysis_team_compare` | `.team-compare-section` | 양팀 비교 데이터 |
| `analysis_full_page` | `body` (뷰포트 전체) | 분석 페이지 전체 |

### 프로토 페이지 (/proto)

| capture_id | CSS 셀렉터 / 영역 | 설명 |
|------------|-------------------|------|
| `proto_odds_table` | `.odds-table` 또는 `.proto-match-list` | 배당률 표 전체 |
| `proto_match_detail` | `.match-row[data-match-id="{{match_id}}"]` | 특정 경기 배당 확대 |
| `proto_calculator` | `.calculator-section` | 배당 계산기/공식 |
| `proto_guide` | `.proto-guide-section` | 프로토 설명/가이드 |
| `proto_full_page` | `body` (뷰포트 전체) | 프로토 페이지 전체 |

### 커뮤니티 페이지 (/community)

| capture_id | CSS 셀렉터 / 영역 | 설명 |
|------------|-------------------|------|
| `community_hit_post` | `.post-detail[data-post-id="{{post_id}}"]` | 적중인증 게시글 |
| `community_hit_list` | `.board-list[data-board="hit"]` | 적중인증 목록 |
| `community_full_page` | `body` (뷰포트 전체) | 커뮤니티 전체 |

> **참고**: `{{match_id}}`, `{{post_id}}` 등은 n8n에서 동적으로 주입.
> CSS 셀렉터는 실제 사이트 구조 확인 후 조정 필요 (Phase 1에서 매핑).

---

## 2. 밈 카탈로그 (MinIO 기반)

기존 v16 워크플로우의 MEME_CATALOG 재활용. MinIO에 mood별 폴더로 저장.

| meme_mood | MinIO 경로 | 파일 수 | 예시 |
|-----------|-----------|---------|------|
| `thinking` | `/memes/thinking/` | 14개 | big_brain_time.png, hackerman.jpg |
| `excited` | `/memes/excited/` | 6개 | 짐캐리 키보드.mp4 |
| `shocked` | `/memes/shocked/` | 12개 | surprised_pikachu.jpg |
| `sad` | `/memes/sad/` | 7개 | squidward_window.jpg |
| `angry` | `/memes/angry/` | 8개 | table_flip.jpg |
| `cool` | `/memes/cool/` | 12개 | tony_stark_sunglasses.jpg |
| `celebrating` | `/memes/celebrating/` | 7개 | leonardo_toast.jpg |
| `money` | `/memes/money/` | 8개 | stonks_meme.jpg, wolf_wallstreet.jpg |

**소싱 로직** (이미지 URL 추출 노드):
```
if (visual_type === "meme") {
  const files = MEME_CATALOG[meme_mood];
  const url = files[Math.floor(Math.random() * files.length)];
}
```

> 기존 MinIO 서버(76.13.182.180:9000)에 이미 업로드되어 있음.
> 신규 밈 추가 시 해당 mood 폴더에 파일 추가 + MEME_CATALOG 배열 업데이트.

---

## 3. 카테고리별 말투 스타일

### 말투 정의 (4종)

```javascript
const TONE_STYLES = {
  hyung: {
    name: '형',
    guide: '반말, 친근하고 확신에 찬 말투. "야 이거 봐", "형이 알려줄게" 스타일.',
    examples: ['야 이거 봐 진짜 미쳤어', '이거 무조건이야 내가 장담해', '형이 알려줄게 잘 들어']
  },
  angry: {
    name: '빡침',
    guide: '반말, 답답하고 빡친 말투. "아 진짜 제발 데이터 좀 보고", "이걸 왜 몰라?" 스타일.',
    examples: ['아 진짜 제발 데이터 좀 보고 찍어', '이걸 왜 몰라 진짜 답답해', '아니 이게 말이 되냐고']
  },
  asmr: {
    name: '차분한 전문가',
    guide: '존댓말, 차분하고 전문적. "심상치 않습니다", "주목해야 할 부분이 있습니다" 스타일.',
    examples: ['여러분 이건 심상치 않습니다', '주목해야 할 부분이 있습니다', '데이터가 말해주고 있습니다']
  },
  friendly: {
    name: '친절한 설명',
    guide: '존댓말, 친절하고 쉬운 말투. "이건 이렇게 하면 돼요", "걱정 마세요 쉬워요" 스타일.',
    examples: ['이건 생각보다 쉬워요', '걱정 마세요 제가 알려드릴게요', '이것만 알면 충분합니다']
  }
};
```

### 카테고리별 허용 말투

| 카테고리 | 허용 말투 | 이유 |
|----------|-----------|------|
| 1. 프로토 배당 | hyung, angry, asmr | 자극적 톤이 배당 콘텐츠에 적합 |
| 2. 경기 분석 | hyung, angry, asmr | 기존 v16과 동일 |
| 3. 결과 속보 | hyung, angry | 빠른 템포, 속보 느낌 |
| 4. 적중인증 | hyung, angry | 흥분/놀라움 톤 |
| 5. 초보자 가이드 | friendly, asmr | **친절한 톤 필수** (입문자 대상) |
| 6. 멀티종목 | hyung, angry | 빠르게 훑는 느낌 |
| 7. 기능 소개 | friendly, hyung | 자연스러운 추천 톤 |

```javascript
const CATEGORY_TONES = {
  1: ['hyung', 'angry', 'asmr'],
  2: ['hyung', 'angry', 'asmr'],
  3: ['hyung', 'angry'],
  4: ['hyung', 'angry'],
  5: ['friendly', 'asmr'],      // 초보자 = 친절 전용
  6: ['hyung', 'angry'],
  7: ['friendly', 'hyung']       // 기능소개 = 친절 우선
};

// 카테고리별 랜덤 선택
const allowedTones = CATEGORY_TONES[category];
const toneKey = allowedTones[Math.floor(Math.random() * allowedTones.length)];
const tone = TONE_STYLES[toneKey];
```

---

## 4. 공통 출력 JSON 스키마

```json
{
  "hook_title": "첫 화면 후킹 자막 (15자 내외)",
  "images": [
    {
      "visual_type": "capture",
      "capture_id": "proto_odds_table",
      "description": "오늘 프로토 배당률 화면"
    },
    {
      "visual_type": "capture",
      "capture_id": "proto_match_detail",
      "capture_params": { "match_id": "12345" },
      "description": "맨시티 리버풀 배당률 확대"
    },
    {
      "visual_type": "pexels",
      "keyword": "soccer stadium"
    },
    {
      "visual_type": "meme",
      "meme_mood": "money"
    }
  ],
  "subtitles": ["자막1", "<em>강조</em> 자막2", "..."],
  "Subject": "유튜브 제목 #라이브365 #아럽토",
  "Caption": "유튜브 설명 #라이브365",
  "Comment": "라이브365에서 더 많은 정보 확인!",
  "category_data": {}
}
```

### images 필드 상세

| visual_type | 필수 필드 | 선택 필드 | 설명 |
|-------------|-----------|-----------|------|
| `capture` | `capture_id`, `description` | `capture_params` | 프리셋 기반 사이트 캡처 |
| `pexels` | `keyword` | — | Pexels 스톡 (영어 명사 1~2개) |
| `meme` | `meme_mood` | — | MinIO 밈 카탈로그 랜덤 |

---

## 5. 공통 프롬프트 블록

```javascript
const COMMON_RULES = `
## 공통 규칙

### 언어 규칙
- 한국어 구어체, 20~30대 남성 타겟
- 영어 알파벳 절대 금지: EPL → 이피엘, TOP3 → 탑3, MVP → 엠브이피, H2H → 상대전적
- 마침표 찍지 마
- <em>태그</em>로 핵심 수치/사실 강조

### 자막(subtitles) 규칙
- 각 subtitle: 띄어쓰기 포함 5자 ~ 15자 (한 호흡 단위)
- subtitles 총 개수: 12~16개
- 전체 글자수: 150~250자 (40초 나레이션 기준)
- 단어 1~2개만 단독 금지

### 이미지(images) 규칙
- 5~6개 (자막보다 적게)
- visual_type 3종:
  - "capture": capture_id(프리셋 ID)와 description 필수
  - "pexels": keyword(영어 명사 1~2개) 필수
  - "meme": meme_mood 필수 (thinking/excited/shocked/sad/angry/cool/celebrating/money)
- capture 최소 2장 이상 (라이브365 화면 노출 필수)
- meme 최대 2개

### CTA 규칙
- 마지막 자막에 반드시 "라이브365" 언급
- Subject/Caption에 #라이브365 #아럽토 필수
- Comment에 라이브365 언급 필수

### capture_id 사용법
- 반드시 아래 프리셋 중에서만 선택:
  home_scoreboard, home_match_row, home_sport_tab_soccer,
  home_sport_tab_baseball, home_sport_tab_basketball,
  home_finished_filter, home_full_page,
  analysis_popup, analysis_standings, analysis_h2h,
  analysis_team_compare, analysis_full_page,
  proto_odds_table, proto_match_detail, proto_calculator,
  proto_guide, proto_full_page,
  community_hit_post, community_hit_list, community_full_page
- match_id/post_id가 필요한 프리셋은 capture_params에 명시

### 출력 형식
- 순수 JSON만 (코드블록 없이)
`;
```

---

## 6. 카테고리별 프롬프트

### 카테고리 1: 프로토 배당 분석

```javascript
function buildProtoPrompt(data, toneBlock) {
  return `너는 스포츠 배당 분석 유튜브 숏츠 대본 전문가야.
아래 실제 프로토 배당 데이터를 바탕으로 35~45초 분량의 프로토 배당 분석 영상 스크립트를 작성해.

## 오늘의 프로토 데이터
종목: ${data.sport} / 리그: ${data.league}
날짜: ${data.today}
발매 경기:
${data.matchesFormatted}

## 영상 구조 (자막 흐름) - 반드시 이 순서!
[1~2] 후킹 - 수익 금액으로 궁금증 유발
  예: "천 원으로 3만 4천 원?" / "오늘 이 배당 실화냐"
[3~5] 고배당 경기 소개 - 경기별 배당률 + 왜 이 배당인지 간단 설명
[6~8] 조합 전략 - 2~3경기 조합 시 총 배당 계산
  반드시 실제 계산: 배당1 × 배당2 × ... = 총배당
[9~11] 수익 시뮬레이션 - 투자금별 예상 수익
[12~14] 리스크 언급 + 최종 추천 조합
[15~16] CTA - "라이브365" 구체적 언급

## ★★★ 팩트 규칙 ★★★
1. 배당률은 제공된 데이터 그대로 - 반올림/변형 금지
2. 계산은 정확하게 - 배당 곱셈, 환급금 계산 틀리면 안 됨
3. "무조건 된다" 식 표현 금지

${toneBlock}

## 이미지 가이드 (capture_id 사용)
- 1번: capture (capture_id: "proto_odds_table") — 배당률 표
- 2번: capture (capture_id: "proto_match_detail") — 주목 경기 배당
- 3번: pexels (경기장/선수 분위기)
- 4번: capture (capture_id: "proto_calculator") — 배당 계산
- 5번: meme (meme_mood: "money" 또는 "excited")
- 6번: capture (capture_id: "proto_full_page") — CTA용

## category_data 필드
{
  "top_match": "가장 주목할 경기명",
  "combo_odds": 총배당(숫자),
  "expected_return_1000": 1000원투자시수익(숫자)
}

${COMMON_RULES}`;
}
```

---

### 카테고리 2: 경기 분석/예측

```javascript
function buildAnalysisPrompt(data, toneBlock) {
  return `너는 스포츠 분석 유튜브 숏츠 대본 전문가야.
아래 실제 크롤링 데이터를 바탕으로 35~45초 분량의 경기 분석 영상 스크립트를 작성해.

## 경기 정보
종목: ${data.sport} / 리그: ${data.league}
대진: ${data.matchup}
날짜: ${data.today}
분석 각도: ${data.angle}

## 실제 데이터
### 리그 순위
${data.standingsSummary}

### 부상/결장
${data.injuriesSummary}

### 상대전적
${data.h2hSummary}

## 영상 구조 - 반드시 이 순서!
[1~2] 이전 픽 결과 언급 (시리즈 연결)
[3~4] 훅 - 궁금증 유발, 결론 숨기기
[5~9] 데이터 분석 - 순위, 폼, 부상자, 홈/원정
[10~11] 반전 요소 (필수) - 상대전적/숨은 변수
[12~14] 최종 픽 공개 (70% 이후)
[15~16] CTA - "라이브365" 구체적 언급

## ★★★ 팩트 규칙 ★★★
1. 크롤링 데이터에 있는 수치/사실만 사용
2. 데이터에 없는 내용 추측 절대 금지
3. 숫자는 원본 그대로

## 이전 픽 결과
${data.prevPickGuide}

${toneBlock}

## 이미지 가이드 (capture_id 사용)
- 1번: capture (capture_id: "analysis_popup") — 분석 팝업
- 2번: capture (capture_id: "analysis_standings") — 리그 순위
- 3번: pexels (해당 종목 이미지)
- 4번: meme (meme_mood: "thinking" 또는 "shocked")
- 5번: capture (capture_id: "home_match_row", capture_params: {match_id}) — 해당 경기
- 6번: capture (capture_id: "analysis_full_page") — CTA용

## category_data 필드
{
  "pick": "최종 픽",
  "pickDetail": "픽 근거 요약",
  "confidence": "높음/보통/낮음"
}

${COMMON_RULES}`;
}
```

---

### 카테고리 3: 경기 결과 속보

```javascript
function buildResultsPrompt(data, toneBlock) {
  return `너는 스포츠 결과 속보 유튜브 숏츠 대본 전문가야.
아래 경기 결과 데이터로 30~40초 분량의 결과 속보 영상 스크립트를 작성해.

## 오늘의 결과
종목: ${data.sport} / 리그: ${data.league}
날짜: ${data.today}

### 경기 결과
${data.resultsFormatted}

### 순위 변동
${data.standingsAfter}

## 영상 구조 - 반드시 이 순서!
[1~2] 후킹 - 가장 충격적인 결과로 시작
[3~6] 주요 결과 나열 - 스코어 + 한줄 포인트
[7~9] 이변/하이라이트
[10~12] 순위 변동
[13~14] 다음 라운드 예고
[15~16] CTA - "라이브365" 구체적 언급

## ★★★ 팩트 규칙 ★★★
1. 스코어는 데이터 그대로
2. "이변" = 하위팀이 상위팀 이긴 경우만
3. 하이라이트는 데이터에 있는 것만

${toneBlock}

## 이미지 가이드 (capture_id 사용)
- 1번: capture (capture_id: "home_finished_filter") — 경기종료 목록
- 2~3번: capture (capture_id: "home_match_row", capture_params: {match_id}) — 주요 결과
- 4번: capture (capture_id: "analysis_standings") — 순위 변동
- 5번: meme (meme_mood: "shocked" 또는 "excited")
- 6번: capture (capture_id: "home_full_page") — CTA용

## category_data 필드
{
  "biggest_upset": "가장 큰 이변 경기",
  "results_count": 전체경기수(숫자)
}

${COMMON_RULES}`;
}
```

---

### 카테고리 4: 적중인증/커뮤니티

```javascript
function buildCommunityPrompt(data, toneBlock) {
  return `너는 스포츠 커뮤니티 하이라이트 유튜브 숏츠 대본 전문가야.
아래 적중인증 데이터로 30~40초 분량의 적중인증 소개 영상 스크립트를 작성해.

## 적중인증 데이터
날짜: ${data.today}

### 적중 사례
${data.postsFormatted}

## 영상 구조 - 반드시 이 순서!
[1~2] 후킹 - 적중 금액으로 충격 유발
[3~5] 적중 내역 소개 - 어떤 경기를 맞췄는지
[6~8] 배당/수익 분석
[9~11] 다른 적중 사례 or 전략 포인트
[12~14] "너도 할 수 있다" + 커뮤니티 소개
[15~16] CTA - "라이브365 커뮤니티" 언급

## ★★★ 팩트 규칙 ★★★
1. 적중 금액/배당 데이터 그대로
2. "쉽다" "무조건" 표현 금지

${toneBlock}

## 이미지 가이드 (capture_id 사용)
- 1번: capture (capture_id: "community_hit_post", capture_params: {post_id}) — 적중 게시글
- 2번: capture (capture_id: "community_hit_list") — 적중인증 목록
- 3번: capture (capture_id: "home_match_row", capture_params: {match_id}) — 적중한 경기
- 4번: meme (meme_mood: "money" 또는 "celebrating")
- 5번: capture (capture_id: "community_full_page") — CTA용

## category_data 필드
{
  "top_return": 최고수익금(숫자),
  "top_odds": 최고배당(숫자),
  "hit_count": 적중사례수(숫자)
}

${COMMON_RULES}`;
}
```

---

### 카테고리 5: 초보자 가이드

```javascript
function buildGuidePrompt(data, toneBlock) {
  return `너는 스포츠 입문자 교육 유튜브 숏츠 대본 전문가야.
아래 주제로 30~40초 분량의 초보자 가이드 영상 스크립트를 작성해.

## 교육 주제
주제: ${data.topic}
날짜: ${data.today}

## 주제별 핵심 내용
${data.topicContent}

## 영상 구조 - 반드시 이 순서!
[1~2] 후킹 - 모르면 손해라는 느낌
[3~5] 기본 개념 - 쉬운 비유 + 핵심만
[6~9] 단계별 가이드 - 1단계 2단계 3단계
[10~12] 실전 예시 - 구체적 숫자
[13~14] 꿀팁 or 주의사항
[15~16] CTA - "라이브365" 언급 (연습배팅/프로토정보)

## 콘텐츠 규칙
1. 전문용어 쓰면 바로 풀어서 설명
2. 비유 적극 활용
3. 숫자 예시 필수 (추상적 설명 금지)
4. "어렵지 않아" "누구나 가능" 톤 유지

${toneBlock}

## 이미지 가이드 (capture_id 사용)
- 1번: pexels (학습/교육 분위기) 또는 meme (meme_mood: "thinking")
- 2번: capture (capture_id: "proto_guide") — 프로토 설명
- 3번: capture (capture_id: "proto_calculator") — 배당 계산
- 4번: capture (capture_id: "proto_odds_table") — 실전 배당 화면
- 5번: capture (capture_id: "proto_full_page") — CTA용

## category_data 필드
{
  "guide_topic": "가이드 주제명",
  "difficulty": "입문/초급/중급"
}

${COMMON_RULES}`;
}
```

---

### 카테고리 6: 멀티종목 비교

```javascript
function buildMultiSportPrompt(data, toneBlock) {
  return `너는 멀티종목 스포츠 요약 유튜브 숏츠 대본 전문가야.
아래 전체 종목 데이터로 30~40초 분량의 종목별 요약 영상 스크립트를 작성해.

## 오늘의 전체 종목 현황
날짜: ${data.today}

### 축구
${data.soccerSummary}

### 야구
${data.baseballSummary}

### 농구
${data.basketballSummary}

### 기타 종목
${data.otherSummary}

## 영상 구조 - 반드시 이 순서!
[1~2] 후킹 - "오늘 스포츠 30초 정리"
[3~5] 축구 주요 결과/일정
[6~8] 야구/농구 주요 결과/일정
[9~11] 오늘의 이변 or 핫한 경기
[12~14] 내일 주목 경기 예고
[15~16] CTA - "라이브365" 언급 (모든 종목 한 곳에서)

## ★★★ 팩트 규칙 ★★★
1. 스코어/일정 데이터 그대로
2. 종목당 1~2경기만 (전부 나열 금지)

${toneBlock}

## 이미지 가이드 (capture_id 사용)
- 1번: capture (capture_id: "home_scoreboard") — 전체 스코어보드
- 2번: capture (capture_id: "home_sport_tab_soccer") — 축구탭
- 3번: capture (capture_id: "home_sport_tab_baseball") — 야구탭
- 4번: pexels (스포츠 종합) 또는 meme (meme_mood: "excited")
- 5번: capture (capture_id: "home_full_page") — CTA용

## category_data 필드
{
  "total_matches": 전체경기수(숫자),
  "hottest_match": "가장 주목할 경기"
}

${COMMON_RULES}`;
}
```

---

### 카테고리 7: 사이트 기능 소개

```javascript
function buildFeaturePrompt(data, toneBlock) {
  return `너는 서비스 소개 유튜브 숏츠 대본 전문가야.
라이브365 기능을 소개하는 30~40초 분량의 영상 스크립트를 작성해.

## 소개 대상
서비스명: 라이브365 (scoredata.org)
포커스 기능: ${data.featureFocus}
날짜: ${data.today}

## 라이브365 주요 기능
- 실시간 스코어: 축구/야구/농구/배구/하키/테니스/이스포츠/격투기 8종목
- 프리미엄분석: 양팀 비교, 전적, 순위, 부상자
- 프로토정보: 배당률 실시간, 계산, 가이드
- 커뮤니티: 자유게시판, 유머, 뉴스, 적중인증
- 연습배팅: 시뮬레이션
- 중계: 실시간 중계

## 영상 구조 - 반드시 이 순서!
[1~2] 후킹 - 문제 제기
[3~5] 핵심 기능 1~2개 소개
[6~9] 추가 기능 빠르게 훑기
[10~12] 차별점
[13~14] 사용 후기 느낌
[15~16] CTA - "라이브365 지금 바로 접속해봐"

## 콘텐츠 규칙
1. 광고 느낌 최소화 - 체험 후기 톤
2. 기능 나열 금지 - 스토리텔링
3. 다른 서비스 비하 금지

${toneBlock}

## 이미지 가이드 (capture_id 사용)
- 1번: pexels (스마트폰 사용) 또는 meme (meme_mood: "thinking")
- 2번: capture (capture_id: "home_scoreboard") — 스코어보드
- 3번: capture (capture_id: "analysis_popup") — 분석 화면
- 4번: capture (capture_id: "proto_full_page") — 프로토
- 5번: capture (capture_id: "community_full_page") — 커뮤니티
- 6번: capture (capture_id: "home_full_page") — CTA용

## category_data 필드
{
  "feature_focus": "포커스 기능명",
  "key_selling_point": "핵심 차별점 한줄"
}

${COMMON_RULES}`;
}
```

---

## 7. n8n 프롬프트 생성 노드 (통합 코드)

```javascript
// === 프롬프트 생성 노드 (라이브365용) ===
const data = $input.first().json;
const category = data.category; // 1~7

// 카테고리별 허용 말투
const CATEGORY_TONES = {
  1: ['hyung', 'angry', 'asmr'],
  2: ['hyung', 'angry', 'asmr'],
  3: ['hyung', 'angry'],
  4: ['hyung', 'angry'],
  5: ['friendly', 'asmr'],
  6: ['hyung', 'angry'],
  7: ['friendly', 'hyung']
};

const TONE_STYLES = { /* 위에 정의된 4종 */ };

const allowedTones = CATEGORY_TONES[category];
const toneKey = allowedTones[Math.floor(Math.random() * allowedTones.length)];
const tone = TONE_STYLES[toneKey];
const toneBlock = `## 말투 스타일: ${tone.name}\n${tone.guide}\n예시:\n- ${tone.examples.join('\n- ')}\n전체 자막을 이 말투로 통일해!`;

let prompt = '';
switch (category) {
  case 1: prompt = buildProtoPrompt(data, toneBlock); break;
  case 2: prompt = buildAnalysisPrompt(data, toneBlock); break;
  case 3: prompt = buildResultsPrompt(data, toneBlock); break;
  case 4: prompt = buildCommunityPrompt(data, toneBlock); break;
  case 5: prompt = buildGuidePrompt(data, toneBlock); break;
  case 6: prompt = buildMultiSportPrompt(data, toneBlock); break;
  case 7: prompt = buildFeaturePrompt(data, toneBlock); break;
}

return [{ json: { prompt, category, toneStyle: tone.name, ...data } }];
```

---

## 8. 콘텐츠 파싱 노드 변경사항

```javascript
// images 검증 (capture_id 기반)
const VALID_CAPTURE_IDS = [
  'home_scoreboard', 'home_match_row', 'home_sport_tab_soccer',
  'home_sport_tab_baseball', 'home_sport_tab_basketball',
  'home_finished_filter', 'home_full_page',
  'analysis_popup', 'analysis_standings', 'analysis_h2h',
  'analysis_team_compare', 'analysis_full_page',
  'proto_odds_table', 'proto_match_detail', 'proto_calculator',
  'proto_guide', 'proto_full_page',
  'community_hit_post', 'community_hit_list', 'community_full_page'
];

data.images = data.images.map((img, idx) => {
  if (!img.visual_type || !['capture', 'pexels', 'meme'].includes(img.visual_type)) {
    img.visual_type = 'pexels';
  }
  if (img.visual_type === 'capture') {
    if (!img.capture_id || !VALID_CAPTURE_IDS.includes(img.capture_id)) {
      img.capture_id = 'home_full_page'; // 폴백
    }
    if (!img.description) img.description = '라이브365 화면';
  }
  if (img.visual_type === 'pexels') {
    if (!img.keyword) img.keyword = 'sports stadium';
  }
  if (img.visual_type === 'meme') {
    if (!img.meme_mood || !VALID_MOODS.includes(img.meme_mood)) {
      img.meme_mood = VALID_MOODS[idx % VALID_MOODS.length];
    }
  }
  return img;
});
```
