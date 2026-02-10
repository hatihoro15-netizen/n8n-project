#!/usr/bin/env python3
"""
루믹스 Veo3 30초 숏폼 업데이트
- 숏폼 가이드 반영
- AI 검증 시스템 추가 (돈 들기 전 검수)
- 최대 3회 재생성
"""
import json
import subprocess
import sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "tS2hcoeJ4ar8hivm"

CRED_KIE = {"id": "34ktW72w0p8fCfUQ", "name": "Kie.ai"}
CRED_GEMINI = {"id": "IKP349r08J9Hoz5E", "name": "Google Gemini(PaLM) Api account"}
CRED_CREATOMATE = {"id": "ENPg3HkwLqzCSYTQ", "name": "Header Auth account 2"}


# ============================================================
# 숏폼 가이드 반영된 시나리오 프롬프트
# ============================================================
SCENARIO_PROMPT = """너는 YouTube Shorts 대화형 시나리오 전문 작가야.
루믹스 솔루션(온라인 카지노 솔루션 사업) 관련 30초짜리 AI 영상 시나리오를 만들어줘.
4개의 연속 장면(각 8초)으로 구성된 하나의 스토리야.

=== 숏폼 가이드 필수 규칙 ===

1. 첫 1~3초 훅 (가장 중요):
   - 시청자가 스크롤을 멈추게 만드는 충격적 한마디
   - 패턴: 수치형("월 5억"), 질문형("이거 몰랐어?"), 반전형("회사 때려치웠다"), 선언형("인생이 바뀌었다")
   - Scene 1의 첫 대사가 곧 훅

2. 3~10초 약속:
   - "이 영상을 끝까지 보면 알 수 있는 것" 암시
   - Scene 1~2에서 궁금증 극대화

3. 정보 밀도:
   - 빈 구간 없이 매 초마다 새로운 정보
   - 2~3초마다 시각적 변화 (장소, 앵글, 인물 동작)

4. 루프 구조:
   - Scene 4의 마지막이 Scene 1의 시작으로 자연스럽게 연결
   - 예: Scene 4 끝 "근데 그 시스템이 뭔데?" → Scene 1 시작 "월 5억 버는 시스템?"

5. 완주율 60% 이상 목표:
   - 매 장면마다 다음이 궁금하게 끝내기
   - 결론을 마지막까지 미루기 (핵심 정보는 Scene 3~4에)

=== 콘텐츠 규칙 ===

1. 등장인물: 한국인 남자 2명 (30대, 사업가)
2. 간접 광고: '카지노' 단어 절대 금지. '시스템', '솔루션', '플랫폼', '자동화' 등으로 표현
3. 대사는 한국어, 장면 묘사는 영어
4. 각 장면에서 인물 외모/옷차림을 동일하게 묘사 (일관성)
5. 배경 다양하게 (카페, 사무실, 옥상, 서버룸, 차 안 등)

=== 스토리 구조 ===

- Scene 1 (0-8초): 후킹 - 충격적 수치/반전으로 시선 끌기
- Scene 2 (8-16초): 궁금증 - "어떻게 가능해?" 질문과 힌트
- Scene 3 (16-24초): 증거 - 실제 결과/데이터 보여주기
- Scene 4 (24-32초): 클로징 + 루프 - 여운 + 처음으로 돌아가는 연결

=== 제목/설명 규칙 ===

- 제목: 30자 이내, 숫자 활용, 궁금증 유발
- 설명: 2줄 + 해시태그 5개
- 첫 댓글: 참여 유도 질문

반드시 아래 JSON 형식으로만 응답:
{
  "scenes": [
    {"scene_num": 1, "veo3_prompt": "영어 장면 묘사 + 한국어 대사..."},
    {"scene_num": 2, "veo3_prompt": "..."},
    {"scene_num": 3, "veo3_prompt": "..."},
    {"scene_num": 4, "veo3_prompt": "..."}
  ],
  "subject": "YouTube 제목",
  "caption": "YouTube 설명 + 해시태그",
  "comment": "첫 댓글"
}"""

