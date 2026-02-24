"""
루믹스 솔루션 - 롱폼 완전자동 워크플로우 생성기
==============================================
2~3분 YouTube 영상 (가로형 1920x1080)
Schedule → AI 대본생성 → 10파트 분할 → 병렬(TTS, Pexels 스톡영상)
→ Shotstack 합성 → YouTube 업로드

특징:
- AI 영상 생성 없음 → Pexels 무료 스톡영상 사용 = 비용 대폭 절감
- 10씬 x 15초 = 약 2.5분
- 비용: TTS ~$0.10 + BGM ~$0.10 + Shotstack ~$0.10 = 약 $0.30/편
"""

import json
import uuid

def uid():
    return str(uuid.uuid4())

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
    while len(connections[from_node][from_type]) <= from_index:
        connections[from_node][from_type].append([])
    connections[from_node][from_type][from_index].append({
        "node": to_node,
        "type": to_type,
        "index": to_index
    })

# ============================================================
# Phase 1: 자동 주제 + 대본 생성
# ============================================================

add_node(
    "스케줄 트리거",
    "n8n-nodes-base.scheduleTrigger",
    1.3,
    [-2400, 300],
    {"rule": {"interval": [{"field": "days", "daysInterval": 1}]}}
)

add_node(
    "AI 대본 생성",
    "@n8n/n8n-nodes-langchain.googleGemini",
    1.1,
    [-2100, 300],
    {
        "modelId": {"__rl": True, "value": "models/gemini-2.5-flash", "mode": "list", "cachedResultName": "models/gemini-2.5-flash"},
        "messages": {"values": [{"content": """너는 루믹스 솔루션(웹/앱 개발 및 IT 솔루션 전문 기업)의 콘텐츠 기획자이자 영상 대본 작가야.
YouTube 롱폼 영상(2~3분)용 대본을 작성해줘.

타겟: IT 솔루션이 필요한 사업자, 스타트업, 중소기업 대표
톤: 전문적이면서 쉽게 설명, 시청자가 끝까지 보게 만드는 스토리텔링
구조: 훅(호기심) → 문제 제기 → 해결책 → 사례/근거 → CTA

아래 주제 카테고리 중 하나를 랜덤으로 골라서 구체적인 주제를 만들어:
1. 웹사이트/앱 제작의 숨겨진 비용과 진짜 가치
2. IT 자동화로 월 100시간 절약하는 방법
3. 성공적인 디지털 전환 실제 사례 분석
4. AI 도입으로 매출 2배 올린 기업 이야기
5. 보안 사고 실제 사례와 예방법
6. 모바일 앱 하나로 매출 구조를 바꾼 사업자
7. 커스텀 개발 vs SaaS: 어떤 게 맞는지 판단하는 법
8. SEO가 광고보다 효과적인 이유 (데이터 기반)
9. 클라우드 마이그레이션 실패하는 3가지 이유
10. 2026년 꼭 알아야 할 IT 트렌드

대본 규칙:
- 자연스러운 구어체 (방송 진행자 톤)
- 총 800~1200자 (한국어 기준, 2~3분 분량)
- 10개 파트로 나눠서 작성 (각 파트 80~120자)
- 각 파트에 Pexels 스톡영상 검색용 영어 키워드 포함

반드시 아래 JSON 형식으로만 응답해. 마크다운 코드블록 없이 순수 JSON만:
{
  "Subject": "영상 제목 (호기심 유발, 20자 이내)",
  "Caption": "YouTube 설명 (해시태그 포함, 5줄)",
  "Comment": "첫 번째 댓글 (질문 유도)",
  "BGM_prompt": "BGM 분위기 영어 설명 (corporate, upbeat 등 15~25단어)",
  "parts": [
    {"text": "나레이션 텍스트 (80~120자)", "keyword": "pexels search keyword in english (2~4 words)"},
    {"text": "...", "keyword": "..."},
    {"text": "...", "keyword": "..."},
    {"text": "...", "keyword": "..."},
    {"text": "...", "keyword": "..."},
    {"text": "...", "keyword": "..."},
    {"text": "...", "keyword": "..."},
    {"text": "...", "keyword": "..."},
    {"text": "...", "keyword": "..."},
    {"text": "...", "keyword": "..."}
  ]
}"""}]},
        "jsonOutput": True,
        "builtInTools": {},
        "options": {}
    }
)

