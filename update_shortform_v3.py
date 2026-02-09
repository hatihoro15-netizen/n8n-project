"""숏폼 워크플로우 v3 업데이트: FLUX 2 Pro + Kie.ai Kling 2.6 + AuraSR"""
import json, uuid, ssl, subprocess

with open('/Users/gimdongseog/n8n-project/shortform_current.json') as f:
    wf = json.load(f)

nodes = wf["nodes"]
connections = wf["connections"]
changes = []

for node in nodes:
    name = node["name"]

    # 1. FLUX Pro → FLUX 2 Pro
    if name == "이미지 생성":
        node["parameters"]["url"] = "https://queue.fal.run/fal-ai/flux-2-pro"
        node["parameters"]["jsonBody"] = '={\n  "prompt": "{{ $json.text }}",\n  "image_size": {\n    "width": 1080,\n    "height": 1920\n  }\n}'
        changes.append("이미지: FLUX Pro → FLUX 2 Pro ($0.06→$0.03)")

    # 2. ESRGAN → AuraSR
    if name == "업스케일 요청":
        node["parameters"]["url"] = "https://queue.fal.run/fal-ai/aura-sr"
        node["parameters"]["jsonBody"] = '={\n  "image_url": "{{ $json.images[0].url }}",\n  "upscaling_factor": 2\n}'
        changes.append("업스케일: ESRGAN → AuraSR (더 선명)")

    # 3. fal.ai Kling → Kie.ai Kling 2.6
    if name == "영상 생성":
        node["parameters"]["url"] = "https://api.kie.ai/api/v1/jobs/createTask"
        node["parameters"]["jsonBody"] = """={
  "model": "kling-2.6/image-to-video",
  "input": {
    "prompt": "{{ $json.prompt || 'cinematic motion, slow camera movement, professional' }}",
    "image_urls": ["{{ $json.image.url }}"],
    "sound": false,
    "duration": "5"
  }
}"""
        changes.append("영상: fal.ai Kling → Kie.ai Kling 2.6 ($0.35→$0.28)")

    # 4. 영상 결과: Kie.ai 응답 형식
    if name == "영상 결과":
        node["parameters"]["url"] = "=https://api.kie.ai/api/v1/jobs/recordInfo?taskId={{ $json.data.taskId }}"
        changes.append("영상 결과: Kie.ai 응답 형식으로 변경")

# 5. Kie.ai 응답 변환 노드 추가
normalize_node = {
    "parameters": {
        "jsCode": """// Kie.ai 응답에서 영상 URL 추출 → fal.ai 호환 형식
const data = $input.first().json;
let videoUrl = '';

if (data.data && data.data.resultJson) {
  try {
    const result = JSON.parse(data.data.resultJson);
    videoUrl = result.resultUrls ? result.resultUrls[0] : '';
  } catch(e) { videoUrl = ''; }
}

return [{ json: { video: { url: videoUrl }, state: data.data?.state || 'unknown' } }];"""
    },
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1200, 950],
    "id": str(uuid.uuid4()),
    "name": "영상 URL 정리"
}
nodes.append(normalize_node)
changes.append("영상 URL 정리 노드 추가 (Kie.ai→fal.ai 호환)")

# 연결 수정: 영상 결과 → 영상 URL 정리 → Merge
if "영상 결과" in connections:
    connections["영상 결과"] = {"main": [[{"node": "영상 URL 정리", "type": "main", "index": 0}]]}
connections["영상 URL 정리"] = {"main": [[{"node": "Merge", "type": "main", "index": 2}]]}

# Shotstack 타임라인 코드에서 영상 참조 업데이트
for node in nodes:
    if node["name"] == "Shotstack 타임라인":
        code = node["parameters"]["jsCode"]
        code = code.replace("$('영상 결과')", "$('영상 URL 정리')")
        node["parameters"]["jsCode"] = code
        changes.append("Shotstack 타임라인: 영상 URL 참조 업데이트")

# 워크플로우 정리
wf["name"] = "루믹스 솔루션 숏폼 (완전자동 v3)"
for key in ["id", "createdAt", "updatedAt", "versionId", "activeVersionId",
            "versionCounter", "triggerCount", "shared", "tags", "activeVersion",
            "isArchived", "description", "meta", "pinData", "staticData", "active"]:
    wf.pop(key, None)
wf["settings"] = {"executionOrder": "v1"}

# 저장
output = '/Users/gimdongseog/n8n-project/workflow_lumix_shortform_v3.json'
with open(output, 'w') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

print("=" * 60)
print("숏폼 v3 워크플로우 생성 완료!")
print(f"파일: {output}")
print(f"노드 수: {len(nodes)}개")
print("=" * 60)
for c in changes:
    print(f"  ✅ {c}")
print()
print("비용: $1.73/편 (기존 $2.50 → 31% 절감)")
