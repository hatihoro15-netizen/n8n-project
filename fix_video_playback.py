#!/usr/bin/env python3
"""
fix_video_playback.py
=====================
Creatomate 타임라인 노드에서:
- Video-{n}.loop = true 제거
- playback_rate 계산 추가 (나레이션 > 영상이면 슬로우모션, 아니면 1)
- 기존 modifications (width, height, source, duration, narration, text, BGM, T24 등) 모두 보존
"""

import json
import urllib.request
import ssl
import sys

# SSL context - bypass verification for self-hosted n8n
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

API_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

HEADERS = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json",
}

# === The new JavaScript code for the Creatomate 타임라인 node ===
NEW_JS_CODE = '''// === Creatomate 타임라인 빌더 ===
const bgmUrl = $('BGM 대기').first().json.audio?.url || '';
const videoDuration = 5; // Kling 영상 생성 길이 (초)
const bitrate = 128000;
let totalDuration = 0;

const modifications = {};

for (let i = 0; i < 5; i++) {
  const n = i + 1;

  // TTS 결과
  const ttsResult = $('TTS 결과').all()[i]?.json;
  const narrationUrl = ttsResult?.audio?.url || '';
  const fileSize = ttsResult?.audio?.file_size || 40000;

  // 오디오 파일 크기로 narration duration 추정
  let narrationDuration = Math.round((fileSize * 8 / bitrate) * 100) / 100;
  if (narrationDuration < 3) narrationDuration = 5;

  // 컴포지션 duration = Math.max(나레이션, 영상)
  const compositionDuration = Math.max(narrationDuration, videoDuration);

  // playback_rate 계산: 나레이션이 영상보다 길면 영상을 느리게 재생
  // compositionDuration > videoDuration 이면 playbackRate = videoDuration / compositionDuration (슬로우)
  // 그 외에는 playbackRate = 1 (정상 속도)
  const playbackRate = compositionDuration > videoDuration
    ? Math.round((videoDuration / compositionDuration) * 1000) / 1000
    : 1;

  // 영상 URL
  const videoResult = $('영상 URL 정리').all()[i]?.json;
  const videoUrl = videoResult?.video?.url || '';

  // 자막 텍스트
  const subtitleText = ($('5파트 분리').all()[i]?.json?.text || '').replace(/\\n/g, '\\\\n');

  // Creatomate modifications
  modifications[`Composition-${n}.duration`] = String(compositionDuration);
  modifications[`Video-${n}.source`] = videoUrl;
  modifications[`Video-${n}.playback_rate`] = String(playbackRate);
  modifications[`Narration-${n}.source`] = narrationUrl;
  modifications[`Text-${n}.text`] = subtitleText;

  totalDuration += compositionDuration;
}

// BGM
modifications['BGM.source'] = bgmUrl;

// 엔딩카드
modifications['Video-T24.time'] = String(totalDuration);
modifications['Video-T24.duration'] = '4';

const payload = {
  template_id: "056a9082-710f-4345-b964-c6384103fbf6",
  output_format: "mp4",
  width: 1080,
  height: 1920,
  h264_profile: "high",
  h264_level: "5.2",
  h264_crf: 10,
  h264_bitrate: 20000000,
  frame_rate: 30,
  duration: String(totalDuration + 8),
  modifications: modifications
};

return [{
  json: {
    creatomate_payload: payload,
    modifications: modifications,
    subject: $('시트 기록').first().json.Subject,
    caption: $('시트 기록').first().json.Caption,
    comment: $('시트 기록').first().json.Comment
  }
}];'''


def api_get(path):
    """GET request to n8n API."""
    req = urllib.request.Request(f"{API_BASE}{path}", headers=HEADERS)
    with urllib.request.urlopen(req, context=ssl_ctx) as resp:
        return json.loads(resp.read().decode())


