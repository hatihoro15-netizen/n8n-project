#!/usr/bin/env python3
"""
fix_veo3_loop.py
================
Replaces the broken SplitInBatches loop in the "루믹스 Veo3 5x8초 숏폼" workflow
with a linear pipeline that processes all 5 items natively through n8n nodes.

Problem: SplitInBatches v3 outputs 0 items on Branch 0 (batch) and goes straight
         to Branch 1 (done), so no videos ever get processed.

Solution: Remove the entire SplitInBatches loop and replace with:
  시나리오 파싱 → Veo3 영상 생성 → taskId 저장 → 생성 대기 (5min) → 영상 확인 →
  영상 처리 → 준비 완료 분기
    → (ready)     업스케일+자막 처리 → 결과 정리 → 최종 결과
    → (not ready) 추가 대기 (2min) → 영상 재확인 → 재확인 처리 → 업스케일+자막 처리
"""

import json
import requests
import sys
from datetime import datetime

# --- Configuration ---
API_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
API_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIi"
    "LCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5"
    "ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2"
    "NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
)
WORKFLOW_ID = "tS2hcoeJ4ar8hivm"

NCA_URL = "http://76.13.182.180:8080"
NCA_KEY = "nca-sagong-2026"
KIE_CREDENTIAL_ID = "34ktW72w0p8fCfUQ"

HEADERS = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json",
}


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# --- Step 1: Fetch the workflow ---
def fetch_workflow():
    log("Fetching workflow...")
    resp = requests.get(f"{API_BASE}/workflows/{WORKFLOW_ID}", headers=HEADERS)
    resp.raise_for_status()
    wf = resp.json()
    log(f"  Workflow: {wf['name']}")
    log(f"  Nodes: {len(wf['nodes'])}")
    return wf


# --- Step 2: Remove old loop nodes ---
NODES_TO_REMOVE = {
    "영상 5개 분리",
    "Veo3 영상 생성",
    "생성 대기",
    "영상 확인",
    "영상 상태 확인",
    "추가 대기",
    "영상 재확인",
    "업스케일 준비",
    "1080p 업스케일",
    "자막 추가",
    "자막 대기",
    "자막 결과 확인",
}


def remove_old_nodes(wf):
    log("Removing old loop nodes...")
    before = len(wf["nodes"])
    wf["nodes"] = [n for n in wf["nodes"] if n["name"] not in NODES_TO_REMOVE]
    removed = before - len(wf["nodes"])
    log(f"  Removed {removed} nodes")

    # Clean connections referencing removed nodes
    new_conns = {}
    for src, conn_data in wf["connections"].items():
        if src in NODES_TO_REMOVE:
            continue
        cleaned = {}
        for conn_type, outputs in conn_data.items():
            cleaned_outputs = []
            for output_list in outputs:
                cleaned_list = [
                    c for c in output_list if c["node"] not in NODES_TO_REMOVE
                ]
                cleaned_outputs.append(cleaned_list)
            cleaned[conn_type] = cleaned_outputs
        new_conns[src] = cleaned
    wf["connections"] = new_conns
    log("  Cleaned connections")
    return wf


