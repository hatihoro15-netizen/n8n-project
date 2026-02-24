#!/usr/bin/env python3
"""
슬롯 쇼츠 (완전자동 v1) 워크플로우 생성 스크립트
루믹스 솔루션 숏폼 v3를 템플릿으로 사용하여 슬롯 게임 정보 쇼츠 워크플로우를 생성합니다.
"""

import json
import uuid


def new_id():
    """Generate a new UUID for node IDs."""
    return str(uuid.uuid4())


def new_webhook_id():
    """Generate a new UUID for webhook IDs."""
    return str(uuid.uuid4())


def build_workflow():
    """Build the slot shorts workflow JSON."""

    nodes = []

    # 1. 스케줄 트리거
    nodes.append({
        "parameters": {
            "rule": {
                "interval": [
                    {
                        "field": "hours",
                        "hoursInterval": 12
                    }
                ]
            }
        },
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.3,
        "position": [-1872, 224],
        "id": new_id(),
        "name": "스케줄 트리거"
    })

    # 2. AI 주제 생성 - SLOT GAME CONTENT
    slot_prompt = """너는 슬롯 게임 정보 채널의 콘텐츠 기획자야.
YouTube Shorts(30~50초)용 콘텐츠를 기획해줘.

타겟: 슬롯 게임에 관심 있는 일반인, 안전하고 건강한 게임 문화에 관심 있는 사람들
톤: 재미있고 유익하면서도 책임감 있는 목소리, 도박 중독을 조장하지 않는 건전한 정보 제공

핵심 원칙:
- 안전하고 책임감 있는 게임 정보 제공
- 게임 메커니즘과 규칙 설명
- 재미있고 흥미로운 슬롯 게임 팁
- 슬롯을 건강하고 책임감 있게 즐기는 방법

아래 주제 카테고리 중 하나를 랜덤으로 골라서 구체적인 주제를 만들어:
1. 슬롯 게임 종류와 특징 (클래식, 비디오, 프로그레시브 등)
2. RTP(환수율) 이해하기 - 수학적 원리와 의미
3. 안전한 게임 사이트 선택법 - 라이선스, 인증, 보안
4. 배팅 전략과 자금 관리 - 예산 설정, 손실 한도
5. 보너스 활용법 - 프리스핀, 와일드, 스캐터 심볼
6. 게임 중독 예방 - 건강한 게임 습관, 자가 진단
7. 재미있는 슬롯 역사와 트리비아 - 최초의 슬롯머신부터 현대까지
8. 인기 슬롯 게임 리뷰 - 게임 특징, 테마, 재미 요소

피드/클릭 최적화:
- 처음 3초 안에 강력한 훅 (놀라운 사실, 질문, 반전)
- 호기심을 자극하는 제목
- 시청자가 끝까지 보고 싶게 만드는 구성

반드시 아래 JSON 형식으로만 응답해. 마크다운 코드블록 없이 순수 JSON만:
{
  "Subject": "영상 제목 (호기심 유발, 15자 이내)",
  "Narration": "나레이션 전문 (30~50초 분량, 200~350자, 자연스러운 말투)",
  "Caption": "YouTube 설명 (해시태그 포함, 3줄)",
  "Comment": "첫 번째 댓글 (질문 유도 또는 CTA)",
  "BGM_prompt": "BGM 분위기 영어 설명 (10~20단어)"
}"""

    nodes.append({
        "parameters": {
            "modelId": {
                "__rl": True,
                "value": "models/gemini-2.5-flash",
                "mode": "list",
                "cachedResultName": "models/gemini-2.5-flash"
            },
            "messages": {
                "values": [
                    {
                        "content": slot_prompt
                    }
                ]
            },
            "jsonOutput": True,
            "builtInTools": {},
            "options": {}
        },
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1.1,
        "position": [-1568, 224],
        "id": new_id(),
        "name": "AI 주제 생성"
    })

    # 3. 주제 파싱
    parse_code = """const text = $input.first().json.content.parts[0].text;
// Remove potential markdown code blocks
const cleanText = text.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();
const data = JSON.parse(cleanText);

return [{
  json: {
    Subject: data.Subject,
    Narration: data.Narration,
    Caption: data.Caption,
    Comment: data.Comment,
    BGM_prompt: data.BGM_prompt,
    Status: '준비',
    Publish: '',
    generatedAt: new Date().toISOString()
  }
}];"""

    nodes.append({
        "parameters": {
            "jsCode": parse_code
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-1264, 224],
        "id": new_id(),
        "name": "주제 파싱"
    })

    # 4. 시트 기록 - SLOT_SHEET_ID / 슬롯
    nodes.append({
        "parameters": {
            "operation": "append",
            "documentId": {
                "__rl": True,
                "value": "SLOT_SHEET_ID",
                "mode": "list",
                "cachedResultName": "슬롯 쇼츠",
                "cachedResultUrl": ""
            },
            "sheetName": {
                "__rl": True,
                "value": "gid=0",
                "mode": "list",
                "cachedResultName": "슬롯",
                "cachedResultUrl": ""
            },
            "columns": {
                "mappingMode": "defineBelow",
                "value": {
                    "Subject": "={{ $json.Subject }}",
                    "Narration": "={{ $json.Narration }}",
                    "Caption": "={{ $json.Caption }}",
                    "댓글": "={{ $json.Comment }}",
                    "BGM prompt": "={{ $json.BGM_prompt }}",
                    "Status": "준비"
                },
                "matchingColumns": [],
                "schema": [
                    {"id": "Subject", "displayName": "Subject", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                    {"id": "Narration", "displayName": "Narration", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                    {"id": "Caption", "displayName": "Caption", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                    {"id": "댓글", "displayName": "댓글", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                    {"id": "BGM prompt", "displayName": "BGM prompt", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                    {"id": "Status", "displayName": "Status", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True}
                ]
            },
            "options": {}
        },
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.7,
        "position": [-960, 224],
        "id": new_id(),
        "name": "시트 기록"
    })

    # 5. 나레이션 분할
    narration_split_content = '=다음 나레이션을 5개 문장으로 나눠줘.\n규칙:\n1. 문장의 의미 단위로 자연스럽게 나눠줘\n2. 각 문장은 비슷한 길이로 균등하게 배분해\n3. 절대 단어 중간에서 끊지 마\n4. 쉼표, 조사, 문장 끝에서만 끊어줘\n\n나레이션: {{ $json.Narration }}\n\n반드시 아래 JSON 형식으로만 응답해. 마크다운 코드블록 없이 순수 JSON만:\n{"narration1": "...", "narration2": "...", "narration3": "...", "narration4": "...", "narration5": "..."}'

    nodes.append({
        "parameters": {
            "modelId": {
                "__rl": True,
                "value": "models/gemini-2.5-flash",
                "mode": "list",
                "cachedResultName": "models/gemini-2.5-flash"
            },
            "messages": {
                "values": [
                    {
                        "content": narration_split_content
                    }
                ]
            },
            "jsonOutput": True,
            "builtInTools": {},
            "options": {}
        },
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1.1,
        "position": [-672, 224],
        "id": new_id(),
        "name": "나레이션 분할"
    })

    # 6. 5파트 분리
    split_code = """const text = $input.first().json.content.parts[0].text;
const cleanText = text.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();
const data = JSON.parse(cleanText);

const items = [];
for (let i = 1; i <= 5; i++) {
  items.push({
    json: {
      text: data[`narration${i}`],
      index: i,
      subject: $('주제 파싱').first().json.Subject,
      bgmPrompt: $('주제 파싱').first().json.BGM_prompt,
      narration: $('주제 파싱').first().json.Narration
    }
  });
}

return items;"""

    nodes.append({
        "parameters": {
            "jsCode": split_code
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-368, 224],
        "id": new_id(),
        "name": "5파트 분리"
    })

    # 7. TTS 요청
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://queue.fal.run/fal-ai/elevenlabs/tts/turbo-v2.5",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\n  \"text\": \"{{ $json.text }}\",\n  \"language_code\": \"ko\",\n  \"voice\": \"FQ3MuLxZh0jHcZmA5vW1\"\n}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-32, 208],
        "id": new_id(),
        "name": "TTS 요청"
    })

    # 8. TTS 대기
    nodes.append({
        "parameters": {"amount": 30},
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [272, 208],
        "id": new_id(),
        "name": "TTS 대기",
        "webhookId": new_webhook_id()
    })

    # 9. TTS 결과
    nodes.append({
        "parameters": {
            "url": "=https://queue.fal.run/fal-ai/elevenlabs/requests/{{ $json.request_id }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [576, 208],
        "id": new_id(),
        "name": "TTS 결과"
    })

    # 10. 이미지 프롬프트 AI - SLOT GAME VISUALS
    slot_image_prompt = """=주어진 나레이션 파트에 정확히 매칭되는 시네마틱 이미지 프롬프트를 1개 생성해 주세요.

핵심 규칙:
1. 이 나레이션 파트가 말하는 구체적인 내용을 직접적으로 시각화할 것
2. 슬롯 게임/카지노 테마에 맞는 화려하고 컬러풀한 비주얼
3. 하나의 강렬한 비주얼 컨셉에 집중할 것
4. 프롬프트는 영어로 작성, 150~200자
5. 큰따옴표("")는 사용하지 않음
6. illustration, cartoon, 2D, anime, drawing 스타일은 절대 금지
7. 프롬프트는 A vertical video. 로 시작할 것
8. 프롬프트 끝에 필수: no text, no letters, no words, no watermark

비주얼 장르 (슬롯 게임 테마):
{{ ['네온 카지노 — neon glow casino colorful slot machines vibrant lights', '골드 럭셔리 — golden luxury premium casino elegant rich warm tones', '사이버 게임 — cyber gaming futuristic digital slot interface neon blue', '레트로 라스베가스 — retro Las Vegas vintage casino classic slot warm analog', '크리스탈 다이아몬드 — crystal diamond sparkling gems treasure jewels radiant', '다크 VIP — dark VIP lounge premium exclusive moody dramatic lighting', '팝 컬러 — pop color vibrant saturated bold cherry seven symbols', '매직 판타지 — magical fantasy enchanted mystical glowing ethereal casino', '동양풍 카지노 — oriental asian lucky themed golden dragon prosperity', '모던 하이테크 — modern high-tech sleek digital casino holographic clean'][Math.floor(Math.random() * 10)] }}

카메라/촬영 스타일 (이 파트용):
{{ ['extreme close-up of slot machine reels with shallow depth of field', 'close-up with dramatic neon rim lighting on casino elements', 'medium shot of vibrant casino floor with cinematic composition', 'wide establishing shot of glamorous casino interior with atmospheric depth', 'aerial perspective of colorful slot machine array with sweeping motion'][($json.index || 1) - 1] }}

금지 패턴:
- 실제 돈/현금 더미, 실제 도박하는 사람 클로즈업
- 중독적이거나 부정적인 도박 이미지
- 실제 카지노 브랜드 로고
- shield/lock/key, arrow/graph/chart, rocket/lightning, puzzle, hourglass/clock

비주얼 생성 가이드:
- 슬롯 머신, 릴, 심볼 (체리, 세븐, BAR, 다이아몬드), 카지노 분위기
- 화려하고 흥미진진하지만 건전한 게임 분위기
- 마치 고급 게임 광고 감독이 스토리보드를 짜는 것처럼

출력 형식 (프롬프트만 1개):
A vertical video. ..., no text, no letters, no words, no watermark

나레이션 파트:
{{ $json.text }}

시드: {{ Math.floor(Math.random() * 99999) }}"""

    nodes.append({
        "parameters": {
            "promptType": "define",
            "text": slot_image_prompt,
            "batching": {}
        },
        "type": "@n8n/n8n-nodes-langchain.chainLlm",
        "typeVersion": 1.9,
        "position": [-336, 432],
        "id": new_id(),
        "name": "이미지 프롬프트 AI",
        "alwaysOutputData": False
    })

    # 11. Gemini Chat Model
    nodes.append({
        "parameters": {"options": {}},
        "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
        "typeVersion": 1,
        "position": [-432, 624],
        "id": new_id(),
        "name": "Gemini Chat Model"
    })

    # 12. 이미지 생성
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://queue.fal.run/fal-ai/flux-2-pro",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\n  \"prompt\": \"{{ $json.text }}\",\n  \"image_size\": {\n    \"width\": 1080,\n    \"height\": 1920\n  }\n}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-32, 432],
        "id": new_id(),
        "name": "이미지 생성"
    })

    # 13. 이미지 대기
    nodes.append({
        "parameters": {"amount": 30},
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [272, 432],
        "id": new_id(),
        "name": "이미지 대기",
        "webhookId": new_webhook_id()
    })

    # 14. 이미지 결과
    nodes.append({
        "parameters": {
            "url": "={{ $json.response_url }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [576, 432],
        "id": new_id(),
        "name": "이미지 결과"
    })

    # 15. 업스케일 요청
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://queue.fal.run/fal-ai/aura-sr",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\n  \"image_url\": \"{{ $json.images[0].url }}\",\n  \"upscaling_factor\": 2\n}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-32, 672],
        "id": new_id(),
        "name": "업스케일 요청"
    })

    # 16. 업스케일 대기
    nodes.append({
        "parameters": {"amount": 30},
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [256, 672],
        "id": new_id(),
        "name": "업스케일 대기",
        "webhookId": new_webhook_id()
    })

    # 17. 업스케일 결과
    nodes.append({
        "parameters": {
            "url": "={{ $json.response_url }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [560, 672],
        "id": new_id(),
        "name": "업스케일 결과"
    })

    # 18. 영상 생성 (Kie.ai)
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://api.kie.ai/api/v1/jobs/createTask",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\n  \"model\": \"kling-2.6/image-to-video\",\n  \"input\": {\n    \"prompt\": \"{{ $json.prompt || 'cinematic motion, slow camera movement, professional' }}\",\n    \"image_urls\": [\"{{ $json.image.url }}\"],\n    \"sound\": false,\n    \"duration\": \"5\"\n  }\n}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-32, 928],
        "id": new_id(),
        "name": "영상 생성"
    })

    # 19. 영상 대기
    nodes.append({
        "parameters": {"amount": 200},
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [256, 928],
        "id": new_id(),
        "name": "영상 대기",
        "webhookId": new_webhook_id()
    })

    # 20. 영상 결과
    nodes.append({
        "parameters": {
            "url": "=https://api.kie.ai/api/v1/jobs/recordInfo?taskId={{ $json.data.taskId }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [560, 928],
        "id": new_id(),
        "name": "영상 결과"
    })

    # 21. 영상 URL 정리
    url_cleanup_code = """// Kie.ai 응답에서 영상 URL 추출 → fal.ai 호환 형식
const data = $input.first().json;
let videoUrl = '';

if (data.data && data.data.resultJson) {
  try {
    const result = JSON.parse(data.data.resultJson);
    videoUrl = result.resultUrls ? result.resultUrls[0] : '';
  } catch(e) { videoUrl = ''; }
}

return [{ json: { video: { url: videoUrl }, state: data.data?.state || 'unknown' } }];"""

    nodes.append({
        "parameters": {"jsCode": url_cleanup_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [800, 928],
        "id": new_id(),
        "name": "영상 URL 정리"
    })

    # 22. BGM 생성
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://fal.run/beatoven/music-generation",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\n  \"prompt\": \"{{ $json.bgmPrompt || 'upbeat exciting casino slot machine background music' }}\",\n  \"duration\": 40,\n  \"refinement\": 100,\n  \"creativity\": 16\n}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-64, -176],
        "id": new_id(),
        "name": "BGM 생성"
    })

    # 23. BGM 대기
    nodes.append({
        "parameters": {"amount": 30},
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [240, -176],
        "id": new_id(),
        "name": "BGM 대기",
        "webhookId": new_webhook_id()
    })

    # 24. Merge
    nodes.append({
        "parameters": {"numberInputs": 3},
        "type": "n8n-nodes-base.merge",
        "typeVersion": 3.2,
        "position": [1008, 192],
        "id": new_id(),
        "name": "Merge"
    })

    # 25. Aggregate
    nodes.append({
        "parameters": {"aggregate": "aggregateAllItemData", "options": {}},
        "type": "n8n-nodes-base.aggregate",
        "typeVersion": 1,
        "position": [1296, 208],
        "id": new_id(),
        "name": "Aggregate"
    })

    # 26. Shotstack 타임라인
    shotstack_code = r"""// === Shotstack 타임라인 빌더 ===
const allItems = $input.first().json.data;

// Collect data from all paths
const bgmUrl = $('BGM 대기').first().json.audio?.url || '';
const videoDuration = 5;
const bitrate = 128000;

let scenes = [];
let currentStart = 0;

for (let i = 0; i < 5; i++) {
  // TTS results
  const ttsResult = $('TTS 결과').all()[i]?.json;
  const narrationUrl = ttsResult?.audio?.url || '';
  const fileSize = ttsResult?.audio?.file_size || 40000;

  // Calculate duration from audio file size
  let duration = Math.round((fileSize * 8 / bitrate) * 100) / 100;
  if (duration < 3) duration = 5;

  // Video results
  const videoResult = $('영상 URL 정리').all()[i]?.json;
  const videoUrl = videoResult?.video?.url || '';

  // Speed calculation
  let speed = 1;
  if (duration > videoDuration) {
    speed = videoDuration / duration;
  }

  // Subtitle text
  const subtitleText = $('5파트 분리').all()[i]?.json?.text || '';

  scenes.push({
    start: currentStart,
    duration: duration,
    videoUrl: videoUrl,
    narrationUrl: narrationUrl,
    subtitleText: subtitleText,
    speed: speed
  });

  currentStart += duration;
}

const totalDuration = currentStart;

// Build Shotstack timeline
const timeline = {
  soundtrack: {
    src: bgmUrl,
    effect: "fadeOut",
    volume: 0.25
  },
  tracks: [
    // Track 1: Video clips
    {
      clips: scenes.map(s => ({
        asset: {
          type: "video",
          src: s.videoUrl,
          volume: 0,
          trim: 0
        },
        start: s.start,
        length: s.duration,
        fit: "cover",
        ...(s.speed !== 1 ? { speed: s.speed } : {})
      }))
    },
    // Track 2: Narration audio
    {
      clips: scenes.map(s => ({
        asset: {
          type: "audio",
          src: s.narrationUrl
        },
        start: s.start,
        length: s.duration
      }))
    },
    // Track 3: Subtitles
    {
      clips: scenes.map(s => ({
        asset: {
          type: "html",
          html: '<p>' + s.subtitleText + '</p>',
          css: "p { font-family: 'Noto Sans KR', sans-serif; font-size: 42px; color: #ffffff; text-align: center; text-shadow: 2px 2px 8px rgba(0,0,0,0.9); line-height: 1.4; padding: 0 40px; font-weight: 700; }",
          width: 1080,
          height: 300
        },
        start: s.start,
        length: s.duration,
        position: "bottom",
        offset: { y: 0.08 }
      }))
    }
  ]
};

const payload = {
  timeline: timeline,
  output: {
    format: "mp4",
    resolution: "hd",
    aspectRatio: "9:16",
    fps: 30,
    quality: "high"
  }
};

// Also save metadata for sheet update
return [{
  json: {
    shotstack_payload: payload,
    totalDuration: totalDuration,
    scenes: scenes,
    subject: $('주제 파싱').first().json.Subject,
    caption: $('주제 파싱').first().json.Caption,
    comment: $('주제 파싱').first().json.Comment,
    bgmUrl: bgmUrl
  }
}];"""

    nodes.append({
        "parameters": {"jsCode": shotstack_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1600, 208],
        "id": new_id(),
        "name": "Shotstack 타임라인"
    })

    # 27. Shotstack 렌더
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://api.shotstack.io/edit/stage/render",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify($json.shotstack_payload) }}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [1008, 464],
        "id": new_id(),
        "name": "Shotstack 렌더"
    })

    # 28. 렌더 대기
    nodes.append({
        "parameters": {"amount": 120},
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [1296, 464],
        "id": new_id(),
        "name": "렌더 대기",
        "webhookId": new_webhook_id()
    })

    # 29. 렌더 결과
    nodes.append({
        "parameters": {
            "url": "=https://api.shotstack.io/edit/stage/render/{{ $json.response.id }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [1600, 464],
        "id": new_id(),
        "name": "렌더 결과"
    })

    # 30. 상태 업데이트 - SLOT_SHEET_ID / 슬롯
    nodes.append({
        "parameters": {
            "operation": "update",
            "documentId": {
                "__rl": True,
                "value": "SLOT_SHEET_ID",
                "mode": "list",
                "cachedResultName": "슬롯 쇼츠",
                "cachedResultUrl": ""
            },
            "sheetName": {
                "__rl": True,
                "value": "gid=0",
                "mode": "list",
                "cachedResultName": "슬롯",
                "cachedResultUrl": ""
            },
            "columns": {
                "mappingMode": "defineBelow",
                "value": {
                    "row_number": "={{ $('시트 기록').first().json.row_number }}",
                    "Status": "생성 완료",
                    "업로드 URL": "={{ $json.response.url }}"
                },
                "matchingColumns": ["row_number"],
                "schema": [
                    {"id": "Status", "displayName": "Status", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                    {"id": "업로드 URL", "displayName": "업로드 URL", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                    {"id": "row_number", "displayName": "row_number", "required": False, "defaultMatch": False, "display": True, "type": "number", "canBeUsedToMatch": True, "readOnly": True}
                ]
            },
            "options": {}
        },
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.7,
        "position": [1904, 400],
        "id": new_id(),
        "name": "상태 업데이트"
    })

    # 31. 영상 다운로드
    nodes.append({
        "parameters": {
            "url": "={{ $json.response.url }}",
            "options": {
                "response": {
                    "response": {
                        "responseFormat": "file"
                    }
                }
            }
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [1904, 592],
        "id": new_id(),
        "name": "영상 다운로드"
    })

    # 32. YouTube 업로드
    nodes.append({
        "parameters": {
            "resource": "video",
            "operation": "upload",
            "title": "={{ $('주제 파싱').first().json.Subject }}",
            "regionCode": "KR",
            "categoryId": "28",
            "options": {
                "description": "={{ $('주제 파싱').first().json.Caption }}",
                "privacyStatus": "public"
            }
        },
        "type": "n8n-nodes-base.youTube",
        "typeVersion": 1,
        "position": [2128, 592],
        "id": new_id(),
        "name": "YouTube 업로드"
    })

    # 33. 첫 댓글
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "youTubeOAuth2Api",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\n  \"snippet\": {\n    \"videoId\": \"{{ $json.id }}\",\n    \"topLevelComment\": {\n      \"snippet\": {\n        \"textOriginal\": \"{{ $('주제 파싱').first().json.Comment }}\"\n      }\n    }\n  }\n}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [2416, 592],
        "id": new_id(),
        "name": "첫 댓글"
    })

    # 34. 발행 완료 - SLOT_SHEET_ID / 슬롯
    nodes.append({
        "parameters": {
            "operation": "update",
            "documentId": {
                "__rl": True,
                "value": "SLOT_SHEET_ID",
                "mode": "list",
                "cachedResultName": "슬롯 쇼츠",
                "cachedResultUrl": ""
            },
            "sheetName": {
                "__rl": True,
                "value": "gid=0",
                "mode": "list",
                "cachedResultName": "슬롯",
                "cachedResultUrl": ""
            },
            "columns": {
                "mappingMode": "defineBelow",
                "value": {
                    "row_number": "={{ $('시트 기록').first().json.row_number }}",
                    "Publish": "발행 완료",
                    "업로드 URL": "=https://youtube.com/shorts/{{ $('YouTube 업로드').first().json.id }}"
                },
                "matchingColumns": ["row_number"],
                "schema": [
                    {"id": "Publish", "displayName": "Publish", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                    {"id": "업로드 URL", "displayName": "업로드 URL", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                    {"id": "row_number", "displayName": "row_number", "required": False, "defaultMatch": False, "display": True, "type": "number", "canBeUsedToMatch": True, "readOnly": True}
                ]
            },
            "options": {}
        },
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.7,
        "position": [2720, 592],
        "id": new_id(),
        "name": "발행 완료"
    })

    # ============================================================
    # CONNECTIONS
    # ============================================================

    connections = {
        "스케줄 트리거": {
            "main": [[{"node": "AI 주제 생성", "type": "main", "index": 0}]]
        },
        "AI 주제 생성": {
            "main": [[{"node": "주제 파싱", "type": "main", "index": 0}]]
        },
        "주제 파싱": {
            "main": [[{"node": "시트 기록", "type": "main", "index": 0}]]
        },
        "시트 기록": {
            "main": [[
                {"node": "나레이션 분할", "type": "main", "index": 0},
                {"node": "BGM 생성", "type": "main", "index": 0}
            ]]
        },
        "나레이션 분할": {
            "main": [[{"node": "5파트 분리", "type": "main", "index": 0}]]
        },
        "5파트 분리": {
            "main": [[
                {"node": "TTS 요청", "type": "main", "index": 0},
                {"node": "이미지 프롬프트 AI", "type": "main", "index": 0}
            ]]
        },
        "TTS 요청": {
            "main": [[{"node": "TTS 대기", "type": "main", "index": 0}]]
        },
        "TTS 대기": {
            "main": [[{"node": "TTS 결과", "type": "main", "index": 0}]]
        },
        "TTS 결과": {
            "main": [[{"node": "Merge", "type": "main", "index": 1}]]
        },
        "이미지 프롬프트 AI": {
            "main": [[{"node": "이미지 생성", "type": "main", "index": 0}]]
        },
        "이미지 생성": {
            "main": [[{"node": "이미지 대기", "type": "main", "index": 0}]]
        },
        "이미지 대기": {
            "main": [[{"node": "이미지 결과", "type": "main", "index": 0}]]
        },
        "이미지 결과": {
            "main": [[{"node": "업스케일 요청", "type": "main", "index": 0}]]
        },
        "업스케일 요청": {
            "main": [[{"node": "업스케일 대기", "type": "main", "index": 0}]]
        },
        "업스케일 대기": {
            "main": [[{"node": "업스케일 결과", "type": "main", "index": 0}]]
        },
        "업스케일 결과": {
            "main": [[{"node": "영상 생성", "type": "main", "index": 0}]]
        },
        "영상 생성": {
            "main": [[{"node": "영상 대기", "type": "main", "index": 0}]]
        },
        "영상 대기": {
            "main": [[{"node": "영상 결과", "type": "main", "index": 0}]]
        },
        "영상 결과": {
            "main": [[{"node": "영상 URL 정리", "type": "main", "index": 0}]]
        },
        "영상 URL 정리": {
            "main": [[{"node": "Merge", "type": "main", "index": 2}]]
        },
        "BGM 생성": {
            "main": [[{"node": "BGM 대기", "type": "main", "index": 0}]]
        },
        "BGM 대기": {
            "main": [[{"node": "Merge", "type": "main", "index": 0}]]
        },
        "Gemini Chat Model": {
            "ai_languageModel": [[{"node": "이미지 프롬프트 AI", "type": "ai_languageModel", "index": 0}]]
        },
        "Merge": {
            "main": [[{"node": "Aggregate", "type": "main", "index": 0}]]
        },
        "Aggregate": {
            "main": [[{"node": "Shotstack 타임라인", "type": "main", "index": 0}]]
        },
        "Shotstack 타임라인": {
            "main": [[{"node": "Shotstack 렌더", "type": "main", "index": 0}]]
        },
        "Shotstack 렌더": {
            "main": [[{"node": "렌더 대기", "type": "main", "index": 0}]]
        },
        "렌더 대기": {
            "main": [[{"node": "렌더 결과", "type": "main", "index": 0}]]
        },
        "렌더 결과": {
            "main": [[
                {"node": "상태 업데이트", "type": "main", "index": 0},
                {"node": "영상 다운로드", "type": "main", "index": 0}
            ]]
        },
        "영상 다운로드": {
            "main": [[{"node": "YouTube 업로드", "type": "main", "index": 0}]]
        },
        "YouTube 업로드": {
            "main": [[{"node": "첫 댓글", "type": "main", "index": 0}]]
        },
        "첫 댓글": {
            "main": [[{"node": "발행 완료", "type": "main", "index": 0}]]
        }
    }

    # ============================================================
    # FINAL WORKFLOW (only: name, nodes, connections, settings)
    # ============================================================

    workflow = {
        "name": "슬롯 쇼츠 (완전자동 v1)",
        "nodes": nodes,
        "connections": connections,
        "settings": {
            "executionOrder": "v1"
        }
    }

    return workflow


def main():
    print("=" * 60)
    print("슬롯 쇼츠 (완전자동 v1) 워크플로우 생성 스크립트")
    print("=" * 60)

    workflow = build_workflow()

    output_path = "/Users/gimdongseog/n8n-project/slot_shorts_v1.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 워크플로우 JSON 생성 완료: {output_path}")
    print(f"  - 이름: {workflow['name']}")
    print(f"  - 노드 수: {len(workflow['nodes'])}")
    print(f"  - 연결 수: {len(workflow['connections'])}")

    # Verify node names match connections
    node_names = {n["name"] for n in workflow["nodes"]}
    conn_sources = set(workflow["connections"].keys())
    conn_targets = set()
    for src, data in workflow["connections"].items():
        for conn_type, outputs in data.items():
            for output_list in outputs:
                for conn in output_list:
                    conn_targets.add(conn["node"])

    missing_sources = conn_sources - node_names
    missing_targets = conn_targets - node_names
    if missing_sources:
        print(f"\n[WARNING] 연결 소스에 없는 노드: {missing_sources}")
    if missing_targets:
        print(f"\n[WARNING] 연결 타겟에 없는 노드: {missing_targets}")

    if not missing_sources and not missing_targets:
        print("  - 모든 연결이 유효합니다.")

    # List Google Sheets nodes
    print("\n[INFO] Google Sheets 노드 (SLOT_SHEET_ID 플레이스홀더):")
    for n in workflow["nodes"]:
        if n["type"] == "n8n-nodes-base.googleSheets":
            doc_id = n["parameters"].get("documentId", {}).get("value", "N/A")
            sheet = n["parameters"].get("sheetName", {}).get("cachedResultName", "N/A")
            print(f"  - {n['name']}: documentId={doc_id}, sheet={sheet}")

    # Verify no credentials
    print("\n[INFO] 크레덴셜 체크:")
    cred_found = False
    for n in workflow["nodes"]:
        if "credentials" in n:
            print(f"  [FOUND] {n['name']}에 credentials 키 발견")
            cred_found = True
    if not cred_found:
        print("  - 크레덴셜 없음 (정상)")

    wf_json = json.dumps(workflow, ensure_ascii=False)
    print(f"\n[OK] 최종 워크플로우 저장: {output_path}")
    print(f"  - 파일 크기: {len(wf_json):,} bytes")

    return output_path


if __name__ == "__main__":
    output_file = main()
    print(f"\n출력 파일: {output_file}")
