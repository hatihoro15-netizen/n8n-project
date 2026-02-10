#!/usr/bin/env python3
"""
이미지 생성 노드 JSON 파싱 에러 수정
- 문제: 이미지 프롬프트에 큰따옴표(")가 포함되면 JSON이 깨짐
- 해결: JSON.stringify()로 안전하게 이스케이프
"""
import json
import subprocess
import sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

# 기존 (안전하지 않음): {{ $json.text }} 가 따옴표 포함 시 JSON 깨짐
# 수정: JSON.stringify()로 prompt 값을 안전하게 이스케이프
SAFE_JSON_BODY = '={{ JSON.stringify({ "prompt": $json.text, "image_size": { "width": 1080, "height": 1920 } }) }}'


def fetch_workflow():
    result = subprocess.run([
        'curl', '-sk', '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


def fix_image_node(nodes):
    """이미지 생성 노드의 jsonBody를 안전한 버전으로 교체"""
    for n in nodes:
        if n['name'] == '이미지 생성':
            old_body = n['parameters'].get('jsonBody', '')
            if 'JSON.stringify' in old_body:
                print("  [SKIP] 이미 JSON.stringify 적용됨")
                return 0

            n['parameters']['jsonBody'] = SAFE_JSON_BODY
            print(f"  [OK] 이미지 생성: jsonBody 수정")
            print(f"       기존: {{ $json.text }} (따옴표 포함 시 깨짐)")
            print(f"       수정: JSON.stringify() (안전한 이스케이프)")
            return 1
    print("  [ERROR] 이미지 생성 노드를 찾을 수 없음")
    return 0


def upload_workflow(workflow_data):
    put_data = {
        "name": workflow_data.get("name"),
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "settings": {
            "executionOrder": workflow_data.get("settings", {}).get("executionOrder", "v1")
        }
    }
    with open('/tmp/lumix_v3_fix_image.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_v3_fix_image.json',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if 'id' in response:
            print(f"  [OK] 업로드 성공 (노드: {len(response.get('nodes', []))}개)")
            return True
        else:
            print(f"  [ERROR] {json.dumps(response, ensure_ascii=False)[:300]}")
            return False
    except json.JSONDecodeError:
        print(f"  [ERROR] 파싱 실패: {result.stdout[:300]}")
        return False


def reactivate():
    subprocess.run([
        'curl', '-sk', '-X', 'POST',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}/deactivate'
    ], capture_output=True, text=True)
    result = subprocess.run([
        'curl', '-sk', '-X', 'POST',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}/activate'
    ], capture_output=True, text=True)
    try:
        response = json.loads(result.stdout)
        print(f"  [OK] 재활성화: active={response.get('active')}")
    except Exception:
        print("  [WARN] 재활성화 응답 확인 필요")


def main():
    print("=" * 50)
    print("이미지 생성 JSON 파싱 에러 수정")
    print("=" * 50)

    print("\n[1/3] 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print("  [ERROR] 실패")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    print("\n[2/3] 이미지 생성 노드 수정...")
    fixed = fix_image_node(workflow['nodes'])

    if fixed == 0:
        print("\n수정할 내용 없음")
        return

    print("\n[3/3] 업로드 + 재활성화...")
    if upload_workflow(workflow):
        reactivate()

    print("\n" + "=" * 50)
    print("수정 완료!")
    print("=" * 50)
    print("\n  원인: 이미지 프롬프트에 큰따옴표(\") 포함 → JSON 깨짐")
    print("  해결: JSON.stringify()로 안전한 이스케이프 적용")
    print("  예시: '\"Lumix Solutions\"' → '\\\"Lumix Solutions\\\"'")


if __name__ == "__main__":
    main()
