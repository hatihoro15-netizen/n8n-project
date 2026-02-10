#!/usr/bin/env python3
"""
Google Sheets 4개에 '분석리포트' 탭 추가 + 헤더 설정
임시 n8n 워크플로우 생성 → 수동 실행 → 완료 후 삭제 가능
"""
import json, subprocess, uuid

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"

CRED_SHEETS = {"googleSheetsOAuth2Api": {"id": "CWBUyXUqCU9p5VAg", "name": "Google Sheets account"}}

SHEETS = [
    {"name": "루믹스", "docId": "1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag"},
    {"name": "온카스터디", "docId": "1hnFCo4Mxnr4w57_zAFfYLMAgOsAB43ocgWhJW3szWK8"},
    {"name": "슬롯", "docId": "1cps-88TuhFld4qJlryQh2QHkKvxhQyxLSgeu5burA_A"},
    {"name": "스포츠", "docId": "1NAVwKXLQOUzBoNckxxesIR_ZS3GoNVGepr8zkBFmz4M"},
]

HEADERS = ["날짜", "채널명", "분석기간", "조회수_상위영상", "좋아요_상위영상",
           "트렌드_키워드", "추천_주제1", "추천_주제2", "추천_주제3",
           "피해야할_주제", "효과적인_훅_팁", "트렌드_각도", "고성과_패턴", "AI_분석_요약"]

def uid():
    return str(uuid.uuid4())

def make_create_tab_node(name, doc_id, pos_y):
    """HTTP Request: Google Sheets batchUpdate로 탭 생성"""
    return {
        "parameters": {
            "method": "POST",
            "url": f"https://sheets.googleapis.com/v4/spreadsheets/{doc_id}:batchUpdate",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "googleSheetsOAuth2Api",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": json.dumps({
                "requests": [{"addSheet": {"properties": {"title": "분석리포트"}}}]
            }),
            "options": {"response": {"response": {"neverError": True}}}
        },
        "name": f"탭생성_{name}",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [pos_y, 224],
        "id": uid(),
        "credentials": CRED_SHEETS
    }

def make_set_headers_node(name, doc_id, pos_y):
    """HTTP Request: Google Sheets values.update로 헤더 설정"""
    return {
        "parameters": {
            "method": "PUT",
            "url": f"https://sheets.googleapis.com/v4/spreadsheets/{doc_id}/values/%EB%B6%84%EC%84%9D%EB%A6%AC%ED%8F%AC%ED%8A%B8!A1:N1?valueInputOption=RAW",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "googleSheetsOAuth2Api",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": json.dumps({"values": [HEADERS]}, ensure_ascii=False),
            "options": {}
        },
        "name": f"헤더_{name}",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [pos_y, 224],
        "id": uid(),
        "credentials": CRED_SHEETS
    }

# Build nodes
nodes = []
connections = {}

# 1. Manual Trigger
trigger = {
    "parameters": {},
    "name": "수동 실행",
    "type": "n8n-nodes-base.manualTrigger",
    "typeVersion": 1,
    "position": [-600, 224],
    "id": uid()
}
nodes.append(trigger)

# 2. Create tab + headers for each sheet (sequential)
prev_name = "수동 실행"
x_pos = -300
for sheet in SHEETS:
    create_node = make_create_tab_node(sheet["name"], sheet["docId"], x_pos)
    header_node = make_set_headers_node(sheet["name"], sheet["docId"], x_pos + 250)
    nodes.extend([create_node, header_node])

    connections[prev_name] = {"main": [[{"node": create_node["name"], "type": "main", "index": 0}]]}
    connections[create_node["name"]] = {"main": [[{"node": header_node["name"], "type": "main", "index": 0}]]}
    prev_name = header_node["name"]
    x_pos += 550

# 3. Done code node
done_node = {
    "parameters": {
        "jsCode": 'return [{json: {message: "분석리포트 탭 4개 생성 + 헤더 설정 완료!", sheets: ["루믹스", "온카스터디", "슬롯", "스포츠"]}}];'
    },
    "name": "완료",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [x_pos, 224],
    "id": uid()
}
nodes.append(done_node)
connections[prev_name] = {"main": [[{"node": "완료", "type": "main", "index": 0}]]}

# Build workflow
workflow = {
    "name": "[임시] 분석리포트 탭 생성",
    "nodes": nodes,
    "connections": connections,
    "settings": {"executionOrder": "v1"}
}

# Upload to n8n
print("워크플로우 업로드 중...")
result = subprocess.run([
    'curl', '-sk', '-X', 'POST', f'{BASE}/workflows',
    '-H', f'X-N8N-API-KEY: {API_KEY}',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(workflow, ensure_ascii=False)
], capture_output=True, text=True)

resp = json.loads(result.stdout)
if resp.get('id'):
    wf_id = resp['id']
    print(f"✅ 워크플로우 생성 완료! ID: {wf_id}")
    print(f"   n8n에서 수동 실행하세요: https://n8n.srv1345711.hstgr.cloud/workflow/{wf_id}")
    print(f"   실행 후 삭제해도 됩니다.")
else:
    print(f"❌ 생성 실패: {result.stdout[:500]}")
