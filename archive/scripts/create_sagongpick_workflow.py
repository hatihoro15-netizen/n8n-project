"""
설명형 숏츠 - 사공픽(스포츠) 워크플로우 생성 스크립트

작업 내용:
1. Google Sheets "스포츠" 탭 생성 + 헤더 추가 (임시 n8n 워크플로우 사용)
2. 기존 '유튜브 광고' 워크플로우 이름 → '설명형 숏츠 - 온카스터디'
3. 기존 워크플로우 복제 → 6개 노드 수정 → '설명형 숏츠 - 사공픽' 생성
"""
import json
import subprocess
import sys
import time
import copy

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
WEBHOOK_BASE = "https://n8n.srv1345711.hstgr.cloud/webhook"

EXISTING_WF_ID = "dEtWqwWQPJfwCWiIM0QYd"
SHEET_ID = "1gkRjLIcK3HxbnTbLCvG6oknMGVt2uz9pgboM3EF_VKg"
GOOGLE_SHEETS_CRED_ID = "CWBUyXUqCU9p5VAg"


def api_request(method, url, data=None):
    """n8n API 요청 공통 함수"""
    cmd = ["curl", "-sk", "-X", method,
           "-H", f"X-N8N-API-KEY: {API_KEY}",
           "-H", "Content-Type: application/json"]
    if data:
        cmd += ["-d", json.dumps(data, ensure_ascii=False)]
    cmd.append(url)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] curl 실패: {result.stderr}")
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"[ERROR] JSON 파싱 실패: {result.stdout[:500]}")
        return None


def step1_create_sports_tab():
    """Google Sheets '스포츠' 탭 생성 (임시 n8n 워크플로우 사용)"""
    print("\n=== Step 1: Google Sheets '스포츠' 탭 생성 ===")

    # 임시 워크플로우 생성: webhook → 탭 생성 → 헤더 추가
    temp_workflow = {
        "name": "임시 - 스포츠 탭 생성 (자동삭제)",
        "nodes": [
            {
                "parameters": {
                    "path": "create-sports-tab-temp",
                    "responseMode": "lastNode",
                    "options": {}
                },
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [0, 0],
                "id": "a0000000-0000-0000-0000-000000000001",
                "name": "Webhook",
                "webhookId": "temp-sports-tab-webhook"
            },
            {
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
                                "properties": {"title": "스포츠"}
                            }
                        }]
                    }),
                    "options": {}
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.3,
                "position": [300, 0],
                "id": "a0000000-0000-0000-0000-000000000002",
                "name": "탭 생성",
                "credentials": {
                    "googleSheetsOAuth2Api": {
                        "id": GOOGLE_SHEETS_CRED_ID,
                        "name": "Google Sheets account"
                    }
                }
            },
            {
                "parameters": {
                    "method": "PUT",
                    "url": f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/%EC%8A%A4%ED%8F%AC%EC%B8%A0!A1:G1?valueInputOption=RAW",
                    "authentication": "predefinedCredentialType",
                    "nodeCredentialType": "googleSheetsOAuth2Api",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": json.dumps({
                        "values": [["topic", "Status", "Hook", "Narration", "Subject", "Caption", "영상 URL"]]
                    }),
                    "options": {}
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.3,
                "position": [600, 0],
                "id": "a0000000-0000-0000-0000-000000000003",
                "name": "헤더 추가",
                "credentials": {
                    "googleSheetsOAuth2Api": {
                        "id": GOOGLE_SHEETS_CRED_ID,
                        "name": "Google Sheets account"
                    }
                }
            }
        ],
        "connections": {
            "Webhook": {
                "main": [[{"node": "탭 생성", "type": "main", "index": 0}]]
            },
            "탭 생성": {
                "main": [[{"node": "헤더 추가", "type": "main", "index": 0}]]
            }
        },
        "settings": {"executionOrder": "v1"}
    }

    # 1) 워크플로우 생성
    print("  임시 워크플로우 생성 중...")
    result = api_request("POST", f"{BASE}/workflows", temp_workflow)
    if not result or "id" not in result:
        print(f"  [ERROR] 임시 워크플로우 생성 실패: {result}")
        return False

    temp_wf_id = result["id"]
    print(f"  임시 워크플로우 생성 완료: {temp_wf_id}")

    # 2) 활성화
    print("  워크플로우 활성화 중...")
    activate_result = api_request("POST",
                                  f"{BASE}/workflows/{temp_wf_id}/activate")
    if not activate_result:
        # 대안: PUT으로 활성화
        activate_result = api_request("PUT",
                                      f"{BASE}/workflows/{temp_wf_id}",
                                      {"active": True, **temp_workflow})
    print(f"  활성화 결과: {activate_result.get('active', 'unknown') if activate_result else 'failed'}")

    # 3) 웹훅 호출
    print("  웹훅 호출로 스포츠 탭 생성 중...")
    time.sleep(2)  # 활성화 대기

    webhook_url = f"{WEBHOOK_BASE}/create-sports-tab-temp"
    webhook_result = subprocess.run(
        ["curl", "-sk", "-X", "POST", webhook_url,
         "-H", "Content-Type: application/json",
         "-d", "{}"],
        capture_output=True, text=True, timeout=30
    )
    print(f"  웹훅 응답: {webhook_result.stdout[:300]}")

    # 4) 임시 워크플로우 삭제
    print("  임시 워크플로우 삭제 중...")
    api_request("DELETE", f"{BASE}/workflows/{temp_wf_id}")
    print("  임시 워크플로우 삭제 완료")

    # 성공 여부 확인
    if "error" in webhook_result.stdout.lower() and "already exists" not in webhook_result.stdout.lower():
        print("  [WARN] 탭 생성에 문제가 있을 수 있습니다. 수동 확인 필요.")
        return False

    print("  스포츠 탭 생성 완료!")
    return True