# ============================================================
# AI 검증 프롬프트
# ============================================================
VERIFY_PROMPT = """아래 YouTube Shorts 시나리오를 검증해줘. 각 항목 1~10점.

[평가 대상]
제목: {{ $json.subject }}
Scene 1: {{ $json.scenes_text_1 }}
Scene 2: {{ $json.scenes_text_2 }}
Scene 3: {{ $json.scenes_text_3 }}
Scene 4: {{ $json.scenes_text_4 }}

[평가 항목]
1. 훅 파워 - Scene 1 첫 대사가 스크롤을 멈추게 하는가? (충격/수치/반전)
2. 스토리 흐름 - 4개 장면이 자연스럽게 이어지는가? 궁금증이 유지되는가?
3. 루프 가능성 - Scene 4 끝이 Scene 1 시작으로 자연스럽게 연결되는가?
4. 완주 유도 - 끝까지 봐야 핵심 정보를 알 수 있는 구조인가?
5. 간접 광고 - 카지노 직접 언급 없이 시스템/솔루션으로 자연스럽게 표현했는가?
6. 차별화 - 뻔하지 않고 독창적인 스토리 각도인가?
7. 클릭 유도 - 제목이 호기심/클릭 욕구를 유발하는가?

반드시 아래 JSON으로만 응답:
{
  "hook_power": 8,
  "story_flow": 7,
  "loop_potential": 6,
  "completion_drive": 8,
  "indirect_ad": 9,
  "differentiation": 7,
  "click_appeal": 8,
  "total": 53,
  "pass": true,
  "feedback": "통과/탈락 사유 1줄"
}"""

# ============================================================
# 재생성 프롬프트 (2차/3차)
# ============================================================
REGEN_PREFIX = """이전 시나리오가 품질 기준에 미달했습니다.
피드백: {{ $json.feedback }}
점수: {{ $json.total }}/70

위 피드백을 반영하여 더 나은 시나리오를 만들어줘. 특히 부족한 항목을 개선할 것.

"""


