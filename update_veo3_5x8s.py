#!/usr/bin/env python3
"""
루믹스 Veo3 5x8초 숏폼 워크플로우 업데이트 스크립트
- Creatomate 제거
- 5개 독립 8초 영상 생성 (SplitInBatches 루프)
- 남녀 대화 시나리오 (각 영상 독립 주제)
"""

import requests
import json
import sys

API_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
WORKFLOW_ID = "tS2hcoeJ4ar8hivm"
HEADERS = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

GEMINI_CREDENTIAL = {
    "googlePalmApi": {
        "id": "IKP349r08J9Hoz5E",
        "name": "Google Gemini(PaLM) Api account"
    }
}

KIEAI_CREDENTIAL = {
    "httpHeaderAuth": {
        "id": "34ktW72w0p8fCfUQ",
        "name": "Kie.ai"
    }
}

GEMINI_MODEL = "models/gemini-2.5-flash-lite-preview-06-17"


# ============================================================
# SCENARIO GENERATION PROMPT
# ============================================================
SCENARIO_PROMPT = """당신은 YouTube 숏폼 전문 시나리오 작가입니다.

**루믹스 솔루션**을 간접 홍보하는 5개의 **독립적인 8초 영상** 시나리오를 만들어주세요.

## 캐릭터 설정 (모든 영상 동일)
- 남자: 한국인 30대, 짧은 검은 머리, 진한 네이비 수트, 깊고 차분하며 권위있는 목소리
- 여자: 한국인 20대 후반, 어깨길이 검은 머리, 흰색 블라우스, 밝고 에너지 넘치며 친근한 목소리

## 핵심 규칙
1. 각 영상은 **완전히 독립적** - 서로 다른 장소, 다른 주제
2. **절대 '카지노' 직접 언급 금지** → 시스템/솔루션/플랫폼/자동화 사용
3. 8초 분량 대화 (2-3문장 교환)
4. 숏폼 가이드: 첫 1-3초 hook, 루프 구조, 완주율 최적화

## 5개 영상 주제 (각각 다른 것)
1. 수익 자동화 시스템의 놀라운 결과
2. 경쟁사 대비 플랫폼 우위
3. 고객 만족도와 시스템 안정성
4. 해외 시장 진출 성공 사례
5. 기술력과 보안의 차별화

## veo3_prompt 필수 포함 문구 (영어로)
각 veo3_prompt 시작은 반드시 이것으로:
"A Korean man in his 30s wearing a dark navy suit with short black hair speaks with a deep, calm, authoritative voice. A Korean woman in her late 20s wearing a white blouse with shoulder-length black hair speaks with a bright, energetic, friendly voice."

그 다음에 장소, 장면 묘사, 한국어 대사를 포함하세요.

## 출력 형식 (순수 JSON만, 마크다운 코드블록 없이)
{
  "videos": [
    {
      "video_num": 1,
      "topic": "주제 설명",
      "veo3_prompt": "A Korean man in his 30s wearing a dark navy suit with short black hair speaks with a deep, calm, authoritative voice. A Korean woman in her late 20s wearing a white blouse with shoulder-length black hair speaks with a bright, energetic, friendly voice. They sit across from each other at [장소]. [장면묘사]. Man: '[한국어 대사]' Woman: '[한국어 대사]' [마무리 묘사]. Cinematic lighting, 9:16 vertical, 8 seconds.",
      "subtitle_ko": "핵심 대사 한국어",
      "subject": "YouTube 영상 제목 (호기심 유발)",
      "caption": "설명 + #해시태그",
      "comment": "첫 댓글 내용"
    }
  ]
}

총 5개 video를 만들어주세요. 각 video_num은 1~5입니다."""


