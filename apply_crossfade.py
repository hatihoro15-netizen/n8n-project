#!/usr/bin/env python3
"""
장면 전환 crossfade 추가
하드컷(뚝 끊김) → 0.4초 페이드 전환으로 자연스럽게
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


def apply_crossfade(wf):
    for node in wf["nodes"]:
        if node.get("name") != "NCA 데이터 준비":
            continue

        code = node["parameters"]["jsCode"]

        if "xfade" in code:
            print("  [SKIP] crossfade 이미 적용됨")
            return 0

        # Find the concat block and replace with crossfade
        # Old: concatInputs → concat filter
        old_block = """let concatInputs = '';
for (let i = 0; i < segments.length; i++) {
    concatInputs += `[v${i}][a${i}]`;
}
concatInputs += '[voutro][aoutro]';
filters.push(`${concatInputs}concat=n=${segments.length + 1}:v=1:a=1[outv][outa]`);"""

        new_block = """// Crossfade transitions (0.4s fade)
const XFADE_DUR = 0.4;
const allV = [...Array(segments.length).keys()].map(i => `v${i}`).concat(['voutro']);
const allA = [...Array(segments.length).keys()].map(i => `a${i}`).concat(['aoutro']);
const allDur = segments.map(s => s.sceneDuration).concat([OUTRO_DURATION]);

if (allV.length <= 1) {
    filters.push(`[${allV[0]}]copy[outv]`);
    filters.push(`[${allA[0]}]acopy[outa]`);
} else {
    // Video crossfade chain
    let prevV = allV[0];
    let cumDur = allDur[0];
    for (let k = 0; k < allV.length - 1; k++) {
        const xOffset = Math.max(0, cumDur - XFADE_DUR);
        const vOut = k === allV.length - 2 ? 'outv' : `vx${k}`;
        filters.push(`[${prevV}][${allV[k+1]}]xfade=transition=fade:duration=${XFADE_DUR}:offset=${xOffset.toFixed(2)}[${vOut}]`);
        prevV = vOut;
        cumDur += allDur[k+1] - XFADE_DUR;
    }
    // Audio crossfade chain
    let prevA = allA[0];
    for (let k = 0; k < allA.length - 1; k++) {
        const aOut = k === allA.length - 2 ? 'outa' : `ax${k}`;
        filters.push(`[${prevA}][${allA[k+1]}]acrossfade=d=${XFADE_DUR}:c1=tri:c2=tri[${aOut}]`);
        prevA = aOut;
    }
}"""

        if old_block in code:
            code = code.replace(old_block, new_block, 1)
            print("  [OK] concat → crossfade 교체 완료")
            print("       - 비디오: xfade (fade transition, 0.4초)")
            print("       - 오디오: acrossfade (triangle curve, 0.4초)")
            node["parameters"]["jsCode"] = code
            return 1
        else:
            # Try to find with regex (whitespace variation)
            print("  [WARN] 정확한 패턴 미일치, 유연 매칭 시도...")
            pattern = re.compile(
                r"let concatInputs = '';\s*"
                r"for \(let i = 0; i < segments\.length; i\+\+\) \{\s*"
                r"concatInputs \+= `\[v\$\{i\}\]\[a\$\{i\}\]`;\s*"
                r"\}\s*"
                r"concatInputs \+= '\[voutro\]\[aoutro\]';\s*"
                r"filters\.push\(`\$\{concatInputs\}concat=n=\$\{segments\.length \+ 1\}:v=1:a=1\[outv\]\[outa\]`\);",
                re.DOTALL
            )
            match = pattern.search(code)
            if match:
                code = code[:match.start()] + new_block + code[match.end():]
                print("  [OK] concat → crossfade 교체 완료 (유연 매칭)")
                node["parameters"]["jsCode"] = code
                return 1
            else:
                print("  [ERROR] concat 블록을 찾을 수 없음")
                # Debug: show nearby code
                idx = code.find('concatInputs')
                if idx >= 0:
                    print(f"  DEBUG: found 'concatInputs' at {idx}")
                    print(f"  SNIPPET: ...{repr(code[idx:idx+200])}...")
                else:
                    print("  DEBUG: 'concatInputs' not found in code")
                return 0

    print("  [ERROR] 'NCA 데이터 준비' 노드 없음")
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
    with open('/tmp/crossfade_update.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/crossfade_update.json',
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
    print("장면 전환 Crossfade 추가 (0.4초)")
    print("=" * 55)

    print("\n1. 워크플로우 가져오기...")
    wf = fetch_workflow()
    print(f"  [OK] {wf.get('name', 'Unknown')} (노드 {len(wf.get('nodes', []))}개)")

    print("\n2. Crossfade 적용...")
    changes = apply_crossfade(wf)

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