def step2_rename_existing_workflow():
    """기존 '유튜브 광고' → '설명형 숏츠 - 온카스터디'로 이름 변경"""
    print("\n=== Step 2: 기존 워크플로우 이름 변경 ===")

    # 기존 워크플로우 가져오기
    wf = api_request("GET", f"{BASE}/workflows/{EXISTING_WF_ID}")
    if not wf:
        print("  [ERROR] 기존 워크플로우 조회 실패")
        return False

    print(f"  현재 이름: {wf.get('name')}")

    # PUT에 필요한 필드만 추출
    update_data = {
        "name": "설명형 숏츠 - 온카스터디",
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": {"executionOrder": "v1"}
    }

    result = api_request("PUT",
                         f"{BASE}/workflows/{EXISTING_WF_ID}",
                         update_data)
    if not result:
        print("  [ERROR] 이름 변경 실패")
        return False

    print(f"  변경 완료: {result.get('name')}")
    return True


def step3_create_sports_workflow():
    """기존 워크플로우 복제 → 6개 노드 수정 → '설명형 숏츠 - 사공픽' 생성"""
    print("\n=== Step 3: 사공픽 워크플로우 생성 ===")

    # 기존 워크플로우 가져오기
    wf = api_request("GET", f"{BASE}/workflows/{EXISTING_WF_ID}")
    if not wf:
        print("  [ERROR] 기존 워크플로우 조회 실패")
        return False

    # 딥카피
    nodes = copy.deepcopy(wf["nodes"])
    connections = copy.deepcopy(wf["connections"])

    # 수정할 노드 찾기 및 수정
    modified_count = 0

    for node in nodes:
        name = node.get("name", "")

        # 1) 주제 읽기 - 시트 탭 변경
        if name == "주제 읽기":
            node["parameters"]["sheetName"]["value"] = "스포츠"
            print(f"  [수정] 주제 읽기: 시트 탭 → 스포츠")
            modified_count += 1

        # 2) 프롬프트 생성 - 사공픽 전용 프롬프트
        elif name == "프롬프트 생성":
            node["parameters"]["jsCode"] = SAGONGPICK_PROMPT_CODE
            print(f"  [수정] 프롬프트 생성: 사공픽 전용 프롬프트")
            modified_count += 1

        # 3) 시트 기록 - 시트 탭 변경
        elif name == "시트 기록":
            node["parameters"]["sheetName"]["value"] = "스포츠"
            print(f"  [수정] 시트 기록: 시트 탭 → 스포츠")
            modified_count += 1

        # 4) 상태 업데이트 - 시트 탭 변경
        elif name == "상태 업데이트":
            node["parameters"]["sheetName"]["value"] = "스포츠"
            print(f"  [수정] 상태 업데이트: 시트 탭 → 스포츠")
            modified_count += 1

        # 5) NCA 데이터 준비 - 출력 파일명 변경
        elif name == "NCA 데이터 준비":
            old_code = node["parameters"]["jsCode"]
            new_code = old_code.replace(
                'file_name: "youtube_ad_final.mp4"',
                'file_name: "sports_shorts_final.mp4"'
            )
            node["parameters"]["jsCode"] = new_code
            print(f"  [수정] NCA 데이터 준비: 파일명 → sports_shorts_final.mp4")
            modified_count += 1

    print(f"  총 {modified_count}개 노드 수정 완료")

    if modified_count != 5:
        print(f"  [WARN] 예상 5개인데 {modified_count}개 수정됨. 확인 필요.")

    # 새 워크플로우 생성
    new_workflow = {
        "name": "설명형 숏츠 - 사공픽",
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"}
    }

    result = api_request("POST", f"{BASE}/workflows", new_workflow)
    if not result or "id" not in result:
        print(f"  [ERROR] 워크플로우 생성 실패: {result}")
        return False

    new_wf_id = result["id"]
    print(f"  사공픽 워크플로우 생성 완료!")
    print(f"  ID: {new_wf_id}")
    print(f"  이름: {result.get('name')}")
    return new_wf_id


