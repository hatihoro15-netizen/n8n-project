import json, requests, time, copy

N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
HEADERS = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}
SOURCE_WF_ID = "9YOHS8N1URWlzGWj"

# Same Google Sheet, new tab
SHEET_DOC_ID = "1gkRjLIcK3HxbnTbLCvG6oknMGVt2uz9pgboM3EF_VKg"
SHEET_TAB_NAME = "온카스터디 숏폼"

print("1. Fetching source workflow (루믹스 v3)...")
resp = requests.get(f"{N8N_URL}/api/v1/workflows/{SOURCE_WF_ID}", headers=HEADERS)
wf = resp.json()
print(f"   Nodes: {len(wf['nodes'])}")

# Deep copy
wf_new = copy.deepcopy(wf)
wf_new['name'] = '온카스터디 숏폼 (완전자동 v3)'

# Remove id, createdAt, updatedAt etc
for key in ['id', 'createdAt', 'updatedAt', 'versionId']:
    wf_new.pop(key, None)

# Generate new node IDs
import uuid
id_map = {}
for node in wf_new['nodes']:
    old_id = node.get('id', '')
    new_id = str(uuid.uuid4())
    id_map[old_id] = new_id
    node['id'] = new_id

print("\n2. Modifying nodes for 온카스터디...")