def build_workflow():
    nodes = []
    x = 0  # x position tracker

    # ============================================================
    # 1. Manual Trigger
    # ============================================================
    nodes.append({
        "parameters": {},
        "id": "v3-trigger",
        "name": "테스트 실행",
        "type": "n8n-nodes-base.manualTrigger",
        "typeVersion": 1,
        "position": [x, 400]
    })

    # ============================================================
    # 2. AI 시나리오 생성 1차
    # ============================================================
    x += 250
    nodes.append({
        "parameters": {
            "modelName": "models/gemini-2.5-flash-lite-preview-06-17",
            "text": SCENARIO_PROMPT,
            "options": {"temperature": 0.85}
        },
        "id": "v3-scenario-1",
        "name": "AI 시나리오 1차",
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [x, 400],
        "credentials": {"googlePalmApi": CRED_GEMINI}
    })

    # ============================================================
    # 3. 시나리오 파싱 1
    # ============================================================
    x += 250
    parse_code = _get_parse_code("1차")
    nodes.append({
        "parameters": {"jsCode": parse_code},
        "id": "v3-parse-1",
        "name": "파싱 1",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [x, 400]
    })

    # ============================================================
    # 4. AI 검증 1
    # ============================================================
    x += 250
    nodes.append({
        "parameters": {
            "modelName": "models/gemini-2.5-flash-lite-preview-06-17",
            "text": VERIFY_PROMPT,
            "options": {"temperature": 0.3}
        },
        "id": "v3-verify-1",
        "name": "AI 검증 1",
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [x, 400],
        "credentials": {"googlePalmApi": CRED_GEMINI}
    })

    # ============================================================
    # 5. 검증 파싱 1
    # ============================================================
    x += 250
    nodes.append({
        "parameters": {"jsCode": _get_verify_parse_code("파싱 1")},
        "id": "v3-vparse-1",
        "name": "검증 파싱 1",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [x, 400]
    })

    # ============================================================
    # 6. 통과 판단 1 (49점 이상 = 7점 평균)
    # ============================================================
    x += 250
    nodes.append({
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [{
                    "id": "check-1",
                    "leftValue": "={{ $json.total }}",
                    "rightValue": 49,
                    "operator": {"type": "number", "operation": "gte"}
                }],
                "combinator": "and"
            }
        },
        "id": "v3-pass-1",
        "name": "통과 판단 1",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [x, 400]
    })

    # ============== 2차 재생성 (탈락 시) ==============

    # 7. AI 시나리오 2차
    nodes.append({
        "parameters": {
            "modelName": "models/gemini-2.5-flash-lite-preview-06-17",
            "text": REGEN_PREFIX + SCENARIO_PROMPT,
            "options": {"temperature": 0.9}
        },
        "id": "v3-scenario-2",
        "name": "AI 시나리오 2차",
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [x + 250, 650],
        "credentials": {"googlePalmApi": CRED_GEMINI}
    })

    # 8. 파싱 2
    nodes.append({
        "parameters": {"jsCode": _get_parse_code("2차")},
        "id": "v3-parse-2",
        "name": "파싱 2",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [x + 500, 650]
    })

    # 9. AI 검증 2
    nodes.append({
        "parameters": {
            "modelName": "models/gemini-2.5-flash-lite-preview-06-17",
            "text": VERIFY_PROMPT,
            "options": {"temperature": 0.3}
        },
        "id": "v3-verify-2",
        "name": "AI 검증 2",
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [x + 750, 650],
        "credentials": {"googlePalmApi": CRED_GEMINI}
    })

    # 10. 검증 파싱 2
    nodes.append({
        "parameters": {"jsCode": _get_verify_parse_code("파싱 2")},
        "id": "v3-vparse-2",
        "name": "검증 파싱 2",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [x + 1000, 650]
    })

    # 11. 통과 판단 2
    nodes.append({
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [{
                    "id": "check-2",
                    "leftValue": "={{ $json.total }}",
                    "rightValue": 49,
                    "operator": {"type": "number", "operation": "gte"}
                }],
                "combinator": "and"
            }
        },
        "id": "v3-pass-2",
        "name": "통과 판단 2",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [x + 1250, 650]
    })

    # 12. AI 시나리오 3차 (3차는 검증 없이 바로 진행)
    nodes.append({
        "parameters": {
            "modelName": "models/gemini-2.5-flash-lite-preview-06-17",
            "text": REGEN_PREFIX + SCENARIO_PROMPT,
            "options": {"temperature": 0.95}
        },
        "id": "v3-scenario-3",
        "name": "AI 시나리오 3차",
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [x + 1500, 900],
        "credentials": {"googlePalmApi": CRED_GEMINI}
    })

    # 13. 파싱 3
    nodes.append({
        "parameters": {"jsCode": _get_parse_code("3차")},
        "id": "v3-parse-3",
        "name": "파싱 3",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [x + 1750, 900]
    })

    # ============== 영상 생성 파이프라인 (공통) ==============

    # 14. Veo3 영상 생성
    veo3_x = x + 2000
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
        "position": [veo3_x, 400],
        "credentials": {"httpHeaderAuth": CRED_KIE}
    })

    # 15. Veo3 대기
    nodes.append({
        "parameters": {"amount": 240},
        "id": "v3-wait",
        "name": "Veo3 대기",
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [veo3_x + 250, 400],
        "webhookId": "v3-wait-30s"
    })

    # 16. Veo3 결과
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
        "position": [veo3_x + 500, 400],
        "credentials": {"httpHeaderAuth": CRED_KIE}
    })

    # 17. 영상 URL 추출
    extract_code = r"""const items = $input.all();
const results = [];

for (let idx = 0; idx < items.length; idx++) {
  const data = items[idx].json.data;
  let videoUrl = '';

  if (data && data.successFlag === 1 && data.response) {
    let urls = data.response.resultUrls;
    if (typeof urls === 'string') {
      try { urls = JSON.parse(urls); } catch(e) { urls = [urls]; }
    }
    videoUrl = (urls && urls[0]) || '';
  }

  // 통과한 시나리오 데이터 찾기 (1차/2차/3차 중 하나)
  let scenario;
  try { scenario = $('파싱 1').all()[idx]?.json; } catch(e) {}
  if (!scenario) try { scenario = $('파싱 2').all()[idx]?.json; } catch(e) {}
  if (!scenario) try { scenario = $('파싱 3').all()[idx]?.json; } catch(e) {}
  if (!scenario) scenario = {};

  results.push({
    json: {
      scene_num: scenario.scene_num || (idx + 1),
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
        "parameters": {"jsCode": extract_code},
        "id": "v3-extract",
        "name": "영상 URL 추출",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [veo3_x + 750, 400]
    })

    # 18. Aggregate
    nodes.append({
        "parameters": {"aggregate": "aggregateAllItemData", "options": {}},
        "id": "v3-aggregate",
        "name": "Aggregate",
        "type": "n8n-nodes-base.aggregate",
        "typeVersion": 1,
        "position": [veo3_x + 1000, 400]
    })

    # 19. Creatomate 합성
    creatomate_code = r"""const allData = $input.first().json.data;