def api_put(path, data):
    """PUT request to n8n API."""
    body = json.dumps(data).encode()
    req = urllib.request.Request(f"{API_BASE}{path}", data=body, headers=HEADERS, method="PUT")
    with urllib.request.urlopen(req, context=ssl_ctx) as resp:
        return json.loads(resp.read().decode())


def main():
    # Step 1: Fetch the workflow
    print("=" * 60)
    print("[Step 1] Fetching workflow...")
    workflow = api_get(f"/workflows/{WORKFLOW_ID}")
    print(f"  Workflow: {workflow['name']}")
    print(f"  Nodes: {len(workflow['nodes'])}")

    # Step 2: Find the Creatomate 타임라인 node
    print("\n" + "=" * 60)
    print("[Step 2] Finding 'Creatomate 타임라인' node...")
    target_node = None
    target_idx = None
    for idx, node in enumerate(workflow["nodes"]):
        if "Creatomate" in node.get("name", "") and "타임라인" in node.get("name", ""):
            target_node = node
            target_idx = idx
            break

    if target_node is None:
        print("  ERROR: 'Creatomate 타임라인' node not found!")
        sys.exit(1)

    print(f"  Found node: '{target_node['name']}' (index {target_idx})")

    old_code = target_node["parameters"].get("jsCode", "")

    # Verify old code has loop
    if ".loop" not in old_code:
        print("  WARNING: '.loop' not found in current code. Proceeding anyway.")
    else:
        loop_count = old_code.count(".loop")
        print(f"  Found {loop_count} occurrence(s) of '.loop' in current code.")

    # Step 3: Show diff summary
    print("\n" + "=" * 60)
    print("[Step 3] Changes to be made:")
    print("  REMOVE: modifications[`Video-${n}.loop`] = true;")
    print("  ADD:    playback_rate calculation (videoDuration / compositionDuration)")
    print("  ADD:    modifications[`Video-${n}.playback_rate`] = String(playbackRate);")

    # Step 4: Apply the new code
    print("\n" + "=" * 60)
    print("[Step 4] Applying new code...")
    workflow["nodes"][target_idx]["parameters"]["jsCode"] = NEW_JS_CODE
    print("  Code replaced in memory.")

    # Step 5: Upload modified workflow
    print("\n" + "=" * 60)
    print("[Step 5] Uploading modified workflow...")

    # Build the update payload - only send what n8n API expects
    update_payload = {
        "name": workflow["name"],
        "nodes": workflow["nodes"],
        "connections": workflow["connections"],
        "settings": workflow.get("settings", {}),
    }

    result = api_put(f"/workflows/{WORKFLOW_ID}", update_payload)
    print(f"  Upload successful! Workflow '{result['name']}' updated.")

    # Step 6: Verify by re-fetching
    print("\n" + "=" * 60)
    print("[Step 6] Verifying changes...")
    verify = api_get(f"/workflows/{WORKFLOW_ID}")

    for node in verify["nodes"]:
        if "Creatomate" in node.get("name", "") and "타임라인" in node.get("name", ""):
            code = node["parameters"].get("jsCode", "")

            has_loop = ".loop" in code
            has_playback_rate = "playback_rate" in code
            has_playbackRate_calc = "videoDuration / compositionDuration" in code

            print(f"  '.loop' present:           {has_loop} (should be False)")
            print(f"  'playback_rate' present:   {has_playback_rate} (should be True)")
            print(f"  playbackRate calc present: {has_playbackRate_calc} (should be True)")

            if not has_loop and has_playback_rate and has_playbackRate_calc:
                print("\n  *** VERIFICATION PASSED ***")
            else:
                print("\n  *** VERIFICATION FAILED ***")
                sys.exit(1)

            print("\n" + "=" * 60)
            print("[Final] Updated JavaScript code:")
            print("=" * 60)
            print(code)
            break

    print("\n" + "=" * 60)
    print("Done! Video playback_rate fix applied successfully.")


if __name__ == "__main__":
    main()
