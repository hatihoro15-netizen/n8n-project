"""
루믹스 솔루션 - 숏폼 완전자동 워크플로우 생성기
==============================================
Schedule → AI 주제생성 → 나레이션 5분할 → 병렬(TTS, 이미지→영상, BGM)
→ Shotstack 합성 → YouTube 업로드

개선사항 (기존 '전용' 대비):
1. 완전 자동: AI가 주제/나레이션/캡션 전부 생성
2. 이미지-나레이션 1:1 매칭 (분할된 텍스트 기반)
3. Kling 2.6 Pro (기존 1.6 Standard → 화질 향상)
4. AuraSR 업스케일 (기존 ESRGAN → 더 선명)
5. Shotstack 편집 (기존 Creatomate → 60% 비용 절감)
6. 비주얼 장르 랜덤 + 카메라 스타일 차별화
"""

import json
import uuid

def uid():
    return str(uuid.uuid4())

# ============================================================
# 노드 정의
# ============================================================

nodes = []
connections = {}

def add_node(name, node_type, type_version, position, parameters=None, **kwargs):
    node = {
        "parameters": parameters or {},
        "type": node_type,
        "typeVersion": type_version,
        "position": position,
        "id": uid(),
        "name": name,
    }
    node.update(kwargs)
    nodes.append(node)
    return name

def connect(from_node, to_node, from_type="main", to_type="main", from_index=0, to_index=0):
    if from_node not in connections:
        connections[from_node] = {}
    if from_type not in connections[from_node]:
        connections[from_node][from_type] = [[]]
    # Ensure enough output indices
    while len(connections[from_node][from_type]) <= from_index:
        connections[from_node][from_type].append([])
    connections[from_node][from_type][from_index].append({
        "node": to_node,
        "type": to_type,
        "index": to_index
    })

# ============================================================
# Phase 1: 자동 주제 생성
# ============================================================

add_node(
    "스케줄 트리거",
    "n8n-nodes-base.scheduleTrigger",
    1.3,
    [-2200, 300],
    {"rule": {"interval": [{"field": "hours", "hoursInterval": 12}]}}
)

add_node(
    "AI 주제 생성",
    "@n8n/n8n-nodes-langchain.googleGemini",
    1.1,
    [-1900, 300],
    {
        "modelId": {"__rl": True, "value": "models/gemini-2.5-flash", "mode": "list", "cachedResultName": "models/gemini-2.5-flash"},
        "messages": {"values": [{"content": """너는 루믹스 솔루션(웹/앱 개발 및 IT 솔루션 전문 기업)의 콘텐츠 기획자야.
YouTube Shorts(30~50초)용 콘텐츠를 기획해줘.

타겟: IT 솔루션이 필요한 사업자, 스타트업, 중소기업 대표
톤: 전문적이면서 쉽게 설명, 신뢰감 있는 목소리

아래 주제 카테고리 중 하나를 랜덤으로 골라서 구체적인 주제를 만들어:
1. 웹사이트/앱 제작의 중요성과 트렌드
2. IT 자동화로 비용 절감하는 방법
3. 성공적인 디지털 전환 사례
4. AI/클라우드 기술 활용법
5. 보안과 데이터 관리의 중요성
6. 모바일 앱으로 매출 올리는 전략
7. SaaS vs 커스텀 개발 비교
8. SEO/마케팅 자동화 전략

반드시 아래 JSON 형식으로만 응답해. 마크다운 코드블록 없이 순수 JSON만:
{
  "Subject": "영상 제목 (호기심 유발, 15자 이내)",
  "Narration": "나레이션 전문 (30~50초 분량, 200~350자, 자연스러운 말투)",
  "Caption": "YouTube 설명 (해시태그 포함, 3줄)",
  "Comment": "첫 번째 댓글 (질문 유도 또는 CTA)",
  "BGM_prompt": "BGM 분위기 영어 설명 (10~20단어)"
}"""}]},
        "jsonOutput": True,
        "builtInTools": {},
        "options": {}
    }
)

add_node(
    "주제 파싱",
    "n8n-nodes-base.code",
    2,
    [-1600, 300],
    {"jsCode": """const text = $input.first().json.content.parts[0].text;
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
}];"""}
)