# --- Step 3: Define new nodes ---
def build_new_nodes():
    """Build the replacement nodes for the linear pipeline."""
    nodes = []

    # -- Node 1: Veo3 영상 생성 (HTTP Request) --
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://api.kie.ai/api/v1/veo/generate",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": '={{ JSON.stringify({ "prompt": $json.veo3_prompt, "aspectRatio": "9:16", "model": "veo3_fast", "callbackUrl": "" }) }}',
            "options": {
                "response": {"response": {"neverError": True}},
                "timeout": 60000,
            },
        },
        "id": "new-veo3-generate",
        "name": "Veo3 영상 생성",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [1400, 400],
        "credentials": {
            "httpHeaderAuth": {"id": KIE_CREDENTIAL_ID, "name": "Kie.ai"}
        },
    })

    # -- Node 2: taskId 저장 (Code) --
    nodes.append({
        "parameters": {
            "jsCode": """// Merge scenario data with Kie.ai generate response
const genItems = $input.all();
const scenarioItems = $('시나리오 파싱').all();

const results = [];
for (let i = 0; i < genItems.length; i++) {
  const gen = genItems[i].json;
  const scenario = scenarioItems[i]?.json || {};

  results.push({
    json: {
      taskId: gen.data?.taskId || '',
      generate_status: gen.code === 200 ? 'submitted' : 'error',
      generate_response: gen,
      video_num: scenario.video_num || (i + 1),
      topic: scenario.topic || '',
      veo3_prompt: scenario.veo3_prompt || '',
      subtitle_ko: scenario.subtitle_ko || '',
      subject: scenario.subject || '',
      caption: scenario.caption || '',
      comment: scenario.comment || '',
    }
  });
}

console.log('Processed ' + results.length + ' video generation requests');
return results;""",
        },
        "id": "new-taskid-save",
        "name": "taskId 저장",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1650, 400],
    })

    # -- Node 3: 생성 대기 (Wait 5 minutes) --
    nodes.append({
        "parameters": {"amount": 300},
        "id": "new-wait-gen",
        "name": "생성 대기",
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [1900, 400],
        "webhookId": "new-wait-gen-hook",
    })

    # -- Node 4: 영상 확인 (HTTP Request) --
    nodes.append({
        "parameters": {
            "url": "=https://api.kie.ai/api/v1/veo/record-info?taskId={{ $json.taskId }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {
                "response": {"response": {"neverError": True}},
                "timeout": 30000,
            },
        },
        "id": "new-check-video",
        "name": "영상 확인",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [2150, 400],
        "credentials": {
            "httpHeaderAuth": {"id": KIE_CREDENTIAL_ID, "name": "Kie.ai"}
        },
    })

    # -- Node 5: 영상 처리 (Code) --
    nodes.append({
        "parameters": {
            "jsCode": """// Process video check results
const checkItems = $input.all();
const savedItems = $('taskId 저장').all();
const results = [];

for (let i = 0; i < checkItems.length; i++) {
  const check = checkItems[i].json;
  const saved = savedItems[i]?.json || {};
  const taskId = saved.taskId || check.data?.taskId || '';

  let videoUrl = '';
  let status = check.data?.status || 'unknown';

  if (check.data?.works?.[0]?.video?.resource) {
    videoUrl = check.data.works[0].video.resource;
  } else if (check.data?.works?.[0]?.resource) {
    videoUrl = check.data.works[0].resource;
  } else if (check.data?.video?.resource) {
    videoUrl = check.data.video.resource;
  } else if (check.data?.videoUrl) {
    videoUrl = check.data.videoUrl;
  }

  results.push({
    json: {
      taskId: taskId,
      video_url: videoUrl,
      video_status: status,
      is_ready: !!(videoUrl && status === 'completed'),
      video_num: saved.video_num || (i + 1),
      topic: saved.topic || '',
      veo3_prompt: saved.veo3_prompt || '',
      subtitle_ko: saved.subtitle_ko || '',
      subject: saved.subject || '',
      caption: saved.caption || '',
      comment: saved.comment || '',
      check_response: check,
    }
  });

  console.log('Video ' + (saved.video_num || i+1) + ': status=' + status + ', url=' + (videoUrl ? 'YES' : 'NO'));
}

return results;""",
        },
        "id": "new-process-check",
        "name": "영상 처리",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2400, 400],
    })

    # -- Node 6: 준비 완료 분기 (Code with 2 outputs) --
    nodes.append({
        "parameters": {
            "jsCode": """// Split items: ready videos (output 0) vs not-ready (output 1)
const items = $input.all();
const ready = [];
const notReady = [];

for (const item of items) {
  if (item.json.is_ready) {
    ready.push(item);
  } else {
    notReady.push(item);
  }
}

console.log('Ready: ' + ready.length + ', Not ready: ' + notReady.length);
return [ready, notReady];""",
            "numberOutputs": 2,
        },
        "id": "new-split-ready",
        "name": "준비 완료 분기",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2650, 400],

    })

    # -- Node 7: 추가 대기 (Wait 2 minutes) --
    nodes.append({
        "parameters": {"amount": 120},
        "id": "new-wait-extra",
        "name": "추가 대기",
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [2650, 700],
        "webhookId": "new-wait-extra-hook",
    })

    # -- Node 8: 영상 재확인 (HTTP Request) --
    nodes.append({
        "parameters": {
            "url": "=https://api.kie.ai/api/v1/veo/record-info?taskId={{ $json.taskId }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {
                "response": {"response": {"neverError": True}},
                "timeout": 30000,
            },
        },
        "id": "new-recheck-video",
        "name": "영상 재확인",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [2900, 700],
        "credentials": {
            "httpHeaderAuth": {"id": KIE_CREDENTIAL_ID, "name": "Kie.ai"}
        },
    })

    # -- Node 9: 재확인 처리 (Code) --
    nodes.append({
        "parameters": {
            "jsCode": """// Process recheck results
const recheckItems = $input.all();
const processedItems = $('영상 처리').all();
const results = [];

for (let i = 0; i < recheckItems.length; i++) {
  const recheck = recheckItems[i].json;
  const taskId = recheck.data?.taskId || '';

  // Find matching saved item by taskId
  let saved = {};
  for (const p of processedItems) {
    if (p.json.taskId === taskId) {
      saved = p.json;
      break;
    }
  }

  let videoUrl = '';
  let status = recheck.data?.status || 'unknown';

  if (recheck.data?.works?.[0]?.video?.resource) {
    videoUrl = recheck.data.works[0].video.resource;
  } else if (recheck.data?.works?.[0]?.resource) {
    videoUrl = recheck.data.works[0].resource;
  } else if (recheck.data?.video?.resource) {
    videoUrl = recheck.data.video.resource;
  } else if (recheck.data?.videoUrl) {
    videoUrl = recheck.data.videoUrl;
  }

  results.push({
    json: {
      taskId: taskId,
      video_url: videoUrl,
      video_status: status,
      is_ready: !!(videoUrl && status === 'completed'),
      video_num: saved.video_num || (i + 1),
      topic: saved.topic || '',
      veo3_prompt: saved.veo3_prompt || '',
      subtitle_ko: saved.subtitle_ko || '',
      subject: saved.subject || '',
      caption: saved.caption || '',
      comment: saved.comment || '',
    }
  });

  console.log('Recheck video ' + (saved.video_num || i+1) + ': status=' + status + ', url=' + (videoUrl ? 'YES' : 'NO'));
}

return results;""",
        },
        "id": "new-recheck-process",
        "name": "재확인 처리",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [3150, 700],
    })

    # -- Node 10: 업스케일+자막 처리 (Code) --
    upscale_caption_code = """// 업스케일 + 자막 처리 (NCA Toolkit)
const items = $input.all();
const NCA_URL = "NCA_URL_PLACEHOLDER";
const NCA_KEY = "NCA_KEY_PLACEHOLDER";
const results = [];

for (const item of items) {
  const d = item.json;
  const videoUrl = d.video_url || '';
  const videoNum = d.video_num || '?';

  if (!videoUrl) {
    console.log('Video ' + videoNum + ': No URL available, skipping');
    results.push({
      json: {
        video_num: d.video_num,
        topic: d.topic,
        subject: d.subject,
        caption: d.caption,
        comment: d.comment,
        subtitle_ko: d.subtitle_ko,
        taskId: d.taskId,
        original_url: '',
        upscaled_url: '',
        captioned_url: '',
        final_url: '',
        video_status: d.video_status,
        processing_status: 'no_video_url'
      }
    });
    continue;
  }

  console.log('Video ' + videoNum + ': Processing ' + videoUrl);

  // Step 1: Upscale to 1080x1920
  let upscaledUrl = videoUrl;
  try {
    const ffmpegCmd = '-i "' + videoUrl + '" -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -preset fast -crf 18 -c:a copy -movflags +faststart output_1080p.mp4';

    const upscaleResp = await this.helpers.httpRequest({
      method: 'POST',
      url: NCA_URL + '/v1/ffmpeg/compose',
      headers: {
        'x-api-key': NCA_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ ffmpeg_command: ffmpegCmd }),
      timeout: 120000,
    });

    const parsed = typeof upscaleResp === 'string' ? JSON.parse(upscaleResp) : upscaleResp;
    upscaledUrl = parsed.response || parsed.output_url || videoUrl;
    console.log('Video ' + videoNum + ': Upscaled -> ' + upscaledUrl);
  } catch(e) {
    console.log('Video ' + videoNum + ': Upscale failed - ' + e.message);
  }

  // Step 2: Add Korean captions
  let captionedUrl = upscaledUrl;
  try {
    const captionBody = {
      video_url: upscaledUrl,
      language: 'ko',
      settings: {
        style: 'highlight',
        line_color: '#FFFFFF',
        word_color: '#FFD700',
        outline_color: '#000000',
        position: 'bottom_center',
        alignment: 'center',
        font_size: 28,
        bold: true,
        outline_width: 3,
        max_words_per_line: 6
      }
    };

    const captionResp = await this.helpers.httpRequest({
      method: 'POST',
      url: NCA_URL + '/v1/video/caption',
      headers: {
        'x-api-key': NCA_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(captionBody),
      timeout: 120000,
    });

    const parsedCaption = typeof captionResp === 'string' ? JSON.parse(captionResp) : captionResp;
    if (parsedCaption.response && typeof parsedCaption.response === 'string' && parsedCaption.response.startsWith('http')) {
      captionedUrl = parsedCaption.response;
    } else if (parsedCaption.output_url) {
      captionedUrl = parsedCaption.output_url;
    }
    console.log('Video ' + videoNum + ': Captioned -> ' + captionedUrl);
  } catch(e) {
    console.log('Video ' + videoNum + ': Caption failed - ' + e.message);
  }

  results.push({
    json: {
      video_num: d.video_num,
      topic: d.topic,
      subject: d.subject,
      caption: d.caption,
      comment: d.comment,
      subtitle_ko: d.subtitle_ko,
      taskId: d.taskId,
      original_url: videoUrl,
      upscaled_url: upscaledUrl,
      captioned_url: captionedUrl,
      final_url: captionedUrl || upscaledUrl || videoUrl,
      video_status: d.video_status,
      processing_status: 'completed'
    }
  });
}

console.log('Processed ' + results.length + ' videos total');
return results;"""

    # Replace placeholders
    upscale_caption_code = upscale_caption_code.replace("NCA_URL_PLACEHOLDER", NCA_URL)
    upscale_caption_code = upscale_caption_code.replace("NCA_KEY_PLACEHOLDER", NCA_KEY)

    nodes.append({
        "parameters": {
            "jsCode": upscale_caption_code,
        },
        "id": "new-upscale-caption",
        "name": "업스케일+자막 처리",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2950, 400],
    })

    return nodes


