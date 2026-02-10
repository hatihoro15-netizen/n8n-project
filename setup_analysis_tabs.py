#!/usr/bin/env python3
"""
자동 설정: 분석리포트 탭 생성 + YouTube 채널 ID 조회
1. n8n 임시 워크플로우 생성 → Google Sheets/YouTube API 호출
2. 4개 시트에 분석리포트 탭 + 헤더 자동 생성
3. YouTube 채널 ID 조회 → 채널 성과 분석 워크플로우에 자동 설정
"""
import json
import subprocess
import sys
import uuid
import time
import urllib.parse

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
ANALYSIS_WORKFLOW_ID = "SeW8pBXuifk04TWw"

SHEETS_CRED = {"id": "CWBUyXUqCU9p5VAg", "name": "Google Sheets account"}
YOUTUBE_CRED = {"id": "kRKBMYWf6cB72qUi", "name": "YouTube account"}

SHEET_CONFIGS = [
    {"name": "루믹스", "docId": "1gkRjLIcK3HxbnTbLCvG6oknMGVt2uz9pgboM3EF_VKg"},
    {"name": "온카스터디", "docId": "1hnFCo4Mxnr4w57_zAFfYLMAgOsAB43ocgWhJW3szWK8"},
    {"name": "슬롯", "docId": "1cps-88TuhFld4qJlryQh2QHkKvxhQyxLSgeu5burA_A"},
    {"name": "스포츠", "docId": "1NAVwKXLQOUzBoNckxxesIR_ZS3GoNVGepr8zkBFmz4M"}
]

REPORT_SHEET_ENCODED = urllib.parse.quote("분석리포트")
HEADERS = ["날짜", "채널명", "분석기간", "조회수_상위영상", "좋아요_상위영상",
           "트렌드_키워드", "추천_주제1", "추천_주제2", "추천_주제3",
           "피해야할_주제", "효과적인_훅_팁", "트렌드_각도", "고성과_패턴", "AI_분석_요약"]


def gen_id():
    return str(uuid.uuid4())