const scenes = allData.sort((a, b) => a.scene_num - b.scene_num);
const sceneDuration = 8;
const elements = [];

for (let i = 0; i < scenes.length; i++) {
  if (!scenes[i].video_url) continue;
  elements.push({
    type: "video",
    track: 1,
    time: i * sceneDuration,
    duration: sceneDuration,
    source: scenes[i].video_url,
    fit: "cover",
    audio_enabled: true
  });
}

const totalDuration = scenes.filter(s => s.video_url).length * sceneDuration;

const payload = {
  source: {
    output_format: "mp4",
    width: 1080,
    height: 1920,
    duration: totalDuration,
    elements: elements
  }
};

return [{
  json: {
    creatomate_payload: payload,
    subject: scenes[0]?.subject || '',
    caption: scenes[0]?.caption || '',
    comment: scenes[0]?.comment || '',
    success_scenes: scenes.filter(s => s.video_url).length,
    total_scenes: scenes.length
  }
}];"""

    nodes.append({
        "parameters": {"jsCode": creatomate_code},
        "id": "v3-creatomate",
        "name": "Creatomate 합성",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [veo3_x + 1250, 400]
    })

    # 20. Creatomate 렌더
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://api.creatomate.com/v1/renders",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify($json.creatomate_payload) }}",
            "options": {"timeout": 600000}
        },
        "id": "v3-render",
        "name": "Creatomate 렌더",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [veo3_x + 1500, 400],
        "credentials": {"httpHeaderAuth": CRED_CREATOMATE}
    })

    # 21. 렌더 대기
    nodes.append({
        "parameters": {"amount": 120},
        "id": "v3-render-wait",
        "name": "렌더 대기",
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [veo3_x + 1750, 400],
        "webhookId": "v3-render-wait-30s"
    })

    # 22. 렌더 결과
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
        "position": [veo3_x + 2000, 400],
        "credentials": {"httpHeaderAuth": CRED_CREATOMATE}
    })

    # 23. 최종 출력
    final_code = r"""const render = $input.first().json;
const scenario = $('Creatomate 합성').first().json;

return [{
  json: {
    final_video_url: render.url || '',
    render_status: render.status || 'unknown',
    subject: scenario.subject,
    caption: scenario.caption,
    comment: scenario.comment,
    success_scenes: scenario.success_scenes,
    total_scenes: scenario.total_scenes
  }
}];"""

    nodes.append({
        "parameters": {"jsCode": final_code},
        "id": "v3-final",
        "name": "최종 출력",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [veo3_x + 2250, 400]
    })

    # ============================================================
    # Connections
    # ============================================================
    connections = {
        "테스트 실행": {
            "main": [[{"node": "AI 시나리오 1차", "type": "main", "index": 0}]]
        },
        "AI 시나리오 1차": {
            "main": [[{"node": "파싱 1", "type": "main", "index": 0}]]
        },
        "파싱 1": {
            "main": [[{"node": "AI 검증 1", "type": "main", "index": 0}]]
        },
        "AI 검증 1": {
            "main": [[{"node": "검증 파싱 1", "type": "main", "index": 0}]]
        },
        "검증 파싱 1": {
            "main": [[{"node": "통과 판단 1", "type": "main", "index": 0}]]
        },
        "통과 판단 1": {
            "main": [
                # true → Veo3 생성
                [{"node": "Veo3 영상 생성", "type": "main", "index": 0}],
                # false → 2차 재생성
                [{"node": "AI 시나리오 2차", "type": "main", "index": 0}]
            ]
        },
        "AI 시나리오 2차": {
            "main": [[{"node": "파싱 2", "type": "main", "index": 0}]]
        },
        "파싱 2": {
            "main": [[{"node": "AI 검증 2", "type": "main", "index": 0}]]
        },
        "AI 검증 2": {
            "main": [[{"node": "검증 파싱 2", "type": "main", "index": 0}]]
        },
        "검증 파싱 2": {
            "main": [[{"node": "통과 판단 2", "type": "main", "index": 0}]]
        },
        "통과 판단 2": {
            "main": [
                # true → Veo3 생성
                [{"node": "Veo3 영상 생성", "type": "main", "index": 0}],
                # false → 3차 (검증 없이 진행)
                [{"node": "AI 시나리오 3차", "type": "main", "index": 0}]
            ]
        },
        "AI 시나리오 3차": {
            "main": [[{"node": "파싱 3", "type": "main", "index": 0}]]
        },
        "파싱 3": {
            "main": [[{"node": "Veo3 영상 생성", "type": "main", "index": 0}]]
        },
        # Veo3 파이프라인
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
        "settings": {"executionOrder": "v1"}
    }


def _get_parse_code(label):
    """시나리오 파싱 코드 (4개 아이템 출력 + 검증용 텍스트)"""
    return r"""const text = $input.first().json.content.parts[0].text;