# =============================================
# AI 주제 생성 프롬프트
# =============================================
ONCASTUDY_PROMPT = """= 최신 채널 분석 리포트:
- 트렌드 키워드: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['트렌드_키워드'], '데이터 없음') }}
- 추천 주제 1: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['추천_주제1'], '없음') }}
- 추천 주제 2: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['추천_주제2'], '없음') }}
- 추천 주제 3: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['추천_주제3'], '없음') }}
- 피해야 할 주제: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['피해야할_주제'], '없음') }}
- 효과적인 훅 팁: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['효과적인_훅_팁'], '없음') }}
- 고성과 패턴: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['고성과_패턴'], '없음') }}

위 분석 결과를 반영하여 콘텐츠를 생성해줘. 추천 주제를 우선 참고하되, 피해야 할 주제는 반드시 피해.

1) 역할
너는 Faceless 자동화 유튜브 쇼츠 콘텐츠 기획 전문가다.

2) 목표
'온카스터디' 먹튀검증 커뮤니티의 핵심 가치를 주제로, 온라인 카지노/토토 이용자를 타겟팅한 직설적인 쇼츠 광고 카피를 생성한다.

핵심 가치 키워드: 먹튀검증, 안전, 신뢰, 커뮤니티, 리워드, 포인트, 보증업체, 실시간, 라이브방송, 이벤트, 정보공유, 무료, 기프티콘, 검증시스템, 회원혜택, 토너먼트, 슬롯리뷰, 스포츠분석, 뉴스, 복권

핵심 묶음 5종:
1) 먹튀검증 · 안전 · 신뢰
2) 커뮤니티 · 정보공유 · 실시간
3) 리워드 · 포인트 · 기프티콘
4) 보증업체 · 검증시스템 · 안전놀이터
5) 라이브방송 · 이벤트 · 토너먼트

생성 모드 설명:
A) 단일 강점 모드 - 키워드 1~2개만 깊게 파고듦
B) 묶음 모드 - 핵심 묶음 3단어 세트 중심
C) 혼합 모드 - 묶음 + 단일 강점 혼합

이번 실행 모드: {{ ($now.day * 2 + ($now.hour >= 12 ? 1 : 0)) % 3 === 0 ? "A) 단일 강점 모드" : (($now.day * 2 + ($now.hour >= 12 ? 1 : 0)) % 3 === 1 ? "B) 묶음 모드" : "C) 혼합 모드") }}
반드시 위에서 지정된 모드로만 생성할 것.

3) 온카스터디 실제 서비스 정보
- 먹튀검증 커뮤니티 플랫폼 (maxpixels.net)
- 주요 서비스:
  1. 먹튀검증 시스템 - 신고 접수, 업체 검증, 보증업체 선정
  2. 포인트 리워드 - 게시글/댓글 작성으로 포인트 적립, 기프티콘 교환
  3. 실시간 라이브 방송 - 슬롯, 카지노 게임 라이브 스트리밍
  4. 커뮤니티 - 자유게시판, 가입인사, 잭팟 제보, 카지노/스포츠 뉴스
  5. 무료 게임 - 복권, 돌림판, 무료 슬롯 체험
- 특징: 활동만으로 실질적 혜택(기프티콘) 획득 가능, 안전한 정보 공유 공간

4) Subject (유튜브 제목) 규칙
- 영상 내용을 종합한 후킹 문구
- Subject 본문(해시태그 앞)에 업종 단어(카지노, 토토, 슬롯, 배팅 등) 직접 언급 금지
- 업종 단어는 해시태그 구간에만 허용
- 핵심 묶음 문구를 그대로 넣지 않고, 의미를 담은 자연스러운 후킹 문구로 작성
- 끝에 고정: 온카스터디 #먹튀검증 #카지노커뮤니티 #토토커뮤니티 #먹튀검증사이트
- 예시: "활동만 해도 기프티콘이 쌓인다고? 온카스터디 #먹튀검증 #카지노커뮤니티 #토토커뮤니티 #먹튀검증사이트"

5) Narration (나레이션) 규칙
- 25~35초 분량, 반드시 5문장, 공백 포함 130~200자
- 문장 끝: . ! ? 중 하나로만 끝남 (쉼표로 끝나는 건 문장 아님)
- 1문장 = 1씬에 대응, 각 문장이 독립적으로 의미 완결
- 톤: 단정형 광고 톤 (짧고 확신 있게), 이용자 관점
- 본문에 업종(카지노, 토토, 슬롯, 배팅 등) 직접 언급 금지
- 전개 구조 (매번 다르게 선택):
  A) 불안한 현실(먹튀 피해) → 온카스터디 해결 → 이용자가 얻는 안전
  B) 온카스터디 약속(핵심 한 문장) → 근거 2가지 → 결과
  C) 기존 방식의 위험 → 온카스터디 전환 → 안전한 결과
  D) 이용자 행동 촉구(지금 확인해라) → 온카스터디 이유 → 결과
- 루프 구조: 마지막 문장이 첫 문장과 자연스럽게 연결 (재시청 유도)
- "온카스터디"는 후반부에 1~2회만 자연스럽게 언급

6) Caption (유튜브 설명) 규칙
- 줄바꿈 없이 한 문단, 반드시 8~12문장 (8문장 미만 금지)
- 키워드 최소 6개 이상 문장 속에 자연스럽게 포함 (나열 금지)
- 구성: 첫 2문장 훅/문제 제기 + 마지막 1문장 CTA(가입/방문/확인 유도)
- 본문에 업종 직접 언급 금지 (해시태그 예외)
- 끝에 고정: #온카스터디 #먹튀검증 #카지노 #토토 #먹튀검증사이트 #보증업체 #리워드커뮤니티 #먹튀신고

7) Comment (댓글) 규칙
- 1~2문장, 영상 핵심 메시지 짧게 요약
- 해시태그 없음
- 본문에 업종 직접 언급 금지
- 예시: "온카스터디에서 활동만 해도 포인트가 쌓입니다. 지금 확인해보세요."

8) BGM 자동 선택 규칙
- Narration에서 가장 우세한 키워드군에 맞는 BGM prompt를 자동 선택:
  | 키워드 | prompt |
  | 안전/검증/보호/먹튀 | "corporate trustworthy, calm and confident, soft synth pads, secure feeling, reassuring, professional, stable" |
  | 커뮤니티/소통/정보 | "warm corporate, friendly, soft acoustic, welcoming, community feel, upbeat light" |
  | 리워드/혜택/포인트 | "growth and success, corporate achievement, building momentum, confident, rewarding" |
  | 실시간/라이브/이벤트 | "innovative tech corporate, futuristic, ambient electronic, energetic, dynamic" |
  | 신뢰/보증/안전놀이터 | "calm professional, corporate ambient, soft background, minimal, trustworthy" |
  | 일반 | "calm professional, corporate ambient, soft background, minimal" |

9) 출력 형식
반드시 아래 JSON 형태로만 응답하세요. JSON 외 텍스트 금지.
{
  "Subject": "제목 텍스트 온카스터디 #먹튀검증 #카지노커뮤니티 #토토커뮤니티 #먹튀검증사이트",
  "Narration": "5문장 나레이션",
  "Caption": "8~12문장 설명 #온카스터디 #먹튀검증 ...",
  "Comment": "1~2문장 댓글",
  "BGM_prompt": "선택된 BGM prompt"
}

📌 단어 반복 금지: 5문장 내에서 동일한 핵심 단어(명사/동사 어근)를 2회 이상 사용하지 마세요."""