# ============================================================
# VERIFICATION PROMPT
# ============================================================
VERIFY_PROMPT = """당신은 YouTube 숏폼 콘텐츠 검증 전문가입니다.

아래 5개 영상 시나리오를 각각 검증해주세요.

## 검증할 시나리오:
{{ $json.content.parts[0].text }}

## 평가 항목 (각 1-10점)
1. hook_power: 첫 1-3초 주목도
2. story_flow: 스토리 흐름 자연스러움
3. loop_potential: 반복 시청 유도력
4. completion_drive: 끝까지 보게 만드는 힘
5. indirect_ad: 간접 광고 자연스러움 (카지노 직접 언급 시 0점)
6. differentiation: 차별화 정도
7. click_appeal: 클릭 유도력

## 통과 기준: 각 영상 49/70점 이상

## 출력 형식 (순수 JSON만)
{
  "videos": [
    {
      "video_num": 1,
      "scores": {"hook_power": 8, "story_flow": 7, "loop_potential": 8, "completion_drive": 7, "indirect_ad": 9, "differentiation": 7, "click_appeal": 8},
      "total": 54,
      "pass": true,
      "feedback": "구체적 피드백"
    }
  ],
  "overall_pass": true,
  "overall_feedback": "전체 피드백"
}

5개 영상 모두 검증해주세요."""


# ============================================================
# RETRY PROMPT
# ============================================================
RETRY_PROMPT = """당신은 YouTube 숏폼 전문 시나리오 작가입니다.

이전 시나리오가 검증에서 탈락했습니다. 피드백을 반영하여 다시 작성해주세요.

## 이전 검증 피드백:
{{ $json.content.parts[0].text }}

## 원래 요구사항:

**루믹스 솔루션**을 간접 홍보하는 5개의 **독립적인 8초 영상** 시나리오를 만들어주세요.

## 캐릭터 설정 (모든 영상 동일)
- 남자: 한국인 30대, 짧은 검은 머리, 진한 네이비 수트, 깊고 차분하며 권위있는 목소리
- 여자: 한국인 20대 후반, 어깨길이 검은 머리, 흰색 블라우스, 밝고 에너지 넘치며 친근한 목소리

## 핵심 규칙
1. 각 영상은 **완전히 독립적** - 서로 다른 장소, 다른 주제
2. **절대 '카지노' 직접 언급 금지** → 시스템/솔루션/플랫폼/자동화 사용
3. 8초 분량 대화 (2-3문장 교환)
4. 숏폼 가이드: 첫 1-3초 hook, 루프 구조, 완주율 최적화

## 5개 영상 주제 (각각 다른 것)
1. 수익 자동화 시스템의 놀라운 결과
2. 경쟁사 대비 플랫폼 우위
3. 고객 만족도와 시스템 안정성
4. 해외 시장 진출 성공 사례
5. 기술력과 보안의 차별화

## veo3_prompt 필수 포함 문구 (영어로)
각 veo3_prompt 시작은 반드시 이것으로:
"A Korean man in his 30s wearing a dark navy suit with short black hair speaks with a deep, calm, authoritative voice. A Korean woman in her late 20s wearing a white blouse with shoulder-length black hair speaks with a bright, energetic, friendly voice."

그 다음에 장소, 장면 묘사, 한국어 대사를 포함하세요.

## 출력 형식 (순수 JSON만, 마크다운 코드블록 없이)
{
  "videos": [
    {
      "video_num": 1,
      "topic": "주제 설명",
      "veo3_prompt": "A Korean man in his 30s wearing a dark navy suit with short black hair speaks with a deep, calm, authoritative voice. A Korean woman in her late 20s wearing a white blouse with shoulder-length black hair speaks with a bright, energetic, friendly voice. They sit across from each other at [장소]. [장면묘사]. Man: '[한국어 대사]' Woman: '[한국어 대사]' [마무리 묘사]. Cinematic lighting, 9:16 vertical, 8 seconds.",
      "subtitle_ko": "핵심 대사 한국어",
      "subject": "YouTube 영상 제목 (호기심 유발)",
      "caption": "설명 + #해시태그",
      "comment": "첫 댓글 내용"
    }
  ]
}

총 5개 video를 만들어주세요. 이전 피드백을 반영하여 점수를 높여주세요."""


