#!/usr/bin/env python3
"""
자막/아웃트로 수정 적용
- 폰트: NanumMyeongjo 42pt → NanumGothicBold 64pt
- 자막 위치: 하단 40px → 하단 200px
- 아웃트로: 중앙크롭 → 상단크롭 (Veo 워터마크 제거)
"""
import json
import subprocess

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"


def fetch_workflow():
    result = subprocess.run([
        'curl', '-sk', '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


def apply_fixes(workflow_data):
    nodes = workflow_data["nodes"]
    changes = 0

    for node in nodes:
        if node.get("name") == "NCA 제작 결과":
            code = node["parameters"]["jsCode"]

            # 1. 폰트 변경: NanumMyeongjo 42 → NanumGothicBold 64
            old_style = "NanumMyeongjo,42,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,30,30,50,1"
            new_style = "NanumGothicBold,64,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,4,1,2,40,40,120,1"
            if old_style in code:
                code = code.replace(old_style, new_style)
                print("  [OK] 폰트: NanumMyeongjo 42pt → NanumGothicBold 64pt")
                changes += 1
            elif new_style in code:
                print("  [SKIP] 폰트 이미 적용됨")
            else:
                print("  [WARN] 폰트 설정을 찾을 수 없음")

            # 2. 자막 위치 상향
            if "FINAL_Y = RES_Y - 40" in code:
                code = code.replace("FINAL_Y = RES_Y - 40", "FINAL_Y = RES_Y - 200")
                print("  [OK] 자막 위치: 하단 40px → 200px")
                changes += 1
            elif "FINAL_Y = RES_Y - 200" in code:
                print("  [SKIP] 자막 위치 이미 적용됨")

            node["parameters"]["jsCode"] = code

        if node.get("name") == "NCA 데이터 준비":
            code = node["parameters"]["jsCode"]

            # 3. 아웃트로 크롭 변경 (Veo 워터마크 제거)
            old_outro = "scale=1080:1989,crop=1080:1920:0:(ih-1920)/2"
            new_outro = "scale=1080:2160,crop=1080:1920:0:0"
            if old_outro in code:
                code = code.replace(old_outro, new_outro)
                print("  [OK] 아웃트로: 중앙크롭 → 상단크롭 (Veo 제거)")
                changes += 1
            elif new_outro in code:
                print("  [SKIP] 아웃트로 이미 적용됨")
            else:
                print("  [WARN] 아웃트로 설정을 찾을 수 없음")

            node["parameters"]["jsCode"] = code

    return changes


def upload_workflow(workflow_data):
    put_data = {
        "name": workflow_data.get("name"),
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "settings": {
            "executionOrder": workflow_data.get("settings", {}).get("executionOrder", "v1")
        }
    }
    with open('/tmp/subtitle_fix_update.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/subtitle_fix_update.json',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if 'id' in response:
            print(f"  [OK] 업로드 성공 (ID: {response['id']})")
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
    result = subprocess.run([
        'curl', '-sk', '-X', 'PATCH',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '{"active": true}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    print("  [OK] 워크플로우 재활성화")


if __name__ == "__main__":
    print("=" * 50)
    print("자막/아웃트로 수정 적용")
    print("=" * 50)

    print("\n1. 워크플로우 가져오기...")
    wf = fetch_workflow()
    print(f"  [OK] {wf.get('name', 'Unknown')} (노드 {len(wf.get('nodes', []))}개)")

    print("\n2. 수정 적용...")
    changes = apply_fixes(wf)
    print(f"  총 {changes}건 변경")

    if changes > 0:
        print("\n3. n8n 서버에 업로드...")
        success = upload_workflow(wf)

        if success:
            print("\n4. 워크플로우 재활성화...")
            reactivate_workflow()

        print("\n" + "=" * 50)
        print("완료!" if success else "실패!")
    else:
        print("\n변경사항 없음 (이미 적용됨)")