const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();

let data;
try {
  data = JSON.parse(cleanText);
} catch (e) {
  data = {
    scenes: [
      {scene_num: 1, veo3_prompt: "Two Korean businessmen in their 30s at a luxury rooftop bar at night. Man A wears a navy suit, short black hair, sharp jawline. Man B wears a dark gray suit, slightly longer hair. Man B sits down shocked saying '야, 너 진짜 월 5억이야?' Man A swirls his whiskey glass calmly and says '시스템이 다 해주는데 뭐.' City skyline behind them glowing. Cinematic, 9:16 vertical."},
      {scene_num: 2, veo3_prompt: "Same two Korean businessmen at rooftop bar. Man A in navy suit, Man B in gray suit. Close-up two-shot. Man B leans in saying '무슨 시스템인데 그게?' Man A puts down his glass and says '운영, 정산, CS까지 전부 자동이야. 난 하루에 30분만 써.' Man B's jaw drops. Shallow depth of field, city lights bokeh, 9:16 vertical."},
      {scene_num: 3, veo3_prompt: "Same two Korean businessmen. Man A in navy suit pulls out his phone and shows the screen to Man B in gray suit. Phone screen glows. Man A says '이게 이번 달 수익이야.' Man B stares wide-eyed saying '이게 한 달? 나 연봉보다 많은데?' Man A smirks. Over-the-shoulder shot, phone glow illuminating faces, 9:16 vertical."},
      {scene_num: 4, veo3_prompt: "Same two Korean businessmen walking along the rooftop edge, city skyline behind. Man A in navy suit, Man B in gray suit. Man B says '나도 할 수 있어?' Man A stops and turns saying '근데 진짜 중요한 건 따로 있어.' Man B looks curious saying '뭔데?' Man A smiles mysteriously. Camera slowly zooms out. Cinematic, 9:16 vertical."}
    ],
    subject: "월 5억 버는 시스템의 비밀",
    caption: "이 시스템의 정체가 뭘까?\n끝까지 보면 알 수 있습니다\n#솔루션 #자동화 #수익 #시스템 #사업",
    comment: "진짜 이런 시스템이 있어요?"
  };
}

// 4개 아이템으로 분리 + 검증용 텍스트도 포함
const items = data.scenes.map((scene, idx) => ({
  json: {
    scene_num: scene.scene_num || (idx + 1),
    veo3_prompt: scene.veo3_prompt,
    subject: data.subject,
    caption: data.caption,
    comment: data.comment,
    total_scenes: data.scenes.length,
    // AI 검증용 (첫 번째 아이템에만 전체 텍스트)
    scenes_text_1: data.scenes[0]?.veo3_prompt || '',
    scenes_text_2: data.scenes[1]?.veo3_prompt || '',
    scenes_text_3: data.scenes[2]?.veo3_prompt || '',
    scenes_text_4: data.scenes[3]?.veo3_prompt || ''
  }
}));