add_node(
    "시트 기록",
    "n8n-nodes-base.googleSheets",
    4.7,
    [-1300, 300],
    {
        "operation": "append",
        "documentId": {"__rl": True, "value": "1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag", "mode": "list",
                       "cachedResultName": "n8n LUMIX",
                       "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag/edit?usp=drivesdk"},
        "sheetName": {"__rl": True, "value": "gid=0", "mode": "list",
                      "cachedResultName": "루믹스",
                      "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag/edit#gid=0"},
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
                {"id": "Status", "displayName": "Status", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
            ]
        },
        "options": {}
    }
)

# ============================================================
# Phase 2: 나레이션 분할
# ============================================================

add_node(
    "나레이션 분할",
    "@n8n/n8n-nodes-langchain.googleGemini",
    1.1,
    [-1000, 300],
    {
        "modelId": {"__rl": True, "value": "models/gemini-2.5-flash", "mode": "list", "cachedResultName": "models/gemini-2.5-flash"},
        "messages": {"values": [{"content": """=다음 나레이션을 5개 문장으로 나눠줘.
규칙:
1. 문장의 의미 단위로 자연스럽게 나눠줘
2. 각 문장은 비슷한 길이로 균등하게 배분해
3. 절대 단어 중간에서 끊지 마
4. 쉼표, 조사, 문장 끝에서만 끊어줘

나레이션: {{ $json.Narration }}

반드시 아래 JSON 형식으로만 응답해. 마크다운 코드블록 없이 순수 JSON만:
{"narration1": "...", "narration2": "...", "narration3": "...", "narration4": "...", "narration5": "..."}"""}]},
        "jsonOutput": True,
        "builtInTools": {},
        "options": {}
    }
)

add_node(
    "5파트 분리",
    "n8n-nodes-base.code",
    2,
    [-700, 300],
    {"jsCode": """const text = $input.first().json.content.parts[0].text;
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

return items;"""}
)

# ============================================================
# Phase 3a: TTS (나레이션 음성 생성)
# ============================================================

add_node(
    "TTS 요청",
    "n8n-nodes-base.httpRequest",
    4.3,
    [-400, 100],
    {
        "method": "POST",
        "url": "https://queue.fal.run/fal-ai/elevenlabs/tts/turbo-v2.5",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={\n  "text": "{{ $json.text }}",\n  "language_code": "ko",\n  "voice": "FQ3MuLxZh0jHcZmA5vW1"\n}',
        "options": {}
    }
)

add_node(
    "TTS 대기",
    "n8n-nodes-base.wait",
    1.1,
    [-100, 100],
    {"amount": 30},
    webhookId=uid()
)

add_node(
    "TTS 결과",
    "n8n-nodes-base.httpRequest",
    4.3,
    [200, 100],
    {
        "url": "=https://queue.fal.run/fal-ai/elevenlabs/requests/{{ $json.request_id }}",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "options": {}
    }
)

# ============================================================
# Phase 3b: 이미지 프롬프트 → 이미지 → 업스케일 → 영상
# ============================================================

