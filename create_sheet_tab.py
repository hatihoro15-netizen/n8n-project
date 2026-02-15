import json, requests, time, uuid

N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
HEADERS = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}

SHEET_ID = "1gkRjLIcK3HxbnTbLCvG6oknMGVt2uz9pgboM3EF_VKg"
TAB_NAME = "온카스터디 숏폼"
WEBHOOK_PATH = "temp-create-tab-" + str(uuid.uuid4())[:8]
HEADERS_ROW = ["Subject", "Narration", "Caption", "댓글", "BGM prompt", "Status", "Publish", "업로드 URL"]

# Use n8n's HTTP Request node with Google OAuth2 instead of Code node
# This is more reliable since HTTP Request node natively supports OAuth2

nodes = [
    {
        "id": str(uuid.uuid4()),
        "name": "Webhook",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [250, 300],
        "webhookId": str(uuid.uuid4()),
        "parameters": {
            "path": WEBHOOK_PATH,
            "httpMethod": "POST",
            "responseMode": "lastNode",
            "options": {}
        }
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Add Sheet Tab",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [470, 300],
        "parameters": {
            "method": "POST",
            "url": f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}:batchUpdate",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "googleSheetsOAuth2Api",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": json.dumps({
                "requests": [{
                    "addSheet": {
                        "properties": {"title": TAB_NAME}
                    }
                }]
            }),
            "options": {}
        },
        "credentials": {
            "googleSheetsOAuth2Api": {
                "id": "CWBUyXUqCU9p5VAg",
                "name": "Google Sheets account"
            }
        }
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Add Headers",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [690, 300],
        "parameters": {
            "method": "PUT",
            "url": f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{requests.utils.quote(TAB_NAME + '!A1:H1')}?valueInputOption=RAW",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "googleSheetsOAuth2Api",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": json.dumps({
                "values": [HEADERS_ROW]
            }),
            "options": {}
        },
        "credentials": {
            "googleSheetsOAuth2Api": {
                "id": "CWBUyXUqCU9p5VAg",
                "name": "Google Sheets account"
            }
        }
    }
]

connections = {
    "Webhook": {
        "main": [[{"node": "Add Sheet Tab", "type": "main", "index": 0}]]
    },
    "Add Sheet Tab": {
        "main": [[{"node": "Add Headers", "type": "main", "index": 0}]]
    }
}

print("1. Creating temporary workflow...")
payload = {
    "name": "[TEMP] Create Sheet Tab",
    "nodes": nodes,
    "connections": connections,
    "settings": {"timezone": "Asia/Seoul"}
}
r = requests.post(f"{N8N_URL}/api/v1/workflows", headers=HEADERS, json=payload)
print(f"   Status: {r.status_code}")

if r.status_code not in (200, 201):
    print(f"   ERROR: {r.text[:500]}")
    exit(1)

wf = r.json()
wf_id = wf['id']
print(f"   Workflow ID: {wf_id}")

print("2. Activating workflow...")
r2 = requests.post(f"{N8N_URL}/api/v1/workflows/{wf_id}/activate", headers=HEADERS)
print(f"   Status: {r2.status_code}")

if r2.status_code != 200:
    print(f"   ERROR: {r2.text[:500]}")
    requests.delete(f"{N8N_URL}/api/v1/workflows/{wf_id}", headers=HEADERS)
    exit(1)

print(f"   Active: {r2.json().get('active')}")
time.sleep(2)

print("3. Triggering webhook...")
webhook_url = f"{N8N_URL}/webhook/{WEBHOOK_PATH}"
print(f"   URL: {webhook_url}")

try:
    r3 = requests.post(webhook_url, json={"action": "create_tab"}, timeout=30)
    print(f"   Status: {r3.status_code}")
    print(f"   Response: {r3.text[:500]}")
except Exception as e:
    print(f"   Error: {e}")

print("4. Cleaning up...")
requests.post(f"{N8N_URL}/api/v1/workflows/{wf_id}/deactivate", headers=HEADERS)
time.sleep(1)
rd = requests.delete(f"{N8N_URL}/api/v1/workflows/{wf_id}", headers=HEADERS)
print(f"   Delete: {rd.status_code}")
print("\nDone!")