# =============================================
# 이미지 프롬프트 AI 텍스트
# =============================================
ONCASTUDY_IMG_PROMPT = """=주어진 나레이션 파트에 정확히 매칭되는 시네마틱 이미지 프롬프트를 1개 생성해 주세요.

핵심 규칙:
1. 나레이션이 말하는 내용을 시청자가 바로 이해할 수 있는 구체적 장면을 만들 것
2. 추상적 비유(체스, 퍼즐 등)가 아닌 실제 상황/장면을 보여줄 것
3. 하나의 강렬한 비주얼 컨셉에 집중할 것
4. 프롬프트는 영어로 작성, 150~200자
5. 큰따옴표("")는 사용하지 않음
6. illustration, cartoon, 2D, anime, drawing 스타일은 절대 금지
7. 프롬프트는 A vertical video. 로 시작할 것
8. 프롬프트 끝에 필수: no text, no letters, no words, no watermark
9. 다른 파트와 시각적으로 겹치지 않도록, 이 파트만의 고유한 장면을 만들 것

비주얼 장르 (이 파트용):
{{ ['사이버 보안 — cyber security monitoring center dark screens neon glow', '디지털 커뮤니티 — modern social platform community interaction digital screens', '데이터 분석 — data analytics verification dashboard modern clean dark', '리워드 혜택 — premium reward gift card luxury gold elegant modern', '신뢰 보증 — trust verification badge official premium clean emblem'][($json.index || 1) - 1] }}

카메라/촬영 스타일 (이 파트용):
{{ ['extreme close-up with shallow depth of field', 'close-up with dramatic rim lighting', 'medium shot with cinematic composition', 'wide establishing shot with atmospheric depth', 'aerial drone perspective with sweeping motion'][($json.index || 1) - 1] }}

파트별 장면 힌트 (참고용, 그대로 쓰지 말 것):
- 파트1 (안전/검증): 보안 모니터링 센터, 다중 스크린 감시 시스템, 사이버 방어 대시보드
- 파트2 (커뮤니티): 소셜 플랫폼 인터페이스, 실시간 채팅, 디지털 네트워크 연결
- 파트3 (데이터/분석): 데이터 분석 대시보드, 검증 프로세스, 실시간 모니터링
- 파트4 (리워드/혜택): 기프트카드 디스플레이, 프리미엄 보상, 골드 포인트 적립
- 파트5 (신뢰/보증): 공식 인증 마크, 보증 엠블럼, 프리미엄 신뢰 배지

금지 패턴:
- 창문 앞 인물 실루엣, 양복 남자가 도시 내려다보는 장면
- shield/lock/key, arrow/graph/chart, rocket/lightning, puzzle, hourglass/clock
- 자연 풍경(산, 논, 바다, 꽃), 동양화/수묵화, 판타지/마법, 동물

출력 형식 (프롬프트만 1개):
A vertical video. ..., no text, no letters, no words, no watermark

나레이션 파트:
{{ $json.text }}

시드: {{ Math.floor(Math.random() * 99999) }}"""