# 이미지 프롬프트 생성 (Gemini Chain LLM - 1:1 매칭)
add_node(
    "이미지 프롬프트 AI",
    "@n8n/n8n-nodes-langchain.chainLlm",
    1.9,
    [-400, 500],
    {
        "promptType": "define",
        "text": """=주어진 나레이션 파트에 정확히 매칭되는 시네마틱 이미지 프롬프트를 1개 생성해 주세요.

핵심 규칙:
1. 이 나레이션 파트가 말하는 구체적인 내용을 직접적으로 시각화할 것
2. 추상적 비주얼이 아닌, 나레이션이 설명하는 실제 상황/장면을 보여줄 것
3. 하나의 강렬한 비주얼 컨셉에 집중할 것
4. 프롬프트는 영어로 작성, 150~200자
5. 큰따옴표("")는 사용하지 않음
6. illustration, cartoon, 2D, anime, drawing 스타일은 절대 금지
7. 프롬프트는 A vertical video. 로 시작할 것
8. 프롬프트 끝에 필수: no text, no letters, no words, no watermark

비주얼 장르 (이번 영상 전체 톤):
{{ ['사이버펑크 네온 — neon glow cyberpunk futuristic dark city', '자연 다큐멘터리 — nature documentary organic earthy warm tones', '미니멀 흑백 — minimal monochrome high contrast black white', '레트로 필름그레인 — retro film grain vintage 70s warm analog', '하이테크 미래 — high-tech futuristic holographic clean blue', '다크 시네마틱 — dark cinematic dramatic shadows moody', '팝아트 컬러풀 — pop art vibrant saturated bold colors', '수중/우주 판타지 — underwater space fantasy ethereal floating', '동양풍 — oriental asian aesthetic ink wash dramatic', '고딕 다크판타지 — gothic dark fantasy mystical ancient'][Math.floor(Math.random() * 10)] }}

카메라/촬영 스타일 (이 파트용):
{{ ['extreme close-up with shallow depth of field', 'close-up with dramatic rim lighting', 'medium shot with cinematic composition', 'wide establishing shot with atmospheric depth', 'aerial drone perspective with sweeping motion'][($json.index || 1) - 1] }}

금지 패턴:
- 창문 앞 인물 실루엣, 골든아워 역광, 양복 남자가 도시 내려다보는 장면
- 악수 장면, 단순 사무실
- shield/lock/key, arrow/graph/chart, rocket/lightning, puzzle, hourglass/clock

비주얼 생성 가이드:
- 나레이션이 말하는 내용을 시청자가 바로 이해할 수 있는 구체적 장면
- 마치 고급 브랜드 광고 감독이 스토리보드를 짜는 것처럼

출력 형식 (프롬프트만 1개):
A vertical video. ..., no text, no letters, no words, no watermark

나레이션 파트:
{{ $json.text }}

시드: {{ Math.floor(Math.random() * 99999) }}""",
        "hasOutputParser": False,
        "batching": {}
    },
    alwaysOutputData=False
)

# Gemini Chat Model (이미지 프롬프트 AI의 서브 노드)
add_node(
    "Gemini Chat Model",
    "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
    1,
    [-500, 700],
    {"modelName": "models/gemini-2.5-flash", "options": {}}
)

# 이미지 생성 (FLUX Pro)
add_node(
    "이미지 생성",
    "n8n-nodes-base.httpRequest",
    4.3,
    [-100, 500],
    {
        "method": "POST",
        "url": "https://queue.fal.run/fal-ai/flux-pro",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={\n  "prompt": "{{ $json.text }}",\n  "image_size": {\n    "width": 1080,\n    "height": 1920\n  },\n  "style": "realistic_image"\n}',
        "options": {}
    }
)

add_node(
    "이미지 대기",
    "n8n-nodes-base.wait",
    1.1,
    [200, 500],
    {"amount": 30},
    webhookId=uid()
)

add_node(
    "이미지 결과",
    "n8n-nodes-base.httpRequest",
    4.3,
    [500, 500],
    {
        "url": "={{ $json.response_url }}",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "options": {}
    }
)

# 업스케일 (AuraSR)
add_node(
    "업스케일 요청",
    "n8n-nodes-base.httpRequest",
    4.3,
    [500, 700],
    {
        "method": "POST",
        "url": "https://queue.fal.run/fal-ai/aura-sr",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={\n  "image_url": "{{ $json.images[0].url }}",\n  "upscaling_factor": 2\n}',
        "options": {}
    }
)

add_node(
    "업스케일 대기",
    "n8n-nodes-base.wait",
    1.1,
    [800, 700],
    {"amount": 30},
    webhookId=uid()
)

add_node(
    "업스케일 결과",
    "n8n-nodes-base.httpRequest",
    4.3,
    [1100, 700],
    {
        "url": "={{ $json.response_url }}",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "options": {}
    }
)

