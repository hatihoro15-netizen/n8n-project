#!/usr/bin/env python3
"""
Replace Creatomate nodes with NCA Toolkit nodes in v3 workflow (9YOHS8N1URWlzGWj).

NCA Toolkit:
- URL: http://76.13.182.180:8080
- API Key: nca-sagong-2026
- Concatenate: POST /v1/video/concatenate
- Caption: POST /v1/video/caption
- FFmpeg Compose: POST /v1/ffmpeg/compose
- Auth header: x-api-key
"""

import requests
import json
import sys
import copy

# ============================================================
# Configuration
# ============================================================
N8N_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

NCA_URL = "http://76.13.182.180:8080"
NCA_API_KEY = "nca-sagong-2026"

HEADERS = {
    "X-N8N-API-KEY": N8N_API_KEY,
    "Content-Type": "application/json",
}


def fetch_workflow():
    """Fetch the workflow from n8n API."""
    url = f"{N8N_BASE}/workflows/{WORKFLOW_ID}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def print_workflow_structure(wf):
    """Print ALL nodes and connections in detail."""
    nodes = wf.get("nodes", [])
    connections = wf.get("connections", {})

    print("=" * 100)
    print(f"WORKFLOW: {wf.get('name', 'N/A')} (ID: {wf.get('id', 'N/A')})")
    print(f"Total nodes: {len(nodes)}")
    print("=" * 100)

    # Print all nodes
    print("\n" + "=" * 100)
    print("ALL NODES")
    print("=" * 100)
    for i, node in enumerate(nodes):
        print(f"\n--- Node {i+1} ---")
        print(f"  Name: {node.get('name', 'N/A')}")
        print(f"  Type: {node.get('type', 'N/A')}")
        print(f"  ID: {node.get('id', 'N/A')}")
        print(f"  Position: {node.get('position', 'N/A')}")
        print(f"  Disabled: {node.get('disabled', False)}")

        params = node.get("parameters", {})
        if params:
            print(f"  Parameters:")
            for key, val in params.items():
                val_str = json.dumps(val, ensure_ascii=False) if isinstance(val, (dict, list)) else str(val)
                # Truncate very long values for readability
                if len(val_str) > 500:
                    print(f"    {key}: {val_str[:500]}... [TRUNCATED, total {len(val_str)} chars]")
                else:
                    print(f"    {key}: {val_str}")

    # Print all connections
    print("\n" + "=" * 100)
    print("ALL CONNECTIONS")
    print("=" * 100)
    for src_name, conn_types in connections.items():
        for conn_type, outputs in conn_types.items():
            for output_idx, targets in enumerate(outputs):
                for target in targets:
                    print(f"  {src_name} [{conn_type}][{output_idx}] --> {target.get('node', 'N/A')} [index={target.get('index', 0)}, type={target.get('type', 'N/A')}]")

    # Print Creatomate-related nodes in full detail
    print("\n" + "=" * 100)
    print("CREATOMATE-RELATED NODES (FULL DETAIL)")
    print("=" * 100)
    creatomate_keywords = ["creatomate", "크리에이토", "렌더", "타임라인", "render"]
    for node in nodes:
        name_lower = node.get("name", "").lower()
        params_str = json.dumps(node.get("parameters", {}), ensure_ascii=False).lower()
        if any(kw in name_lower for kw in creatomate_keywords) or "creatomate" in params_str:
            print(f"\n{'='*60}")
            print(f"NODE: {node.get('name')}")
            print(f"TYPE: {node.get('type')}")
            print(f"ID: {node.get('id')}")
            print(f"FULL PARAMETERS:")
            print(json.dumps(node.get("parameters", {}), indent=2, ensure_ascii=False))
            print(f"{'='*60}")

    return nodes, connections


def find_creatomate_nodes(nodes):
    """Find all Creatomate-related nodes."""
    creatomate_nodes = []
    creatomate_keywords = ["creatomate", "크리에이토", "렌더"]
    for node in nodes:
        name_lower = node.get("name", "").lower()
        params_str = json.dumps(node.get("parameters", {}), ensure_ascii=False).lower()
        if any(kw in name_lower for kw in creatomate_keywords) or "creatomate" in params_str:
            creatomate_nodes.append(node)
    return creatomate_nodes


