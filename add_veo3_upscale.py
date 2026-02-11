#!/usr/bin/env python3
"""
Veo3 5x8초 워크플로우에 1080x1920 업스케일 단계를 추가하는 스크립트
- NCA Toolkit FFmpeg compose를 사용하여 업스케일
- 자막 추가 전에 업스케일 단계 삽입
"""

import requests
import json
import copy
import sys
import re

# ── 설정 ──
N8N_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
WORKFLOW_ID = "tS2hcoeJ4ar8hivm"

NCA_URL = "http://76.13.182.180:8080"
NCA_API_KEY = "nca-sagong-2026"

HEADERS = {
    "X-N8N-API-KEY": N8N_API_KEY,
    "Content-Type": "application/json",
}


def fetch_workflow():
    """워크플로우 가져오기"""
    url = f"{N8N_BASE}/workflows/{WORKFLOW_ID}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def print_workflow_structure(wf):
    """워크플로우 구조 출력"""
    nodes = wf.get("nodes", [])
    connections = wf.get("connections", {})

    print("=" * 80)
    print("워크플로우 노드 목록")
    print("=" * 80)
    for i, node in enumerate(nodes):
        node_id = node.get("id", "N/A")
        node_name = node.get("name", "N/A")
        node_type = node.get("type", "N/A")
        pos = node.get("position", [0, 0])
        print(f"  [{i:2d}] ID={node_id} | Name=\"{node_name}\" | Type={node_type} | Pos={pos}")

    print()
    print("=" * 80)
    print("연결(Connections) 목록")
    print("=" * 80)
    for source_name, outputs in connections.items():
        if isinstance(outputs, dict):
            for output_type, output_list in outputs.items():
                if isinstance(output_list, list):
                    for idx, conns in enumerate(output_list):
                        if isinstance(conns, list):
                            for conn in conns:
                                target = conn.get("node", "?")
                                target_type = conn.get("type", "?")
                                target_idx = conn.get("index", 0)
                                print(f"  \"{source_name}\" --[{output_type}][{idx}]--> \"{target}\" (type={target_type}, index={target_idx})")
    print()


def find_node_by_name(nodes, name):
    """노드 이름으로 검색"""
    for node in nodes:
        if node.get("name") == name:
            return node
    return None


def inspect_caption_node(nodes):
    """자막 추가 노드의 설정을 확인"""
    caption_node = find_node_by_name(nodes, "자막 추가")
    if caption_node:
        print("=" * 80)
        print("자막 추가 노드 상세")
        print("=" * 80)
        print(json.dumps(caption_node, indent=2, ensure_ascii=False))
        print()
    else:
        print("WARNING: '자막 추가' 노드를 찾을 수 없습니다!")
    return caption_node


def inspect_status_nodes(nodes):
    """영상 상태 확인 / 영상 재확인 노드 확인"""
    for name in ["영상 상태 확인", "영상 재확인"]:
        node = find_node_by_name(nodes, name)
        if node:
            print("=" * 80)
            print(f"\"{name}\" 노드 상세")
            print("=" * 80)
            print(json.dumps(node, indent=2, ensure_ascii=False))
            print()


