import json
import copy
import uuid

with open('/Users/gimdongseog/n8n-project/workflow_original.json', 'r') as f:
    original = json.load(f)

# Create new workflow from original
new_wf = {
    "name": "전용 (개선판 - 이미지 매칭)",
    "nodes": copy.deepcopy(original["nodes"]),
    "connections": copy.deepcopy(original["connections"]),
    "settings": original.get("settings", {}),
    "staticData": None,
    "pinData": {}
}

nodes = new_wf["nodes"]
connections = new_wf["connections"]

# ============================================================
# 핵심 개선: 이미지 프롬프트가 분할된 나레이션을 1:1로 받도록 변경
#
# 현재 문제:
#   Get row(s) in sheet → 이미지 프롬프트 (전체 나레이션으로 5개 한번에)
#   Message a model1 → Code in JavaScript2 → 나레이션 음성 입력 (5개 분할)
#   → 이미지와 나레이션이 독립적으로 생성되어 안 맞음
#
# 개선:
#   Message a model1 → Code in JavaScript2 → 각 분할 텍스트를
#   이미지 프롬프트에도 전달하여 1:1 매칭
# ============================================================

# 1. Find the image prompt node and update its prompt
for node in nodes:
    if node["name"] == "이미지 프롬프트":
        # Change the prompt to use SPLIT narration from Code in JavaScript2
        # instead of the full narration from Get row(s) in sheet
        node["parameters"]["text"] = """=주어진 나레이션 파트에 정확히 매칭되는 시네마틱 이미지 프롬프트를 1개 생성해 주세요.

핵심 규칙:
1. 이 나레이션 파트가 말하는 구체적인 내용을 직접적으로 시각화할 것
2. 추상적 비주얼이 아닌, 나레이션이 설명하는 실제 상황/장면을 보여줄 것
3. 하나의 강렬한 비주얼 컨셉에 집중할 것
4. 프롬프트는 영어로 작성, 150~200자
5. 큰따옴표("")는 사용하지 않음
6. illustration, cartoon, 2D, anime, drawing 스타일은 절대 금지
7. 프롬프트는 A vertical video. 로 시작할 것
8. 프롬프트 끝에 필수: no text, no letters, no words, no watermark

비주얼 장르 (이번 영상 전체 톤):
{{ ['사이버펑크 네온 — neon glow cyberpunk futuristic dark city', '자연 다큐멘터리 — nature documentary organic earthy warm tones', '미니멀 흑백 — minimal monochrome high contrast black white', '레트로 필름그레인 — retro film grain vintage 70s warm analog', '하이테크 미래 — high-tech futuristic holographic clean blue', '다크 시네마틱 — dark cinematic dramatic shadows moody', '팝아트 컬러풀 — pop art vibrant saturated bold colors', '수중/우주 판타지 — underwater space fantasy ethereal floating', '동양풍 — oriental asian aesthetic ink wash dramatic', '고딕 다크판타지 — gothic dark fantasy mystical ancient'][Math.floor(Math.random() * 10)] }}

이 장르의 느낌을 반영하되, 나레이션 내용을 정확히 시각화하는 것이 최우선입니다.

카메라/촬영 스타일 (이 파트용):
{{ ['extreme close-up with shallow depth of field', 'close-up with dramatic rim lighting', 'medium shot with cinematic composition', 'wide establishing shot with atmospheric depth', 'aerial drone perspective with sweeping motion'][($json.index || 1) - 1] }}

금지 패턴:
- 창문 앞 인물 실루엣, 골든아워 역광, 양복 남자가 도시 내려다보는 장면
- 악수 장면, 단순 사무실
- shield/lock/key, arrow/graph/chart, rocket/lightning, puzzle, hourglass/clock

비주얼 생성 가이드:
- 나레이션이 말하는 내용을 시청자가 바로 이해할 수 있는 구체적 장면
- 예시: 서버 관리 → 서버룸, 자동화 → 대시보드, 수익 → 금화/돈, 모바일 → 스마트폰 UI
- 마치 고급 브랜드 광고 감독이 이 한 장면의 스토리보드를 짜는 것처럼

출력 형식 (번호 없이 프롬프트만 1개 출력):
A vertical video. ..., no text, no letters, no words, no watermark

나레이션 파트 (이 파트만 시각화하세요):
{{ $json.text }}

시드: {{ Math.floor(Math.random() * 99999) }}"""

        # Change to generate 1 item instead of 5
        node["parameters"]["hasOutputParser"] = True

        # Update position to be after Code in JavaScript2
        node["position"] = [-480, 464]
        break

# 2. Update the Item List Output Parser to expect 1 item instead of 5
for node in nodes:
    if node["name"] == "Item List Output Parser":
        node["parameters"]["options"]["numberOfItems"] = 1
        break

# 3. Change the connection: 이미지 프롬프트 should receive from Code in JavaScript2
#    instead of Get row(s) in sheet
# Remove old connection: Get row(s) in sheet → 이미지 프롬프트
if "Get row(s) in sheet" in connections:
    old_main = connections["Get row(s) in sheet"]["main"][0]
    connections["Get row(s) in sheet"]["main"][0] = [
        conn for conn in old_main
        if conn["node"] != "이미지 프롬프트"
    ]

# Add new connection: Code in JavaScript2 → 이미지 프롬프트
if "Code in JavaScript2" in connections:
    existing = connections["Code in JavaScript2"]["main"][0]
    # Add 이미지 프롬프트 as additional output from Code in JavaScript2
    existing.append({
        "node": "이미지 프롬프트",
        "type": "main",
        "index": 0
    })
else:
    connections["Code in JavaScript2"] = {
        "main": [[
            {"node": "나레이션 음성 입력", "type": "main", "index": 0},
            {"node": "이미지 프롬프트", "type": "main", "index": 0}
        ]]
    }

# 4. Update Flux Pro image input - remove generic style suffix
for node in nodes:
    if node["name"] == "이미지 입력":
        node["parameters"]["jsonBody"] = """={
  "prompt": "{{ $json.text }}",
  "image_size": {
    "width": 1080,
    "height": 1920
  },
  "style": "realistic_image"
}"""
        break

# 5. Generate new unique IDs for all nodes to avoid conflicts
for node in nodes:
    node["id"] = str(uuid.uuid4())

# Save the modified workflow
output_path = '/Users/gimdongseog/n8n-project/workflow_improved.json'
with open(output_path, 'w') as f:
    json.dump(new_wf, f, ensure_ascii=False, indent=2)

print("개선된 워크플로우 JSON 생성 완료!")
print(f"파일: {output_path}")
print()
print("주요 변경사항:")
print("1. 이미지 프롬프트: 전체 나레이션 → 분할된 나레이션 1:1 매칭")
print("2. 이미지 프롬프트: 5개 한번에 → 각 파트별 1개씩 생성")
print("3. 비주얼 장르: 10개 중 랜덤 선택 (매번 다른 느낌)")
print("4. 카메라 스타일: 파트 인덱스에 따라 자동 차별화")
print("5. Flux Pro: 범용 스타일 제거, AI 프롬프트 자체에 스타일 포함")
