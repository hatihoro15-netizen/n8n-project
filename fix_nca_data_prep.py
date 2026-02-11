#!/usr/bin/env python3
"""
Fix the "NCA 데이터 준비" node in the v3 workflow (9YOHS8N1URWlzGWj).
Replaces the jsCode to correctly parse the Aggregate node output.
"""

import json
import requests

API_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

HEADERS = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json",
}

# The n8n PUT API requires exactly these fields
REQUIRED_FIELDS = ["name", "nodes", "connections", "settings"]

NEW_JS_CODE = r'''// NCA Toolkit 데이터 준비
// Aggregate 노드에서 수집된 데이터를 NCA Toolkit API 형식으로 변환

const firstItem = $input.first().json;
const dataArray = firstItem.data || [];

console.log('Aggregate data items:', dataArray.length);

// 분류: 나레이션(audio+timestamps), 비디오(video+state), BGM(audio+metadata)
const narrations = [];
const videos = [];
let bgmUrl = '';

for (const item of dataArray) {
    if (item.video && item.video.url) {
        // 비디오 아이템
        videos.push(item.video.url);
    } else if (item.audio && item.audio.url) {
        if (item.metadata && item.metadata.duration) {
            // BGM (metadata.duration이 있는 오디오)
            bgmUrl = item.audio.url;
            console.log('BGM found:', bgmUrl);
        } else {
            // 나레이션 오디오
            const fileSize = item.audio.file_size || 0;
            const estimatedDuration = Math.round((fileSize * 8 / 128000) * 100) / 100;
            narrations.push({
                url: item.audio.url,
                file_size: fileSize,
                duration: Math.max(estimatedDuration, 3), // 최소 3초
            });
        }
    }
}

console.log('Narrations:', narrations.length);
console.log('Videos:', videos.length);
console.log('BGM:', bgmUrl ? 'YES' : 'NO');

// 자막 텍스트 가져오기 (5파트 분리 노드에서)
let subtitleTexts = [];
try {
    const partItems = $('5파트 분리').all();
    subtitleTexts = partItems.map(item => {
        const j = item.json;
        return j.subtitle || j.text || j.narration || j.narration_text || j.content || '';
    });
    console.log('Subtitles from 5파트 분리:', subtitleTexts.length);
} catch (e) {
    console.log('Could not get subtitles from 5파트 분리:', e.message);
}

// 5개 파트 조합
const parts = [];
const partCount = Math.min(narrations.length, videos.length, 5);

for (let i = 0; i < 5; i++) {
    parts.push({
        video_url: videos[i] || '',
        audio_url: narrations[i] ? narrations[i].url : '',
        subtitle: subtitleTexts[i] || '',
        duration: narrations[i] ? narrations[i].duration : 5,
    });
}

// 자막 SRT 생성
let srtContent = '';
let currentTime = 0;
parts.forEach((part, idx) => {
    if (part.subtitle) {
        const dur = part.duration || 5;
        const startTime = formatSrtTime(currentTime);
        const endTime = formatSrtTime(currentTime + dur);
        srtContent += `${idx + 1}\n${startTime} --> ${endTime}\n${part.subtitle}\n\n`;
        currentTime += dur;
    }
});

function formatSrtTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 1000);
    return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')},${String(ms).padStart(3,'0')}`;
}

const totalDuration = parts.reduce((sum, p) => sum + (p.duration || 5), 0);

console.log('Parts prepared:', parts.length);
console.log('Total duration:', totalDuration);
console.log('Video URLs:', parts.map(p => p.video_url ? 'OK' : 'MISSING'));
console.log('Audio URLs:', parts.map(p => p.audio_url ? 'OK' : 'MISSING'));

return [{
    json: {
        parts: parts,
        video_urls: parts.map(p => p.video_url).filter(u => u),
        bgm_url: bgmUrl,
        ending_card_url: '',
        srt_content: srtContent,
        total_duration: totalDuration,
    }
}];'''


def main():
    # Step 1: Fetch workflow
    print(f"[1/5] Fetching workflow {WORKFLOW_ID}...")
    resp = requests.get(f"{API_BASE}/workflows/{WORKFLOW_ID}", headers=HEADERS)
    resp.raise_for_status()
    workflow = resp.json()
    print(f"  Workflow name: {workflow.get('name', 'N/A')}")
    print(f"  Total nodes: {len(workflow.get('nodes', []))}")

    # Step 2: Find "NCA 데이터 준비" node
    print(f"\n[2/5] Searching for 'NCA 데이터 준비' node...")
    target_node = None
    target_idx = None
    for idx, node in enumerate(workflow["nodes"]):
        if node.get("name") == "NCA 데이터 준비":
            target_node = node
            target_idx = idx
            break

    if target_node is None:
        print("  ERROR: Node 'NCA 데이터 준비' not found!")
        print("  Available Code nodes:")
        for node in workflow["nodes"]:
            if node.get("type") == "n8n-nodes-base.code":
                print(f"    - {node['name']}")
        return

    print(f"  Found node at index {target_idx}")
    print(f"  Node type: {target_node.get('type')}")

    # Show old code snippet
    old_code = target_node.get("parameters", {}).get("jsCode", "")
    print(f"  Old jsCode length: {len(old_code)} chars")
    if old_code:
        first_lines = old_code.split("\n")[:3]
        for line in first_lines:
            print(f"    | {line}")
        print(f"    | ... ({len(old_code.splitlines())} lines total)")

    # Step 3: Replace jsCode
    print(f"\n[3/5] Replacing jsCode with new code...")
    workflow["nodes"][target_idx]["parameters"]["jsCode"] = NEW_JS_CODE
    print(f"  New jsCode length: {len(NEW_JS_CODE)} chars")

    # Step 4: Upload workflow (only required fields)
    print(f"\n[4/5] Uploading updated workflow...")
    update_payload = {k: workflow[k] for k in REQUIRED_FIELDS if k in workflow}
    update_resp = requests.put(
        f"{API_BASE}/workflows/{WORKFLOW_ID}",
        headers=HEADERS,
        json=update_payload,
    )
    if update_resp.status_code != 200:
        print(f"  ERROR: {update_resp.status_code} - {update_resp.text[:500]}")
        return
    result = update_resp.json()
    print(f"  Upload successful!")
    print(f"  Updated at: {result.get('updatedAt', 'N/A')}")

    # Step 5: Verify
    print(f"\n[5/5] Verifying update...")
    verify_resp = requests.get(f"{API_BASE}/workflows/{WORKFLOW_ID}", headers=HEADERS)
    verify_resp.raise_for_status()
    verified = verify_resp.json()

    verified_node = None
    for node in verified["nodes"]:
        if node.get("name") == "NCA 데이터 준비":
            verified_node = node
            break

    if verified_node is None:
        print("  ERROR: Node not found after update!")
        return

    verified_code = verified_node.get("parameters", {}).get("jsCode", "")
    if "Aggregate data items" in verified_code and "formatSrtTime" in verified_code:
        print("  Verification PASSED!")
        print(f"  Code length: {len(verified_code)} chars")
        print(f"  Key markers found: 'Aggregate data items', 'formatSrtTime'")
    else:
        print("  WARNING: Verification may have failed - key markers not found in code")
        print(f"  Code starts with: {verified_code[:100]}")

    print("\nDone! 'NCA 데이터 준비' node has been updated successfully.")


if __name__ == "__main__":
    main()
