#!/usr/bin/env python3
"""
업스케일 제거 - AuraSR 4x 업스케일 단계 삭제
이미지 결과 → 업스케일(3노드) → 영상 생성  =>  이미지 결과 → 영상 생성
+ 영상 생성 이미지 URL 참조 변경: $json.image.url → $json.images[0].url
"""
import json
import subprocess

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

UPSCALE_NODES = ["업스케일 요청", "업스케일 대기", "업스케일 결과"]


def fetch_workflow():
    result = subprocess.run([
        'curl', '-sk', '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


def remove_upscale(wf):
    nodes = wf["nodes"]
    conns = wf["connections"]
    changes = 0

    # 1. Remove 3 upscale nodes
    before_count = len(nodes)
    wf["nodes"] = [n for n in nodes if n.get("name") not in UPSCALE_NODES]
    removed = before_count - len(wf["nodes"])
    if removed > 0:
        print(f"  [OK] 업스케일 노드 {removed}개 삭제 ({', '.join(UPSCALE_NODES)})")
        changes += 1
    else:
        print("  [SKIP] 업스케일 노드 이미 없음")

    # 2. Reconnect: 이미지 결과 → 영상 생성 (bypass upscale)
    if "이미지 결과" in conns:
        old_target = conns["이미지 결과"]["main"][0][0]["node"] if conns["이미지 결과"]["main"][0] else None
        conns["이미지 결과"]["main"][0] = [{
            "node": "영상 생성",
            "type": "main",
            "index": 0
        }]
        print(f"  [OK] 연결 변경: 이미지 결과 → {old_target} ⇒ 이미지 결과 → 영상 생성")
        changes += 1

    # 3. Remove upscale connection entries
    for name in UPSCALE_NODES:
        if name in conns:
            del conns[name]
            print(f"  [OK] 연결 삭제: {name}")
            changes += 1

    # 4. Update 영상 생성 jsonBody: $json.image.url → $json.images[0].url
    for node in wf["nodes"]:
        if node.get("name") == "영상 생성":
            body = node["parameters"].get("jsonBody", "")
            if "$json.image.url" in body and "$json.images[0].url" not in body:
                body = body.replace("$json.image.url", "$json.images[0].url")
                node["parameters"]["jsonBody"] = body
                print("  [OK] 영상 생성 이미지 URL: $json.image.url → $json.images[0].url")
                changes += 1
            elif "$json.images[0].url" in body:
                print("  [SKIP] 이미지 URL 이미 수정됨")
            else:
                print(f"  [WARN] 영상 생성 jsonBody에서 image URL 패턴 못 찾음")

    return changes


def upload_workflow(wf):
    put_data = {
        "name": wf.get("name"),
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": {
            "executionOrder": wf.get("settings", {}).get("executionOrder", "v1")
        }
    }
    with open('/tmp/remove_upscale_update.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/remove_upscale_update.json',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if 'id' in response:
            print(f"  [OK] 업로드 성공 (ID: {response['id']}, 노드 {len(response.get('nodes',[]))}개)")
            return True
        else:
            print(f"  [ERROR] 업로드 실패: {json.dumps(response, ensure_ascii=False)[:500]}")
            return False
    except json.JSONDecodeError:
        print(f"  [ERROR] 응답 파싱 실패: {result.stdout[:300]}")
        return False


def reactivate_workflow():
    subprocess.run([
        'curl', '-sk', '-X', 'PATCH',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '{"active": false}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    subprocess.run([
        'curl', '-sk', '-X', 'PATCH',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '{"active": true}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    print("  [OK] 워크플로우 재활성화")


if __name__ == "__main__":
    print("=" * 55)
    print("업스케일 제거 (AuraSR 4x)")
    print("=" * 55)

    print("\n1. 워크플로우 가져오기...")
    wf = fetch_workflow()
    print(f"  [OK] {wf.get('name', 'Unknown')} (노드 {len(wf.get('nodes', []))}개)")

    print("\n2. 업스케일 제거...")
    changes = remove_upscale(wf)
    print(f"\n  총 {changes}건 변경")

    if changes > 0:
        print("\n3. n8n 서버에 업로드...")
        success = upload_workflow(wf)

        if success:
            print("\n4. 워크플로우 재활성화...")
            reactivate_workflow()

        print("\n" + "=" * 55)
        print("완료!" if success else "실패!")
    else:
        print("\n변경사항 없음")
