#!/usr/bin/env python3
"""
Ken Burns 효과 추가 - 분할 반복 영상 문제 해결
나레이션이 길어서 같은 영상이 반복될 때,
각 세그먼트에 다른 줌/패닝 효과를 적용하여 다른 앵글처럼 보이게 함
"""
import json
import subprocess
import re

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"


def fetch_workflow():
    result = subprocess.run([
        'curl', '-sk', '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


def apply_ken_burns(wf):
    for node in wf["nodes"]:
        if node.get("name") != "NCA 데이터 준비":
            continue

        code = node["parameters"]["jsCode"]
        changes = 0

        # 1. Add splitIndex to split segments
        if "splitIndex" not in code:
            old = "type: 'split'"
            new = "type: 'split', splitIndex: s"
            if old in code:
                code = code.replace(old, new)
                changes += 1
                print("  [OK] splitIndex 추가")
            else:
                print("  [WARN] 'type: split' 패턴 없음")
        else:
            print("  [SKIP] splitIndex 이미 존재")

        # 2. Add Ken Burns filter for split segments
        if "Ken Burns" not in code:
            # Find the video filter section marker
            marker_pattern = re.compile(
                r'(    // .*[필필].*\n    )(if \(dur > MAX_SLOW_SECONDS\) \{)'
            )
            match = marker_pattern.search(code)

            if not match:
                # Try English-only fallback
                marker_pattern2 = re.compile(
                    r'(\n    )(if \(dur > MAX_SLOW_SECONDS\) \{)'
                )
                match = marker_pattern2.search(code)

            if match:
                prefix = match.group(1)
                old_if = match.group(2)
                full_match = match.group(0)

                # Ken Burns block to insert before the existing if
                kb_block = prefix + """// Ken Burns for split segments (avoid repetition)
    if (seg.type === 'split') {
        const KB = 1.12;
        const kbW = Math.round(1080 * KB);
        const kbH = Math.round(1920 * KB);
        const dx = kbW - 1080;
        const dy = kbH - 1920;
        const dxH = Math.round(dx / 2);
        const dyH = Math.round(dy / 2);
        const kbVariants = [
            `scale=${kbW}:${kbH},crop=1080:1920:${dxH}*t/${dur.toFixed(2)}:${dyH}*t/${dur.toFixed(2)}`,
            `scale=${kbW}:${kbH},crop=1080:1920:${dx}-${dx}*t/${dur.toFixed(2)}:${dy}-${dy}*t/${dur.toFixed(2)}`,
            `scale=${kbW}:${kbH},crop=1080:1920:${dx}*t/${dur.toFixed(2)}:${dyH}`,
            `scale=${kbW}:${kbH},crop=1080:1920:${dx}-${dx}*t/${dur.toFixed(2)}:${dyH}`,
        ];
        const kbEffect = kbVariants[seg.splitIndex % kbVariants.length];
        filters.push(`[${vIdx}:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,${kbEffect},trim=duration=${dur.toFixed(2)},setpts=PTS-STARTPTS[v${i}]`);
    } else """ + old_if

                code = code.replace(full_match, kb_block, 1)
                changes += 1
                print("  [OK] Ken Burns 필터 추가 (4가지 패닝 효과)")
                print("       - Variant 0: 좌상→우하 대각선 패닝")
                print("       - Variant 1: 우하→좌상 대각선 패닝")
                print("       - Variant 2: 좌→우 수평 패닝")
                print("       - Variant 3: 우→좌 수평 패닝")
            else:
                print("  [ERROR] 비디오 필터 섹션을 찾을 수 없음")
                print("  Code snippet:", code[code.find('MAX_SLOW')-100:code.find('MAX_SLOW')+100] if 'MAX_SLOW' in code else 'N/A')
        else:
            print("  [SKIP] Ken Burns 이미 적용됨")

        node["parameters"]["jsCode"] = code
        return changes

    print("  [ERROR] 'NCA 데이터 준비' 노드를 찾을 수 없음")
    return 0


def upload_workflow(wf):
    put_data = {
        "name": wf.get("name"),
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": {
            "executionOrder": wf.get("settings", {}).get("executionOrder", "v1")
        }
    }
    with open('/tmp/ken_burns_update.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/ken_burns_update.json',
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
    print("=" * 55)
    print("Ken Burns 효과 추가 - 반복 영상 문제 해결")
    print("=" * 55)

    print("\n1. 워크플로우 가져오기...")
    wf = fetch_workflow()
    print(f"  [OK] {wf.get('name', 'Unknown')} (노드 {len(wf.get('nodes', []))}개)")

    print("\n2. Ken Burns 효과 적용...")
    changes = apply_ken_burns(wf)
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