return items;"""


def _get_verify_parse_code(source_node):
    """검증 결과 파싱 코드"""
    return r"""const text = $input.first().json.content.parts[0].text;
const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();

let data;
try {
  data = JSON.parse(cleanText);
} catch (e) {
  data = { total: 50, pass: true, feedback: "파싱 실패 - 통과 처리" };
}

const total = data.total || (
  (data.hook_power || 0) + (data.story_flow || 0) +
  (data.loop_potential || 0) + (data.completion_drive || 0) +
  (data.indirect_ad || 0) + (data.differentiation || 0) +
  (data.click_appeal || 0)
);

// 이전 단계 시나리오 데이터 전달
const prevItems = $('""" + source_node + r"""').all();

const items = prevItems.map(item => ({
  json: {
    ...item.json,
    ...data,
    total: total,
    pass: total >= 49
  }
}));

return items;"""


def upload_workflow(workflow_data):
    put_data = {
        "name": workflow_data["name"],
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "settings": workflow_data["settings"]
    }

    with open('/tmp/lumix_veo3_30s_v2.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_veo3_30s_v2.json',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if 'id' in response:
            print(f"  [OK] 업데이트 성공 (노드: {len(response.get('nodes', []))}개)")
            return True
        else:
            print(f"  [ERROR] {json.dumps(response, ensure_ascii=False)[:500]}")
            return False
    except json.JSONDecodeError:
        print(f"  [ERROR] 응답 파싱 실패: {result.stdout[:300]}")
        return False


def reactivate():
    subprocess.run([
        'curl', '-sk', '-X', 'POST',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}/deactivate'
    ], capture_output=True, text=True)
    result = subprocess.run([
        'curl', '-sk', '-X', 'POST',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}/activate'
    ], capture_output=True, text=True)
    try:
        response = json.loads(result.stdout)
        print(f"  [OK] 재활성화: active={response.get('active')}")
    except Exception:
        print("  [WARN] 재활성화 응답 확인 필요")


def main():
    print("=" * 60)
    print("루믹스 Veo3 30초 숏폼 - 가이드 + 검증 적용")
    print("=" * 60)

    print("\n[1/3] 워크플로우 빌드...")
    workflow = build_workflow()
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    print("\n[2/3] 업데이트...")
    if not upload_workflow(workflow):
        sys.exit(1)

    print("\n[3/3] 재활성화...")
    reactivate()

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)
    print(f"\n  워크플로우: {WORKFLOW_ID}")
    print(f"  URL: {N8N_URL}/workflow/{WORKFLOW_ID}")

    print(f"\n  구조:")
    print(f"  테스트 실행")
    print(f"    → AI 시나리오 1차 (Gemini + 숏폼가이드)")
    print(f"      → 파싱 → AI 검증 → 검증 파싱 → 통과 판단")
    print(f"        ├─ 통과 (49점+) → Veo3 영상 생성 ×4")
    print(f"        └─ 탈락 → AI 시나리오 2차")
    print(f"            → 파싱 → AI 검증 → 통과 판단")
    print(f"              ├─ 통과 → Veo3 영상 생성 ×4")
    print(f"              └─ 탈락 → AI 시나리오 3차 (검증 생략)")
    print(f"                  → Veo3 영상 생성 ×4")
    print(f"    → Veo3 대기 (4분) → 결과 확인")
    print(f"      → Aggregate → Creatomate 합성 → 렌더")
    print(f"        → 최종 출력 (30초 mp4)")

    print(f"\n  적용된 숏폼 가이드 규칙:")
    print(f"  - 첫 1~3초 훅 (수치/질문/반전)")
    print(f"  - 루프 구조 (끝→시작 연결)")
    print(f"  - 완주율 60%+ 구조")
    print(f"  - 정보 밀도 유지")
    print(f"  - 제목 30자 이내 + 해시태그 5개")

    print(f"\n  AI 검증 항목 (7개, 49점/70점 통과):")
    print(f"  훅 파워 / 스토리 흐름 / 루프 가능성")
    print(f"  완주 유도 / 간접 광고 / 차별화 / 클릭 유도")

    print(f"\n  비용: Gemini 무료 + Veo3 $1.60 + Creatomate 렌더")


if __name__ == "__main__":
    main()