# -- Step 4: Define new connections --
def build_new_connections():
    return {
        "시나리오 파싱": {
            "main": [[{"node": "Veo3 영상 생성", "type": "main", "index": 0}]]
        },
        "Veo3 영상 생성": {
            "main": [[{"node": "taskId 저장", "type": "main", "index": 0}]]
        },
        "taskId 저장": {
            "main": [[{"node": "생성 대기", "type": "main", "index": 0}]]
        },
        "생성 대기": {
            "main": [[{"node": "영상 확인", "type": "main", "index": 0}]]
        },
        "영상 확인": {
            "main": [[{"node": "영상 처리", "type": "main", "index": 0}]]
        },
        "영상 처리": {
            "main": [[{"node": "준비 완료 분기", "type": "main", "index": 0}]]
        },
        "준비 완료 분기": {
            "main": [
                [{"node": "업스케일+자막 처리", "type": "main", "index": 0}],
                [{"node": "추가 대기", "type": "main", "index": 0}],
            ]
        },
        "추가 대기": {
            "main": [[{"node": "영상 재확인", "type": "main", "index": 0}]]
        },
        "영상 재확인": {
            "main": [[{"node": "재확인 처리", "type": "main", "index": 0}]]
        },
        "재확인 처리": {
            "main": [[{"node": "업스케일+자막 처리", "type": "main", "index": 0}]]
        },
        "업스케일+자막 처리": {
            "main": [[{"node": "결과 정리", "type": "main", "index": 0}]]
        },
        "결과 정리": {
            "main": [[{"node": "최종 결과", "type": "main", "index": 0}]]
        },
    }


