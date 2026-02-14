import json, requests, time, copy, uuid

N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
HEADERS = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}
SOURCE_WF_ID = "tS2hcoeJ4ar8hivm"

print("1. Fetching source workflow (루믹스 Veo3)...")
resp = requests.get(f"{N8N_URL}/api/v1/workflows/{SOURCE_WF_ID}", headers=HEADERS)
wf = resp.json()
print(f"   Nodes: {len(wf['nodes'])}")

wf_new = copy.deepcopy(wf)
wf_new['name'] = '온카스터디 Veo3 5x8초 숏폼'

for key in ['id', 'createdAt', 'updatedAt', 'versionId']:
    wf_new.pop(key, None)

for node in wf_new['nodes']:
    node['id'] = str(uuid.uuid4())

# =============================================
# 온카스터디 Veo3 시나리오 프롬프트
# =============================================
ONCASTUDY_VEO3_PROMPT = """당신은 YouTube 숏폼 전문 시나리오 작가입니다.

**온카스터디** 먹튀검증 커뮤니티를 간접 홍보하는 5개의 **독립적인 8초 영상** 시나리오를 만들어주세요.

## 캐릭터 설정 (모든 영상 동일)
- 남자: 한국인 30대, 짧은 검은 머리, 진한 네이비 수트, 깊고 차분하며 권위있는 목소리
- 여자: 한국인 20대 후반, 어깨길이 검은 머리, 흰색 블라우스, 밝고 에너지 넘치며 친근한 목소리

## 핵심 규칙
1. 각 영상은 **완전히 독립적** - 서로 다른 장소, 다른 주제
2. **절대 '카지노/토토/슬롯/배팅' 직접 언급 금지** → 검증/커뮤니티/안전/혜택/정보 사용
3. 8초 분량 대화 (2-3문장 교환)
4. 숏폼 가이드: 첫 1-3초 hook, 루프 구조, 완주율 최적화
5. 온카스터디의 가치: 먹튀검증, 포인트 리워드, 라이브 방송, 커뮤니티, 안전한 정보 공유

## 5개 영상 주제 (각각 다른 것)
1. 먹튀 피해를 막는 검증 시스템의 가치
2. 활동만으로 포인트/기프티콘을 받는 리워드 혜택
3. 실시간 라이브 방송과 커뮤니티의 즐거움
4. 보증업체 선정과 안전놀이터의 중요성
5. 정보 공유와 신뢰 커뮤니티의 힘

## veo3_prompt 필수 포함 문구 (영어로)
각 veo3_prompt 시작은 반드시 이것으로:
"A Korean man in his 30s wearing a dark navy suit with short black hair speaks with a deep, calm, authoritative voice. A Korean woman in her late 20s wearing a white blouse with shoulder-length black hair speaks with a bright, energetic, friendly voice."

그 다음에 장소, 장면 묘사, 한국어 대사를 포함하세요.

## subject/caption 규칙
- subject: 후킹 문구 + 온카스터디 #먹튀검증 #카지노커뮤니티 #토토커뮤니티 #먹튀검증사이트
- caption: 8~12문장 설명 + #온카스터디 #먹튀검증 #카지노 #토토 #먹튀검증사이트 #보증업체 #리워드커뮤니티 #먹튀신고
- comment: 1~2문장, 업종 직접 언급 금지

## 출력 형식 (순수 JSON만, 마크다운 코드블록 없이)
{
  "videos": [
    {
      "video_num": 1,
      "topic": "주제 설명",
      "veo3_prompt": "A Korean man in his 30s wearing a dark navy suit with short black hair speaks with a deep, calm, authoritative voice. A Korean woman in her late 20s wearing a white blouse with shoulder-length black hair speaks with a bright, energetic, friendly voice. They sit across from each other at [장소]. [장면묘사]. Man: '[한국어 대사]' Woman: '[한국어 대사]' [마무리 묘사]. Cinematic lighting, 9:16 vertical, 8 seconds.",
      "subtitle_ko": "핵심 대사 한국어",
      "subject": "YouTube 영상 제목 온카스터디 #먹튀검증 #카지노커뮤니티 #토토커뮤니티 #먹튀검증사이트",
      "caption": "설명 + #해시태그",
      "comment": "첫 댓글 내용"
    }
  ]
}

총 5개 video를 만들어주세요. 각 video_num은 1~5입니다."""