def find_node_by_name(nodes, name):
    """Find a node by its exact name."""
    for node in nodes:
        if node.get("name") == name:
            return node
    return None


def find_connections_to(connections, target_name):
    """Find all nodes that connect TO the given node."""
    sources = []
    for src_name, conn_types in connections.items():
        for conn_type, outputs in conn_types.items():
            for output_idx, targets in enumerate(outputs):
                for target in targets:
                    if target.get("node") == target_name:
                        sources.append({
                            "source": src_name,
                            "type": conn_type,
                            "output_index": output_idx,
                            "target_index": target.get("index", 0),
                        })
    return sources


def find_connections_from(connections, source_name):
    """Find all nodes that the given node connects TO."""
    targets = []
    if source_name in connections:
        for conn_type, outputs in connections[source_name].items():
            for output_idx, target_list in enumerate(outputs):
                for target in target_list:
                    targets.append({
                        "target": target.get("node"),
                        "type": conn_type,
                        "output_index": output_idx,
                        "target_index": target.get("index", 0),
                    })
    return targets


def build_nca_replacement_nodes(creatomate_nodes, nodes, connections):
    """
    Identify the specific Creatomate nodes: timeline, render, and wait/check nodes.
    """
    timeline_node = None
    render_node = None
    wait_nodes = []

    for node in creatomate_nodes:
        name = node.get("name", "")
        if "타임라인" in name or "timeline" in name.lower():
            timeline_node = node
        elif "렌더" in name or "render" in name.lower():
            if "대기" in name or "wait" in name.lower() or "체크" in name or "check" in name.lower() or "완료" in name:
                wait_nodes.append(node)
            else:
                render_node = node

    # If we couldn't identify them by name, try by type
    if not timeline_node:
        for node in creatomate_nodes:
            if node.get("type") == "n8n-nodes-base.code":
                timeline_node = node
                break

    if not render_node:
        for node in creatomate_nodes:
            if node.get("type") == "n8n-nodes-base.httpRequest" and node != timeline_node:
                render_node = node
                break

    # Check for remaining unclassified Creatomate nodes
    classified = set()
    if timeline_node:
        classified.add(timeline_node.get("name"))
    if render_node:
        classified.add(render_node.get("name"))
    for wn in wait_nodes:
        classified.add(wn.get("name"))

    unclassified = [n for n in creatomate_nodes if n.get("name") not in classified]
    if unclassified:
        print(f"\nWARNING: Unclassified Creatomate nodes:")
        for n in unclassified:
            print(f"  - {n.get('name')} ({n.get('type')})")
            # Add unclassified nodes as wait nodes for removal
            wait_nodes.append(n)

    print("\n" + "=" * 100)
    print("IDENTIFIED CREATOMATE NODES:")
    print(f"  Timeline/Code node: {timeline_node.get('name') if timeline_node else 'NOT FOUND'}")
    print(f"  Render/HTTP node: {render_node.get('name') if render_node else 'NOT FOUND'}")
    print(f"  Wait/Check nodes: {[n.get('name') for n in wait_nodes]}")
    print("=" * 100)

    return timeline_node, render_node, wait_nodes