# 영상 생성 (Kling 2.6 Pro)
add_node(
    "영상 생성",
    "n8n-nodes-base.httpRequest",
    4.3,
    [500, 950],
    {
        "method": "POST",
        "url": "https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={\n  "prompt": "{{ $json.prompt || \'cinematic motion, slow camera movement\' }}",\n  "image_url": "{{ $json.image.url }}",\n  "duration": "5",\n  "aspect_ratio": "9:16"\n}',
        "options": {}
    }
)

add_node(
    "영상 대기",
    "n8n-nodes-base.wait",
    1.1,
    [800, 950],
    {"amount": 200},
    webhookId=uid()
)

add_node(
    "영상 결과",
    "n8n-nodes-base.httpRequest",
    4.3,
    [1100, 950],
    {
        "url": "={{ $json.response_url }}",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "options": {}
    }
)

# ============================================================
# Phase 3c: BGM (한번만 실행)
# ============================================================

add_node(
    "BGM 생성",
    "n8n-nodes-base.httpRequest",
    4.3,
    [-400, -100],
    {
        "method": "POST",
        "url": "https://fal.run/beatoven/music-generation",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={\n  "prompt": "{{ $json.bgmPrompt || \'upbeat corporate technology background music\' }}",\n  "duration": 40,\n  "refinement": 100,\n  "creativity": 16\n}',
        "options": {}
    }
)

add_node(
    "BGM 대기",
    "n8n-nodes-base.wait",
    1.1,
    [-100, -100],
    {"amount": 30},
    webhookId=uid()
)

# ============================================================
# Phase 4: 합치기
# ============================================================

add_node(
    "Merge",
    "n8n-nodes-base.merge",
    3.2,
    [1400, 300],
    {"numberInputs": 3}
)

add_node(
    "Aggregate",
    "n8n-nodes-base.aggregate",
    1,
    [1600, 300],
    {"aggregate": "aggregateAllItemData", "options": {}}
)

# Shotstack 타임라인 빌드 + Duration 계산
add_node(
    "Shotstack 타임라인",
    "n8n-nodes-base.code",
    2,
    [1800, 300],
    {"jsCode": """// === Shotstack 타임라인 빌더 ===
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
  const videoResult = $('영상 결과').all()[i]?.json;
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
}];"""}
)

# Shotstack 렌더 요청
add_node(
    "Shotstack 렌더",
    "n8n-nodes-base.httpRequest",
    4.3,
    [2100, 300],
    {
        "method": "POST",
        "url": "https://api.shotstack.io/edit/stage/render",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json.shotstack_payload) }}",
        "options": {}
    }
)

add_node(
    "렌더 대기",
    "n8n-nodes-base.wait",
    1.1,
    [2400, 300],
    {"amount": 120},
    webhookId=uid()
)

add_node(
    "렌더 결과",
    "n8n-nodes-base.httpRequest",
    4.3,
    [2700, 300],
    {
        "url": "=https://api.shotstack.io/edit/stage/render/{{ $json.response.id }}",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "options": {}
    }
)

# ============================================================
# Phase 5: 시트 업데이트 + YouTube 업로드
# ============================================================

add_node(
    "상태 업데이트",
    "n8n-nodes-base.googleSheets",
    4.7,
    [3000, 200],
    {
        "operation": "update",
        "documentId": {"__rl": True, "value": "1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag", "mode": "list",
                       "cachedResultName": "n8n LUMIX",
                       "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag/edit?usp=drivesdk"},
        "sheetName": {"__rl": True, "value": "gid=0", "mode": "list",
                      "cachedResultName": "루믹스",
                      "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag/edit#gid=0"},
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
    }
)

# 영상 다운로드 (YouTube 업로드용)
add_node(
    "영상 다운로드",
    "n8n-nodes-base.httpRequest",
    4.3,
    [3000, 400],
    {
        "url": "={{ $json.response.url }}",
        "options": {"response": {"response": {"responseFormat": "file"}}}
    }
)

add_node(
    "YouTube 업로드",
    "n8n-nodes-base.youTube",
    1,
    [3300, 400],
    {
        "resource": "video",
        "operation": "upload",
        "title": "={{ $('주제 파싱').first().json.Subject }}",
        "regionCode": "KR",
        "categoryId": "28",
        "options": {
            "description": "={{ $('주제 파싱').first().json.Caption }}",
            "privacyStatus": "public"
        }
    }
)

add_node(
    "첫 댓글",
    "n8n-nodes-base.httpRequest",
    4.3,
    [3600, 400],
    {
        "method": "POST",
        "url": "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "youTubeOAuth2Api",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": """={
  "snippet": {
    "videoId": "{{ $json.id }}",
    "topLevelComment": {
      "snippet": {
        "textOriginal": "{{ $('주제 파싱').first().json.Comment }}"
      }
    }
  }
}""",
        "options": {}
    }
)

add_node(
    "발행 완료",
    "n8n-nodes-base.googleSheets",
    4.7,
    [3900, 400],
    {
        "operation": "update",
        "documentId": {"__rl": True, "value": "1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag", "mode": "list",
                       "cachedResultName": "n8n LUMIX",
                       "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag/edit?usp=drivesdk"},
        "sheetName": {"__rl": True, "value": "gid=0", "mode": "list",
                      "cachedResultName": "루믹스",
                      "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag/edit#gid=0"},
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
    }
)