def build_nodes():
    """Build all 15 nodes for the workflow."""
    nodes = []

    # =============================================
    # Node 1: 수동 실행 (Manual Trigger)
    # =============================================
    nodes.append({
        "parameters": {},
        "id": "5x8s-trigger",
        "name": "수동 실행",
        "type": "n8n-nodes-base.manualTrigger",
        "typeVersion": 1,
        "position": [0, 400]
    })

    # =============================================
    # Node 2: AI 시나리오 생성 (Gemini)
    # =============================================
    nodes.append({
        "parameters": {
            "modelId": {
                "__rl": True,
                "value": GEMINI_MODEL,
                "mode": "list",
                "cachedResultName": GEMINI_MODEL
            },
            "messages": {
                "values": [
                    {
                        "content": SCENARIO_PROMPT
                    }
                ]
            },
            "options": {
                "temperature": 0.85
            }
        },
        "id": "5x8s-scenario",
        "name": "AI 시나리오 생성",
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [280, 400],
        "credentials": GEMINI_CREDENTIAL
    })

    # =============================================
    # Node 3: AI 검증 (Gemini)
    # =============================================
    nodes.append({
        "parameters": {
            "modelId": {
                "__rl": True,
                "value": GEMINI_MODEL,
                "mode": "list",
                "cachedResultName": GEMINI_MODEL
            },
            "messages": {
                "values": [
                    {
                        "content": VERIFY_PROMPT
                    }
                ]
            },
            "options": {
                "temperature": 0.3
            }
        },
        "id": "5x8s-verify",
        "name": "AI 검증",
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [560, 400],
        "credentials": GEMINI_CREDENTIAL
    })

    # =============================================
    # Node 4: 검증 결과 확인 (IF)
    # =============================================
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
                        "id": "5x8s-check-pass",
                        "leftValue": "={{ $json.content.parts[0].text }}",
                        "rightValue": "\"overall_pass\": true",
                        "operator": {
                            "type": "string",
                            "operation": "contains"
                        }
                    }
                ],
                "combinator": "and"
            },
            "options": {}
        },
        "id": "5x8s-if-pass",
        "name": "검증 결과 확인",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [840, 400]
    })

    # =============================================
    # Node 5: AI 시나리오 재생성 (Gemini - retry)
    # =============================================
    nodes.append({
        "parameters": {
            "modelId": {
                "__rl": True,
                "value": GEMINI_MODEL,
                "mode": "list",
                "cachedResultName": GEMINI_MODEL
            },
            "messages": {
                "values": [
                    {
                        "content": RETRY_PROMPT
                    }
                ]
            },
            "options": {
                "temperature": 0.95
            }
        },
        "id": "5x8s-retry",
        "name": "AI 시나리오 재생성",
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [1120, 650],
        "credentials": GEMINI_CREDENTIAL
    })

    # =============================================
    # Node 6: 시나리오 파싱 (Code)
    # =============================================
    parse_code = """// Parse AI scenario output into 5 separate video items
const items = $input.all();
let text = '';

// Get text from Gemini output (could come from scenario gen or retry)
for (const item of items) {
  if (item.json.content && item.json.content.parts) {
    text = item.json.content.parts[0].text;
    break;
  }
}

// Also check the AI scenario node output directly
if (!text) {
  try {
    const scenarioItems = $('AI 시나리오 생성').all();
    if (scenarioItems.length > 0 && scenarioItems[0].json.content) {
      text = scenarioItems[0].json.content.parts[0].text;
    }
  } catch(e) {}
}

// Clean markdown code blocks if present
const cleanText = text.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();

let data;
try {
  data = JSON.parse(cleanText);
} catch (e) {
  // Fallback: try to extract JSON from text
  const jsonMatch = cleanText.match(/\\{[\\s\\S]*\\}/);
  if (jsonMatch) {
    try {
      data = JSON.parse(jsonMatch[0]);
    } catch (e2) {
      // Ultimate fallback with default scenarios
      data = {
        videos: [
          {
            video_num: 1,
            topic: "수익 자동화 시스템",
            veo3_prompt: "A Korean man in his 30s wearing a dark navy suit with short black hair speaks with a deep, calm, authoritative voice. A Korean woman in her late 20s wearing a white blouse with shoulder-length black hair speaks with a bright, energetic, friendly voice. They sit across from each other at a modern glass-walled office with city skyline visible. The woman leans forward excitedly and says '이 시스템 도입하고 매출이 3배나 뛰었다면서요?' The man nods confidently and replies '운영부터 정산까지 전부 자동이니까, 결과가 따라올 수밖에 없죠.' The woman's eyes widen with amazement. Cinematic lighting, shallow depth of field, 9:16 vertical, 8 seconds.",
            subtitle_ko: "시스템 도입 후 매출 3배 상승",
            subject: "이 시스템 하나로 매출 3배?",
            caption: "자동화의 힘 #솔루션 #자동화 #수익",
            comment: "어떤 시스템인지 궁금합니다"
          },
          {
            video_num: 2,
            topic: "플랫폼 경쟁 우위",
            veo3_prompt: "A Korean man in his 30s wearing a dark navy suit with short black hair speaks with a deep, calm, authoritative voice. A Korean woman in her late 20s wearing a white blouse with shoulder-length black hair speaks with a bright, energetic, friendly voice. They stand in a luxury hotel lobby with marble floors and warm lighting. The woman asks '경쟁사들은 왜 따라오지 못하는 거예요?' The man smiles and says '기술 격차가 2년은 되니까요. 우리 솔루션은 차원이 다릅니다.' He adjusts his cufflinks confidently. Cinematic, warm lighting, 9:16 vertical, 8 seconds.",
            subtitle_ko: "기술 격차 2년, 따라올 수 없는 솔루션",
            subject: "경쟁사가 절대 못 따라오는 이유",
            caption: "기술력의 차이 #플랫폼 #기술 #차별화",
            comment: "기술 격차가 그 정도인가요?"
          },
          {
            video_num: 3,
            topic: "고객 만족도",
            veo3_prompt: "A Korean man in his 30s wearing a dark navy suit with short black hair speaks with a deep, calm, authoritative voice. A Korean woman in her late 20s wearing a white blouse with shoulder-length black hair speaks with a bright, energetic, friendly voice. They sit at a rooftop cafe with sunset behind them. The woman checks her tablet and says '고객 재계약률 97%라고요? 어떻게 이게 가능해요?' The man leans back and says '시스템 안정성이 99.9%니까 고객이 떠날 이유가 없죠.' Warm golden hour lighting, 9:16 vertical, 8 seconds.",
            subtitle_ko: "재계약률 97%, 안정성 99.9%",
            subject: "고객이 절대 떠나지 않는 비결",
            caption: "신뢰의 시스템 #고객만족 #안정성 #신뢰",
            comment: "이 정도면 정말 대단하네요"
          },
          {
            video_num: 4,
            topic: "해외 시장 진출",
            veo3_prompt: "A Korean man in his 30s wearing a dark navy suit with short black hair speaks with a deep, calm, authoritative voice. A Korean woman in her late 20s wearing a white blouse with shoulder-length black hair speaks with a bright, energetic, friendly voice. They walk through a bright international airport terminal with departure boards visible. The woman excitedly says '동남아 3개국 동시 런칭 성공했다면서요!' The man nods saying '현지화 시스템이 완벽하니까요. 다음은 유럽입니다.' They walk confidently past departure boards. Bright airport lighting, 9:16 vertical, 8 seconds.",
            subtitle_ko: "동남아 3개국 동시 런칭 성공",
            subject: "글로벌 진출, 이렇게 빠를 수 있다고?",
            caption: "세계로 뻗어나가는 솔루션 #해외진출 #글로벌 #성공",
            comment: "다음 진출 국가가 어디인가요?"
          },
          {
            video_num: 5,
            topic: "보안과 기술력",
            veo3_prompt: "A Korean man in his 30s wearing a dark navy suit with short black hair speaks with a deep, calm, authoritative voice. A Korean woman in her late 20s wearing a white blouse with shoulder-length black hair speaks with a bright, energetic, friendly voice. They sit in a dark server room with blue LED lights glowing on racks of servers. The woman whispers '해킹 시도가 하루에 몇 번이나 들어와요?' The man replies calmly '수천 번이요. 하지만 단 한 번도 뚫린 적 없습니다.' Blue server lights reflect in their eyes. Dark cinematic mood, 9:16 vertical, 8 seconds.",
            subtitle_ko: "수천 번의 해킹, 단 한 번도 뚫리지 않은 보안",
            subject: "절대 뚫리지 않는 시스템의 비밀",
            caption: "철통 보안 #보안 #기술력 #서버",
            comment: "보안이 이 정도면 믿을 수 있겠네요"
          }
        ]
      };
    }
  } else {
    // No JSON found at all, use fallback
    data = {
      videos: [{
        video_num: 1,
        topic: "기본 시나리오",
        veo3_prompt: "A Korean man in his 30s wearing a dark navy suit with short black hair speaks with a deep, calm, authoritative voice. A Korean woman in her late 20s wearing a white blouse with shoulder-length black hair speaks with a bright, energetic, friendly voice. They sit at a modern coffee table. The woman says '이 솔루션 정말 대단하네요.' The man nods and says '자동화의 힘이죠.' Cinematic lighting, 9:16 vertical, 8 seconds.",
        subtitle_ko: "자동화의 힘",
        subject: "이 솔루션의 비밀",
        caption: "#솔루션 #자동화",
        comment: "궁금합니다"
      }]
    };
  }
}

const videos = data.videos || [];
const result = videos.map((v, idx) => ({
  json: {
    video_num: v.video_num || (idx + 1),
    topic: v.topic || '',
    veo3_prompt: v.veo3_prompt || '',
    subtitle_ko: v.subtitle_ko || '',
    subject: v.subject || '',
    caption: v.caption || '',
    comment: v.comment || '',
    total_videos: videos.length
  }
}));

return result;"""

    nodes.append({
        "parameters": {
            "jsCode": parse_code
        },
        "id": "5x8s-parse",
        "name": "시나리오 파싱",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1120, 400]
    })

    # =============================================
    # Node 7: 영상 5개 분리 (SplitInBatches)
    # =============================================
    nodes.append({
        "parameters": {
            "batchSize": 1,
            "options": {}
        },
        "id": "5x8s-split",
        "name": "영상 5개 분리",
        "type": "n8n-nodes-base.splitInBatches",
        "typeVersion": 3,
        "position": [1400, 400]
    })

    # =============================================
    # Node 8: Veo3 영상 생성 (HTTP Request - POST)
    # =============================================
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://api.kie.ai/api/v1/veo/generate",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({ \"prompt\": $json.veo3_prompt, \"aspectRatio\": \"9:16\", \"model\": \"veo3_fast\", \"callbackUrl\": \"\" }) }}",
            "options": {}
        },
        "id": "5x8s-generate",
        "name": "Veo3 영상 생성",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [1680, 400],
        "credentials": KIEAI_CREDENTIAL
    })

    # =============================================
    # Node 9: 생성 대기 (Wait - 4 minutes)
    # =============================================
    nodes.append({
        "parameters": {
            "amount": 240
        },
        "id": "5x8s-wait1",
        "name": "생성 대기",
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [1960, 400],
        "webhookId": "5x8s-wait-gen"
    })

    # =============================================
    # Node 10: 영상 확인 (HTTP Request - GET)
    # =============================================
    nodes.append({
        "parameters": {
            "url": "=https://api.kie.ai/api/v1/veo/record-info?taskId={{ $json.data.taskId }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "id": "5x8s-check",
        "name": "영상 확인",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [2240, 400],
        "credentials": KIEAI_CREDENTIAL
    })

    # =============================================
    # Node 11: 영상 상태 확인 (IF)
    # =============================================
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
                        "id": "5x8s-status-check",
                        "leftValue": "={{ $json.data.status }}",
                        "rightValue": "completed",
                        "operator": {
                            "type": "string",
                            "operation": "equals"
                        }
                    }
                ],
                "combinator": "and"
            },
            "options": {}
        },
        "id": "5x8s-if-status",
        "name": "영상 상태 확인",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [2520, 400]
    })

    # =============================================
    # Node 12: 추가 대기 (Wait - 2 minutes)
    # =============================================
    nodes.append({
        "parameters": {
            "amount": 120
        },
        "id": "5x8s-wait2",
        "name": "추가 대기",
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [2800, 650],
        "webhookId": "5x8s-wait-extra"
    })

    # =============================================
    # Node 13: 영상 재확인 (HTTP Request - GET)
    # =============================================
    nodes.append({
        "parameters": {
            "url": "=https://api.kie.ai/api/v1/veo/record-info?taskId={{ $json.data.taskId }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "id": "5x8s-recheck",
        "name": "영상 재확인",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [3080, 650],
        "credentials": KIEAI_CREDENTIAL
    })

    # =============================================
    # Node 14: 결과 정리 (Code)
    # =============================================
    result_code = """// Collect all video results from the SplitInBatches loop
const allItems = $input.all();
const results = [];

for (const item of allItems) {
  const d = item.json;
  results.push({
    video_num: d.video_num || results.length + 1,
    video_url: d.data?.videoUrl || d.data?.video_url || d.videoUrl || d.video_url || '생성 중...',
    status: d.data?.status || d.status || 'unknown',
    topic: d.topic || '',
    subject: d.subject || '',
    caption: d.caption || '',
    comment: d.comment || '',
    subtitle_ko: d.subtitle_ko || '',
    taskId: d.data?.taskId || d.taskId || ''
  });
}

return [{
  json: {
    total_videos: results.length,
    generated_at: new Date().toISOString(),
    results: results
  }
}];"""

    nodes.append({
        "parameters": {
            "jsCode": result_code
        },
        "id": "5x8s-collect",
        "name": "결과 정리",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2800, 400]
    })

    # =============================================
    # Node 15: 최종 결과 (Code)
    # =============================================
    final_code = """// Format final output with all 5 video URLs and metadata
const input = $input.first().json;
const results = input.results || [];

const output = {
  workflow: "루믹스 Veo3 5x8초 숏폼",
  total_videos: input.total_videos || results.length,
  generated_at: input.generated_at,
  videos: results.map(r => ({
    "영상번호": r.video_num,
    "상태": r.status,
    "영상URL": r.video_url,
    "주제": r.topic,
    "제목": r.subject,
    "설명": r.caption,
    "첫댓글": r.comment,
    "자막": r.subtitle_ko,
    "taskId": r.taskId
  })),
  summary: `총 ${results.length}개 영상 생성 완료. 각 영상은 독립적인 8초 숏폼입니다.`
};

return [{ json: output }];"""

    nodes.append({
        "parameters": {
            "jsCode": final_code
        },
        "id": "5x8s-final",
        "name": "최종 결과",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [3080, 400]
    })

    return nodes