def add_upscale_nodes(wf):
    """업스케일 노드 2개 추가 및 연결 수정"""
    nodes = wf["nodes"]
    connections = wf["connections"]

    # 1) 기존 노드 위치 파악
    status_node = find_node_by_name(nodes, "영상 상태 확인")
    recheck_node = find_node_by_name(nodes, "영상 재확인")
    caption_node = find_node_by_name(nodes, "자막 추가")

    if not caption_node:
        print("ERROR: '자막 추가' 노드를 찾을 수 없습니다!")
        sys.exit(1)

    # 자막 추가 노드의 위치를 기준으로 새 노드 위치 결정
    caption_pos = caption_node.get("position", [0, 0])

    # ── 자막 추가 노드에서 video_url이 어떻게 참조되는지 확인 ──
    print("=" * 80)
    print("자막 추가 노드의 body/parameters 분석")
    print("=" * 80)

    caption_params = caption_node.get("parameters", {})
    caption_type = caption_node.get("type", "")
    print(f"  Type: {caption_type}")

    # 모든 parameters 키 출력
    for k, v in caption_params.items():
        val_str = str(v)
        if len(val_str) > 300:
            val_str = val_str[:300] + "..."
        print(f"  {k}: {val_str}")
    print()

    # 표현식 검색
    caption_params_str = json.dumps(caption_params, ensure_ascii=False)
    print("자막 추가 노드 파라미터에서 표현식 검색:")

    expressions = re.findall(r'\{\{.*?\}\}', caption_params_str)
    for expr in expressions:
        print(f"  표현식: {expr}")

    json_refs = re.findall(r'\$json\.[a-zA-Z0-9_.\[\]]+', caption_params_str)
    for ref in json_refs:
        print(f"  $json 참조: {ref}")

    node_refs = re.findall(r"\$\(['\"].*?['\"]\)", caption_params_str)
    for ref in node_refs:
        print(f"  노드 참조: {ref}")

    print()

    # ── 2) "업스케일 준비" Code 노드 생성 ──
    upscale_prep_code = r"""// 업스케일 준비 - FFmpeg 명령어 생성
// 이전 노드(영상 상태 확인 또는 영상 재확인)에서 비디오 URL 가져오기

const videoUrl = $json.data?.works?.[0]?.video?.resource 
  || $json.data?.video?.resource 
  || $json.data?.works?.[0]?.resource
  || $json.data?.resource
  || $json.video_url
  || $json.url;

if (!videoUrl) {
  throw new Error('비디오 URL을 찾을 수 없습니다. 응답: ' + JSON.stringify($json).substring(0, 500));
}

// 1080x1920 (세로 숏폼) 업스케일 FFmpeg 명령어
const ffmpegCommand = `-i "${videoUrl}" -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -preset fast -crf 18 -c:a copy -movflags +faststart output_1080p.mp4`;

return [{
  json: {
    ffmpeg_command: ffmpegCommand,
    original_video_url: videoUrl,
    // 원본 데이터도 전달
    original_data: $json
  }
}];"""

    upscale_prep_node = {
        "parameters": {
            "jsCode": upscale_prep_code,
            "mode": "runOnceForEachItem"
        },
        "id": "upscale-prep-001",
        "name": "업스케일 준비",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [caption_pos[0] - 500, caption_pos[1]],
    }

    # ── HTTP Request 노드: 1080p 업스케일 ──
    upscale_http_node = {
        "parameters": {
            "method": "POST",
            "url": f"{NCA_URL}/v1/ffmpeg/compose",
            "authentication": "none",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "x-api-key", "value": NCA_API_KEY},
                    {"name": "Content-Type", "value": "application/json"},
                ]
            },
            "sendBody": True,
            "contentType": "raw",
            "rawContentType": "application/json",
            "body": "={{ JSON.stringify({ ffmpeg_command: $json.ffmpeg_command }) }}",
            "options": {
                "timeout": 120000,
            },
        },
        "id": "upscale-http-001",
        "name": "1080p 업스케일",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [caption_pos[0] - 250, caption_pos[1]],
    }

    # ── 3) 노드 추가 ──
    nodes.append(upscale_prep_node)
    nodes.append(upscale_http_node)
    print("새 노드 추가 완료:")
    print(f"  - 업스케일 준비 (Code) at position {upscale_prep_node['position']}")
    print(f"  - 1080p 업스케일 (HTTP Request) at position {upscale_http_node['position']}")
    print()

    # ── 4) 연결 수정 ──
    print("=" * 80)
    print("연결 수정")
    print("=" * 80)

    modified_connections = []

    for source_name in list(connections.keys()):
        if isinstance(connections[source_name], dict):
            for output_type in connections[source_name]:
                if isinstance(connections[source_name][output_type], list):
                    for idx, conns in enumerate(connections[source_name][output_type]):
                        if isinstance(conns, list):
                            new_conns = []
                            for conn in conns:
                                target = conn.get("node", "")
                                if target == "자막 추가" and source_name in ["영상 상태 확인", "영상 재확인"]:
                                    new_conn = copy.deepcopy(conn)
                                    new_conn["node"] = "업스케일 준비"
                                    new_conns.append(new_conn)
                                    modified_connections.append(
                                        f"  {source_name} -> 자막 추가  ==>  {source_name} -> 업스케일 준비"
                                    )
                                else:
                                    new_conns.append(conn)
                            connections[source_name][output_type][idx] = new_conns

    # 새 연결 추가: 업스케일 준비 → 1080p 업스케일
    connections["업스케일 준비"] = {
        "main": [
            [{"node": "1080p 업스케일", "type": "main", "index": 0}]
        ]
    }

    # 새 연결 추가: 1080p 업스케일 → 자막 추가
    connections["1080p 업스케일"] = {
        "main": [
            [{"node": "자막 추가", "type": "main", "index": 0}]
        ]
    }

    for m in modified_connections:
        print(m)
    print(f"  + 업스케일 준비 -> 1080p 업스케일 (new)")
    print(f"  + 1080p 업스케일 -> 자막 추가 (new)")
    print()

    # ── 5) 자막 추가 노드의 video_url 수정 ──
    print("=" * 80)
    print("자막 추가 노드의 video URL 참조 수정")
    print("=" * 80)

    # 업스케일된 영상 URL은 NCA Toolkit 응답의 response 필드
    # NCA 응답: {"code": 200, "response": "https://...url...", "message": "success"}
    # 따라서 $json.response 가 업스케일된 비디오 URL

    new_video_ref = "$json.response"
    caption_params_str = json.dumps(caption_params, ensure_ascii=False)

    # 기존 video URL 참조 패턴들
    old_patterns = [
        "$json.data.works[0].video.resource",
        "$json.data.works[0].resource",
        "$json.data.video.resource",
        "$json.data.resource",
    ]

    replaced = False
    for old_pattern in old_patterns:
        if old_pattern in caption_params_str:
            caption_params_str = caption_params_str.replace(old_pattern, new_video_ref)
            print(f"  교체: {old_pattern} -> {new_video_ref}")
            replaced = True

    if replaced:
        caption_node["parameters"] = json.loads(caption_params_str)
        print("  자막 추가 노드 파라미터 업데이트 완료")
    else:
        print("  WARNING: 기존 video URL 패턴을 찾을 수 없습니다.")
        print("  자막 추가 노드의 파라미터를 수동 확인 필요.")
        print()
        
        # Code 노드인 경우 jsCode 확인
        if "jsCode" in caption_params:
            js_code = caption_params["jsCode"]
            print(f"  자막 추가 노드는 Code 노드입니다.")
            print(f"  jsCode 내용 (처음 600자):")
            print(f"  {js_code[:600]}")
            print()

        # body 확인
        if "body" in caption_params:
            body = caption_params["body"]
            print(f"  body 내용:")
            print(f"  {str(body)[:500]}")
            print()

        # bodyParametersJson 확인
        if "bodyParametersJson" in caption_params:
            body_json = caption_params["bodyParametersJson"]
            print(f"  bodyParametersJson 내용:")
            print(f"  {str(body_json)[:500]}")
            print()
        
        # sendBody + parameters 확인
        if "bodyParameters" in caption_params:
            bp = caption_params["bodyParameters"]
            print(f"  bodyParameters 내용:")
            print(f"  {json.dumps(bp, indent=2, ensure_ascii=False)[:500]}")
            print()

        # 더 넓은 검색 - 모든 $json 참조를 찾아 교체 시도
        all_json_refs = re.findall(r'\$json\.[a-zA-Z0-9_.\[\]]+', caption_params_str)
        if all_json_refs:
            print(f"  발견된 $json 참조들: {all_json_refs}")
            
            # video/resource/url 관련 참조 찾기
            for ref in all_json_refs:
                if any(kw in ref.lower() for kw in ['video', 'resource', 'url', 'media']):
                    print(f"  -> video 관련 참조 발견: {ref} -> {new_video_ref} 로 교체")
                    caption_params_str = caption_params_str.replace(ref, new_video_ref)
                    replaced = True

            if replaced:
                caption_node["parameters"] = json.loads(caption_params_str)
                print("  자막 추가 노드 파라미터 업데이트 완료")

        # $('노드명') 참조도 확인
        all_node_refs = re.findall(r"\$\(['\"].*?['\"]\)\.[a-zA-Z0-9_.()[\]]+", caption_params_str)
        if all_node_refs:
            print(f"  발견된 노드 참조들: {all_node_refs}")
            for ref in all_node_refs:
                if any(kw in ref for kw in ['영상 상태', '영상 재확인', 'video', 'resource']):
                    print(f"  -> 관련 참조 발견: {ref} -> {new_video_ref} 로 교체")
                    caption_params_str = caption_params_str.replace(ref, new_video_ref)
                    replaced = True
            
            if replaced:
                caption_node["parameters"] = json.loads(caption_params_str)
                print("  자막 추가 노드 파라미터 업데이트 완료")

    print()
    return wf


