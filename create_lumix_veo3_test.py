#!/usr/bin/env python3
"""
루믹스 Veo3 Fast 테스트 워크플로우 생성
- Kie.ai Veo3 Fast API ($0.40/8초)
- 야나두 스타일 대화형 숏폼
- 기존 루믹스 v3와 별도 워크플로우
"""
import json
import subprocess
import sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"

# Credentials (기존 연결된 것 재사용)
CRED_KIE = {"id": "34ktW72w0p8fCfUQ", "name": "Kie.ai"}
CRED_GEMINI = {"id": "IKP349r08J9Hoz5E", "name": "Google Gemini(PaLM) Api account"}
CRED_SHEETS = {"id": "CWBUyXUqCU9p5VAg", "name": "Google Sheets account"}
CRED_YOUTUBE = {"id": "kRKBMYWf6cB72qUi", "name": "YouTube OAuth2 API"}


def build_workflow():
    """Veo3 테스트 워크플로우 JSON 생성"""

    nodes = []

    # ============================================================
    # 1. Manual Trigger
    # ============================================================
    nodes.append({
        "parameters": {},
        "id": "veo3-trigger",
        "name": "테스트 실행",
        "type": "n8n-nodes-base.manualTrigger",
        "typeVersion": 1,
        "position": [0, 300]
    })

    # ============================================================
    # 2. AI 시나리오 생성 (Gemini)
    # ============================================================
    scenario_prompt = """너는 YouTube Shorts 대화형 시나리오 작가야.
루믹스 솔루션(카지노 솔루션 사업) 관련 8초짜리 AI 영상 시나리오를 만들어줘.

참고 스타일: 야나두 영어회화 쇼츠 (외국인이 한국 음식 먹으면서 대화하는 AI 영상)
우리는 이 스타일을 카지노 솔루션 사업에 맞게 변형할 거야.

규칙:
1. 2명의 인물이 대화하는 장면 (예: 사업가끼리, 개발자와 클라이언트 등)
2. 8초 안에 완결되는 짧은 대화
3. 간접 광고 - 카지노 솔루션 사업을 직접 언급하지 않고 '시스템', '솔루션', '플랫폼' 등으로 표현
4. 한국어 대화
5. 시각적으로 흥미로운 장소 (카페, 고급 사무실, 서버룸, 옥상 등)
6. 첫 대사가 후킹 (놀라운 사실, 질문, 충격적 수치 등)

반드시 아래 JSON 형식으로만 응답:
{
  "veo3_prompt": "Veo3에 보낼 영어 프롬프트. 장면 묘사 + 대화 내용 포함. 예: Two Korean businessmen sitting in a modern cafe. Man A says '이 시스템 하나로 월 3억을 벌었다고?' Man B smiles and replies '자동화가 핵심이지'. Camera slowly zooms in. Cinematic lighting, 9:16 vertical format.",
  "subject": "YouTube 제목 (한국어, 호기심 유발, 30자 이내)",
  "caption": "YouTube 설명 (한국어, 2줄, 해시태그 포함)",
  "comment": "첫 댓글 (호기심/참여 유도, 1줄)"
}"""

    nodes.append({
        "parameters": {
            "modelName": "models/gemini-2.5-flash-lite-preview-06-17",
            "text": scenario_prompt,
            "options": {
                "temperature": 0.9
            }
        },
        "id": "veo3-scenario",
        "name": "AI 시나리오 생성",
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [250, 300],
        "credentials": {
            "googlePalmApi": CRED_GEMINI
        }
    })

    # ============================================================
    # 3. 시나리오 파싱 (Code)
    # ============================================================
    parse_code = r"""const text = $input.first().json.content.parts[0].text;
const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();

let data;
try {
  data = JSON.parse(cleanText);
} catch (e) {
  // JSON 파싱 실패시 기본값
  data = {
    veo3_prompt: "Two Korean businessmen in a sleek modern office. Man A looks at a laptop screen and says '이 시스템 하나로 운영이 전부 자동화됐어.' Man B nods impressed and replies '이게 진짜 미래지.' Cinematic lighting, slow camera movement, 9:16 vertical video.",
    subject: "자동화 시스템의 놀라운 비밀",
    caption: "이런 시스템이 있었다니... #솔루션 #자동화 #IT사업",
    comment: "이거 실제로 가능한 건가요?"
  };
}

return [{
  json: {
    veo3_prompt: data.veo3_prompt,
    subject: data.subject,
    caption: data.caption,
    comment: data.comment
  }
}];"""

    nodes.append({
        "parameters": {
            "jsCode": parse_code
        },
        "id": "veo3-parse",
        "name": "시나리오 파싱",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [500, 300]
    })

    # ============================================================
    # 4. Veo3 영상 생성 (HTTP Request → Kie.ai)
    # ============================================================
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://api.kie.ai/api/v1/veo/generate",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": '={{ JSON.stringify({ "prompt": $json.veo3_prompt, "model": "veo3_fast", "aspect_ratio": "9:16" }) }}',
            "options": {}
        },
        "id": "veo3-generate",
        "name": "Veo3 영상 생성",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [750, 300],
        "credentials": {
            "httpHeaderAuth": CRED_KIE
        }
    })

    # ============================================================
    # 5. Veo3 대기 (Wait 240초 = 4분)
    # ============================================================
    nodes.append({
        "parameters": {
            "amount": 240
        },
        "id": "veo3-wait",
        "name": "Veo3 대기",
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [1000, 300],
        "webhookId": "veo3-wait-hook"
    })

    # ============================================================
    # 6. Veo3 결과 확인 (HTTP Request)
    # ============================================================
    nodes.append({
        "parameters": {
            "url": "=https://api.kie.ai/api/v1/veo/record-info?taskId={{ $json.data.taskId }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "id": "veo3-result",
        "name": "Veo3 결과",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [1250, 300],
        "credentials": {
            "httpHeaderAuth": CRED_KIE
        }
    })

    # ============================================================
    # 7. 결과 판단 (IF - successFlag == 1)
    # ============================================================
    nodes.append({
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "typeValidation": "strict"
                },
                "conditions": [
                    {
                        "id": "veo3-check",
                        "leftValue": "={{ $json.data.successFlag }}",
                        "rightValue": 1,
                        "operator": {
                            "type": "number",
                            "operation": "equals"
                        }
                    }
                ],
                "combinator": "and"
            }
        },
        "id": "veo3-check",
        "name": "생성 완료?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [1500, 300]
    })

    # ============================================================
    # 8a. 성공 → 영상 URL 추출
    # ============================================================
    success_code = r"""const data = $input.first().json.data;
let resultUrls = [];

if (data.response && data.response.resultUrls) {
  if (typeof data.response.resultUrls === 'string') {
    try {
      resultUrls = JSON.parse(data.response.resultUrls);
    } catch(e) {
      resultUrls = [data.response.resultUrls];
    }
  } else {
    resultUrls = data.response.resultUrls;
  }
}

const videoUrl = resultUrls[0] || '';

// 시나리오 파싱 데이터 가져오기
const scenario = $('시나리오 파싱').first().json;

return [{
  json: {
    video_url: videoUrl,
    taskId: data.taskId,
    resolution: data.response?.resolution || '',
    subject: scenario.subject,
    caption: scenario.caption,
    comment: scenario.comment,
    veo3_prompt: scenario.veo3_prompt,
    status: '성공'
  }
}];"""

    nodes.append({
        "parameters": {
            "jsCode": success_code
        },
        "id": "veo3-success",
        "name": "영상 URL 추출",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1750, 200]
    })

    # ============================================================
    # 8b. 미완료 → 추가 대기 60초 + 재확인
    # ============================================================
    nodes.append({
        "parameters": {
            "amount": 60
        },
        "id": "veo3-retry-wait",
        "name": "추가 대기",
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [1750, 450],
        "webhookId": "veo3-retry-hook"
    })

    nodes.append({
        "parameters": {
            "url": "=https://api.kie.ai/api/v1/veo/record-info?taskId={{ $('Veo3 영상 생성').first().json.data.taskId }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "id": "veo3-retry-result",
        "name": "Veo3 재확인",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [2000, 450],
        "credentials": {
            "httpHeaderAuth": CRED_KIE
        }
    })

    # ============================================================
    # 9. 재확인 후 URL 추출
    # ============================================================
    retry_success_code = r"""const data = $input.first().json.data;
let resultUrls = [];

if (data.response && data.response.resultUrls) {
  if (typeof data.response.resultUrls === 'string') {
    try {
      resultUrls = JSON.parse(data.response.resultUrls);
    } catch(e) {
      resultUrls = [data.response.resultUrls];
    }
  } else {
    resultUrls = data.response.resultUrls;
  }
}

const videoUrl = resultUrls[0] || '';
const scenario = $('시나리오 파싱').first().json;

const status = data.successFlag === 1 ? '성공' : '실패 (successFlag: ' + data.successFlag + ')';

return [{
  json: {
    video_url: videoUrl,
    taskId: data.taskId,
    resolution: data.response?.resolution || '',
    subject: scenario.subject,
    caption: scenario.caption,
    comment: scenario.comment,
    veo3_prompt: scenario.veo3_prompt,
    status: status,
    successFlag: data.successFlag
  }
}];"""

    nodes.append({
        "parameters": {
            "jsCode": retry_success_code
        },
        "id": "veo3-retry-extract",
        "name": "최종 결과",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2250, 450]
    })

    # ============================================================
    # Connections
    # ============================================================
    connections = {
        "테스트 실행": {
            "main": [[{"node": "AI 시나리오 생성", "type": "main", "index": 0}]]
        },
        "AI 시나리오 생성": {
            "main": [[{"node": "시나리오 파싱", "type": "main", "index": 0}]]
        },
        "시나리오 파싱": {
            "main": [[{"node": "Veo3 영상 생성", "type": "main", "index": 0}]]
        },
        "Veo3 영상 생성": {
            "main": [[{"node": "Veo3 대기", "type": "main", "index": 0}]]
        },
        "Veo3 대기": {
            "main": [[{"node": "Veo3 결과", "type": "main", "index": 0}]]
        },
        "Veo3 결과": {
            "main": [[{"node": "생성 완료?", "type": "main", "index": 0}]]
        },
        "생성 완료?": {
            "main": [
                [{"node": "영상 URL 추출", "type": "main", "index": 0}],
                [{"node": "추가 대기", "type": "main", "index": 0}]
            ]
        },
        "추가 대기": {
            "main": [[{"node": "Veo3 재확인", "type": "main", "index": 0}]]
        },
        "Veo3 재확인": {
            "main": [[{"node": "최종 결과", "type": "main", "index": 0}]]
        }
    }

    workflow = {
        "name": "루믹스 Veo3 테스트",
        "nodes": nodes,
        "connections": connections,
        "settings": {
            "executionOrder": "v1"
        }
    }

    return workflow


