#!/usr/bin/env python3
"""
NCA Toolkit 자막(Caption) 노드를 Veo3 5x8초 워크플로우에 추가하는 스크립트.
- 영상 상태 확인 성공 후, 영상 5개 분리(SplitInBatches)로 돌아가기 전에
  자막 추가 → 자막 대기 → 자막 결과 확인 노드를 삽입한다.
"""

import requests
import json
import sys
import copy

# ─── 설정 ───────────────────────────────────────────────────────────────────────
API_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
WORKFLOW_ID = "tS2hcoeJ4ar8hivm"

HEADERS = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json",
}

NCA_URL = "http://76.13.182.180:8080"
NCA_API_KEY = "nca-sagong-2026"


def fetch_workflow():
    """워크플로우를 API에서 가져온다."""
    url = f"{API_BASE}/workflows/{WORKFLOW_ID}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def update_workflow(wf):
    """워크플로우를 API에 업로드한다."""
    url = f"{API_BASE}/workflows/{WORKFLOW_ID}"
    payload = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": wf.get("settings", {}),
    }
    resp = requests.put(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()


def print_nodes(wf):
    """모든 노드의 이름, 타입, ID를 출력한다."""
    print("\n" + "=" * 80)
    print("현재 노드 목록")
    print("=" * 80)
    for i, node in enumerate(wf["nodes"]):
        print(f"  [{i}] name={node['name']!r}  type={node['type']!r}  id={node.get('id', 'N/A')}")
        pos = node.get("position", [0, 0])
        print(f"       position=[{pos[0]}, {pos[1]}]")
    print()


def print_connections(wf):
    """모든 연결을 출력한다."""
    print("=" * 80)
    print("현재 연결 (connections)")
    print("=" * 80)
    for src_name, outputs in wf["connections"].items():
        for output_key, output_list in outputs.items():
            for conn_group_idx, conn_group in enumerate(output_list):
                for conn in conn_group:
                    dest = conn.get("node", "?")
                    dest_type = conn.get("type", "?")
                    dest_idx = conn.get("index", 0)
                    print(f"  {src_name!r} --[{output_key}][{conn_group_idx}]--> {dest!r} (type={dest_type}, index={dest_idx})")
    print()


def print_node_params(wf, node_name):
    """특정 노드의 파라미터를 출력한다."""
    for node in wf["nodes"]:
        if node["name"] == node_name:
            print(f"\n--- {node_name} 파라미터 ---")
            print(json.dumps(node.get("parameters", {}), indent=2, ensure_ascii=False))
            return
    print(f"  노드 '{node_name}'을 찾을 수 없습니다.")


def find_node(wf, name):
    """이름으로 노드를 찾는다."""
    for node in wf["nodes"]:
        if node["name"] == name:
            return node
    return None


def add_caption_nodes(wf):
    """
    자막 추가, 자막 대기, 자막 결과 확인 노드를 추가하고
    연결을 재배선한다.
    """
    nodes = wf["nodes"]
    connections = wf["connections"]

    # ── 기존 노드 확인 ──────────────────────────────────────────────────────────
    status_check_node = find_node(wf, "영상 상태 확인")
    retry_check_node = find_node(wf, "영상 재확인")
    split_node = find_node(wf, "영상 5개 분리")

    if not status_check_node:
        print("ERROR: '영상 상태 확인' 노드를 찾을 수 없습니다.")
        sys.exit(1)
    if not split_node:
        print("ERROR: '영상 5개 분리' 노드를 찾을 수 없습니다.")
        sys.exit(1)

    # ── 위치 계산 ────────────────────────────────────────────────────────────────
    status_pos = status_check_node.get("position", [0, 0])
    caption_x = status_pos[0] + 300
    caption_y = status_pos[1] + 200

    # ── 1. 자막 추가 (HTTP Request) ──────────────────────────────────────────────
    caption_add_node = {
        "parameters": {
            "method": "POST",
            "url": f"{NCA_URL}/v1/video/caption",
            "authentication": "genericCredentialType",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "x-api-key", "value": NCA_API_KEY},
                    {"name": "Content-Type", "value": "application/json"},
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": '={\n  "video_url": "{{ $json.data.works[0].video.resource }}",\n  "language": "ko",\n  "settings": {\n    "style": "highlight",\n    "line_color": "#FFFFFF",\n    "word_color": "#FFD700",\n    "outline_color": "#000000",\n    "position": "bottom_center",\n    "alignment": "center",\n    "font_size": 28,\n    "bold": true,\n    "outline_width": 3,\n    "max_words_per_line": 6\n  }\n}',
            "options": {
                "timeout": 120000,
            },
        },
        "name": "자막 추가",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [caption_x, caption_y],
    }

    # ── 2. 자막 대기 (Wait) ──────────────────────────────────────────────────────
    caption_wait_node = {
        "parameters": {
            "amount": 60,
            "unit": "seconds",
        },
        "name": "자막 대기",
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [caption_x + 250, caption_y],
        "webhookId": "caption-wait-001",
    }

    # ── 3. 자막 결과 확인 (Code) ─────────────────────────────────────────────────
    caption_result_code = r"""// 자막 결과 확인
// NCA Toolkit 응답: { code: 200, response: "https://...", message: "success" }
const items = $input.all();
const results = [];

for (const item of items) {
  const captionResponse = item.json;
  let videoUrl = '';
  let captionSuccess = false;

  // 자막 응답에서 URL 추출
  if (captionResponse.code === 200 && captionResponse.response && 
      typeof captionResponse.response === 'string' && 
      captionResponse.response.startsWith('http')) {
    videoUrl = captionResponse.response;
    captionSuccess = true;
  } else {
    // 자막 실패 시 원본 영상 URL 사용
    try {
      const checkData = $('영상 확인').first().json;
      videoUrl = checkData.data.works[0].video.resource || '';
    } catch(e) {
      try {
        const retryData = $('영상 재확인').first().json;
        videoUrl = retryData.data.works[0].video.resource || '';
      } catch(e2) {
        videoUrl = '';
      }
    }
  }

  // 이전 노드에서 전달된 데이터 보존
  let video_num, topic, subject, caption, comment, subtitle_ko;
  try {
    const scenarioData = $('시나리오 파싱').first().json;
    video_num = scenarioData.video_num || '';
    topic = scenarioData.topic || '';
    subject = scenarioData.subject || '';
    caption = scenarioData.caption || '';
    comment = scenarioData.comment || '';
    subtitle_ko = scenarioData.subtitle_ko || '';
  } catch(e) {
    video_num = '';
    topic = '';
    subject = '';
    caption = '';
    comment = '';
    subtitle_ko = '';
  }

  results.push({
    json: {
      video_url: videoUrl,
      caption_applied: captionSuccess,
      video_num: video_num,
      topic: topic,
      subject: subject,
      caption: caption,
      comment: comment,
      subtitle_ko: subtitle_ko,
      original_caption_response: captionResponse,
    }
  });
}

return results;"""

    caption_result_node = {
        "parameters": {
            "jsCode": caption_result_code,
        },
        "name": "자막 결과 확인",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [caption_x + 500, caption_y],
    }

    # ── 노드 추가 ────────────────────────────────────────────────────────────────
    nodes.append(caption_add_node)
    nodes.append(caption_wait_node)
    nodes.append(caption_result_node)

    # ── 연결 재배선 ──────────────────────────────────────────────────────────────
    # 1) 영상 상태 확인 → (success) 의 대상을 영상 5개 분리 → 자막 추가 로 변경
    if "영상 상태 확인" in connections:
        for output_key, output_list in connections["영상 상태 확인"].items():
            for conn_group_idx, conn_group in enumerate(output_list):
                new_group = []
                for conn in conn_group:
                    if conn.get("node") == "영상 5개 분리":
                        new_conn = copy.deepcopy(conn)
                        new_conn["node"] = "자막 추가"
                        new_group.append(new_conn)
                        print(f"  [REWIRE] '영상 상태 확인' output[{output_key}][{conn_group_idx}]: '영상 5개 분리' -> '자막 추가'")
                    else:
                        new_group.append(conn)
                output_list[conn_group_idx] = new_group

    # 2) 영상 재확인 → 의 대상을 영상 5개 분리 → 자막 추가 로 변경
    if "영상 재확인" in connections:
        for output_key, output_list in connections["영상 재확인"].items():
            for conn_group_idx, conn_group in enumerate(output_list):
                new_group = []
                for conn in conn_group:
                    if conn.get("node") == "영상 5개 분리":
                        new_conn = copy.deepcopy(conn)
                        new_conn["node"] = "자막 추가"
                        new_group.append(new_conn)
                        print(f"  [REWIRE] '영상 재확인' output[{output_key}][{conn_group_idx}]: '영상 5개 분리' -> '자막 추가'")
                    else:
                        new_group.append(conn)
                output_list[conn_group_idx] = new_group

    # 3) 자막 추가 → 자막 대기
    connections["자막 추가"] = {
        "main": [
            [{"node": "자막 대기", "type": "main", "index": 0}]
        ]
    }

    # 4) 자막 대기 → 자막 결과 확인
    connections["자막 대기"] = {
        "main": [
            [{"node": "자막 결과 확인", "type": "main", "index": 0}]
        ]
    }

    # 5) 자막 결과 확인 → 영상 5개 분리 (루프 복귀)
    connections["자막 결과 확인"] = {
        "main": [
            [{"node": "영상 5개 분리", "type": "main", "index": 0}]
        ]
    }

    print("\n  [OK] 3개 자막 노드 추가 및 연결 재배선 완료")
    return wf


