#!/usr/bin/env python3
"""
스포츠 숏폼 (완전자동 v1) n8n 워크플로우 생성 및 업로드 스크립트
- 루믹스 숏폼 v3 템플릿 기반
- 스포츠 콘텐츠 전용 프롬프트 및 설정
"""

import json, copy, uuid, subprocess, sys

TEMPLATE_PATH = "/Users/gimdongseog/n8n-project/v3_current.json"
OUTPUT_PATH = "/Users/gimdongseog/n8n-project/sports_shortform_v1.json"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud/api/v1/workflows"
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"

# ============================================================
# Credentials
# ============================================================
CRED_FAL = {"httpHeaderAuth": {"id": "R0m2RD0rtE8IKRt6", "name": "Header Auth account"}}
CRED_KIE = {"httpHeaderAuth": {"id": "34ktW72w0p8fCfUQ", "name": "Kie.ai"}}
CRED_SHOTSTACK = {"httpHeaderAuth": {"id": "3oEYwvtDnmFeylkp", "name": "Shotstack"}}
CRED_GEMINI = {"googlePalmApi": {"id": "IKP349r08J9Hoz5E", "name": "Google Gemini(PaLM) Api account"}}
CRED_SHEETS = {"googleSheetsOAuth2Api": {"id": "CWBUyXUqCU9p5VAg", "name": "Google Sheets account"}}
CRED_YOUTUBE = {"youTubeOAuth2Api": {"id": "kRKBMYWf6cB72qUi", "name": "YouTube account"}}

# ============================================================
# Google Sheets config
# ============================================================
SHEET_DOC_ID = "1NAVwKXLQOUzBoNckxxesIR_ZS3GoNVGepr8zkBFmz4M"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_DOC_ID}/edit?usp=drivesdk"
SHEET_GID_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_DOC_ID}/edit#gid=0"

# ============================================================
# Sports-specific prompts
# ============================================================
SPORTS_TOPIC_PROMPT = """너는 스포츠 전문 콘텐츠 기획자야.
YouTube Shorts(30~50초)용 스포츠 콘텐츠를 기획해줘.

타겟: 스포츠 팬, 배팅 분석에 관심 있는 사람, 경기 결과/소식이 궁금한 시청자
톤: 스포츠 전문가, 친근하면서 신뢰감 있는 목소리, 데이터 기반 분석

아래 [콘텐츠 스타일] 중 하나를 랜덤으로 골라서 적용해:
a. 경기 분석형: "오늘 토트넘 vs 아스날, 승부 가를 핵심 포인트 3가지"
b. 베팅 정보형: "프로야구 배당률 분석, 이 팀이 저평가된 이유"
c. 선수 소식형: "손흥민 최근 폼 분석, 다음 경기 활약 가능성은?"
d. 하이라이트/리뷰형: "어제 경기 미쳤다... 역전 드라마 총정리"
e. 전략/팁형: "스포츠 분석 잘하는 사람들의 공통점 5가지"

아래 [주제 카테고리] 중 하나를 랜덤으로 골라서 구체적인 주제를 만들어:
1. 축구 (EPL, 라리가, K리그, 국대)
2. 야구 (MLB, KBO)
3. 농구 (NBA, KBL)
4. 종합격투기 (UFC)
5. 배당률/확률 분석
6. 스포츠 데이터 분석 방법
7. 시즌 프리뷰/리뷰
8. 선수 이적/부상 영향 분석
9. 테니스 (그랜드슬램, ATP/WTA)
10. e스포츠 (LoL, 발로란트)

[피드/클릭 최적화 규칙]
- 첫 문장은 반드시 강력한 훅으로 시작 (질문, 충격, 공감 중 하나)
- 제목은 호기심 유발 (숫자, 비밀, 충격적 사실 활용)
- 감정 흐름: 호기심 → 정보/분석 → 솔루션(플랫폼 언급) → CTA

[간접 광고 규칙 - OO 플랫폼]
- 나레이션 후반부에서 "OO 플랫폼"을 자연스럽게 1~2회 언급
- 다양한 간접 광고 스타일 중 하나를 랜덤 선택:
  * 대화형: "친구가 알려준 건데, OO 플랫폼에서 이런 분석 자료 다 볼 수 있더라고"
  * 후기형: "나도 처음엔 반신반의했는데, OO 플랫폼 써보니까 데이터 정리가 확실히 다르더라"
  * 정보형: "이런 분석 자료가 OO 플랫폼에 다 정리되어 있더라"
  * 비교형: "여기저기 찾아봤는데, OO 플랫폼만큼 깔끔하게 정리된 곳은 없었어"
- 절대 직접적인 광고/홍보 느낌이 나면 안 됨

반드시 아래 JSON 형식으로만 응답해. 마크다운 코드블록 없이 순수 JSON만:
{
  "Subject": "영상 제목 (호기심 유발, 15자 이내, 숫자/비밀/충격 활용)",
  "Narration": "나레이션 전문 (30~50초 분량, 200~350자, 자연스러운 말투, 후반부에 OO 플랫폼 자연스럽게 1~2회 언급)",
  "Caption": "YouTube 설명 (해시태그 포함, 3줄, #스포츠 #분석 등)",
  "Comment": "첫 번째 댓글 (질문 유도 또는 CTA, 스포츠 관련)",
  "BGM_prompt": "energetic exciting sports stadium atmosphere background music"
}"""