def step4_verify():
    """검증: n8n 워크플로우 2개, Google Sheets 탭 확인"""
    print("\n=== Step 4: 검증 ===")

    # 모든 워크플로우 목록 가져오기
    result = api_request("GET", f"{BASE}/workflows")
    if not result:
        print("  [ERROR] 워크플로우 목록 조회 실패")
        return False

    workflows = result.get("data", [])
    target_names = ["설명형 숏츠 - 온카스터디", "설명형 숏츠 - 사공픽"]
    found = []

    for wf in workflows:
        if wf["name"] in target_names:
            found.append(wf)
            print(f"  [확인] {wf['name']} (ID: {wf['id']})")

    if len(found) == 2:
        print("\n  워크플로우 2개 확인 완료!")
    else:
        print(f"\n  [WARN] {len(found)}/2 워크플로우만 확인됨")

    return len(found) == 2


# 사공픽(스포츠) 전용 프롬프트 생성 코드
SAGONGPICK_PROMPT_CODE = r"""const topic = $input.first().json.topic || $input.first().json['주제'] || '';

if (!topic) {
  throw new Error('topic이 비어있습니다. 시트에 topic 컬럼을 확인하세요.');
}

const prompt = `너는 '사공픽' 스포츠 분석/예측 커뮤니티의 YouTube Shorts 설명형 콘텐츠 기획자야.
아래 주제로 40~55초 분량의 설명형 나레이션 숏츠 스크립트를 작성해줘.

## 반드시 지킬 주제
${topic}

위 주제를 중심으로 콘텐츠를 작성하되, 후반부에 '사공픽'을 자연스럽게 1~2회 언급해 (광고 티 없이).
모든 scene의 dialogue는 반드시 "${topic}" 주제와 직접 관련된 내용이어야 해.
주제와 무관한 내용(요리, 패션, 여행 등)은 절대 포함하지 마.

## 사공픽 소개
사공픽은 스포츠 분석/예측 커뮤니티로, 축구/야구/농구 등 주요 스포츠 경기 분석, 승부 예측, 전문가 픽 공유 등을 제공합니다.
커뮤니티 기능으로는 자유게시판, 전문가 분석 게시판, 경기 리뷰, 통계 자료실 등이 있고,
포인트 시스템을 통해 다양한 활동에 참여할 수 있습니다.

## 영상 스타일
- 총 40~55초, 9:16 세로 영상
- 상단: 고정된 훅 제목 (핵심 키워드 1~2개는 <y>태그</y>로 감싸기)
- 중간: AI 생성 이미지 (장면마다 다른 분위기)
- 하단: 나레이션 자막
- 오디오: TTS 나레이션

## 나레이션 규칙
1. 시청자를 끌어당기는 강렬한 hook으로 시작 (질문 or 충격적 사실)
2. "${topic}" 주제의 핵심 정보를 간결하게 전달
3. 자연스러운 한국어 구어체 (반말+존댓말 믹스, "~거든요", "~잖아요")
4. 후반부에 사공픽을 해결책으로 자연스럽게 언급
5. CTA로 마무리 ("사공픽 검색해보세요", "링크 확인" 등)
6. 각 장면은 4~7초 분량 (한 문장, 짧고 임팩트 있게)

## 이미지 프롬프트 규칙
- 영어로 작성
- "${topic}" 주제와 직접 관련된 시각적 장면 묘사
- 항상 포함: "photorealistic, cinematic lighting, 4k quality, portrait orientation 9:16"
- 감정/분위기를 강조 (excited, focused, analytical, confident 등)

## 출력 (순수 JSON, 코드블록 없이)
{
  "hook_title": "훅 제목 (15자 이내, 핵심 키워드 <y>태그</y>)",
  "scenes": [
    {
      "dialogue": "나레이션 텍스트 (한 문장)",
      "image_prompt": "영어 이미지 프롬프트",
      "keyword": "Pexels 검색용 영어 키워드 1~3단어 (예: soccer analysis, basketball stats)"
    }
  ],
  "Subject": "영상 제목 #사공픽 #스포츠분석 + 주제관련 해시태그",
  "Caption": "영상 설명 #사공픽 #스포츠분석 + 주제관련 해시태그",
  "Comment": "구글에 사공픽 검색!"
}

주의:
- scenes는 7~10개
- 반드시 위 JSON 형식 그대로 출력
- "${topic}" 주제와 무관한 내용 절대 금지`;

return [{
  json: {
    prompt,
    topic,
    row_number: $input.first().json.row_number,
    ...$input.first().json
  }
}];"""