def build_setup_workflow():
    """임시 설정 워크플로우 JSON 생성"""
    webhook_path = f"setup-tabs-{uuid.uuid4().hex[:8]}"

    sheets_js = json.dumps(SHEET_CONFIGS, ensure_ascii=False)
    headers_js = json.dumps(HEADERS, ensure_ascii=False)

    setup_code = f"""const sheets = {sheets_js};
return sheets.map(s => ({{json: s}}));"""

    results_code = """const channelsResponse = $input.first().json;
const items = channelsResponse.items || [];
const channels = items.map(ch => ({
  id: ch.id,
  title: ch.snippet ? ch.snippet.title : '',
  customUrl: ch.snippet ? (ch.snippet.customUrl || '') : ''
}));

const mapping = {"루믹스": "CHANNEL_ID_LUMIX", "온카": "CHANNEL_ID_ONCA", "슬롯": "CHANNEL_ID_SLOT", "스포츠": "CHANNEL_ID_SPORTS"};
const matched = {};
for (const ch of channels) {
  for (const [keyword, placeholder] of Object.entries(mapping)) {
    if (ch.title.includes(keyword) || ch.customUrl.includes(keyword.toLowerCase())) {
      matched[placeholder] = ch.id;
      matched[placeholder + "_name"] = ch.title;
    }
  }
}

return [{json: {allChannels: channels, matched: matched, totalFound: channels.length}}];"""

    nodes = [
        {
            "parameters": {
                "path": webhook_path,
                "responseMode": "responseNode",
                "options": {}
            },
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [0, 300],
            "id": gen_id(),
            "name": "Webhook"
        },
        {
            "parameters": {"jsCode": setup_code},
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [220, 300],
            "id": gen_id(),
            "name": "시트 설정"
        },
        {
            "parameters": {"batchSize": 1, "options": {}},
            "type": "n8n-nodes-base.splitInBatches",
            "typeVersion": 3,
            "position": [440, 300],
            "id": gen_id(),
            "name": "시트별 처리"
        },
        {
            "parameters": {
                "method": "POST",
                "url": "=https://sheets.googleapis.com/v4/spreadsheets/{{ $json.docId }}:batchUpdate",
                "authentication": "predefinedCredentialType",
                "nodeCredentialType": "googleSheetsOAuth2Api",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": '={"requests": [{"addSheet": {"properties": {"title": "분석리포트"}}}]}',
                "options": {}
            },
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [660, 460],
            "id": gen_id(),
            "name": "탭 생성",
            "onError": "continueRegularOutput",
            "credentials": {"googleSheetsOAuth2Api": SHEETS_CRED}
        },
        {
            "parameters": {
                "method": "PUT",
                "url": f"=https://sheets.googleapis.com/v4/spreadsheets/{{{{ $('시트별 처리').first().json.docId }}}}/values/{REPORT_SHEET_ENCODED}!A1:N1?valueInputOption=RAW",
                "authentication": "predefinedCredentialType",
                "nodeCredentialType": "googleSheetsOAuth2Api",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": '={"values": [' + json.dumps(HEADERS, ensure_ascii=False) + ']}',
                "options": {}
            },
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [880, 460],
            "id": gen_id(),
            "name": "헤더 추가",
            "onError": "continueRegularOutput",
            "credentials": {"googleSheetsOAuth2Api": SHEETS_CRED}
        },
        {
            "parameters": {
                "method": "GET",
                "url": "https://www.googleapis.com/youtube/v3/channels?part=snippet,id&mine=true&maxResults=50",
                "authentication": "predefinedCredentialType",
                "nodeCredentialType": "youTubeOAuth2Api",
                "options": {}
            },
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [660, 140],
            "id": gen_id(),
            "name": "YouTube 채널 조회",
            "onError": "continueRegularOutput",
            "credentials": {"youTubeOAuth2Api": YOUTUBE_CRED}
        },
        {
            "parameters": {"jsCode": results_code},
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [880, 140],
            "id": gen_id(),
            "name": "결과 정리"
        },
        {
            "parameters": {"options": {}},
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1.1,
            "position": [1100, 140],
            "id": gen_id(),
            "name": "응답 반환"
        }
    ]

    connections = {
        "Webhook": {"main": [[{"node": "시트 설정", "type": "main", "index": 0}]]},
        "시트 설정": {"main": [[{"node": "시트별 처리", "type": "main", "index": 0}]]},
        "시트별 처리": {"main": [
            [{"node": "YouTube 채널 조회", "type": "main", "index": 0}],
            [{"node": "탭 생성", "type": "main", "index": 0}]
        ]},
        "탭 생성": {"main": [[{"node": "헤더 추가", "type": "main", "index": 0}]]},
        "헤더 추가": {"main": [[{"node": "시트별 처리", "type": "main", "index": 0}]]},
        "YouTube 채널 조회": {"main": [[{"node": "결과 정리", "type": "main", "index": 0}]]},
        "결과 정리": {"main": [[{"node": "응답 반환", "type": "main", "index": 0}]]}
    }

    workflow = {
        "name": "[임시] 분석리포트 탭 생성 + 채널ID 조회",
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"}
    }

    return workflow, webhook_path


def api_call(method, endpoint, data=None):
    """n8n API 호출 헬퍼"""
    cmd = ['curl', '-sk', '-X', method, '-H', f'X-N8N-API-KEY: {API_KEY}',
           '-H', 'Content-Type: application/json']
    if data:
        cmd.extend(['-d', json.dumps(data, ensure_ascii=False)])
    cmd.append(f'{N8N_URL}{endpoint}')
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": result.stdout[:500]}


def update_channel_ids(matched_channels):
    """채널 성과 분석 워크플로우의 채널 ID 업데이트"""
    if not matched_channels:
        print("  [SKIP] 매칭된 채널 없음 - 채널 ID 업데이트 건너뜀")
        return False

    workflow = api_call('GET', f'/api/v1/workflows/{ANALYSIS_WORKFLOW_ID}')
    if 'nodes' not in workflow:
        print(f"  [ERROR] 분석 워크플로우 조회 실패")
        return False

    nodes = workflow['nodes']
    for n in nodes:
        if n['name'] == '채널 설정':
            code = n['parameters']['jsCode']
            for placeholder, channel_id in matched_channels.items():
                if placeholder.startswith("CHANNEL_ID_"):
                    code = code.replace(placeholder, channel_id)
            n['parameters']['jsCode'] = code
            break

    put_data = {
        "name": workflow["name"],
        "nodes": nodes,
        "connections": workflow["connections"],
        "settings": {"executionOrder": workflow.get("settings", {}).get("executionOrder", "v1")}
    }

    response = api_call('PUT', f'/api/v1/workflows/{ANALYSIS_WORKFLOW_ID}', put_data)
    if 'id' in response:
        print(f"  [OK] 채널 ID 업데이트 완료")
        # 재활성화
        api_call('PATCH', f'/api/v1/workflows/{ANALYSIS_WORKFLOW_ID}', {"active": False})
        api_call('PATCH', f'/api/v1/workflows/{ANALYSIS_WORKFLOW_ID}', {"active": True})
        print(f"  [OK] 분석 워크플로우 재활성화")
        return True
    else:
        print(f"  [ERROR] 업데이트 실패: {json.dumps(response, ensure_ascii=False)[:300]}")
        return False


