#!/usr/bin/env python3
"""
루믹스 Veo3 30초 숏폼 워크플로우
- 4개 Scene × 8초 = 32초
- Veo3 Fast ($0.40 × 4 = $1.60/영상)
- Creatomate로 4개 합성
"""
import json
import subprocess
import sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
OLD_WORKFLOW_ID = "MPFGLXw5m8bfokIo"  # 기존 테스트 워크플로우

# Credentials
CRED_KIE = {"id": "34ktW72w0p8fCfUQ", "name": "Kie.ai"}
CRED_GEMINI = {"id": "IKP349r08J9Hoz5E", "name": "Google Gemini(PaLM) Api account"}
CRED_CREATOMATE = {"id": "ENPg3HkwLqzCSYTQ", "name": "Header Auth account 2"}
CRED_SHEETS = {"id": "CWBUyXUqCU9p5VAg", "name": "Google Sheets account"}
CRED_YOUTUBE = {"id": "kRKBMYWf6cB72qUi", "name": "YouTube OAuth2 API"}


def build_workflow():
    nodes = []

    # ============================================================
    # 1. Manual Trigger
    # ============================================================
    nodes.append({
        "parameters": {},
        "id": "v3-trigger",
        "name": "테스트 실행",
        "type": "n8n-nodes-base.manualTrigger",
        "typeVersion": 1,
        "position": [0, 400]
    })

    # ============================================================
    # 2. AI 시나리오 생성 (Gemini)
    # ============================================================
    scenario_prompt = """너는 YouTube Shorts 대화형 시나리오 전문 작가야.
루믹스 솔루션(온라인 카지노 솔루션 사업) 관련 30초짜리 AI 영상 시나리오를 만들어줘.
4개의 연속 장면(각 8초)으로 구성된 하나의 스토리야.

참고: 야나두 영어회화 쇼츠처럼 AI가 실사 인물을 생성하고 대화하는 방식이야.

규칙:
1. 등장인물: 한국인 남자 2명 (30대, 사업가 느낌)
2. 4개 장면이 하나의 스토리로 자연스럽게 이어져야 함
3. 간접 광고 - '카지노'라는 단어 절대 사용 금지. '시스템', '솔루션', '플랫폼', '자동화' 등으로 표현
4. 모든 대사는 한국어
5. Scene 1은 강력한 후킹 (충격적 수치, 질문, 반전)
6. Scene 4는 여운 남기는 클로징
7. 각 장면의 배경/장소가 달라도 됨 (카페, 사무실, 옥상, 서버룸 등)
8. Veo3 프롬프트는 반드시 영어로, 대사만 한국어로

스토리 구조:
- Scene 1 (0-8초): 후킹 - 놀라운 사실로 시선 끌기
- Scene 2 (8-16초): 궁금증 - 어떻게 가능한지 질문
- Scene 3 (16-24초): 증거 - 실제 결과 보여주기
- Scene 4 (24-32초): 클로징 - 행동 유도

반드시 아래 JSON 형식으로만 응답:
{
  "scenes": [
    {
      "scene_num": 1,
      "veo3_prompt": "영어 장면 묘사 + 한국어 대사. 예: Two Korean men in their 30s sitting at a luxury cafe. Man A in a navy suit sips coffee. Man B rushes in excitedly. Man B says '야, 너 진짜 월 5억 번다며?' Man A smiles calmly and replies '시스템이 알아서 해주니까.' Warm cinematic lighting, shallow depth of field, 9:16 vertical format."
    },
    {
      "scene_num": 2,
      "veo3_prompt": "장면2 영어 묘사 + 한국어 대사..."
    },
    {
      "scene_num": 3,
      "veo3_prompt": "장면3 영어 묘사 + 한국어 대사..."
    },
    {
      "scene_num": 4,
      "veo3_prompt": "장면4 영어 묘사 + 한국어 대사..."
    }
  ],
  "subject": "YouTube 제목 (한국어, 호기심 유발, 30자 이내)",
  "caption": "YouTube 설명 (한국어, 2-3줄, 해시태그 5개 포함)",
  "comment": "첫 댓글 (참여 유도, 1줄)"
}

주의: 각 scene의 veo3_prompt는 독립적으로 Veo3에 전달되므로, 인물 외모/옷차림 묘사를 매 장면마다 동일하게 반복해야 인물 일관성이 유지됨."""

    nodes.append({
        "parameters": {
            "modelName": "models/gemini-2.5-flash-lite-preview-06-17",
            "text": scenario_prompt,
            "options": {
                "temperature": 0.85
            }
        },
        "id": "v3-scenario",
        "name": "AI 시나리오 생성",
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [250, 400],
        "credentials": {
            "googlePalmApi": CRED_GEMINI
        }
    })

    # ============================================================
    # 3. 시나리오 파싱 → 4개 아이템 출력
    # ============================================================
    parse_code = r"""const text = $input.first().json.content.parts[0].text;
const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();

let data;
try {
  data = JSON.parse(cleanText);
} catch (e) {
  // 파싱 실패시 기본 시나리오
  data = {
    scenes: [
      {
        scene_num: 1,
        veo3_prompt: "Two Korean businessmen in their 30s at a sleek modern cafe. Man A wears a navy suit, short black hair. Man B wears a gray suit, slightly longer hair. Man B rushes in and sits down, saying '야, 너 진짜 회사 때려치운 거야?' Man A sips his coffee calmly and replies '때려치운 게 아니라, 이제 필요가 없어진 거지.' Warm cinematic lighting, shallow depth of field, 9:16 vertical format."
      },
      {
        scene_num: 2,
        veo3_prompt: "Same two Korean businessmen at the same cafe, closer shot. Man A in navy suit, Man B in gray suit. Man B leans forward curiously asking '무슨 시스템이 알아서 다 해준다는 거야?' Man A replies confidently '운영, 정산, 관리... 전부 자동이야. 나는 확인만 해.' Man B's eyes widen saying '진짜?' Tight two-shot, warm cafe background, 9:16 vertical format."
      },
      {
        scene_num: 3,
        veo3_prompt: "Same two Korean businessmen. Man A in navy suit turns his laptop screen toward Man B in gray suit. The laptop shows a glowing dashboard. Man A says '지난달 수익이야.' Man B stares at the screen in shock saying '이게... 한 달?' Man A nods saying '시스템이 24시간 돌아가니까.' Over-the-shoulder shot, laptop glow on faces, 9:16 vertical format."
      },
      {
        scene_num: 4,
        veo3_prompt: "Same two Korean businessmen walking out of the cafe onto a city street at night. Man A in navy suit, Man B in gray suit. City lights in background. Man B asks '나도 할 수 있어?' Man A puts his hand on B's shoulder and says '누구나 할 수 있어. 중요한 건 시작하는 거지.' Man B pulls out his phone and starts typing. Wide shot, city night bokeh, 9:16 vertical format."
      }
    ],
    subject: "회사 때려치운 친구의 비밀",
    caption: "시스템 하나로 인생이 바뀐 이야기\n자동화의 힘을 믿으세요\n#솔루션 #자동화 #시스템 #수익 #사업",
    comment: "이 시스템 진짜 있는 건가요?"
  };
}

// 4개 아이템으로 분리 출력
const items = data.scenes.map((scene, idx) => ({
  json: {
    scene_num: scene.scene_num || (idx + 1),
    veo3_prompt: scene.veo3_prompt,
    subject: data.subject,
    caption: data.caption,
    comment: data.comment,
    total_scenes: data.scenes.length
  }
}));

return items;"""

    nodes.append({
        "parameters": {
            "jsCode": parse_code
        },
        "id": "v3-parse",
        "name": "시나리오 파싱",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [500, 400]
    })

    # ============================================================
    # 4. Veo3 영상 생성 (4개 아이템 각각 API 호출)
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
        "id": "v3-generate",
        "name": "Veo3 영상 생성",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [750, 400],
        "credentials": {
            "httpHeaderAuth": CRED_KIE
        }
    })

    # ============================================================
    # 5. Veo3 대기 (4분 = 240초)
    # ============================================================
    nodes.append({
        "parameters": {
            "amount": 240
        },
        "id": "v3-wait",
        "name": "Veo3 대기",
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [1000, 400],
        "webhookId": "v3-wait-hook-30s"
    })

    # ============================================================
    # 6. Veo3 결과 확인 (4개 아이템 각각)
    # ============================================================
    nodes.append({
        "parameters": {
            "url": "=https://api.kie.ai/api/v1/veo/record-info?taskId={{ $json.data.taskId }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "id": "v3-result",
        "name": "Veo3 결과",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [1250, 400],
        "credentials": {
            "httpHeaderAuth": CRED_KIE
        }
    })

    # ============================================================
    # 7. 영상 URL 추출 (4개 아이템 각각)
    # ============================================================
    extract_code = r"""const items = $input.all();
const results = [];

for (const item of items) {
  const data = item.json.data;
  let videoUrl = '';

  if (data && data.successFlag === 1 && data.response) {
    let urls = data.response.resultUrls;
    if (typeof urls === 'string') {
      try { urls = JSON.parse(urls); } catch(e) { urls = [urls]; }
    }
    videoUrl = (urls && urls[0]) || '';
  }

  // 시나리오 파싱 데이터 가져오기
  const sceneIdx = results.length;
  const scenario = $('시나리오 파싱').all()[sceneIdx]?.json || {};

  results.push({
    json: {
      scene_num: scenario.scene_num || (sceneIdx + 1),
      video_url: videoUrl,
      taskId: data?.taskId || '',
      successFlag: data?.successFlag,
      subject: scenario.subject || '',
      caption: scenario.caption || '',
      comment: scenario.comment || ''
    }
  });
}

return results;"""

    nodes.append({
        "parameters": {
            "jsCode": extract_code
        },
        "id": "v3-extract",
        "name": "영상 URL 추출",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1500, 400]
    })

    # ============================================================
    # 8. Aggregate (4개 → 1개)
    # ============================================================
    nodes.append({
        "parameters": {
            "aggregate": "aggregateAllItemData",
            "options": {}
        },
        "id": "v3-aggregate",
        "name": "Aggregate",
        "type": "n8n-nodes-base.aggregate",
        "typeVersion": 1,
        "position": [1750, 400]
    })

    # ============================================================
    # 9. Creatomate 합성 (Code - 4개 영상 이어붙이기 payload 생성)
    # ============================================================
    creatomate_code = r"""const allData = $input.first().json.data;

// 장면 순서대로 정렬
const scenes = allData.sort((a, b) => a.scene_num - b.scene_num);

// 각 장면 8초씩
const sceneDuration = 8;
const totalDuration = scenes.length * sceneDuration;

// Creatomate source 기반 렌더링 (템플릿 없이)
const elements = [];

for (let i = 0; i < scenes.length; i++) {
  const scene = scenes[i];
  if (!scene.video_url) continue;

  elements.push({
    type: "video",
    track: 1,
    time: i * sceneDuration,
    duration: sceneDuration,
    source: scene.video_url,
    fit: "cover",
    audio_enabled: true
  });
}

// 실패한 장면 체크
const failedScenes = scenes.filter(s => !s.video_url);
if (failedScenes.length > 0) {
  const failedNums = failedScenes.map(s => s.scene_num).join(', ');
  // 실패한 장면이 있어도 나머지로 계속 진행
}

const payload = {
  source: {
    output_format: "mp4",
    width: 1080,
    height: 1920,
    duration: totalDuration,
    elements: elements
  }
};

const subject = scenes[0]?.subject || '루믹스 Veo3 테스트';
const caption = scenes[0]?.caption || '';
const comment = scenes[0]?.comment || '';

return [{
  json: {
    creatomate_payload: payload,
    subject: subject,
    caption: caption,
    comment: comment,
    total_scenes: scenes.length,
    success_scenes: scenes.filter(s => s.video_url).length,
    failed_scenes: failedScenes ? failedScenes.length : 0,
    video_urls: scenes.map(s => s.video_url)
  }
}];"""

    nodes.append({
        "parameters": {
            "jsCode": creatomate_code
        },
        "id": "v3-creatomate-build",
        "name": "Creatomate 합성",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2000, 400]
    })

    # ============================================================
    # 10. Creatomate 렌더 (HTTP Request)
    # ============================================================
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://api.creatomate.com/v1/renders",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify($json.creatomate_payload) }}",
            "options": {
                "timeout": 600000
            }
        },
        "id": "v3-creatomate-render",
        "name": "Creatomate 렌더",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [2250, 400],
        "credentials": {
            "httpHeaderAuth": CRED_CREATOMATE
        }
    })

    # ============================================================
    # 11. 렌더 대기 (2분)
    # ============================================================
    nodes.append({
        "parameters": {
            "amount": 120
        },
        "id": "v3-render-wait",
        "name": "렌더 대기",
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [2500, 400],
        "webhookId": "v3-render-wait-hook"
    })

    # ============================================================
    # 12. 렌더 결과 확인
    # ============================================================
    nodes.append({
        "parameters": {
            "url": "=https://api.creatomate.com/v1/renders/{{ Array.isArray($json) ? $json[0].id : $json.id }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "id": "v3-render-result",
        "name": "렌더 결과",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [2750, 400],
        "credentials": {
            "httpHeaderAuth": CRED_CREATOMATE
        }
    })

    # ============================================================
    # 13. 최종 출력
    # ============================================================
    final_code = r"""const render = $input.first().json;
const scenario = $('Creatomate 합성').first().json;

// Creatomate 렌더 결과에서 URL 추출
let finalUrl = '';
if (render.url) {
  finalUrl = render.url;
} else if (render.status === 'succeeded' && render.url) {
  finalUrl = render.url;
}

return [{
  json: {
    final_video_url: finalUrl,
    render_status: render.status || 'unknown',
    render_id: render.id || '',
    subject: scenario.subject,
    caption: scenario.caption,
    comment: scenario.comment,
    success_scenes: scenario.success_scenes,
    total_scenes: scenario.total_scenes,
    individual_urls: scenario.video_urls
  }
}];"""

    nodes.append({
        "parameters": {
            "jsCode": final_code
        },
        "id": "v3-final",
        "name": "최종 출력",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [3000, 400]
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
            "main": [[{"node": "영상 URL 추출", "type": "main", "index": 0}]]
        },
        "영상 URL 추출": {
            "main": [[{"node": "Aggregate", "type": "main", "index": 0}]]
        },
        "Aggregate": {
            "main": [[{"node": "Creatomate 합성", "type": "main", "index": 0}]]
        },
        "Creatomate 합성": {
            "main": [[{"node": "Creatomate 렌더", "type": "main", "index": 0}]]
        },
        "Creatomate 렌더": {
            "main": [[{"node": "렌더 대기", "type": "main", "index": 0}]]
        },
        "렌더 대기": {
            "main": [[{"node": "렌더 결과", "type": "main", "index": 0}]]
        },
        "렌더 결과": {
            "main": [[{"node": "최종 출력", "type": "main", "index": 0}]]
        }
    }

    return {
        "name": "루믹스 Veo3 30초 숏폼",
        "nodes": nodes,
        "connections": connections,
        "settings": {
            "executionOrder": "v1"
        }
    }


def delete_old_workflow():
    """기존 8초 테스트 워크플로우 비활성화"""
    subprocess.run([
        'curl', '-sk', '-X', 'POST',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{OLD_WORKFLOW_ID}/deactivate'
    ], capture_output=True, text=True)
    print(f"  [OK] 기존 테스트 워크플로우 비활성화 ({OLD_WORKFLOW_ID})")


def upload_workflow(workflow_data):
    with open('/tmp/lumix_veo3_30s.json', 'w') as f:
        json.dump(workflow_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'POST',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_veo3_30s.json',
        f'{N8N_URL}/api/v1/workflows'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if 'id' in response:
            print(f"  [OK] 생성 성공!")
            print(f"  ID: {response['id']}")
            print(f"  노드: {len(response.get('nodes', []))}개")
            return response['id']
        else:
            print(f"  [ERROR] {json.dumps(response, ensure_ascii=False)[:500]}")
            return None
    except json.JSONDecodeError:
        print(f"  [ERROR] 응답 파싱 실패: {result.stdout[:300]}")
        return None


def activate_workflow(workflow_id):
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
    print("=" * 60)
    print("루믹스 Veo3 30초 숏폼 워크플로우")
    print("=" * 60)

    print("\n[1/4] 기존 테스트 워크플로우 정리...")
    delete_old_workflow()

    print("\n[2/4] 워크플로우 빌드...")
    workflow = build_workflow()
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    print("\n[3/4] n8n 업로드...")
    workflow_id = upload_workflow(workflow)
    if not workflow_id:
        sys.exit(1)

    print("\n[4/4] 활성화...")
    activate_workflow(workflow_id)

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)
    print(f"\n  워크플로우: 루믹스 Veo3 30초 숏폼")
    print(f"  ID: {workflow_id}")
    print(f"  URL: {N8N_URL}/workflow/{workflow_id}")
    print(f"\n  구조:")
    print(f"  테스트 실행 → AI 시나리오 생성 (Gemini)")
    print(f"    → 시나리오 파싱 (4개 장면)")
    print(f"      → Veo3 영상 생성 ×4 ($0.40 × 4)")
    print(f"        → 4분 대기")
    print(f"          → 결과 확인 ×4")
    print(f"            → Aggregate")
    print(f"              → Creatomate 합성 (4개 → 1개)")
    print(f"                → 2분 대기")
    print(f"                  → 최종 출력 (30초 mp4)")
    print(f"\n  비용: $1.60/영상 + Creatomate 렌더 비용")
    print(f"  소요시간: ~7분 (Veo3 4분 + 렌더 2분 + 처리)")
    print(f"\n  테스트: n8n에서 Execute workflow 클릭")


if __name__ == "__main__":
    main()