if __name__ == "__main__":
    print("=" * 60)
    print("설명형 숏츠 워크플로우 분리: 온카스터디 + 사공픽")
    print("=" * 60)

    # Step 1: Google Sheets 스포츠 탭 생성
    tab_ok = step1_create_sports_tab()
    if not tab_ok:
        print("\n[INFO] 스포츠 탭 생성 실패. Google Sheets에서 수동으로 '스포츠' 탭을 추가해주세요.")
        print("       (시트 URL: https://docs.google.com/spreadsheets/d/1gkRjLIcK3HxbnTbLCvG6oknMGVt2uz9pgboM3EF_VKg)")
        resp = input("계속 진행하시겠습니까? (y/n): ")
        if resp.lower() != "y":
            sys.exit(1)

    # Step 2: 기존 워크플로우 이름 변경
    rename_ok = step2_rename_existing_workflow()
    if not rename_ok:
        print("[ERROR] 워크플로우 이름 변경 실패. 중단합니다.")
        sys.exit(1)

    # Step 3: 사공픽 워크플로우 생성
    new_wf_id = step3_create_sports_workflow()
    if not new_wf_id:
        print("[ERROR] 사공픽 워크플로우 생성 실패. 중단합니다.")
        sys.exit(1)

    # Step 4: 검증
    step4_verify()

    print("\n" + "=" * 60)
    print("완료!")
    print(f"  온카스터디: {EXISTING_WF_ID}")
    print(f"  사공픽: {new_wf_id}")
    print("=" * 60)