# =============================================
# 온카스터디 Veo3 검증 프롬프트
# =============================================
ONCASTUDY_VEO3_VERIFY = """당신은 YouTube 숏폼 콘텐츠 검증 전문가입니다.

아래 5개 영상 시나리오를 각각 검증해주세요.

## 검증할 시나리오:
{{ $json.content.parts[0].text }}

## 검증 기준 (각 항목 1-10점)
1. **훅 파워** - 첫 대사가 스크롤을 멈추게 하는가?
2. **스토리 흐름** - 8초 안에 기승전결이 있는가?
3. **루프 가능성** - 끝→시작 자연 연결되는가?
4. **완주 유도** - 끝까지 보고 싶게 만드는가?
5. **간접 광고** - 카지노/토토 직접 언급 없이 온카스터디를 자연스럽게 홍보하는가?
6. **차별화** - 뻔하지 않고 신선한가?
7. **클릭 유도** - subject가 클릭하고 싶게 만드는가?

## 출력 (순수 JSON만)
{
  "total_score": 49,
  "pass": true,
  "feedback": "전체 피드백 1-2줄",
  "videos": [
    {"video_num": 1, "score": 48, "feedback": "피드백"}
  ]
}

통과 기준: total_score 49점 이상 (평균 7점)"""

# =============================================
# 재생성 프롬프트
# =============================================
ONCASTUDY_VEO3_RETRY = """당신은 YouTube 숏폼 전문 시나리오 작가입니다.

이전 시나리오가 검증에서 탈락했습니다. 피드백을 반영하여 다시 작성해주세요.

## 이전 검증 피드백:
{{ $json.content.parts[0].text }}

""" + ONCASTUDY_VEO3_PROMPT

print("\n2. Modifying nodes for 온카스터디...")

for node in wf_new['nodes']:
    name = node.get('name', '')
    p = node.get('parameters', {})

    if name == 'AI 시나리오 생성':
        msgs = p.get('messages', {})
        if isinstance(msgs, dict) and 'values' in msgs:
            for m in msgs['values']:
                if m.get('content', '') and len(m['content']) > 50:
                    m['content'] = ONCASTUDY_VEO3_PROMPT
                    print(f"   ✓ AI 시나리오 생성: 온카스터디")
                    break

    elif name == 'AI 검증':
        msgs = p.get('messages', {})
        if isinstance(msgs, dict) and 'values' in msgs:
            for m in msgs['values']:
                if m.get('content', '') and len(m['content']) > 50:
                    m['content'] = ONCASTUDY_VEO3_VERIFY
                    print(f"   ✓ AI 검증: 온카스터디")
                    break

    elif name == 'AI 시나리오 재생성':
        msgs = p.get('messages', {})
        if isinstance(msgs, dict) and 'values' in msgs:
            for m in msgs['values']:
                if m.get('content', '') and len(m['content']) > 50:
                    m['content'] = ONCASTUDY_VEO3_RETRY
                    print(f"   ✓ AI 시나리오 재생성: 온카스터디")
                    break

    elif name == 'Webhook Trigger':
        p['path'] = 'oncastudy-veo3-trigger'
        print(f"   ✓ Webhook: oncastudy-veo3-trigger")

    elif name == '수동 실행':
        pass  # Keep as is

# Settings
if 'settings' not in wf_new:
    wf_new['settings'] = {}
wf_new['settings']['timezone'] = 'Asia/Seoul'

# Create
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

    # Verify
    time.sleep(1)
    r2 = requests.get(f"{N8N_URL}/api/v1/workflows/{new_wf_id}", headers=HEADERS)
    vwf = r2.json()
    print(f"\n=== VERIFY ===")
    print(f"   Nodes: {len(vwf['nodes'])}")
    for node in vwf['nodes']:
        n = node.get('name', '')
        if n == 'AI 시나리오 생성':
            msgs = node['parameters'].get('messages', {})
            if isinstance(msgs, dict) and 'values' in msgs:
                content = msgs['values'][0].get('content', '')
                print(f"   AI 시나리오: 온카스터디={'온카스터디' in content}")
else:
    print(f"   ERROR: {r.text[:500]}")