# =============================================
# AI 검증 프롬프트 (타겟 수정)
# =============================================
ONCASTUDY_VERIFY_PROMPT = """아래 숏폼 콘텐츠를 6개 항목으로 평가해줘. 각 항목 1~10점.

[평가 대상]
Subject: {{ $json.Subject }}
Narration: {{ $json.Narration }}
Caption: {{ $json.Caption }}

[평가 항목]
1. 훅 파워 - 첫 문장이 스크롤을 멈추게 하는가? (질문/충격/수치 등 강력한 후킹)
2. 주제 관련성 - 트렌드/추천 주제와 부합하는가?
3. 나레이션 품질 - 5문장 구성, 80~150자, 자연스러운 흐름, 업종 직접 언급 안 하는가?
4. 클릭 유도력 - 제목이 호기심/클릭 욕구를 유발하는가?
5. 타겟 적합도 - 온라인 카지노/토토 이용자, 먹튀검증 관심자 대상에 맞는가?
6. 차별화 - 뻔하지 않고 독창적인 각도인가?

반드시 아래 JSON으로만 응답:
{
  "hook_power": 8,
  "topic_relevance": 7,
  "narration_quality": 9,
  "click_appeal": 7,
  "target_fit": 8,
  "differentiation": 6,
  "total": 45,
  "pass": true,
  "feedback": "통과/탈락 사유 1줄"
}"""

# =============================================
# Apply modifications
# =============================================
for node in wf_new['nodes']:
    name = node.get('name', '')
    p = node.get('parameters', {})

    # AI 주제 생성 (1차)
    if name == 'AI 주제 생성':
        msgs = p.get('messages', {})
        if isinstance(msgs, dict) and 'values' in msgs:
            for m in msgs['values']:
                if m.get('content', '') and len(m['content']) > 50:
                    m['content'] = ONCASTUDY_PROMPT
                    print(f"   ✓ AI 주제 생성: 온카스터디 프롬프트")
                    break

    # AI 주제 생성 2차
    elif name == 'AI 주제 생성 2차':
        msgs = p.get('messages', {})
        if isinstance(msgs, dict) and 'values' in msgs:
            for m in msgs['values']:
                if m.get('content', '') and len(m['content']) > 50:
                    m['content'] = ONCASTUDY_PROMPT
                    print(f"   ✓ AI 주제 생성 2차: 온카스터디 프롬프트")
                    break

    # AI 주제 생성 3차
    elif name == 'AI 주제 생성 3차':
        msgs = p.get('messages', {})
        if isinstance(msgs, dict) and 'values' in msgs:
            for m in msgs['values']:
                if m.get('content', '') and len(m['content']) > 50:
                    m['content'] = ONCASTUDY_PROMPT
                    print(f"   ✓ AI 주제 생성 3차: 온카스터디 프롬프트")
                    break

    # AI 검증 1, 2
    elif name in ('AI 검증 1', 'AI 검증 2'):
        msgs = p.get('messages', {})
        if isinstance(msgs, dict) and 'values' in msgs:
            for m in msgs['values']:
                if m.get('content', '') and '타겟 적합도' in m['content']:
                    m['content'] = ONCASTUDY_VERIFY_PROMPT
                    print(f"   ✓ {name}: 온카스터디 검증 프롬프트")
                    break

    # 이미지 프롬프트 AI
    elif name == '이미지 프롬프트 AI':
        if 'text' in p:
            p['text'] = ONCASTUDY_IMG_PROMPT
            print(f"   ✓ 이미지 프롬프트 AI: 온카스터디 비주얼")

    # 시트 기록
    elif name == '시트 기록':
        sn = p.get('sheetName', {})
        if isinstance(sn, dict):
            sn['value'] = 'gid=0'
            sn['cachedResultName'] = SHEET_TAB_NAME
        print(f"   ✓ 시트 기록: {SHEET_TAB_NAME}")

    # 상태 업데이트
    elif name == '상태 업데이트':
        sn = p.get('sheetName', {})
        if isinstance(sn, dict):
            sn['value'] = 'gid=0'
            sn['cachedResultName'] = SHEET_TAB_NAME
        print(f"   ✓ 상태 업데이트: {SHEET_TAB_NAME}")

    # 발행 완료
    elif name == '발행 완료':
        sn = p.get('sheetName', {})
        if isinstance(sn, dict):
            sn['value'] = 'gid=0'
            sn['cachedResultName'] = SHEET_TAB_NAME
        print(f"   ✓ 발행 완료: {SHEET_TAB_NAME}")

    # 분석 리포트 읽기
    elif name == '분석 리포트 읽기':
        sn = p.get('sheetName', {})
        if isinstance(sn, dict):
            sn['value'] = '분석리포트'
        print(f"   ✓ 분석 리포트 읽기: 분석리포트 탭")

    # 첫 댓글
    elif name == '첫 댓글':
        p['jsonBody'] = '={\n  "snippet": {\n    "videoId": "{{ $json.uploadId }}",\n    "topLevelComment": {\n      "snippet": {\n        "textOriginal": "구글에 온카스터디 검색"\n      }\n    }\n  }\n}'
        print(f"   ✓ 첫 댓글: 구글에 온카스터디 검색")

    # 스케줄 트리거
    elif name == '스케줄 트리거':
        p['rule'] = {'interval': [{'field': 'cronExpression', 'expression': '0 1,13 * * *'}]}
        print(f"   ✓ 스케줄: 매일 01:00, 13:00 KST")