SPORTS_IMAGE_PROMPT = """=주어진 나레이션 파트에 정확히 매칭되는 스포츠 시네마틱 이미지 프롬프트를 1개 생성해 주세요.

핵심 규칙:
1. 이 나레이션 파트가 말하는 구체적인 스포츠 내용을 직접적으로 시각화할 것
2. 추상적 비주얼이 아닌, 나레이션이 설명하는 실제 스포츠 상황/장면을 보여줄 것
3. 하나의 강렬한 비주얼 컨셉에 집중할 것
4. 프롬프트는 영어로 작성, 150~200자
5. 큰따옴표("")는 사용하지 않음
6. illustration, cartoon, 2D, anime, drawing 스타일은 절대 금지
7. 프롬프트는 A vertical video. 로 시작할 것
8. 프롬프트 끝에 필수: no text, no letters, no words, no watermark

금지 콘텐츠:
- 실제 선수 얼굴 (특정 인물 묘사 금지)
- 팀 로고, 저작권 있는 콘텐츠
- 특정 유니폼 디자인 직접 묘사

비주얼 장르 (이번 영상 전체 톤):
{{ ['stadium atmosphere dramatic lighting — packed stadium roaring crowd floodlights dramatic shadows', 'dynamic sports action — motion blur athletic movement powerful dramatic angle', 'data stats overlay — futuristic holographic sports statistics neon data visualization', 'dramatic sports moment — cinematic slow motion decisive moment high contrast', 'neon sports graphics — vibrant neon glow modern sports aesthetic dark background electric'][Math.floor(Math.random() * 5)] }}

카메라/촬영 스타일 (이 파트용):
{{ ['extreme close-up with shallow depth of field', 'close-up with dramatic rim lighting', 'medium shot with cinematic composition', 'wide establishing shot with atmospheric depth', 'aerial drone perspective with sweeping motion'][($json.index || 1) - 1] }}

금지 패턴:
- 창문 앞 인물 실루엣, 골든아워 역광, 양복 남자가 도시 내려다보는 장면
- 악수 장면, 단순 사무실
- shield/lock/key, arrow/graph/chart, rocket/lightning, puzzle, hourglass/clock

비주얼 생성 가이드:
- 스포츠 현장의 생동감과 긴장감을 극대화
- 시네마틱 스포츠 포토그래피 스타일
- 마치 ESPN/DAZN 광고 감독이 스토리보드를 짜는 것처럼

출력 형식 (프롬프트만 1개):
A vertical video. ..., no text, no letters, no words, no watermark

나레이션 파트:
{{ $json.text }}

시드: {{ Math.floor(Math.random() * 99999) }}"""


def find_node(nodes, name):
    for n in nodes:
        if n["name"] == name:
            return n
    return None