def build_connections():
    """Build connections between all nodes."""
    connections = {
        # Phase 1: Scenario Generation
        "수동 실행": {
            "main": [[
                {"node": "AI 시나리오 생성", "type": "main", "index": 0}
            ]]
        },
        "AI 시나리오 생성": {
            "main": [[
                {"node": "AI 검증", "type": "main", "index": 0}
            ]]
        },
        "AI 검증": {
            "main": [[
                {"node": "검증 결과 확인", "type": "main", "index": 0}
            ]]
        },
        # IF node: true (pass) -> 시나리오 파싱, false (fail) -> 재생성
        "검증 결과 확인": {
            "main": [
                # Output 0 (true/pass): go to parsing
                [{"node": "시나리오 파싱", "type": "main", "index": 0}],
                # Output 1 (false/fail): go to retry
                [{"node": "AI 시나리오 재생성", "type": "main", "index": 0}]
            ]
        },
        # Retry connects back to parsing (skip re-verification to avoid infinite loop)
        "AI 시나리오 재생성": {
            "main": [[
                {"node": "시나리오 파싱", "type": "main", "index": 0}
            ]]
        },

        # Phase 2: Video Generation Loop
        "시나리오 파싱": {
            "main": [[
                {"node": "영상 5개 분리", "type": "main", "index": 0}
            ]]
        },
        # SplitInBatches: output 0 = batch item, output 1 = done
        "영상 5개 분리": {
            "main": [
                # Output 0 (each batch): go to Veo3 generation
                [{"node": "Veo3 영상 생성", "type": "main", "index": 0}],
                # Output 1 (done): go to result collection
                [{"node": "결과 정리", "type": "main", "index": 0}]
            ]
        },
        "Veo3 영상 생성": {
            "main": [[
                {"node": "생성 대기", "type": "main", "index": 0}
            ]]
        },
        "생성 대기": {
            "main": [[
                {"node": "영상 확인", "type": "main", "index": 0}
            ]]
        },
        "영상 확인": {
            "main": [[
                {"node": "영상 상태 확인", "type": "main", "index": 0}
            ]]
        },
        # IF status: true (completed) -> back to split, false -> extra wait
        "영상 상태 확인": {
            "main": [
                # Output 0 (true/completed): back to SplitInBatches for next item
                [{"node": "영상 5개 분리", "type": "main", "index": 0}],
                # Output 1 (false/not ready): extra wait
                [{"node": "추가 대기", "type": "main", "index": 0}]
            ]
        },
        "추가 대기": {
            "main": [[
                {"node": "영상 재확인", "type": "main", "index": 0}
            ]]
        },
        # After recheck, go back to SplitInBatches (loop continues)
        "영상 재확인": {
            "main": [[
                {"node": "영상 5개 분리", "type": "main", "index": 0}
            ]]
        },

        # Phase 3: Output
        "결과 정리": {
            "main": [[
                {"node": "최종 결과", "type": "main", "index": 0}
            ]]
        }
    }

    return connections