# Set timezone
if 'settings' not in wf_new:
    wf_new['settings'] = {}
wf_new['settings']['timezone'] = 'Asia/Seoul'

# =============================================
# Create new workflow
# =============================================
print("\n3. Creating new workflow...")
payload = {
    "name": wf_new['name'],
    "nodes": wf_new['nodes'],
    "connections": wf_new['connections'],
    "settings": wf_new['settings'],
    "staticData": wf_new.get('staticData', None),
}

r = requests.post(f"{N8N_URL}/api/v1/workflows", headers=HEADERS, json=payload)
print(f"   POST: {r.status_code}")

if r.status_code in (200, 201):
    new_wf = r.json()
    new_wf_id = new_wf['id']
    print(f"   New workflow ID: {new_wf_id}")
    print(f"   Name: {new_wf['name']}")

    # Activate
    print("\n4. Activating...")
    ra = requests.post(f"{N8N_URL}/api/v1/workflows/{new_wf_id}/activate", headers=HEADERS)
    print(f"   Activate: {ra.status_code}")

    # Verify
    time.sleep(1)
    r2 = requests.get(f"{N8N_URL}/api/v1/workflows/{new_wf_id}", headers=HEADERS)
    vwf = r2.json()
    print(f"\n=== VERIFY ===")
    print(f"   Active: {vwf.get('active')}")
    print(f"   Nodes: {len(vwf['nodes'])}")
    print(f"   Timezone: {vwf['settings'].get('timezone')}")

    for node in vwf['nodes']:
        n = node.get('name', '')
        if n == 'AI 주제 생성':
            msgs = node['parameters'].get('messages', {})
            if isinstance(msgs, dict) and 'values' in msgs:
                content = msgs['values'][0].get('content', '')
                print(f"   AI 주제 생성: 온카스터디={'온카스터디' in content}")
        elif n == '첫 댓글':
            body = node['parameters'].get('jsonBody', '')
            print(f"   첫 댓글: 온카스터디={'온카스터디' in body}")
        elif n == '이미지 프롬프트 AI':
            text = node['parameters'].get('text', '')
            print(f"   이미지 프롬프트: 사이버={'사이버' in text}")
else:
    print(f"   ERROR: {r.text[:500]}")