def main():
    print("=" * 60)
    print("자동 설정: 분석리포트 탭 + YouTube 채널 ID")
    print("=" * 60)

    # 1. 임시 워크플로우 생성
    print("\n[1/6] 임시 워크플로우 생성...")
    workflow_json, webhook_path = build_setup_workflow()
    response = api_call('POST', '/api/v1/workflows', workflow_json)

    if 'id' not in response:
        print(f"  [ERROR] 워크플로우 생성 실패: {json.dumps(response, ensure_ascii=False)[:300]}")
        sys.exit(1)

    temp_wf_id = response['id']
    print(f"  [OK] 임시 워크플로우 생성 (ID: {temp_wf_id})")

    # 2. 활성화
    print("\n[2/6] 워크플로우 활성화...")
    api_call('PATCH', f'/api/v1/workflows/{temp_wf_id}', {"active": True})
    print(f"  [OK] 활성화 완료")
    time.sleep(2)  # Webhook 등록 대기

    # 3. Webhook 트리거
    print(f"\n[3/6] Webhook 트리거 (탭 생성 + 채널 조회 실행중)...")
    webhook_url = f'{N8N_URL}/webhook/{webhook_path}'
    result = subprocess.run([
        'curl', '-sk', '-X', 'POST',
        '-H', 'Content-Type: application/json',
        '-d', '{}',
        webhook_url
    ], capture_output=True, text=True, timeout=60)

    try:
        webhook_response = json.loads(result.stdout)
    except (json.JSONDecodeError, Exception) as e:
        print(f"  [WARN] Webhook 응답 파싱: {e}")
        print(f"  [INFO] 응답 내용: {result.stdout[:500]}")
        webhook_response = {}

    # 4. 결과 분석
    print(f"\n[4/6] 결과 분석...")
    all_channels = webhook_response.get('allChannels', [])
    matched = webhook_response.get('matched', {})
    total_found = webhook_response.get('totalFound', 0)

    print(f"  YouTube 채널 {total_found}개 발견:")
    for ch in all_channels:
        print(f"    - {ch.get('title', '?')} (ID: {ch.get('id', '?')})")

    if matched:
        print(f"\n  자동 매칭된 채널:")
        for key, val in matched.items():
            if not key.endswith("_name"):
                name = matched.get(f"{key}_name", "")
                print(f"    {key}: {val} ({name})")
    else:
        print(f"  [INFO] 자동 매칭된 채널 없음 (채널명에 루믹스/온카/슬롯/스포츠 포함 필요)")

    # 5. 채널 ID 업데이트
    print(f"\n[5/6] 채널 성과 분석 워크플로우 업데이트...")
    channel_ids_only = {k: v for k, v in matched.items() if not k.endswith("_name")}
    if channel_ids_only:
        update_channel_ids(channel_ids_only)
    else:
        print("  [SKIP] 매칭된 채널 ID 없음 - 수동 설정 필요")

    # 6. 임시 워크플로우 삭제
    print(f"\n[6/6] 임시 워크플로우 삭제...")
    api_call('PATCH', f'/api/v1/workflows/{temp_wf_id}', {"active": False})
    delete_response = api_call('DELETE', f'/api/v1/workflows/{temp_wf_id}')
    print(f"  [OK] 임시 워크플로우 삭제 완료")

    # 최종 요약
    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)
    print("\n  [분석리포트 탭]")
    for s in SHEET_CONFIGS:
        print(f"    ✓ {s['name']}: 분석리포트 탭 + 헤더 14컬럼 생성")
    print(f"\n  [YouTube 채널 ID]")
    if channel_ids_only:
        for k, v in channel_ids_only.items():
            print(f"    ✓ {k} → {v}")
        print(f"    → 채널 성과 분석 워크플로우에 자동 반영")
    else:
        print(f"    ! 매칭된 채널 없음")
        print(f"    ! YouTube에서 채널을 생성한 후 다시 실행하거나")
        print(f"    ! n8n 에디터에서 '채널 설정' 노드의 Channel ID를 수동 입력하세요")


if __name__ == "__main__":
    main()