# ============================================================
# 연결 (Connections)
# ============================================================

# Phase 1: 주제 생성
connect("스케줄 트리거", "AI 주제 생성")
connect("AI 주제 생성", "주제 파싱")
connect("주제 파싱", "시트 기록")

# Phase 2: 나레이션 분할
connect("시트 기록", "나레이션 분할")
connect("나레이션 분할", "5파트 분리")

# Phase 3: 병렬 처리
# 5파트 분리 → TTS + 이미지 프롬프트 (1:1 매칭)
connect("5파트 분리", "TTS 요청")
connect("5파트 분리", "이미지 프롬프트 AI")

# BGM은 시트 기록 후 바로 (5파트 분리와 별개)
connect("시트 기록", "BGM 생성")

# TTS path
connect("TTS 요청", "TTS 대기")
connect("TTS 대기", "TTS 결과")
connect("TTS 결과", "Merge", to_index=0)

# Image → Video path
connect("이미지 프롬프트 AI", "이미지 생성")
connect("이미지 생성", "이미지 대기")
connect("이미지 대기", "이미지 결과")
connect("이미지 결과", "업스케일 요청")
connect("업스케일 요청", "업스케일 대기")
connect("업스케일 대기", "업스케일 결과")
connect("업스케일 결과", "영상 생성")
connect("영상 생성", "영상 대기")
connect("영상 대기", "영상 결과")
connect("영상 결과", "Merge", to_index=2)

# BGM path
connect("BGM 생성", "BGM 대기")
connect("BGM 대기", "Merge", to_index=1)

# Gemini Chat Model → 이미지 프롬프트 AI (AI 서브노드 연결)
connect("Gemini Chat Model", "이미지 프롬프트 AI", from_type="ai_languageModel", to_type="ai_languageModel")

# Phase 4: 합성
connect("Merge", "Aggregate")
connect("Aggregate", "Shotstack 타임라인")
connect("Shotstack 타임라인", "Shotstack 렌더")
connect("Shotstack 렌더", "렌더 대기")
connect("렌더 대기", "렌더 결과")

# Phase 5: 저장 & 업로드
connect("렌더 결과", "상태 업데이트")
connect("렌더 결과", "영상 다운로드")
connect("영상 다운로드", "YouTube 업로드")
connect("YouTube 업로드", "첫 댓글")
connect("첫 댓글", "발행 완료")

# ============================================================
# 워크플로우 JSON 생성
# ============================================================

workflow = {
    "name": "루믹스 솔루션 숏폼 (완전자동 v2)",
    "nodes": nodes,
    "connections": connections,
    "settings": {"executionOrder": "v1"}
}

output_path = '/Users/gimdongseog/n8n-project/workflow_lumix_shortform.json'
with open(output_path, 'w') as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print("=" * 60)
print("루믹스 솔루션 숏폼 워크플로우 생성 완료!")
print(f"파일: {output_path}")
print("=" * 60)
print()
print("워크플로우 구조:")
print(f"  총 노드 수: {len(nodes)}개")
print()
print("흐름:")
print("  [스케줄 트리거] → [AI 주제 생성] → [주제 파싱] → [시트 기록]")
print("       → [나레이션 분할] → [5파트 분리]")
print("       → 병렬 처리:")
print("         Path A: [TTS 요청] → [대기] → [TTS 결과]")
print("         Path B: [이미지 프롬프트] → [이미지 생성] → [업스케일] → [영상 생성]")
print("         Path C: [BGM 생성] → [대기]")
print("       → [Merge] → [Aggregate] → [Shotstack 타임라인]")
print("       → [렌더] → [상태 업데이트] + [YouTube 업로드] → [발행 완료]")
print()
print("필요한 Credential 설정 (n8n에서):")
print("  1. Google Sheets (기존 사용 중)")
print("  2. Google Gemini (기존 사용 중)")
print("  3. fal.ai HTTP Header Auth (기존 사용 중)")
print("  4. YouTube OAuth2 (기존 사용 중)")
print("  5. ★ Shotstack API Key (새로 추가 필요)")
print("     → https://shotstack.io 가입 → API Key 복사")
print("     → n8n에서 HTTP Header Auth 생성:")
print("       Name: Shotstack")
print("       Header Name: x-api-key")
print("       Header Value: (API Key)")