# -- Step 5: Update result nodes --
def update_result_nodes(wf):
    for node in wf["nodes"]:
        if node["name"] == "결과 정리":
            node["parameters"]["jsCode"] = """// Collect all video results from the linear pipeline
const allItems = $input.all();
const results = [];

for (const item of allItems) {
  const d = item.json;
  results.push({
    video_num: d.video_num || results.length + 1,
    video_url: d.final_url || d.captioned_url || d.upscaled_url || d.original_url || d.video_url || '생성 중...',
    original_url: d.original_url || d.video_url || '',
    upscaled_url: d.upscaled_url || '',
    captioned_url: d.captioned_url || '',
    status: d.processing_status || d.video_status || 'unknown',
    topic: d.topic || '',
    subject: d.subject || '',
    caption: d.caption || '',
    comment: d.comment || '',
    subtitle_ko: d.subtitle_ko || '',
    taskId: d.taskId || ''
  });
}

console.log('Collected ' + results.length + ' video results');

return [{
  json: {
    total_videos: results.length,
    generated_at: new Date().toISOString(),
    results: results
  }
}];"""
            node["position"] = [3200, 400]
            log("  Updated 결과 정리 Code node")

        elif node["name"] == "최종 결과":
            node["parameters"]["jsCode"] = """// Format final output with all video URLs and metadata
const input = $input.first().json;
const results = input.results || [];

const output = {
  workflow: "루믹스 Veo3 5x8초 숏폼",
  total_videos: input.total_videos || results.length,
  generated_at: input.generated_at,
  videos: results.map(r => ({
    "영상번호": r.video_num,
    "상태": r.status,
    "영상URL": r.video_url,
    "원본URL": r.original_url,
    "업스케일URL": r.upscaled_url,
    "자막URL": r.captioned_url,
    "주제": r.topic,
    "제목": r.subject,
    "설명": r.caption,
    "첫댓글": r.comment,
    "자막": r.subtitle_ko,
    "taskId": r.taskId
  })),
  summary: '총 ' + results.length + '개 영상 처리 완료. 각 영상은 독립적인 8초 숏폼입니다.'
};

return [{ json: output }];"""
            node["position"] = [3450, 400]
            log("  Updated 최종 결과 Code node")

    return wf