def main():
    print("=" * 80)
    print("NCA Toolkit Caption 노드 추가 스크립트")
    print(f"  대상 워크플로우: {WORKFLOW_ID}")
    print("=" * 80)

    # ── 1. 워크플로우 가져오기 ──────────────────────────────────────────────────
    print("\n[1] 워크플로우 가져오기...")
    wf = fetch_workflow()
    print(f"  이름: {wf['name']}")
    print(f"  노드 수: {len(wf['nodes'])}")

    # ── 2. 노드 및 연결 출력 ────────────────────────────────────────────────────
    print_nodes(wf)
    print_connections(wf)

    # ── 3. 영상 확인 / 영상 재확인 노드 파라미터 출력 ────────────────────────────
    print("\n[3] 영상 확인 노드 파라미터 확인...")
    print_node_params(wf, "영상 확인")
    print_node_params(wf, "영상 재확인")
    print_node_params(wf, "영상 상태 확인")

    # ── 4. 자막 노드 추가 ───────────────────────────────────────────────────────
    print("\n[4] 자막 노드 추가 및 연결 재배선...")
    wf = add_caption_nodes(wf)

    # ── 5. 변경된 연결 확인 ─────────────────────────────────────────────────────
    print("\n[5] 변경 후 연결 확인...")
    print_connections(wf)

    # ── 6. 업로드 ───────────────────────────────────────────────────────────────
    print("\n[6] 워크플로우 업로드...")
    result = update_workflow(wf)
    print(f"  업로드 완료! 워크플로우 이름: {result.get('name', '?')}")
    print(f"  노드 수: {len(result.get('nodes', []))}")

    # ── 7. 검증 ─────────────────────────────────────────────────────────────────
    print("\n[7] 업로드 결과 검증...")
    wf_verify = fetch_workflow()

    # 자막 노드 존재 확인
    caption_names = ["자막 추가", "자막 대기", "자막 결과 확인"]
    for name in caption_names:
        node = find_node(wf_verify, name)
        if node:
            print(f"  [OK] '{name}' 노드 존재 확인")
        else:
            print(f"  [FAIL] '{name}' 노드를 찾을 수 없습니다!")

    # 연결 확인
    verify_conns = wf_verify["connections"]

    # 자막 추가 → 자막 대기
    if "자막 추가" in verify_conns:
        targets = [c["node"] for cg in verify_conns["자막 추가"].get("main", []) for c in cg]
        if "자막 대기" in targets:
            print("  [OK] '자막 추가' -> '자막 대기' 연결 확인")
        else:
            print(f"  [FAIL] '자막 추가' 연결 대상: {targets}")

    # 자막 대기 → 자막 결과 확인
    if "자막 대기" in verify_conns:
        targets = [c["node"] for cg in verify_conns["자막 대기"].get("main", []) for c in cg]
        if "자막 결과 확인" in targets:
            print("  [OK] '자막 대기' -> '자막 결과 확인' 연결 확인")
        else:
            print(f"  [FAIL] '자막 대기' 연결 대상: {targets}")

    # 자막 결과 확인 → 영상 5개 분리
    if "자막 결과 확인" in verify_conns:
        targets = [c["node"] for cg in verify_conns["자막 결과 확인"].get("main", []) for c in cg]
        if "영상 5개 분리" in targets:
            print("  [OK] '자막 결과 확인' -> '영상 5개 분리' 연결 확인")
        else:
            print(f"  [FAIL] '자막 결과 확인' 연결 대상: {targets}")

    # 영상 상태 확인 연결 확인
    if "영상 상태 확인" in verify_conns:
        all_targets = []
        for output_key, output_list in verify_conns["영상 상태 확인"].items():
            for cg in output_list:
                for c in cg:
                    all_targets.append(c["node"])
        if "자막 추가" in all_targets:
            print("  [OK] '영상 상태 확인' -> '자막 추가' 연결 확인")
        if "영상 5개 분리" in all_targets:
            print("  [WARN] '영상 상태 확인' -> '영상 5개 분리' 직접 연결이 아직 있습니다 (다른 output일 수 있음)")

    print("\n" + "=" * 80)
    print("완료! n8n 에디터에서 워크플로우를 확인하세요.")
    print(f"  URL: https://n8n.srv1345711.hstgr.cloud/workflow/{WORKFLOW_ID}")
    print("=" * 80)


if __name__ == "__main__":
    main()
