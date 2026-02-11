#!/usr/bin/env python3
"""
Fix Veo3 workflow: 
  1. 시나리오 파싱 node - read from AI scenario generation nodes directly
  2. 영상 5개 분리 (SplitInBatches) - add reset: true
"""

import requests
import json
import sys

API_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
WORKFLOW_ID = "tS2hcoeJ4ar8hivm"

HEADERS = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json",
}

# New code for 시나리오 파싱 node
NEW_PARSING_CODE = """// Parse AI scenario output into 5 separate video items
// ALWAYS read from the scenario generation node, not from the input (which is verification data)

let text = '';

// Try to get scenario from AI 시나리오 재생성 first (retry scenario)
try {
  const retryItems = $('AI 시나리오 재생성').all();
  if (retryItems.length > 0 && retryItems[0].json.content && retryItems[0].json.content.parts) {
    text = retryItems[0].json.content.parts[0].text;
    console.log('Got scenario from AI 시나리오 재생성');
  }
} catch(e) {
  console.log('No retry scenario available');
}

// If no retry, get from AI 시나리오 생성 (first attempt)
if (!text) {
  try {
    const scenarioItems = $('AI 시나리오 생성').all();
    if (scenarioItems.length > 0 && scenarioItems[0].json.content && scenarioItems[0].json.content.parts) {
      text = scenarioItems[0].json.content.parts[0].text;
      console.log('Got scenario from AI 시나리오 생성');
    }
  } catch(e) {
    console.log('Error reading AI 시나리오 생성:', e.message);
  }
}

if (!text) {
  throw new Error('시나리오 텍스트를 찾을 수 없습니다');
}

// Clean markdown code blocks
const cleanText = text.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();

let data;
try {
  data = JSON.parse(cleanText);
} catch (e) {
  const jsonMatch = cleanText.match(/\\{[\\s\\S]*\\}/);
  if (jsonMatch) {
    data = JSON.parse(jsonMatch[0]);
  } else {
    throw new Error('JSON 파싱 실패: ' + cleanText.substring(0, 200));
  }
}

const videos = data.videos || [];
console.log('Parsed videos count:', videos.length);

if (videos.length === 0) {
  throw new Error('파싱된 비디오가 없습니다');
}

// Return 5 separate items for SplitInBatches
const result = videos.slice(0, 5).map((v, idx) => ({
  json: {
    video_num: v.video_num || (idx + 1),
    topic: v.topic || '',
    veo3_prompt: v.veo3_prompt || '',
    subtitle_ko: v.subtitle_ko || '',
    subject: v.subject || '',
    caption: v.caption || '',
    comment: v.comment || '',
    total_videos: Math.min(videos.length, 5)
  }
}));

console.log('Returning items:', result.length);
console.log('First item topic:', result[0]?.json?.topic);
console.log('First item has prompt:', !!result[0]?.json?.veo3_prompt);

return result;"""