def create_nca_nodes(timeline_node, render_node, wait_nodes, nodes, connections):
    """
    Create NCA Toolkit replacement nodes and determine connection updates.
    """
    timeline_name = timeline_node.get("name") if timeline_node else None
    render_name = render_node.get("name") if render_node else None

    # Find the last Creatomate node in the chain
    last_creatomate_name = render_name
    if wait_nodes:
        # Find which wait node is last by checking connections
        last_creatomate_name = wait_nodes[-1].get("name")

    # Find the full Creatomate chain to determine the actual last node
    all_creatomate_names = set()
    if timeline_name:
        all_creatomate_names.add(timeline_name)
    if render_name:
        all_creatomate_names.add(render_name)
    for wn in wait_nodes:
        all_creatomate_names.add(wn.get("name"))

    # Find the actual last node: one whose outgoing targets are NOT in the Creatomate set
    for name in all_creatomate_names:
        outgoing = find_connections_from(connections, name)
        has_external_target = any(t["target"] not in all_creatomate_names for t in outgoing)
        if has_external_target or not outgoing:
            last_creatomate_name = name

    # Find incoming connections to the first Creatomate node (timeline)
    incoming = find_connections_to(connections, timeline_name) if timeline_name else []
    # Find outgoing connections from the last Creatomate node
    outgoing = find_connections_from(connections, last_creatomate_name) if last_creatomate_name else []
    # Filter outgoing to only external targets
    outgoing = [o for o in outgoing if o["target"] not in all_creatomate_names]

    print(f"\nFirst Creatomate node: {timeline_name}")
    print(f"Last Creatomate node: {last_creatomate_name}")
    print(f"Incoming connections to Creatomate chain: {incoming}")
    print(f"Outgoing connections from Creatomate chain: {outgoing}")

    # Get position of the timeline node for placing new nodes nearby
    base_pos = timeline_node.get("position", [0, 0]) if timeline_node else [2000, 400]
    base_x = base_pos[0] if isinstance(base_pos, list) else base_pos.get("x", 2000)
    base_y = base_pos[1] if isinstance(base_pos, list) else base_pos.get("y", 400)

    # ============================================================
    # Build NCA Toolkit nodes
    # ============================================================

    # Node 1: NCA 데이터 준비 (Code)
    nca_prepare_node = {
        "parameters": {
            "jsCode": """// NCA Toolkit 데이터 준비
// 이전 노드들에서 수집된 5개 파트의 데이터를 NCA Toolkit API 형식으로 변환

const items = $input.all();
const firstItem = items[0]?.json || {};
console.log('Input data keys:', Object.keys(firstItem));
console.log('Input data preview:', JSON.stringify(firstItem).substring(0, 2000));

let parts = [];
let bgmUrl = '';
let endingCardUrl = '';

// 패턴 1: parts 배열
if (firstItem.parts && Array.isArray(firstItem.parts)) {
    parts = firstItem.parts.map((p, i) => ({
        video_url: p.video_url || p.videoUrl || p.video || '',
        audio_url: p.audio_url || p.audioUrl || p.narration || p.tts || p.tts_url || '',
        subtitle: p.subtitle || p.text || p.narration_text || '',
        duration: p.duration || p.audio_duration || 0,
    }));
}
// 패턴 2: part1_video, part2_video... 
else if (firstItem.part1_video || firstItem.video_1) {
    for (let i = 1; i <= 5; i++) {
        parts.push({
            video_url: firstItem[`part${i}_video`] || firstItem[`video_${i}`] || '',
            audio_url: firstItem[`part${i}_audio`] || firstItem[`audio_${i}`] || firstItem[`part${i}_tts`] || firstItem[`tts_${i}`] || '',
            subtitle: firstItem[`part${i}_text`] || firstItem[`text_${i}`] || firstItem[`part${i}_subtitle`] || '',
            duration: firstItem[`part${i}_duration`] || firstItem[`duration_${i}`] || 0,
        });
    }
}
// 패턴 3: 여러 아이템
else if (items.length >= 5) {
    for (let i = 0; i < Math.min(items.length, 5); i++) {
        const item = items[i].json;
        parts.push({
            video_url: item.video_url || item.videoUrl || item.video || item.output_url || '',
            audio_url: item.audio_url || item.audioUrl || item.narration || item.tts || item.tts_url || '',
            subtitle: item.subtitle || item.text || item.narration_text || '',
            duration: item.duration || item.audio_duration || 0,
        });
    }
}
// 패턴 4: 원본 Creatomate 타임라인 형식 호환
else {
    // elements나 다른 형식 처리
    console.log('Attempting to parse unknown format...');
    console.log('Full data:', JSON.stringify(firstItem));
    for (let i = 1; i <= 5; i++) {
        const videoKey = Object.keys(firstItem).find(k => k.includes(`${i}`) && (k.includes('video') || k.includes('image') || k.includes('kie')));
        const audioKey = Object.keys(firstItem).find(k => k.includes(`${i}`) && (k.includes('audio') || k.includes('tts') || k.includes('narr')));
        const textKey = Object.keys(firstItem).find(k => k.includes(`${i}`) && (k.includes('text') || k.includes('subtitle') || k.includes('narr')));
        parts.push({
            video_url: videoKey ? firstItem[videoKey] : '',
            audio_url: audioKey ? firstItem[audioKey] : '',
            subtitle: textKey ? firstItem[textKey] : '',
            duration: 0,
        });
    }
}

bgmUrl = firstItem.bgm_url || firstItem.bgm || firstItem.bgmUrl || firstItem.bgm_audio || '';
endingCardUrl = firstItem.ending_card || firstItem.endingCard || firstItem.ending_video || firstItem.ending_card_url || '';

// 자막 SRT 생성
let srtContent = '';
let currentTime = 0;
parts.forEach((part, idx) => {
    if (part.subtitle) {
        const dur = part.duration || 5; // 기본 5초
        const startTime = formatSrtTime(currentTime);
        const endTime = formatSrtTime(currentTime + dur);
        srtContent += `${idx + 1}\\n${startTime} --> ${endTime}\\n${part.subtitle}\\n\\n`;
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

console.log(`Prepared ${parts.length} parts`);
console.log(`BGM URL: ${bgmUrl}`);
console.log(`Ending card URL: ${endingCardUrl}`);

return [{
    json: {
        parts: parts,
        video_urls: parts.map(p => p.video_url).filter(u => u),
        bgm_url: bgmUrl,
        ending_card_url: endingCardUrl,
        srt_content: srtContent,
        total_duration: parts.reduce((sum, p) => sum + (p.duration || 5), 0),
    }
}];
"""
        },
        "name": "NCA 데이터 준비",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [base_x, base_y],
    }

    # Node 2: NCA 파트별 합성 (Code - calls NCA API for each part)
    nca_compose_parts_node = {
        "parameters": {
            "jsCode": """// NCA Toolkit: 파트별 영상+나레이션 합성
// 각 파트의 비디오와 나레이션 오디오를 합성하여 개별 클립 생성

const data = $input.first().json;
const parts = data.parts || [];
const NCA_URL = "http://76.13.182.180:8080";
const NCA_API_KEY = "nca-sagong-2026";

const composedVideos = [];

for (let i = 0; i < parts.length; i++) {
    const part = parts[i];
    if (!part.video_url || !part.audio_url) {
        console.log(`Part ${i+1}: Missing video or audio URL, using video as-is`);
        composedVideos.push({ part_index: i+1, url: part.video_url || '', error: 'missing_input' });
        continue;
    }

    console.log(`Processing Part ${i+1}...`);
    console.log(`  Video: ${part.video_url}`);
    console.log(`  Audio: ${part.audio_url}`);

    try {
        // FFmpeg: 비디오를 오디오 길이만큼 반복 + 1080x1920 스케일
        const ffmpegCmd = `-stream_loop -1 -i "${part.video_url}" -i "${part.audio_url}" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -movflags +faststart output_part${i+1}.mp4`;

        const response = await $http.request({
            method: 'POST',
            url: `${NCA_URL}/v1/ffmpeg/compose`,
            headers: {
                'x-api-key': NCA_API_KEY,
                'Content-Type': 'application/json',
            },
            body: {
                ffmpeg_command: ffmpegCmd,
            },
            json: true,
        });

        console.log(`Part ${i+1} response:`, JSON.stringify(response).substring(0, 500));
        
        const outputUrl = response.output_url || response.url || response.result_url || response.video_url || '';
        const taskId = response.task_id || response.id || '';
        
        composedVideos.push({
            part_index: i + 1,
            url: outputUrl,
            task_id: taskId,
            raw_response: response,
        });
    } catch (error) {
        console.error(`Part ${i+1} error:`, error.message);
        composedVideos.push({
            part_index: i + 1,
            url: part.video_url, // fallback to original video
            error: error.message,
        });
    }
}

return [{
    json: {
        composed_videos: composedVideos,
        video_urls: composedVideos.map(v => v.url).filter(u => u),
        bgm_url: data.bgm_url,
        ending_card_url: data.ending_card_url,
        srt_content: data.srt_content,
        total_duration: data.total_duration,
        parts: data.parts,
    }
}];
"""
        },
        "name": "NCA 파트별 합성",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [base_x + 300, base_y],
    }

    # Node 3: NCA 영상 합치기 (HTTP Request - concatenate)
    nca_concatenate_node = {
        "parameters": {
            "method": "POST",
            "url": f"{NCA_URL}/v1/video/concatenate",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "x-api-key", "value": NCA_API_KEY},
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": '={{ JSON.stringify({ "video_urls": $json.video_urls.concat($json.ending_card_url ? [$json.ending_card_url] : []) }) }}',
            "options": {
                "timeout": 300000,
            },
        },
        "name": "NCA 영상 합치기",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [base_x + 600, base_y],
    }

    # Node 4: NCA 합치기 결과 처리 (Code)
    nca_concat_result_node = {
        "parameters": {
            "jsCode": """// NCA 합치기 결과 처리 및 BGM 추가 준비
const prevData = $('NCA 파트별 합성').first().json;
const concatResult = $input.first().json;

console.log('Concatenation result:', JSON.stringify(concatResult).substring(0, 500));

const concatenatedUrl = concatResult.output_url || concatResult.url || concatResult.result_url || concatResult.video_url || '';
const bgmUrl = prevData.bgm_url || '';

let output = {
    concatenated_url: concatenatedUrl,
    bgm_url: bgmUrl,
    srt_content: prevData.srt_content,
    total_duration: prevData.total_duration,
    parts: prevData.parts,
};

// BGM FFmpeg 명령 준비
if (concatenatedUrl && bgmUrl) {
    output.bgm_ffmpeg_command = `-i "${concatenatedUrl}" -i "${bgmUrl}" -filter_complex "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]" -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -movflags +faststart output_with_bgm.mp4`;
    output.has_bgm = true;
} else {
    output.bgm_ffmpeg_command = null;
    output.has_bgm = false;
    output.final_video_url = concatenatedUrl;
}

return [{ json: output }];
"""
        },
        "name": "NCA 합치기 결과 처리",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [base_x + 900, base_y],
    }

    # Node 5: NCA BGM 분기 (IF)
    nca_bgm_if_node = {
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "typeValidation": "strict",
                },
                "conditions": [
                    {
                        "id": "bgm-check",
                        "leftValue": "={{ $json.has_bgm }}",
                        "rightValue": True,
                        "operator": {
                            "type": "boolean",
                            "operation": "true",
                        },
                    }
                ],
                "combinator": "and",
            },
        },
        "name": "NCA BGM 분기",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [base_x + 1200, base_y],
    }

    # Node 6: NCA BGM 추가 (HTTP Request)
    nca_bgm_node = {
        "parameters": {
            "method": "POST",
            "url": f"{NCA_URL}/v1/ffmpeg/compose",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "x-api-key", "value": NCA_API_KEY},
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": '={{ JSON.stringify({ "ffmpeg_command": $json.bgm_ffmpeg_command }) }}',
            "options": {
                "timeout": 300000,
            },
        },
        "name": "NCA BGM 추가",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [base_x + 1500, base_y - 150],
    }

    # Node 7: NCA BGM 결과 처리 (Code)
    nca_bgm_result_node = {
        "parameters": {
            "jsCode": """// BGM 추가 결과 처리
const prevData = $('NCA 합치기 결과 처리').first().json;
const bgmResult = $input.first().json;

console.log('BGM result:', JSON.stringify(bgmResult).substring(0, 500));

const videoWithBgm = bgmResult.output_url || bgmResult.url || bgmResult.result_url || bgmResult.video_url || '';

return [{
    json: {
        video_url: videoWithBgm || prevData.concatenated_url,
        srt_content: prevData.srt_content,
        total_duration: prevData.total_duration,
        parts: prevData.parts,
    }
}];
"""
        },
        "name": "NCA BGM 결과 처리",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [base_x + 1800, base_y - 150],
    }

    # Node 8: NCA BGM 없음 처리 (Code)
    nca_no_bgm_node = {
        "parameters": {
            "jsCode": """// BGM 없이 진행
const prevData = $('NCA 합치기 결과 처리').first().json;
return [{
    json: {
        video_url: prevData.concatenated_url || prevData.final_video_url,
        srt_content: prevData.srt_content,
        total_duration: prevData.total_duration,
        parts: prevData.parts,
    }
}];
"""
        },
        "name": "NCA BGM 없음 처리",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [base_x + 1800, base_y + 150],
    }

    # Node 9: NCA 자막 준비 (Code)
    nca_caption_prepare_node = {
        "parameters": {
            "jsCode": """// NCA 자막 추가 준비
let videoUrl = '';
let srtContent = '';
let parts = [];

try {
    const bgmData = $('NCA BGM 결과 처리').first().json;
    videoUrl = bgmData.video_url;
    srtContent = bgmData.srt_content;
    parts = bgmData.parts;
} catch (e) {
    try {
        const noBgmData = $('NCA BGM 없음 처리').first().json;
        videoUrl = noBgmData.video_url;
        srtContent = noBgmData.srt_content;
        parts = noBgmData.parts;
    } catch (e2) {
        const concatData = $('NCA 합치기 결과 처리').first().json;
        videoUrl = concatData.concatenated_url || concatData.final_video_url;
        srtContent = concatData.srt_content;
        parts = concatData.parts;
    }
}

console.log('Video for captioning:', videoUrl);
console.log('SRT content:', srtContent ? srtContent.substring(0, 200) : 'NONE');

return [{
    json: {
        video_url: videoUrl,
        srt_content: srtContent,
        parts: parts,
        caption_options: {
            font: "NanumGothicBold",
            font_size: 40,
            font_color: "#FFFFFF",
            stroke_color: "#000000",
            stroke_width: 2,
            position: "bottom",
            margin_bottom: 80,
        },
    }
}];
"""
        },
        "name": "NCA 자막 준비",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [base_x + 2100, base_y],
    }

    # Node 10: NCA 자막 추가 (HTTP Request)
    nca_caption_node = {
        "parameters": {
            "method": "POST",
            "url": f"{NCA_URL}/v1/video/caption",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "x-api-key", "value": NCA_API_KEY},
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": """={{ JSON.stringify({
  "video_url": $json.video_url,
  "srt_content": $json.srt_content,
  "font": $json.caption_options.font,
  "font_size": $json.caption_options.font_size,
  "font_color": $json.caption_options.font_color,
  "stroke_color": $json.caption_options.stroke_color,
  "stroke_width": $json.caption_options.stroke_width,
  "position": $json.caption_options.position
}) }}""",
            "options": {
                "timeout": 300000,
            },
        },
        "name": "NCA 자막 추가",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [base_x + 2400, base_y],
    }

    # Node 11: NCA 최종 결과 (Code)
    nca_final_node = {
        "parameters": {
            "jsCode": """// NCA Toolkit 최종 결과 처리
const captionResult = $input.first().json;
const prevData = $('NCA 자막 준비').first().json;

console.log('Caption result:', JSON.stringify(captionResult).substring(0, 500));

const finalUrl = captionResult.output_url || captionResult.url || captionResult.result_url || captionResult.video_url || prevData.video_url;

return [{
    json: {
        final_video_url: finalUrl,
        // Creatomate 호환 필드 (다음 노드들이 이 필드를 참조할 수 있음)
        url: finalUrl,
        output_url: finalUrl,
        status: 'succeeded',
    }
}];
"""
        },
        "name": "NCA 최종 결과",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [base_x + 2700, base_y],
    }

    new_nodes = [
        nca_prepare_node,
        nca_compose_parts_node,
        nca_concatenate_node,
        nca_concat_result_node,
        nca_bgm_if_node,
        nca_bgm_node,
        nca_bgm_result_node,
        nca_no_bgm_node,
        nca_caption_prepare_node,
        nca_caption_node,
        nca_final_node,
    ]

    # Define connections between NCA nodes
    new_connections = {
        "NCA 데이터 준비": {
            "main": [[{"node": "NCA 파트별 합성", "type": "main", "index": 0}]]
        },
        "NCA 파트별 합성": {
            "main": [[{"node": "NCA 영상 합치기", "type": "main", "index": 0}]]
        },
        "NCA 영상 합치기": {
            "main": [[{"node": "NCA 합치기 결과 처리", "type": "main", "index": 0}]]
        },
        "NCA 합치기 결과 처리": {
            "main": [[{"node": "NCA BGM 분기", "type": "main", "index": 0}]]
        },
        "NCA BGM 분기": {
            "main": [
                [{"node": "NCA BGM 추가", "type": "main", "index": 0}],
                [{"node": "NCA BGM 없음 처리", "type": "main", "index": 0}],
            ]
        },
        "NCA BGM 추가": {
            "main": [[{"node": "NCA BGM 결과 처리", "type": "main", "index": 0}]]
        },
        "NCA BGM 결과 처리": {
            "main": [[{"node": "NCA 자막 준비", "type": "main", "index": 0}]]
        },
        "NCA BGM 없음 처리": {
            "main": [[{"node": "NCA 자막 준비", "type": "main", "index": 0}]]
        },
        "NCA 자막 준비": {
            "main": [[{"node": "NCA 자막 추가", "type": "main", "index": 0}]]
        },
        "NCA 자막 추가": {
            "main": [[{"node": "NCA 최종 결과", "type": "main", "index": 0}]]
        },
    }

    return new_nodes, new_connections, incoming, outgoing


def apply_replacement(wf, timeline_node, render_node, wait_nodes, new_nodes, new_connections, incoming, outgoing):
    """Apply the replacement to the workflow."""
    wf = copy.deepcopy(wf)
    nodes = wf["nodes"]
    connections = wf["connections"]

    # Collect names of nodes to remove
    remove_names = set()
    if timeline_node:
        remove_names.add(timeline_node["name"])
    if render_node:
        remove_names.add(render_node["name"])
    for wn in wait_nodes:
        remove_names.add(wn["name"])

    print(f"\nRemoving nodes: {remove_names}")

    # Remove old Creatomate nodes
    nodes = [n for n in nodes if n.get("name") not in remove_names]

    # Remove connections from/to removed nodes
    for name in remove_names:
        connections.pop(name, None)
    for src_name in list(connections.keys()):
        for conn_type in list(connections[src_name].keys()):
            for output_idx in range(len(connections[src_name][conn_type])):
                connections[src_name][conn_type][output_idx] = [
                    t for t in connections[src_name][conn_type][output_idx]
                    if t.get("node") not in remove_names
                ]

    # Add new NCA nodes
    for node in new_nodes:
        nodes.append(node)

    # Add new NCA connections
    connections.update(new_connections)

    # Reconnect incoming connections to "NCA 데이터 준비"
    first_nca_node = "NCA 데이터 준비"
    for inc in incoming:
        src = inc["source"]
        # Overwrite the source node's connections to point to the first NCA node
        connections[src] = {
            "main": [[{"node": first_nca_node, "type": "main", "index": 0}]]
        }

    # Reconnect outgoing connections from "NCA 최종 결과"
    last_nca_node = "NCA 최종 결과"
    if outgoing:
        connections[last_nca_node] = {
            "main": [[]]
        }
        for out in outgoing:
            connections[last_nca_node]["main"][0].append({
                "node": out["target"],
                "type": "main",
                "index": out.get("target_index", 0),
            })

    wf["nodes"] = nodes
    wf["connections"] = connections

    return wf


def update_workflow(wf):
    """Update the workflow via n8n API."""
    url = f"{N8N_BASE}/workflows/{WORKFLOW_ID}"
    # n8n API only accepts specific fields in PUT body
    update_payload = {
        'name': wf.get('name'),
        'nodes': wf.get('nodes'),
        'connections': wf.get('connections'),
        'settings': wf.get('settings', {}),
    }
    resp = requests.put(url, headers=HEADERS, json=update_payload)
    resp.raise_for_status()
    return resp.json()


def main():
    # ============================================================
    # PHASE 1: Fetch and analyze
    # ============================================================
    print("Fetching workflow...")
    wf = fetch_workflow()

    print("\nPrinting full workflow structure...\n")
    nodes, connections = print_workflow_structure(wf)

    # Save raw workflow for reference
    with open("/Users/gimdongseog/n8n-project/v3_before_nca_replacement.json", "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    print("\nSaved original workflow to v3_before_nca_replacement.json")

    # ============================================================
    # PHASE 2: Identify Creatomate nodes
    # ============================================================
    creatomate_nodes = find_creatomate_nodes(nodes)
    print(f"\nFound {len(creatomate_nodes)} Creatomate-related nodes:")
    for n in creatomate_nodes:
        print(f"  - {n.get('name')} ({n.get('type')})")

    if not creatomate_nodes:
        print("\nERROR: No Creatomate-related nodes found!")
        print("Listing all node names for manual identification:")
        for n in nodes:
            print(f"  - {n.get('name')} ({n.get('type')})")
        sys.exit(1)

    timeline_node, render_node, wait_nodes = build_nca_replacement_nodes(
        creatomate_nodes, nodes, connections
    )

    # ============================================================
    # PHASE 2.5: Print detailed analysis
    # ============================================================
    print("\n" + "=" * 100)
    print("CONNECTION CHAIN ANALYSIS")
    print("=" * 100)

    all_creatomate = []
    if timeline_node:
        all_creatomate.append(timeline_node)
    if render_node:
        all_creatomate.append(render_node)
    all_creatomate.extend(wait_nodes)

    for node in all_creatomate:
        nn = node.get("name")
        print(f"\nNodes connecting TO '{nn}':")
        for inc in find_connections_to(connections, nn):
            print(f"  <-- {inc}")
        print(f"Nodes connecting FROM '{nn}':")
        for out in find_connections_from(connections, nn):
            print(f"  --> {out}")

    # ============================================================
    # PHASE 3: Build and apply replacement
    # ============================================================
    print("\n" + "=" * 100)
    print("BUILDING NCA TOOLKIT REPLACEMENT")
    print("=" * 100)

    new_nodes, new_connections, incoming, outgoing = create_nca_nodes(
        timeline_node, render_node, wait_nodes, nodes, connections
    )

    print(f"\nNew NCA nodes to add: {len(new_nodes)}")
    for n in new_nodes:
        print(f"  + {n.get('name')} ({n.get('type')})")

    print(f"\nNew connections:")
    for src, conns in new_connections.items():
        for conn_type, outputs in conns.items():
            for idx, targets in enumerate(outputs):
                for t in targets:
                    print(f"  {src} --> {t.get('node')}")

    # Apply the replacement
    updated_wf = apply_replacement(
        wf, timeline_node, render_node, wait_nodes,
        new_nodes, new_connections, incoming, outgoing
    )

    # Save the modified workflow for review
    with open("/Users/gimdongseog/n8n-project/v3_after_nca_replacement.json", "w", encoding="utf-8") as f:
        json.dump(updated_wf, f, indent=2, ensure_ascii=False)
    print("\nSaved modified workflow to v3_after_nca_replacement.json")

    # ============================================================
    # PHASE 4: Upload to n8n
    # ============================================================
    print("\n" + "=" * 100)
    print("UPLOADING MODIFIED WORKFLOW TO N8N")
    print("=" * 100)

    try:
        result = update_workflow(updated_wf)
        print(f"\nWorkflow updated successfully!")
        print(f"  ID: {result.get('id')}")
        print(f"  Name: {result.get('name')}")
        print(f"  Total nodes: {len(result.get('nodes', []))}")
    except requests.exceptions.HTTPError as e:
        print(f"\nERROR updating workflow: {e}")
        print(f"Response: {e.response.text if e.response else 'N/A'}")
        print("\nThe modified workflow has been saved locally. You can review and upload manually.")
        sys.exit(1)

    print("\n" + "=" * 100)
    print("REPLACEMENT COMPLETE!")
    print("=" * 100)
    print("""
Summary of changes:
1. REMOVED Creatomate nodes (타임라인, 렌더, etc.)
2. ADDED NCA Toolkit nodes:
   - NCA 데이터 준비: Prepares data from previous nodes
   - NCA 파트별 합성: Creates individual clips (video + narration) for each part
   - NCA 영상 합치기: Concatenates all clips into one video
   - NCA 합치기 결과 처리: Processes concatenation result
   - NCA BGM 분기: Checks if BGM exists
   - NCA BGM 추가: Overlays BGM audio (if exists)
   - NCA BGM 결과 처리: Processes BGM result
   - NCA BGM 없음 처리: Passes through when no BGM
   - NCA 자막 준비: Prepares subtitle data
   - NCA 자막 추가: Adds Korean subtitles
   - NCA 최종 결과: Final output with Creatomate-compatible fields

NCA Toolkit API endpoints used:
- POST /v1/ffmpeg/compose (video+audio composition, BGM overlay)
- POST /v1/video/concatenate (merge clips)
- POST /v1/video/caption (add subtitles)

IMPORTANT: Review the workflow in n8n UI to verify all connections are correct.
Test with a single execution before running in production.
""")


if __name__ == "__main__":
    main()
