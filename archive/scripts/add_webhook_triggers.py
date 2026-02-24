import json, subprocess, uuid

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
WEBHOOK_BASE = "https://n8n.srv1345711.hstgr.cloud/webhook"

WORKFLOWS = {
    "9YOHS8N1URWlzGWj": {"name": "루믹스 숏폼 v3", "path": "lumix-short"},
    "dsP2aQ1YRyeFRRNA": {"name": "루믹스 롱폼 v1", "path": "lumix-long"},
    "Rn7dlQMowuMGQ72g": {"name": "온카스터디 숏폼 v1", "path": "onca-short"},
    "u8m6S0WheOK6Kvqd": {"name": "온카스터디 롱폼 v1", "path": "onca-long"},
    "vhlxnOE44ioOMPtq": {"name": "슬롯 쇼츠 v1", "path": "slot-short"},
    "kJlaa6b2kKj7Jlb9": {"name": "스포츠 숏폼 v1", "path": "sports-short"},
}


def api_get(endpoint):
    result = subprocess.run([
        'curl', '-sk', f'{BASE}/{endpoint}',
        '-H', f'X-N8N-API-KEY: {API_KEY}'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


def api_put(endpoint, data):
    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        f'{BASE}/{endpoint}',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(data, ensure_ascii=False)
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


def api_post_activate(wf_id):
    result = subprocess.run([
        'curl', '-sk', '-X', 'POST',
        f'{BASE}/workflows/{wf_id}/activate',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


results = []

for wf_id, info in WORKFLOWS.items():
    print(f"\n{'='*60}")
    print(f"📌 {info['name']} ({wf_id})")
    print(f"{'='*60}")

    # 1. 다운로드
    wf = api_get(f'workflows/{wf_id}')
    if not wf.get('nodes'):
        print("  ❌ 다운로드 실패")
        results.append((info['name'], False, ""))
        continue

    # 2. 이미 Webhook 트리거가 있는지 확인
    has_webhook = any(n.get('type') == 'n8n-nodes-base.webhook' for n in wf['nodes'])
    if has_webhook:
        print("  ⚠️ 이미 Webhook 트리거가 있음 - 스킵")
        # Find webhook path
        for n in wf['nodes']:
            if n.get('type') == 'n8n-nodes-base.webhook':
                path = n.get('parameters', {}).get('path', '')
                print(f"  → URL: {WEBHOOK_BASE}/{path}")
        results.append((info['name'], True, f"{WEBHOOK_BASE}/{path}"))
        continue

    # 3. 스케줄 트리거가 연결된 대상 노드 찾기
    schedule_name = None
    for n in wf['nodes']:
        if n.get('type') == 'n8n-nodes-base.scheduleTrigger':
            schedule_name = n['name']
            break

    if not schedule_name:
        print("  ❌ 스케줄 트리거를 찾을 수 없음")
        results.append((info['name'], False, ""))
        continue

    # 스케줄 트리거의 연결 대상 찾기
    connections = wf.get('connections', {})
    target_connections = connections.get(schedule_name, {}).get('main', [[]])[0]

    if not target_connections:
        print(f"  ❌ '{schedule_name}'의 연결 대상이 없음")
        results.append((info['name'], False, ""))
        continue

    target_node = target_connections[0]['node']
    print(f"  스케줄 트리거 → {target_node}")

    # 4. 스케줄 트리거 위치 찾기 (Webhook을 옆에 배치)
    schedule_pos = None
    for n in wf['nodes']:
        if n['name'] == schedule_name:
            schedule_pos = n.get('position', [-1872, 224])
            break

    # 5. Webhook 트리거 노드 생성
    webhook_node = {
        "parameters": {
            "path": info['path'],
            "responseMode": "lastNode",
            "options": {}
        },
        "name": "Webhook 트리거",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [schedule_pos[0], schedule_pos[1] - 200],
        "id": str(uuid.uuid4()),
        "webhookId": str(uuid.uuid4())
    }

    # 6. 노드 추가
    wf['nodes'].append(webhook_node)

    # 7. Webhook 연결 추가 (스케줄 트리거와 동일한 대상에 연결)
    connections["Webhook 트리거"] = {
        "main": [target_connections.copy()]
    }

    print(f"  ✅ Webhook 트리거 추가 → {target_node}")
    print(f"  → Path: {info['path']}")

    # 8. 업로드
    clean_wf = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": connections,
        "settings": {"executionOrder": "v1"}
    }

    resp = api_put(f'workflows/{wf_id}', clean_wf)
    if resp.get('id'):
        print(f"  ✅ 업로드 성공")
    else:
        print(f"  ❌ 업로드 실패: {str(resp)[:200]}")
        results.append((info['name'], False, ""))
        continue

    # 9. 활성화 (Webhook 등록을 위해)
    act_resp = api_post_activate(wf_id)
    if act_resp.get('active') or act_resp.get('id'):
        print(f"  ✅ 활성화 완료")
    else:
        print(f"  ⚠️ 활성화 응답: {str(act_resp)[:200]}")

    webhook_url = f"{WEBHOOK_BASE}/{info['path']}"
    print(f"  🔗 Webhook URL: {webhook_url}")
    results.append((info['name'], True, webhook_url))


# 결과 요약
print(f"\n{'='*60}")
print("📊 Webhook 추가 결과 요약")
print(f"{'='*60}")
for name, success, url in results:
    status = "✅" if success else "❌"
    print(f"  {status} {name}")
    if url:
        print(f"     → {url}")

print(f"\n💡 실행 방법: curl -sk -X POST <URL>")