def main():
    # Step 1: Fetch the workflow
    print(f"[1] Fetching workflow {WORKFLOW_ID}...")
    resp = requests.get(f"{API_BASE}/workflows/{WORKFLOW_ID}", headers=HEADERS)
    if resp.status_code != 200:
        print(f"ERROR: Failed to fetch workflow. Status: {resp.status_code}")
        print(resp.text[:500])
        sys.exit(1)

    workflow = resp.json()
    print(f"    Workflow name: {workflow.get('name')}")
    print(f"    Total nodes: {len(workflow.get('nodes', []))}")

    nodes = workflow.get("nodes", [])

    # Step 2: Fix 시나리오 파싱 node
    parsing_node = None
    split_node = None

    for node in nodes:
        name = node.get("name", "")
        if name == "시나리오 파싱":
            parsing_node = node
        elif name == "영상 5개 분리":
            split_node = node

    # --- Fix Issue 1: 시나리오 파싱 ---
    if parsing_node:
        print(f"\n[2] Fixing '시나리오 파싱' node...")
        print(f"    Node type: {parsing_node.get('type')}")
        print(f"    TypeVersion: {parsing_node.get('typeVersion')}")

        old_code = parsing_node.get("parameters", {}).get("jsCode", "")
        print(f"    Old code length: {len(old_code)} chars")
        print(f"    Old code preview: {old_code[:150]}...")

        parsing_node["parameters"]["jsCode"] = NEW_PARSING_CODE
        print(f"    New code length: {len(NEW_PARSING_CODE)} chars")
        print("    [OK] 시나리오 파싱 code replaced.")
    else:
        print("\n[!] WARNING: '시나리오 파싱' node NOT FOUND!")
        print("    Available nodes:")
        for n in nodes:
            print(f"      - {n.get('name')}")

    # --- Fix Issue 2: 영상 5개 분리 (SplitInBatches) ---
    if split_node:
        print(f"\n[3] Fixing '영상 5개 분리' (SplitInBatches) node...")
        print(f"    Node type: {split_node.get('type')}")
        type_version = split_node.get("typeVersion", 1)
        print(f"    TypeVersion: {type_version}")
        print(f"    Current parameters: {json.dumps(split_node.get('parameters', {}), ensure_ascii=False)}")

        params = split_node.get("parameters", {})

        # For typeVersion 3, reset is at parameter level
        # For typeVersion 1/2, reset is inside options
        if type_version >= 3:
            params["reset"] = True
            print(f"    Set reset=true at parameter level (typeVersion={type_version})")
        else:
            if "options" not in params:
                params["options"] = {}
            params["options"]["reset"] = True
            print(f"    Set options.reset=true (typeVersion={type_version})")

        split_node["parameters"] = params
        print(f"    Updated parameters: {json.dumps(split_node.get('parameters', {}), ensure_ascii=False)}")
        print("    [OK] SplitInBatches reset option set.")
    else:
        print("\n[!] WARNING: '영상 5개 분리' node NOT FOUND!")
        print("    Available nodes with 'split' or '분리':")
        for n in nodes:
            if "split" in n.get("type", "").lower() or "분리" in n.get("name", ""):
                print(f"      - {n.get('name')} (type: {n.get('type')})")

    # Step 4: Upload the updated workflow
    print(f"\n[4] Uploading updated workflow...")

    # Build the update payload
    update_payload = {
        "nodes": workflow["nodes"],
        "connections": workflow["connections"],
        "settings": workflow.get("settings", {}),
        "name": workflow.get("name"),
    }

    resp = requests.put(
        f"{API_BASE}/workflows/{WORKFLOW_ID}",
        headers=HEADERS,
        json=update_payload,
    )

    if resp.status_code == 200:
        print("    [OK] Workflow updated successfully!")
    else:
        print(f"    ERROR: Failed to update. Status: {resp.status_code}")
        print(f"    Response: {resp.text[:500]}")
        sys.exit(1)

    # Step 5: Verify by re-fetching
    print(f"\n[5] Verifying changes...")
    resp = requests.get(f"{API_BASE}/workflows/{WORKFLOW_ID}", headers=HEADERS)
    if resp.status_code != 200:
        print(f"    ERROR: Failed to verify. Status: {resp.status_code}")
        sys.exit(1)

    updated = resp.json()
    for node in updated.get("nodes", []):
        if node.get("name") == "시나리오 파싱":
            code = node.get("parameters", {}).get("jsCode", "")
            print(f"\n{'='*60}")
            print(f"시나리오 파싱 - Updated jsCode")
            print(f"{'='*60}")
            print(code)
            print(f"{'='*60}")
            print(f"Code length: {len(code)}")

            # Verify key patterns
            if "$('AI 시나리오 재생성')" in code:
                print("[PASS] Contains $('AI 시나리오 재생성') reference")
            else:
                print("[FAIL] Missing $('AI 시나리오 재생성') reference")

            if "$('AI 시나리오 생성')" in code:
                print("[PASS] Contains $('AI 시나리오 생성') reference")
            else:
                print("[FAIL] Missing $('AI 시나리오 생성') reference")

        if node.get("name") == "영상 5개 분리":
            params = node.get("parameters", {})
            print(f"\n{'='*60}")
            print(f"영상 5개 분리 - Updated parameters")
            print(f"{'='*60}")
            print(json.dumps(params, indent=2, ensure_ascii=False))

            # Check reset is set
            reset_found = params.get("reset") or params.get("options", {}).get("reset")
            if reset_found:
                print("[PASS] reset=true is set")
            else:
                print("[FAIL] reset option NOT found!")

    print(f"\n{'='*60}")
    print("[DONE] All fixes applied successfully.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