def update_workflow(wf):
    """워크플로우 업데이트"""
    url = f"{N8N_BASE}/workflows/{WORKFLOW_ID}"

    payload = {
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "name": wf.get("name", ""),
        "settings": wf.get("settings", {}),
        "staticData": wf.get("staticData", None),
    }

    resp = requests.put(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()


def activate_workflow():
    """워크플로우 활성화"""
    url = f"{N8N_BASE}/workflows/{WORKFLOW_ID}/activate"
    resp = requests.post(url, headers=HEADERS)
    if resp.status_code == 200:
        print("워크플로우 활성화 완료")
    else:
        print(f"활성화 응답: {resp.status_code} - {resp.text[:200]}")


def main():
    print("=" * 80)
    print("Veo3 5x8초 워크플로우 업스케일 단계 추가")
    print(f"워크플로우 ID: {WORKFLOW_ID}")
    print("=" * 80)
    print()

    # 1) 워크플로우 가져오기
    print("1. 워크플로우 가져오기...")
    wf = fetch_workflow()
    print(f"   워크플로우 이름: {wf.get('name', 'N/A')}")
    print(f"   노드 수: {len(wf.get('nodes', []))}")
    print()

    # 2) 구조 출력
    print("2. 현재 워크플로우 구조:")
    print_workflow_structure(wf)

    # 3) 주요 노드 상세 확인
    print("3. 주요 노드 상세:")
    inspect_status_nodes(wf.get("nodes", []))
    inspect_caption_node(wf.get("nodes", []))

    # 4) 업스케일 노드 추가
    print("4. 업스케일 노드 추가 및 연결 수정...")
    wf = add_upscale_nodes(wf)

    # 5) 수정된 구조 확인
    print("5. 수정된 워크플로우 구조:")
    print_workflow_structure(wf)

    # 6) 워크플로우 업데이트
    print("6. 워크플로우 업데이트 중...")
    try:
        result = update_workflow(wf)
        print(f"   업데이트 성공! 노드 수: {len(result.get('nodes', []))}")
        print()
    except requests.exceptions.HTTPError as e:
        print(f"   업데이트 실패: {e}")
        print(f"   응답: {e.response.text[:1000] if e.response else 'N/A'}")
        sys.exit(1)

    # 7) 활성화
    print("7. 워크플로우 활성화...")
    activate_workflow()

    print()
    print("=" * 80)
    print("완료! 새로운 플로우:")
    print("  영상 상태 확인 -> 업스케일 준비 -> 1080p 업스케일 -> 자막 추가 -> ...")
    print("  영상 재확인 -> 업스케일 준비 -> 1080p 업스케일 -> 자막 추가 -> ...")
    print("=" * 80)


if __name__ == "__main__":
    main()