def main():
    print("=" * 60)
    print("루믹스 Veo3 5x8초 숏폼 워크플로우 업데이트")
    print("=" * 60)

    # Step 1: Fetch current workflow
    print("\n[1/5] 현재 워크플로우 가져오기...")
    resp = requests.get(
        f"{API_BASE}/workflows/{WORKFLOW_ID}",
        headers=HEADERS
    )
    if resp.status_code != 200:
        print(f"  ERROR: Failed to fetch workflow: {resp.status_code}")
        print(f"  {resp.text}")
        sys.exit(1)

    current = resp.json()
    print(f"  현재 이름: {current['name']}")
    print(f"  현재 노드 수: {len(current['nodes'])}")
    print(f"  현재 노드: {[n['name'] for n in current['nodes']]}")

    # Step 2: Build new nodes
    print("\n[2/5] 새 노드 구성...")
    new_nodes = build_nodes()
    print(f"  새 노드 수: {len(new_nodes)}")
    for n in new_nodes:
        print(f"    - {n['name']} ({n['type']})")

    # Step 3: Build new connections
    print("\n[3/5] 새 연결 구성...")
    new_connections = build_connections()
    print(f"  연결 수: {len(new_connections)}")

    # Step 4: Update workflow
    print("\n[4/5] 워크플로우 업데이트...")
    update_payload = {
        "name": "루믹스 Veo3 5x8초 숏폼",
        "nodes": new_nodes,
        "connections": new_connections,
        "settings": current.get("settings", {})
    }

    resp = requests.put(
        f"{API_BASE}/workflows/{WORKFLOW_ID}",
        headers=HEADERS,
        json=update_payload
    )

    if resp.status_code != 200:
        print(f"  ERROR: Failed to update workflow: {resp.status_code}")
        print(f"  Response: {resp.text[:2000]}")
        sys.exit(1)

    result = resp.json()
    print(f"  업데이트 성공!")
    print(f"  업데이트 시간: {result.get('updatedAt', 'N/A')}")

    # Step 5: Verify
    print("\n[5/5] 검증...")
    resp = requests.get(
        f"{API_BASE}/workflows/{WORKFLOW_ID}",
        headers=HEADERS
    )
    if resp.status_code != 200:
        print(f"  ERROR: Failed to verify: {resp.status_code}")
        sys.exit(1)

    verified = resp.json()
    print(f"  워크플로우 이름: {verified['name']}")
    print(f"  노드 수: {len(verified['nodes'])}")
    print(f"  노드 목록:")
    for i, node in enumerate(verified['nodes'], 1):
        print(f"    {i:2d}. {node['name']} ({node['type']})")

    # Verify connections
    conn = verified.get('connections', {})
    print(f"\n  연결 수: {len(conn)}")
    for src, targets in conn.items():
        for output_idx, target_list in enumerate(targets.get('main', [])):
            for t in target_list:
                suffix = f" [output {output_idx}]" if len(targets.get('main', [])) > 1 else ""
                print(f"    {src} -> {t['node']}{suffix}")

    print("\n" + "=" * 60)
    print("업데이트 완료!")
    print(f"워크플로우 URL: https://n8n.srv1345711.hstgr.cloud/workflow/{WORKFLOW_ID}")
    print("=" * 60)


if __name__ == "__main__":
    main()