def main():
    # Read template
    with open(TEMPLATE_PATH, "r") as f:
        template = json.load(f)

    nodes = copy.deepcopy(template["nodes"])
    connections = copy.deepcopy(template["connections"])

    # Generate new IDs
    for n in nodes:
        n["id"] = str(uuid.uuid4())
        if "webhookId" in n:
            n["webhookId"] = str(uuid.uuid4())

    # 1. Update AI topic prompt
    ai_node = find_node(nodes, "AI 주제 생성")
    ai_node["parameters"]["messages"]["values"][0]["content"] = SPORTS_TOPIC_PROMPT

    # 2. Update Google Sheets document IDs
    for sheet_name in ["시트 기록", "상태 업데이트", "발행 완료"]:
        sn = find_node(nodes, sheet_name)
        if sn:
            sn["parameters"]["documentId"]["value"] = SHEET_DOC_ID
            sn["parameters"]["documentId"]["cachedResultName"] = "n8n 스포츠"
            sn["parameters"]["documentId"]["cachedResultUrl"] = SHEET_URL
            sn["parameters"]["sheetName"]["cachedResultName"] = "스포츠"
            sn["parameters"]["sheetName"]["cachedResultUrl"] = SHEET_GID_URL

    # 3. Update image prompt
    img_node = find_node(nodes, "이미지 프롬프트 AI")
    img_node["parameters"]["text"] = SPORTS_IMAGE_PROMPT

    # 4. Update BGM default
    bgm_node = find_node(nodes, "BGM 생성")
    bgm_node["parameters"]["jsonBody"] = '={\n  "prompt": "{{ $json.bgmPrompt || \'energetic exciting sports stadium atmosphere background music\' }}",\n  "duration": 40,\n  "refinement": 100,\n  "creativity": 16\n}'

    # 5. Assign ALL credentials
    for name in ["AI 주제 생성", "나레이션 분할"]:
        find_node(nodes, name)["credentials"] = CRED_GEMINI
    find_node(nodes, "Gemini Chat Model")["credentials"] = CRED_GEMINI

    for name in ["시트 기록", "상태 업데이트", "발행 완료"]:
        find_node(nodes, name)["credentials"] = CRED_SHEETS

    yt = find_node(nodes, "YouTube 업로드")
    yt["credentials"] = CRED_YOUTUBE
    yt["parameters"]["categoryId"] = "17"  # Sports

    find_node(nodes, "첫 댓글")["credentials"] = CRED_YOUTUBE

    for name in ["TTS 요청", "TTS 결과", "이미지 생성", "이미지 결과", "업스케일 요청", "업스케일 결과", "BGM 생성"]:
        find_node(nodes, name)["credentials"] = CRED_FAL

    for name in ["영상 생성", "영상 결과"]:
        find_node(nodes, name)["credentials"] = CRED_KIE

    for name in ["Shotstack 렌더", "렌더 결과"]:
        find_node(nodes, name)["credentials"] = CRED_SHOTSTACK

    # Build output
    workflow = {
        "name": "스포츠 숏폼 (완전자동 v1)",
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"}
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)

    print(f"[OK] Workflow JSON saved to: {OUTPUT_PATH}")
    print(f"     Nodes: {len(nodes)}, Connections: {len(connections)}")

    # Upload
    print("\n[INFO] Uploading to n8n...")
    result = subprocess.run(
        ["curl", "-sk", "-X", "POST", N8N_URL,
         "-H", f"X-N8N-API-KEY: {N8N_API_KEY}",
         "-H", "Content-Type: application/json",
         "-d", f"@{OUTPUT_PATH}"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"[ERROR] curl failed: {result.stderr}")
        sys.exit(1)

    try:
        response = json.loads(result.stdout)
        wf_id = response.get("id", "UNKNOWN")
        print(f"\n[SUCCESS] Workflow uploaded!")
        print(f"  Workflow ID: {wf_id}")
        print(f"  Name: {response.get('name')}")
        print(f"  URL: https://n8n.srv1345711.hstgr.cloud/workflow/{wf_id}")
    except json.JSONDecodeError:
        print(f"[ERROR] Response: {result.stdout[:500]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