# -- Step 6: Assemble and upload --
def assemble_workflow(wf):
    new_nodes = build_new_nodes()
    new_conns = build_new_connections()

    for node in new_nodes:
        wf["nodes"].append(node)
        log(f"  Added node: {node['name']}")

    for src, conn_data in new_conns.items():
        wf["connections"][src] = conn_data

    return wf


def upload_workflow(wf):
    log("Uploading workflow...")

    payload = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": wf.get("settings", {}),
        "staticData": wf.get("staticData", None),
    }

    resp = requests.put(
        f"{API_BASE}/workflows/{WORKFLOW_ID}",
        headers=HEADERS,
        json=payload,
    )

    if resp.status_code != 200:
        log(f"  ERROR: {resp.status_code}")
        log(f"  Response: {resp.text[:2000]}")
        resp.raise_for_status()

    result = resp.json()
    log(f"  Upload successful!")
    log(f"  Workflow: {result.get('name')}")
    log(f"  Nodes: {len(result.get('nodes', []))}")
    return result


def verify_workflow(wf):
    log("Verifying workflow structure...")

    node_names = {n["name"] for n in wf["nodes"]}

    expected_nodes = {
        "수동 실행", "Webhook Trigger",
        "AI 시나리오 생성", "AI 검증", "검증 결과 확인", "AI 시나리오 재생성",
        "시나리오 파싱",
        "Veo3 영상 생성", "taskId 저장", "생성 대기", "영상 확인",
        "영상 처리", "준비 완료 분기",
        "추가 대기", "영상 재확인", "재확인 처리",
        "업스케일+자막 처리",
        "결과 정리", "최종 결과",
    }

    missing = expected_nodes - node_names
    extra_old = NODES_TO_REMOVE & node_names

    if missing:
        log(f"  WARNING: Missing nodes: {missing}")
    if extra_old:
        log(f"  WARNING: Old nodes still present: {extra_old}")

    conns = wf["connections"]

    pipeline = [
        ("시나리오 파싱", "Veo3 영상 생성"),
        ("Veo3 영상 생성", "taskId 저장"),
        ("taskId 저장", "생성 대기"),
        ("생성 대기", "영상 확인"),
        ("영상 확인", "영상 처리"),
        ("영상 처리", "준비 완료 분기"),
        ("추가 대기", "영상 재확인"),
        ("영상 재확인", "재확인 처리"),
        ("재확인 처리", "업스케일+자막 처리"),
        ("업스케일+자막 처리", "결과 정리"),
        ("결과 정리", "최종 결과"),
    ]

    all_ok = True
    for src, dst in pipeline:
        if src not in conns:
            log(f"  MISSING CONNECTION: {src} -> {dst}")
            all_ok = False
            continue
        targets = []
        for output_list in conns[src].get("main", []):
            for c in output_list:
                targets.append(c["node"])
        if dst not in targets:
            log(f"  MISSING CONNECTION: {src} -> {dst} (found targets: {targets})")
            all_ok = False

    if "준비 완료 분기" in conns:
        outputs = conns["준비 완료 분기"].get("main", [])
        if len(outputs) >= 2:
            out0 = [c["node"] for c in outputs[0]]
            out1 = [c["node"] for c in outputs[1]]
            if "업스케일+자막 처리" in out0 and "추가 대기" in out1:
                log("  Branch logic OK: ready -> 업스케일+자막, not-ready -> 추가 대기")
            else:
                log(f"  WARNING: Branch outputs unexpected: {out0}, {out1}")
                all_ok = False

    if all_ok and not missing and not extra_old:
        log("  All checks passed!")
    else:
        log("  Some checks failed - review warnings above")

    return all_ok