def upload_workflow(workflow_data):
    """n8n에 워크플로우 업로드"""
    with open('/tmp/lumix_veo3_test.json', 'w') as f:
        json.dump(workflow_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'POST',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_veo3_test.json',
        f'{N8N_URL}/api/v1/workflows'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if 'id' in response:
            print(f"  [OK] 워크플로우 생성 성공!")
            print(f"  ID: {response['id']}")
            print(f"  이름: {response['name']}")
            print(f"  노드: {len(response.get('nodes', []))}개")
            return response['id']
        else:
            print(f"  [ERROR] {json.dumps(response, ensure_ascii=False)[:500]}")
            return None
    except json.JSONDecodeError:
        print(f"  [ERROR] 응답 파싱 실패")
        print(f"  stdout: {result.stdout[:300]}")
        return None


def activate_workflow(workflow_id):
    """워크플로우 활성화"""
    result = subprocess.run([
        'curl', '-sk', '-X', 'POST',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{workflow_id}/activate'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        print(f"  [OK] 활성화: active={response.get('active')}")
    except Exception:
        print("  [WARN] 활성화 응답 확인 필요")


def main():
    print("=" * 55)
    print("루믹스 Veo3 Fast 테스트 워크플로우 생성")
    print("=" * 55)

    print("\n[1/3] 워크플로우 빌드...")
    workflow = build_workflow()
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    print("\n[2/3] n8n 업로드...")
    workflow_id = upload_workflow(workflow)
    if not workflow_id:
        print("  업로드 실패!")
        sys.exit(1)

    print("\n[3/3] 활성화...")
    activate_workflow(workflow_id)

    print("\n" + "=" * 55)
    print("완료!")
    print("=" * 55)
    print(f"\n  워크플로우 ID: {workflow_id}")
    print(f"  URL: {N8N_URL}/workflow/{workflow_id}")
    print(f"\n  테스트 방법:")
    print(f"  1. n8n에서 워크플로우 열기")
    print(f"  2. 'Execute workflow' 클릭")
    print(f"  3. ~5분 후 결과 확인")
    print(f"\n  비용: $0.40/영상 (Veo3 Fast)")
    print(f"  결과: 영상 URL 추출 또는 최종 결과 노드에서 확인")


if __name__ == "__main__":
    main()