add_node(
    "대본 파싱",
    "n8n-nodes-base.code",
    2,
    [-1800, 300],
    {"jsCode": """const text = $input.first().json.content.parts[0].text;
const cleanText = text.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();
const data = JSON.parse(cleanText);

return [{
  json: {
    Subject: data.Subject,
    Caption: data.Caption,
    Comment: data.Comment,
    BGM_prompt: data.BGM_prompt,
    parts: data.parts,
    fullNarration: data.parts.map(p => p.text).join(' '),
    Status: '준비',
    generatedAt: new Date().toISOString()
  }
}];"""}
)

add_node(
    "시트 기록",
    "n8n-nodes-base.googleSheets",
    4.7,
    [-1500, 300],
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
                "Narration": "={{ $json.fullNarration }}",
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
# Phase 2: 10파트 분리
# ============================================================

add_node(
    "파트 분리",
    "n8n-nodes-base.code",
    2,
    [-1200, 300],
    {"jsCode": """const data = $('대본 파싱').first().json;

const items = data.parts.map((part, i) => ({
  json: {
    text: part.text,
    keyword: part.keyword,
    index: i + 1,
    subject: data.Subject,
    bgmPrompt: data.BGM_prompt
  }
}));

return items;"""}
)

# ============================================================
# Phase 3a: TTS (나레이션 음성 생성) - 10파트 각각
# ============================================================

add_node(
    "TTS 요청",
    "n8n-nodes-base.httpRequest",
    4.3,
    [-900, 100],
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
    [-600, 100],
    {"amount": 30},
    webhookId=uid()
)

add_node(
    "TTS 결과",
    "n8n-nodes-base.httpRequest",
    4.3,
    [-300, 100],
    {
        "url": "=https://queue.fal.run/fal-ai/elevenlabs/requests/{{ $json.request_id }}",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "options": {}
    }
)

# ============================================================
# Phase 3b: Pexels 스톡영상 검색 - 10파트 각각
# ============================================================

add_node(
    "Pexels 검색",
    "n8n-nodes-base.httpRequest",
    4.3,
    [-900, 500],
    {
        "method": "GET",
        "url": "=https://api.pexels.com/videos/search?query={{ encodeURIComponent($json.keyword) }}&per_page=3&orientation=landscape&size=medium",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "options": {}
    }
)

add_node(
    "영상 URL 추출",
    "n8n-nodes-base.code",
    2,
    [-600, 500],
    {"jsCode": """const result = $input.first().json;
const videos = result.videos || [];

let videoUrl = '';
let videoDuration = 0;

if (videos.length > 0) {
  // Pick a random video from top 3 results for variety
  const video = videos[Math.floor(Math.random() * Math.min(3, videos.length))];
  videoDuration = video.duration || 10;

  // Find HD quality file (prefer 1920x1080)
  const files = video.video_files || [];
  const hdFile = files.find(f => f.width >= 1920 && f.quality === 'hd')
    || files.find(f => f.width >= 1280)
    || files.find(f => f.quality === 'hd')
    || files[0];

  if (hdFile) {
    videoUrl = hdFile.link;
  }
}

// Fallback: generic business/technology video
if (!videoUrl) {
  videoUrl = 'https://cdn.pixabay.com/video/2024/02/14/200717-913266610_large.mp4';
  videoDuration = 15;
}

return [{
  json: {
    videoUrl: videoUrl,
    videoDuration: videoDuration,
    keyword: $('파트 분리').item.json.keyword,
    index: $('파트 분리').item.json.index
  }
}];"""}
)

# ============================================================
# Phase 3c: BGM (한번만 실행, 3분)
# ============================================================

add_node(
    "BGM 생성",
    "n8n-nodes-base.httpRequest",
    4.3,
    [-900, -100],
    {
        "method": "POST",
        "url": "https://fal.run/beatoven/music-generation",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={\n  "prompt": "{{ $json.bgmPrompt || \'corporate technology upbeat inspiring background music\' }}",\n  "duration": 200,\n  "refinement": 100,\n  "creativity": 16\n}',
        "options": {}
    }
)

add_node(
    "BGM 대기",
    "n8n-nodes-base.wait",
    1.1,
    [-600, -100],
    {"amount": 60},
    webhookId=uid()
)

# ============================================================
# Phase 4: 합치기
# ============================================================

add_node(
    "Merge",
    "n8n-nodes-base.merge",
    3.2,
    [0, 300],
    {"numberInputs": 3}
)

add_node(
    "Aggregate",
    "n8n-nodes-base.aggregate",
    1,
    [200, 300],
    {"aggregate": "aggregateAllItemData", "options": {}}
)

# Shotstack 타임라인 빌드 (롱폼 - 가로형)
add_node(
    "Shotstack 타임라인",
    "n8n-nodes-base.code",
    2,
    [400, 300],
    {"jsCode": """// === Shotstack 롱폼 타임라인 빌더 (1920x1080 가로) ===
const bgmUrl = $('BGM 대기').first().json.audio?.url || '';
const bitrate = 128000;
const PART_COUNT = 10;

let scenes = [];
let currentStart = 0;

for (let i = 0; i < PART_COUNT; i++) {
  // TTS 결과
  const ttsResult = $('TTS 결과').all()[i]?.json;
  const narrationUrl = ttsResult?.audio?.url || '';
  const fileSize = ttsResult?.audio?.file_size || 50000;

  // Duration from audio file size
  let duration = Math.round((fileSize * 8 / bitrate) * 100) / 100;
  if (duration < 5) duration = 10;

  // Stock video URL
  const stockResult = $('영상 URL 추출').all()[i]?.json;
  const videoUrl = stockResult?.videoUrl || '';

  // Subtitle
  const subtitleText = $('파트 분리').all()[i]?.json?.text || '';

  scenes.push({
    start: currentStart,
    duration: duration,
    videoUrl: videoUrl,
    narrationUrl: narrationUrl,
    subtitleText: subtitleText
  });

  currentStart += duration;
}

const totalDuration = currentStart;

// === Shotstack Timeline (Landscape 1920x1080) ===
const timeline = {
  soundtrack: {
    src: bgmUrl,
    effect: "fadeOut",
    volume: 0.15
  },
  background: "#000000",
  tracks: [
    // Track 1: Stock video clips with transitions
    {
      clips: scenes.map((s, i) => ({
        asset: {
          type: "video",
          src: s.videoUrl,
          volume: 0,
          trim: 0
        },
        start: s.start,
        length: s.duration,
        fit: "cover",
        transition: i > 0 ? {
          in: "fade",
          out: i < scenes.length - 1 ? "fade" : undefined
        } : undefined
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
    // Track 3: Subtitles (bottom bar style)
    {
      clips: scenes.map(s => ({
        asset: {
          type: "html",
          html: '<div class="sub"><p>' + s.subtitleText.replace(/'/g, "\\\\'") + '</p></div>',
          css: ".sub { background: linear-gradient(transparent, rgba(0,0,0,0.7)); padding: 30px 60px 20px; } p { font-family: 'Noto Sans KR', sans-serif; font-size: 36px; color: #ffffff; text-align: center; line-height: 1.5; font-weight: 600; text-shadow: 1px 1px 4px rgba(0,0,0,0.8); }",
          width: 1920,
          height: 200
        },
        start: s.start,
        length: s.duration,
        position: "bottom",
        offset: { y: 0 }
      }))
    },
    // Track 4: 채널 로고/워터마크 (선택사항)
    {
      clips: [{
        asset: {
          type: "html",
          html: "<p>LUMIX Solution</p>",
          css: "p { font-family: 'Inter', sans-serif; font-size: 18px; color: rgba(255,255,255,0.5); letter-spacing: 2px; }",
          width: 300,
          height: 40
        },
        start: 0,
        length: totalDuration,
        position: "topRight",
        offset: { x: -0.02, y: 0.02 }
      }]
    }
  ]
};

// Intro fade-in (first scene)
if (timeline.tracks[0].clips.length > 0) {
  timeline.tracks[0].clips[0].transition = { in: "fade" };
}

const payload = {
  timeline: timeline,
  output: {
    format: "mp4",
    resolution: "hd",
    aspectRatio: "16:9",
    fps: 30,
    quality: "high"
  }
};

return [{
  json: {
    shotstack_payload: payload,
    totalDuration: totalDuration,
    sceneCount: scenes.length,
    subject: $('대본 파싱').first().json.Subject,
    caption: $('대본 파싱').first().json.Caption,
    comment: $('대본 파싱').first().json.Comment
  }
}];"""}
)

# ============================================================
# Phase 5: Shotstack 렌더
# ============================================================

add_node(
    "Shotstack 렌더",
    "n8n-nodes-base.httpRequest",
    4.3,
    [700, 300],
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
    [1000, 300],
    {"amount": 180},
    webhookId=uid()
)

add_node(
    "렌더 결과",
    "n8n-nodes-base.httpRequest",
    4.3,
    [1300, 300],
    {
        "url": "=https://api.shotstack.io/edit/stage/render/{{ $json.response.id }}",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "options": {}
    }
)

# 렌더 완료 확인 (상태 체크)
add_node(
    "렌더 완료 확인",
    "n8n-nodes-base.if",
    2.2,
    [1600, 300],
    {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{
                "id": uid(),
                "leftValue": "={{ $json.response.status }}",
                "rightValue": "done",
                "operator": {"type": "string", "operation": "equals"}
            }]
        }
    }
)