# -- Main --
def main():
    log("=" * 60)
    log("Fix Veo3 SplitInBatches Loop")
    log("Replace with linear pipeline (parallel item processing)")
    log("=" * 60)

    # Step 1: Fetch
    wf = fetch_workflow()

    # Backup
    backup_path = "/tmp/veo3_workflow_backup.json"
    with open(backup_path, "w") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    log(f"  Backup saved to {backup_path}")

    # Step 2: Remove old nodes
    wf = remove_old_nodes(wf)

    # Step 3: Update result nodes
    wf = update_result_nodes(wf)

    # Step 4: Add new nodes and connections
    wf = assemble_workflow(wf)

    # Step 5: Verify before upload
    log("")
    verify_workflow(wf)

    # Save pre-upload version
    pre_upload_path = "/tmp/veo3_workflow_modified.json"
    with open(pre_upload_path, "w") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    log(f"  Modified workflow saved to {pre_upload_path}")

    # Step 6: Upload
    log("")
    result = upload_workflow(wf)

    # Step 7: Final verification
    log("")
    log("Fetching uploaded workflow for final verification...")
    final_wf = fetch_workflow()
    verify_workflow(final_wf)

    # Print summary
    log("")
    log("=" * 60)
    log("SUMMARY")
    log("=" * 60)
    log(f"Workflow: {final_wf['name']}")
    log(f"Total nodes: {len(final_wf['nodes'])}")
    log("")
    log("New pipeline:")
    log("  시나리오 파싱")
    log("    -> Veo3 영상 생성 (5 parallel HTTP requests to Kie.ai)")
    log("    -> taskId 저장 (merge scenario data + taskIds)")
    log("    -> 생성 대기 (5 minutes)")
    log("    -> 영상 확인 (5 parallel status checks)")
    log("    -> 영상 처리 (extract video URLs)")
    log("    -> 준비 완료 분기")
    log("       [ready]     -> 업스케일+자막 처리 -> 결과 정리 -> 최종 결과")
    log("       [not ready] -> 추가 대기 (2min) -> 영상 재확인 -> 재확인 처리")
    log("                     -> 업스케일+자막 처리 -> 결과 정리 -> 최종 결과")
    log("")
    log("Removed nodes (old SplitInBatches loop):")
    for name in sorted(NODES_TO_REMOVE):
        log(f"  - {name}")
    log("")
    log("Done! The SplitInBatches loop has been replaced.")


if __name__ == "__main__":
    main()