# 아직 안됐으면 다시 대기
add_node(
    "추가 대기",
    "n8n-nodes-base.wait",
    1.1,
    [1600, 500],
    {"amount": 60},
    webhookId=uid()
)

add_node(
    "렌더 재확인",
    "n8n-nodes-base.httpRequest",
    4.3,
    [1900, 500],
    {
        "url": "=https://api.shotstack.io/edit/stage/render/{{ $('Shotstack 렌더').first().json.response.id }}",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "options": {}
    }
)

# ============================================================
# Phase 6: 시트 업데이트 + YouTube 업로드
# ============================================================

add_node(
    "상태 업데이트",
    "n8n-nodes-base.googleSheets",
    4.7,
    [1900, 200],
    {
        "operation": "update",
        "documentId": {"__rl": True, "value": "1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag", "mode": "list",
                       "cachedResultName": "n8n LUMIX"},
        "sheetName": {"__rl": True, "value": "gid=0", "mode": "list",
                      "cachedResultName": "루믹스"},
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

add_node(
    "영상 다운로드",
    "n8n-nodes-base.httpRequest",
    4.3,
    [1900, 400],
    {
        "url": "={{ $json.response.url }}",
        "options": {"response": {"response": {"responseFormat": "file"}}}
    }
)

add_node(
    "YouTube 업로드",
    "n8n-nodes-base.youTube",
    1,
    [2200, 400],
    {
        "resource": "video",
        "operation": "upload",
        "title": "={{ $('대본 파싱').first().json.Subject }}",
        "regionCode": "KR",
        "categoryId": "28",
        "options": {
            "description": "={{ $('대본 파싱').first().json.Caption }}",
            "privacyStatus": "public"
        }
    }
)

add_node(
    "첫 댓글",
    "n8n-nodes-base.httpRequest",
    4.3,
    [2500, 400],
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
        "textOriginal": "{{ $('대본 파싱').first().json.Comment }}"
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
    [2800, 400],
    {
        "operation": "update",
        "documentId": {"__rl": True, "value": "1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag", "mode": "list",
                       "cachedResultName": "n8n LUMIX"},
        "sheetName": {"__rl": True, "value": "gid=0", "mode": "list",
                      "cachedResultName": "루믹스"},
        "columns": {
            "mappingMode": "defineBelow",
            "value": {
                "row_number": "={{ $('시트 기록').first().json.row_number }}",
                "Publish": "발행 완료",
                "업로드 URL": "=https://youtube.com/watch?v={{ $('YouTube 업로드').first().json.id }}"
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

# Phase 1: 대본 생성
connect("스케줄 트리거", "AI 대본 생성")
connect("AI 대본 생성", "대본 파싱")
connect("대본 파싱", "시트 기록")

# Phase 2: 파트 분리
connect("시트 기록", "파트 분리")

# Phase 3: 병렬 처리
# TTS path (per part)
connect("파트 분리", "TTS 요청")
connect("TTS 요청", "TTS 대기")
connect("TTS 대기", "TTS 결과")
connect("TTS 결과", "Merge", to_index=0)

# Pexels path (per part)
connect("파트 분리", "Pexels 검색")
connect("Pexels 검색", "영상 URL 추출")
connect("영상 URL 추출", "Merge", to_index=1)

# BGM path (once)
connect("시트 기록", "BGM 생성")
connect("BGM 생성", "BGM 대기")
connect("BGM 대기", "Merge", to_index=2)

# Phase 4: 합성
connect("Merge", "Aggregate")
connect("Aggregate", "Shotstack 타임라인")
connect("Shotstack 타임라인", "Shotstack 렌더")
connect("Shotstack 렌더", "렌더 대기")
connect("렌더 대기", "렌더 결과")
connect("렌더 결과", "렌더 완료 확인")

# 렌더 완료 → 저장 & 업로드 (true branch = index 0)
connect("렌더 완료 확인", "상태 업데이트", from_index=0)
connect("렌더 완료 확인", "영상 다운로드", from_index=0)

# 렌더 미완료 → 재시도 (false branch = index 1)
connect("렌더 완료 확인", "추가 대기", from_index=1)
connect("추가 대기", "렌더 재확인")
connect("렌더 재확인", "렌더 완료 확인")

# Phase 5: 업로드
connect("영상 다운로드", "YouTube 업로드")
connect("YouTube 업로드", "첫 댓글")
connect("첫 댓글", "발행 완료")

# ============================================================
# 워크플로우 JSON 생성
# ============================================================

workflow = {
    "name": "루믹스 솔루션 롱폼 (완전자동 v1)",
    "nodes": nodes,
    "connections": connections,
    "settings": {"executionOrder": "v1"}
}

output_path = '/Users/gimdongseog/n8n-project/workflow_lumix_longform.json'
with open(output_path, 'w') as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print("=" * 60)
print("루믹스 솔루션 롱폼 워크플로우 생성 완료!")
print(f"파일: {output_path}")
print("=" * 60)
print()
print(f"총 노드 수: {len(nodes)}개")
print()
print("워크플로우 구조:")
print("  [매일 스케줄] → [Gemini: 주제+대본 2~3분 자동생성]")
print("       → [대본 파싱] → [시트 기록] → [10파트 분리]")
print("       → 병렬 처리:")
print("         Path A: [TTS x10] → [대기] → [결과]")
print("         Path B: [Pexels 스톡검색 x10] → [URL 추출]")
print("         Path C: [BGM 3분 생성] → [대기]")
print("       → [Merge] → [Aggregate]")
print("       → [Shotstack 타임라인 (16:9 가로)]")
print("       → [렌더] → [완료 확인 + 재시도]")
print("       → [YouTube 업로드] → [댓글] → [발행 완료]")
print()
print("비용 비교 (숏폼 vs 롱폼):")
print("  숏폼: ~$2.50/편 (AI 영상 생성 비용)")
print("  롱폼: ~$0.30/편 (스톡영상 무료!)")
print()
print("추가 필요 Credential:")
print("  ★ Pexels API Key (무료)")
print("     → https://www.pexels.com/api/ 가입")
print("     → n8n에서 HTTP Header Auth 생성:")
print("       Name: Pexels")
print("       Header Name: Authorization")
print("       Header Value: (API Key)")
print("  ★ Shotstack API Key (숏폼에서 이미 설정했으면 동일)")
