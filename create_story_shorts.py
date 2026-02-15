#!/usr/bin/env python3
"""
온카스터디 스토리형 숏츠 (완전자동 v1) 워크플로우 생성기
======================================================
실제 카지노 영상 클립(Pexels 스톡)을 짜집기하여
상단 훅 제목 + 하단 자막 + TTS 나레이션으로 구성하는 숏츠.

구조:
  Schedule → AI 콘텐츠 생성 → 파싱 → 시트 기록 → 세그먼트 분리
  → 병렬(TTS, Pexels 검색, BGM)
  → NCA FFmpeg 합성(트림+합치기+배너/자막+오디오)
  → YouTube 업로드

핵심 차이점 (기존 숏폼 v3 대비):
  - 영상 소스: Pexels 스톡 영상 검색 (AI 영상 생성 없음)
  - 비용: ~$0.10/편 (TTS+BGM만)
  - 상단 배너: 회색 배너 + 훅 제목 (강조 컬러)
  - 나레이션: 7~10문장 (40~50초)
  - 합성: NCA Toolkit FFmpeg

Credential IDs:
  - Gemini: IKP349r08J9Hoz5E
  - Pexels: 1vPRgFSX7u4ecIy4
  - fal.ai (TTS): R0m2RD0rtE8IKRt6
  - Google Sheets: CWBUyXUqCU9p5VAg
  - YouTube: kRKBMYWf6cB72qUi
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
        "index": to_index,
    })


# ============================================================
# Phase 1: 콘텐츠 생성
# ============================================================

# 1. 스케줄 트리거 (매일 03:00, 15:00 KST)
add_node(
    "스케줄 트리거",
    "n8n-nodes-base.scheduleTrigger",
    1.3,
    [-2400, 300],
    {
        "rule": {
            "interval": [
                {
                    "field": "cronExpression",
                    "expression": "0 3,15 * * *"
                }
            ]
        }
    }
)

# 2. AI 콘텐츠 생성 (Gemini 2.5 Flash)
ai_prompt = """너는 '온카스터디' 먹튀검증 커뮤니티의 YouTube Shorts 스토리형 콘텐츠 기획자야.
**실제 영상 클립을 편집한 스토리형 숏츠**를 기획해줘.

## 영상 구조
- 총 40~50초, 9:16 세로 영상
- 상단 배너: 고정된 훅 제목 (강조할 단어는 <y>태그</y>로 감싸기)
- 중간: Pexels 스톡 영상 (3~5초 간격 전환)
- 하단: 나레이션 자막
- 오디오: TTS 나레이션 + BGM

## 핵심 규칙
1. hook_title: 1~2줄, 강렬한 후킹. <y>강조단어</y> 1~3개
2. 나레이션 7~10문장, 총 40~50초
3. 각 문장마다 Pexels 검색용 영어 키워드 (2~4단어)
4. 키워드: casino, roulette, poker chips, slot machine, money, gambling 등 실제 영상 있는 키워드
5. "온카스터디"는 후반부 1~2회만 자연스럽게 언급
6. subject에 해시태그: 온카스터디 #먹튀검증 #카지노커뮤니티 ...

## 주제 카테고리 (하나 랜덤 선택)
1. 카지노에서 절대 해서는 안 되는 행동
2. 먹튀 사이트 구별하는 확실한 방법
3. 온라인 카지노의 숨겨진 함정
4. 초보자가 반드시 알아야 할 카지노 상식
5. 환전 사고 실제 사례와 예방법
6. 카지노 보너스의 진짜 의미
7. 안전한 배팅 사이트 선택 기준
8. 카지노에서 돈 잃는 심리적 이유
9. VIP 시스템의 진실
10. 블랙잭/바카라/룰렛 기본 전략

## 출력 (순수 JSON, 마크다운 코드블록 없이)
{
  "hook_title": "카지노에서 가장 <y>무서운</y> 숫자는 <y>7</y>이 아니라 <y>0</y>입니다",
  "narration_segments": [
    {"text": "첫 번째 문장.", "keyword": "casino roulette table"},
    {"text": "두 번째 문장.", "keyword": "poker chips stack"},
    {"text": "세 번째 문장.", "keyword": "slot machine spinning"},
    {"text": "네 번째 문장.", "keyword": "money cash bills"},
    {"text": "다섯 번째 문장.", "keyword": "gambling dice cards"},
    {"text": "여섯 번째 문장.", "keyword": "casino neon lights"},
    {"text": "일곱 번째 문장.", "keyword": "poker game table"},
    {"text": "여덟 번째 문장.", "keyword": "roulette wheel spinning"}
  ],
  "Subject": "제목 온카스터디 #먹튀검증 #카지노 #온라인카지노 #카지노커뮤니티",
  "Caption": "설명 + #해시태그",
  "Comment": "구글에 온카스터디 검색",
  "BGM_prompt": "dark cinematic tension suspense mysterious casino atmosphere"
}"""

add_node(
    "AI 콘텐츠 생성",
    "@n8n/n8n-nodes-langchain.googleGemini",
    1.1,
    [-2100, 300],
    {
        "modelId": {
            "__rl": True,
            "value": "models/gemini-2.5-flash",
            "mode": "list",
            "cachedResultName": "models/gemini-2.5-flash"
        },
        "messages": {
            "values": [{"content": ai_prompt}]
        },
        "jsonOutput": True,
        "builtInTools": {},
        "options": {}
    }
)

# 3. 콘텐츠 파싱
parse_code = r"""const text = $input.first().json.content.parts[0].text;
const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
const data = JSON.parse(cleanText);

// Validate segments
if (!data.narration_segments || data.narration_segments.length < 7) {
  throw new Error('narration_segments must have at least 7 items');
}

return [{
  json: {
    hook_title: data.hook_title,
    narration_segments: data.narration_segments,
    Subject: data.Subject,
    Caption: data.Caption,
    Comment: data.Comment,
    BGM_prompt: data.BGM_prompt,
    fullNarration: data.narration_segments.map(s => s.text).join(' '),
    segmentCount: data.narration_segments.length,
    Status: '준비',
    generatedAt: new Date().toISOString()
  }
}];"""

add_node(
    "콘텐츠 파싱",
    "n8n-nodes-base.code",
    2,
    [-1800, 300],
    {"jsCode": parse_code}
)

# 4. 시트 기록
add_node(
    "시트 기록",
    "n8n-nodes-base.googleSheets",
    4.7,
    [-1500, 300],
    {
        "operation": "append",
        "documentId": {
            "__rl": True,
            "value": "STORY_SHORTS_SHEET_ID",
            "mode": "list",
            "cachedResultName": "온카스터디 스토리형 숏츠",
            "cachedResultUrl": ""
        },
        "sheetName": {
            "__rl": True,
            "value": "gid=0",
            "mode": "list",
            "cachedResultName": "스토리형 숏츠",
            "cachedResultUrl": ""
        },
        "columns": {
            "mappingMode": "defineBelow",
            "value": {
                "Subject": "={{ $json.Subject }}",
                "Hook": "={{ $json.hook_title }}",
                "Narration": "={{ $json.fullNarration }}",
                "Caption": "={{ $json.Caption }}",
                "댓글": "={{ $json.Comment }}",
                "BGM prompt": "={{ $json.BGM_prompt }}",
                "Status": "준비"
            },
            "matchingColumns": [],
            "schema": [
                {"id": "Subject", "displayName": "Subject", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                {"id": "Hook", "displayName": "Hook", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
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
# Phase 2: 세그먼트 분리
# ============================================================

# 5. 세그먼트 분리
segment_split_code = r"""const data = $('콘텐츠 파싱').first().json;

const items = data.narration_segments.map((seg, i) => ({
  json: {
    text: seg.text,
    keyword: seg.keyword,
    index: i + 1,
    hook_title: data.hook_title,
    subject: data.Subject,
    bgmPrompt: data.BGM_prompt,
    segmentCount: data.segmentCount
  }
}));

return items;"""

add_node(
    "세그먼트 분리",
    "n8n-nodes-base.code",
    2,
    [-1200, 300],
    {"jsCode": segment_split_code}
)

# ============================================================
# Phase 3a: TTS (나레이션 음성 생성)
# ============================================================

# 6. TTS 요청
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

# 7. TTS 대기
add_node(
    "TTS 대기",
    "n8n-nodes-base.wait",
    1.1,
    [-600, 100],
    {"amount": 30},
    webhookId=uid()
)

# 8. TTS 결과
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
# Phase 3b: Pexels 스톡 영상 검색 (portrait 우선)
# ============================================================

# 9. Pexels 검색
add_node(
    "Pexels 검색",
    "n8n-nodes-base.httpRequest",
    4.3,
    [-900, 500],
    {
        "method": "GET",
        "url": "=https://api.pexels.com/videos/search?query={{ encodeURIComponent($json.keyword) }}&per_page=3&orientation=portrait&size=medium",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "options": {}
    }
)

# 10. 영상 URL 추출
video_extract_code = r"""const result = $input.first().json;
const videos = result.videos || [];

let videoUrl = '';
let videoDuration = 0;
let isPortrait = true;

if (videos.length > 0) {
  // Pick a random video from top 3 results for variety
  const video = videos[Math.floor(Math.random() * Math.min(3, videos.length))];
  videoDuration = video.duration || 10;

  // Find HD quality file (prefer portrait 1080x1920)
  const files = video.video_files || [];
  const hdFile = files.find(f => f.height >= 1920 && f.width <= 1080 && f.quality === 'hd')
    || files.find(f => f.height >= 1080 && f.quality === 'hd')
    || files.find(f => f.quality === 'hd')
    || files[0];

  if (hdFile) {
    videoUrl = hdFile.link;
    // Check if actually portrait
    isPortrait = (hdFile.height || 0) > (hdFile.width || 0);
  }
}

// Fallback: generic casino video
if (!videoUrl) {
  videoUrl = 'https://videos.pexels.com/video-files/3249925/3249925-hd_1080_1920_25fps.mp4';
  videoDuration = 10;
  isPortrait = true;
}

return [{
  json: {
    videoUrl: videoUrl,
    videoDuration: videoDuration,
    isPortrait: isPortrait,
    keyword: $('세그먼트 분리').item.json.keyword,
    index: $('세그먼트 분리').item.json.index,
    text: $('세그먼트 분리').item.json.text
  }
}];"""

add_node(
    "영상 URL 추출",
    "n8n-nodes-base.code",
    2,
    [-600, 500],
    {"jsCode": video_extract_code}
)

# ============================================================
# Phase 3c: BGM 생성
# ============================================================

# 11. BGM 생성
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
        "jsonBody": '={\n  "prompt": "{{ $json.bgmPrompt || \'dark cinematic tension suspense casino atmosphere\' }}",\n  "duration": 60,\n  "refinement": 100,\n  "creativity": 16\n}',
        "options": {}
    }
)

# 12. BGM 대기
add_node(
    "BGM 대기",
    "n8n-nodes-base.wait",
    1.1,
    [-600, -100],
    {"amount": 60},
    webhookId=uid()
)

# ============================================================
# Phase 4: 데이터 통합
# ============================================================

# 13. Merge (3개 입력: TTS, Pexels, BGM)
add_node(
    "Merge",
    "n8n-nodes-base.merge",
    3.2,
    [0, 300],
    {"numberInputs": 3}
)

# 14. Aggregate
add_node(
    "Aggregate",
    "n8n-nodes-base.aggregate",
    1,
    [200, 300],
    {"aggregate": "aggregateAllItemData", "options": {}}
)

# 15. NCA 데이터 준비 (TTS duration 계산 + 모든 데이터 통합)
nca_data_prep_code = r"""// NCA 스토리형 숏츠 데이터 준비
// TTS 결과 + Pexels 영상 + BGM 통합

const NCA_URL = "http://76.13.182.180:8080";
const NCA_API_KEY = "nca-sagong-2026";
const bitrate = 128000;

const hookTitle = $('콘텐츠 파싱').first().json.hook_title;
const segmentCount = $('콘텐츠 파싱').first().json.segmentCount;
const bgmUrl = $('BGM 대기').first().json.audio?.url || '';

let segments = [];
let currentStart = 0;

for (let i = 0; i < segmentCount; i++) {
  // TTS 결과
  const ttsResult = $('TTS 결과').all()[i]?.json;
  const audioUrl = ttsResult?.audio?.url || '';
  const fileSize = ttsResult?.audio?.file_size || 40000;

  // Duration from audio file size
  let duration = Math.round((fileSize * 8 / bitrate) * 100) / 100;
  if (duration < 2) duration = 4;

  // Pexels 영상
  const pexelsResult = $('영상 URL 추출').all()[i]?.json;
  const videoUrl = pexelsResult?.videoUrl || '';
  const isPortrait = pexelsResult?.isPortrait !== false;

  // Subtitle text
  const subtitleText = $('세그먼트 분리').all()[i]?.json?.text || '';

  segments.push({
    index: i + 1,
    videoUrl: videoUrl,
    audioUrl: audioUrl,
    duration: duration,
    start: currentStart,
    subtitleText: subtitleText,
    isPortrait: isPortrait,
  });

  currentStart += duration;
}

const totalDuration = currentStart;

return [{
  json: {
    segments: segments,
    totalDuration: totalDuration,
    segmentCount: segmentCount,
    hookTitle: hookTitle,
    bgmUrl: bgmUrl,
    NCA_URL: NCA_URL,
    NCA_API_KEY: NCA_API_KEY,
    subject: $('콘텐츠 파싱').first().json.Subject,
    caption: $('콘텐츠 파싱').first().json.Caption,
    comment: $('콘텐츠 파싱').first().json.Comment,
  }
}];"""

add_node(
    "NCA 데이터 준비",
    "n8n-nodes-base.code",
    2,
    [400, 300],
    {"jsCode": nca_data_prep_code}
)

# ============================================================
# Phase 5: NCA FFmpeg 합성
# ============================================================

# 16. NCA 파트별 트림 (각 Pexels 영상을 세그먼트 duration에 맞게 트림 + 세로 crop)
nca_trim_code = r"""// NCA: 파트별 영상 트림 + 세로 crop + 나레이션 합성
const data = $input.first().json;
const segments = data.segments || [];
const NCA_URL = data.NCA_URL;
const NCA_API_KEY = data.NCA_API_KEY;

const composedVideos = [];

for (let i = 0; i < segments.length; i++) {
  const seg = segments[i];
  if (!seg.videoUrl) {
    composedVideos.push({ index: i + 1, url: '', error: 'no_video_url' });
    continue;
  }

  try {
    // FFmpeg: trim to duration, loop if needed, crop to portrait, add narration audio
    let vfilter = '';
    if (seg.isPortrait) {
      vfilter = 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2';
    } else {
      // Landscape -> crop to portrait center
      vfilter = 'scale=-1:1920,crop=1080:1920';
    }

    let ffmpegCmd = '';
    if (seg.audioUrl) {
      // With narration audio
      ffmpegCmd = `-stream_loop -1 -i "${seg.videoUrl}" -i "${seg.audioUrl}" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -vf "${vfilter}" -t ${seg.duration} -movflags +faststart output_part${i+1}.mp4`;
    } else {
      // Video only
      ffmpegCmd = `-stream_loop -1 -i "${seg.videoUrl}" -c:v libx264 -preset fast -crf 23 -an -pix_fmt yuv420p -vf "${vfilter}" -t ${seg.duration} -movflags +faststart output_part${i+1}.mp4`;
    }

    const response = await $http.request({
      method: 'POST',
      url: `${NCA_URL}/v1/ffmpeg/compose`,
      headers: {
        'x-api-key': NCA_API_KEY,
        'Content-Type': 'application/json',
      },
      body: { ffmpeg_command: ffmpegCmd },
      json: true,
    });

    const outputUrl = response.output_url || response.url || response.result_url || response.video_url || '';
    composedVideos.push({
      index: i + 1,
      url: outputUrl,
      task_id: response.task_id || response.id || '',
    });
  } catch (error) {
    console.error(`Part ${i+1} error:`, error.message);
    composedVideos.push({
      index: i + 1,
      url: seg.videoUrl,
      error: error.message,
    });
  }
}

return [{
  json: {
    composed_videos: composedVideos,
    video_urls: composedVideos.map(v => v.url).filter(u => u),
    hookTitle: data.hookTitle,
    bgmUrl: data.bgmUrl,
    segments: data.segments,
    totalDuration: data.totalDuration,
    NCA_URL: data.NCA_URL,
    NCA_API_KEY: data.NCA_API_KEY,
    subject: data.subject,
    caption: data.caption,
    comment: data.comment,
  }
}];"""

add_node(
    "NCA 파트별 트림",
    "n8n-nodes-base.code",
    2,
    [700, 300],
    {"jsCode": nca_trim_code}
)

# 17. NCA 트림 대기
add_node(
    "NCA 트림 대기",
    "n8n-nodes-base.wait",
    1.1,
    [1000, 300],
    {"amount": 60},
    webhookId=uid()
)

# 18. NCA 영상 합치기
add_node(
    "NCA 영상 합치기",
    "n8n-nodes-base.httpRequest",
    4.3,
    [1300, 300],
    {
        "method": "POST",
        "url": "http://76.13.182.180:8080/v1/video/concatenate",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "x-api-key", "value": "nca-sagong-2026"}
            ]
        },
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={{ JSON.stringify({ "video_urls": $json.video_urls }) }}',
        "options": {"timeout": 300000}
    }
)

# 19. NCA 합치기 결과 처리 + 배너/자막 오버레이 준비
overlay_prep_code = r"""// NCA 배너 + 자막 오버레이 FFmpeg 명령 준비
const prevData = $('NCA 트림 대기').first().json;
const concatResult = $input.first().json;

const concatenatedUrl = concatResult.output_url || concatResult.url || concatResult.result_url || concatResult.video_url || '';
const hookTitle = prevData.hookTitle || '';
const segments = prevData.segments || [];
const totalDuration = prevData.totalDuration || 50;

// Parse hook title: extract <y>강조</y> parts
const hookClean = hookTitle.replace(/<y>/g, '').replace(/<\/y>/g, '');

// Build drawtext filter for banner
// Top 15%: gray banner (288px high) with hook title
let filterParts = [];

// Gray banner background
filterParts.push(`drawbox=y=0:w=1080:h=288:color=#404040@0.85:t=fill`);

// Hook title (centered, white text, yellow highlights)
// Split by <y> tags to apply different colors
const titleParts = hookTitle.split(/(<y>.*?<\/y>)/);
let titleFilters = [];
let xOffset = 0;

// For simplicity: render full title in white, then overlay yellow parts
// Use a single centered text for the clean version
const escapedTitle = hookClean.replace(/'/g, "\\'").replace(/:/g, "\\:");
filterParts.push(`drawtext=text='${escapedTitle}':fontsize=52:fontcolor=white:fontfile=/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf:x=(w-tw)/2:y=120:line_spacing=8`);

// Subtitle overlays (bottom 15%)
for (let i = 0; i < segments.length; i++) {
  const seg = segments[i];
  const startTime = seg.start;
  const endTime = seg.start + seg.duration;
  const subText = seg.subtitleText.replace(/'/g, "\\'").replace(/:/g, "\\:");

  filterParts.push(
    `drawtext=text='${subText}':fontsize=42:fontcolor=white:fontfile=/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf:x=(w-tw)/2:y=h-180:line_spacing=6:borderw=3:bordercolor=black:enable='between(t,${startTime.toFixed(1)},${endTime.toFixed(1)})'`
  );
}

const filterComplex = filterParts.join(',');
const ffmpegCmd = `-i "${concatenatedUrl}" -vf "${filterComplex}" -c:v libx264 -preset fast -crf 23 -c:a copy -movflags +faststart output_overlay.mp4`;

return [{
  json: {
    concatenated_url: concatenatedUrl,
    overlay_ffmpeg_command: ffmpegCmd,
    bgmUrl: prevData.bgmUrl,
    totalDuration: totalDuration,
    segments: segments,
    hookTitle: hookTitle,
    NCA_URL: prevData.NCA_URL,
    NCA_API_KEY: prevData.NCA_API_KEY,
    subject: prevData.subject,
    caption: prevData.caption,
    comment: prevData.comment,
  }
}];"""

add_node(
    "NCA 오버레이 준비",
    "n8n-nodes-base.code",
    2,
    [1600, 300],
    {"jsCode": overlay_prep_code}
)

# 20. NCA 배너+자막 오버레이
add_node(
    "NCA 배너자막 오버레이",
    "n8n-nodes-base.httpRequest",
    4.3,
    [1900, 300],
    {
        "method": "POST",
        "url": "http://76.13.182.180:8080/v1/ffmpeg/compose",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "x-api-key", "value": "nca-sagong-2026"}
            ]
        },
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={{ JSON.stringify({ "ffmpeg_command": $json.overlay_ffmpeg_command }) }}',
        "options": {"timeout": 300000}
    }
)

# 21. NCA 오버레이 대기
add_node(
    "NCA 오버레이 대기",
    "n8n-nodes-base.wait",
    1.1,
    [2200, 300],
    {"amount": 60},
    webhookId=uid()
)

# 22. NCA 오디오 합성 준비 (TTS concat + BGM mix)
audio_prep_code = r"""// NCA 오디오 합성: TTS + BGM 믹스
const prevData = $('NCA 오버레이 준비').first().json;
const overlayResult = $input.first().json;

const overlayedUrl = overlayResult.output_url || overlayResult.url || overlayResult.result_url || overlayResult.video_url || '';
const bgmUrl = prevData.bgmUrl || '';

let output = {
  video_url: overlayedUrl,
  bgmUrl: bgmUrl,
  totalDuration: prevData.totalDuration,
  subject: prevData.subject,
  caption: prevData.caption,
  comment: prevData.comment,
  NCA_URL: prevData.NCA_URL,
  NCA_API_KEY: prevData.NCA_API_KEY,
};

// BGM FFmpeg: mix BGM at low volume with existing audio
if (overlayedUrl && bgmUrl) {
  output.bgm_ffmpeg_command = `-i "${overlayedUrl}" -i "${bgmUrl}" -filter_complex "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]" -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -movflags +faststart output_final.mp4`;
  output.has_bgm = true;
} else {
  output.has_bgm = false;
  output.final_video_url = overlayedUrl;
}

return [{ json: output }];"""

add_node(
    "NCA 오디오 준비",
    "n8n-nodes-base.code",
    2,
    [2500, 300],
    {"jsCode": audio_prep_code}
)

# 23. NCA BGM 분기
add_node(
    "NCA BGM 분기",
    "n8n-nodes-base.if",
    2.2,
    [2800, 300],
    {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{
                "id": uid(),
                "leftValue": "={{ $json.has_bgm }}",
                "rightValue": True,
                "operator": {"type": "boolean", "operation": "true"}
            }],
            "combinator": "and"
        }
    }
)

# 24. NCA BGM 추가 (true branch)
add_node(
    "NCA BGM 추가",
    "n8n-nodes-base.httpRequest",
    4.3,
    [3100, 200],
    {
        "method": "POST",
        "url": "http://76.13.182.180:8080/v1/ffmpeg/compose",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "x-api-key", "value": "nca-sagong-2026"}
            ]
        },
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={{ JSON.stringify({ "ffmpeg_command": $json.bgm_ffmpeg_command }) }}',
        "options": {"timeout": 300000}
    }
)

# 25. NCA BGM 대기
add_node(
    "NCA BGM 대기",
    "n8n-nodes-base.wait",
    1.1,
    [3400, 200],
    {"amount": 60},
    webhookId=uid()
)

# 26. NCA BGM 결과 처리
bgm_result_code = r"""// BGM 추가 결과
const prevData = $('NCA 오디오 준비').first().json;
const bgmResult = $input.first().json;

const videoWithBgm = bgmResult.output_url || bgmResult.url || bgmResult.result_url || bgmResult.video_url || '';

return [{
  json: {
    final_video_url: videoWithBgm || prevData.video_url,
    url: videoWithBgm || prevData.video_url,
    subject: prevData.subject,
    caption: prevData.caption,
    comment: prevData.comment,
  }
}];"""

add_node(
    "NCA BGM 결과",
    "n8n-nodes-base.code",
    2,
    [3700, 200],
    {"jsCode": bgm_result_code}
)

# 27. NCA BGM 없음 (false branch)
no_bgm_code = r"""// BGM 없이 진행
const prevData = $('NCA 오디오 준비').first().json;
return [{
  json: {
    final_video_url: prevData.video_url || prevData.final_video_url,
    url: prevData.video_url || prevData.final_video_url,
    subject: prevData.subject,
    caption: prevData.caption,
    comment: prevData.comment,
  }
}];"""

add_node(
    "NCA BGM 없음",
    "n8n-nodes-base.code",
    2,
    [3700, 500],
    {"jsCode": no_bgm_code}
)

# 28. NCA 최종 Merge (BGM 있음/없음 합류)
add_node(
    "NCA 최종 Merge",
    "n8n-nodes-base.merge",
    3.2,
    [4000, 300],
    {"mode": "chooseBranch", "numberInputs": 2}
)

# ============================================================
# Phase 6: 업로드
# ============================================================

# 29. 상태 업데이트 ("생성 완료")
add_node(
    "상태 업데이트",
    "n8n-nodes-base.googleSheets",
    4.7,
    [4300, 200],
    {
        "operation": "update",
        "documentId": {
            "__rl": True,
            "value": "STORY_SHORTS_SHEET_ID",
            "mode": "list",
            "cachedResultName": "온카스터디 스토리형 숏츠"
        },
        "sheetName": {
            "__rl": True,
            "value": "gid=0",
            "mode": "list",
            "cachedResultName": "스토리형 숏츠"
        },
        "columns": {
            "mappingMode": "defineBelow",
            "value": {
                "row_number": "={{ $('시트 기록').first().json.row_number }}",
                "Status": "생성 완료",
                "영상 URL": "={{ $json.final_video_url || $json.url }}"
            },
            "matchingColumns": ["row_number"],
            "schema": [
                {"id": "Status", "displayName": "Status", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                {"id": "영상 URL", "displayName": "영상 URL", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                {"id": "row_number", "displayName": "row_number", "required": False, "defaultMatch": False, "display": True, "type": "number", "canBeUsedToMatch": True, "readOnly": True}
            ]
        },
        "options": {}
    }
)

# 30. 영상 다운로드
add_node(
    "영상 다운로드",
    "n8n-nodes-base.httpRequest",
    4.3,
    [4300, 400],
    {
        "url": "={{ $json.final_video_url || $json.url }}",
        "options": {"response": {"response": {"responseFormat": "file"}}}
    }
)

# 31. YouTube 업로드
add_node(
    "YouTube 업로드",
    "n8n-nodes-base.youTube",
    1,
    [4600, 400],
    {
        "resource": "video",
        "operation": "upload",
        "title": "={{ $('콘텐츠 파싱').first().json.Subject }}",
        "regionCode": "KR",
        "categoryId": "28",
        "options": {
            "description": "={{ $('콘텐츠 파싱').first().json.Caption }}",
            "privacyStatus": "public"
        }
    }
)

# 32. 첫 댓글
add_node(
    "첫 댓글",
    "n8n-nodes-base.httpRequest",
    4.3,
    [4900, 400],
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
        "textOriginal": "{{ $('콘텐츠 파싱').first().json.Comment }}"
      }
    }
  }
}""",
        "options": {}
    }
)

# 33. 발행 완료
add_node(
    "발행 완료",
    "n8n-nodes-base.googleSheets",
    4.7,
    [5200, 400],
    {
        "operation": "update",
        "documentId": {
            "__rl": True,
            "value": "STORY_SHORTS_SHEET_ID",
            "mode": "list",
            "cachedResultName": "온카스터디 스토리형 숏츠"
        },
        "sheetName": {
            "__rl": True,
            "value": "gid=0",
            "mode": "list",
            "cachedResultName": "스토리형 숏츠"
        },
        "columns": {
            "mappingMode": "defineBelow",
            "value": {
                "row_number": "={{ $('시트 기록').first().json.row_number }}",
                "Publish": "발행 완료",
                "영상 URL": "=https://youtube.com/shorts/{{ $('YouTube 업로드').first().json.id }}"
            },
            "matchingColumns": ["row_number"],
            "schema": [
                {"id": "Publish", "displayName": "Publish", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                {"id": "영상 URL", "displayName": "영상 URL", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                {"id": "row_number", "displayName": "row_number", "required": False, "defaultMatch": False, "display": True, "type": "number", "canBeUsedToMatch": True, "readOnly": True}
            ]
        },
        "options": {}
    }
)

# ============================================================
# Connections
# ============================================================

# Phase 1: 콘텐츠 생성
connect("스케줄 트리거", "AI 콘텐츠 생성")
connect("AI 콘텐츠 생성", "콘텐츠 파싱")
connect("콘텐츠 파싱", "시트 기록")
connect("시트 기록", "세그먼트 분리")

# Phase 2: 병렬 처리
# TTS path
connect("세그먼트 분리", "TTS 요청")
connect("TTS 요청", "TTS 대기")
connect("TTS 대기", "TTS 결과")
connect("TTS 결과", "Merge", to_index=0)

# Pexels path
connect("세그먼트 분리", "Pexels 검색")
connect("Pexels 검색", "영상 URL 추출")
connect("영상 URL 추출", "Merge", to_index=1)

# BGM path (once, from 시트 기록)
connect("시트 기록", "BGM 생성")
connect("BGM 생성", "BGM 대기")
connect("BGM 대기", "Merge", to_index=2)

# Phase 3: 데이터 통합
connect("Merge", "Aggregate")
connect("Aggregate", "NCA 데이터 준비")

# Phase 4: NCA FFmpeg 합성
connect("NCA 데이터 준비", "NCA 파트별 트림")
connect("NCA 파트별 트림", "NCA 트림 대기")
connect("NCA 트림 대기", "NCA 영상 합치기")
connect("NCA 영상 합치기", "NCA 오버레이 준비")
connect("NCA 오버레이 준비", "NCA 배너자막 오버레이")
connect("NCA 배너자막 오버레이", "NCA 오버레이 대기")
connect("NCA 오버레이 대기", "NCA 오디오 준비")
connect("NCA 오디오 준비", "NCA BGM 분기")

# BGM 분기
connect("NCA BGM 분기", "NCA BGM 추가", from_index=0)  # true
connect("NCA BGM 분기", "NCA BGM 없음", from_index=1)   # false

connect("NCA BGM 추가", "NCA BGM 대기")
connect("NCA BGM 대기", "NCA BGM 결과")

# 최종 Merge (BGM 있음/없음 합류)
connect("NCA BGM 결과", "NCA 최종 Merge", to_index=0)
connect("NCA BGM 없음", "NCA 최종 Merge", to_index=1)

# Phase 5: 업로드
connect("NCA 최종 Merge", "상태 업데이트")
connect("NCA 최종 Merge", "영상 다운로드")
connect("영상 다운로드", "YouTube 업로드")
connect("YouTube 업로드", "첫 댓글")
connect("첫 댓글", "발행 완료")

# ============================================================
# 워크플로우 JSON 생성
# ============================================================

workflow = {
    "name": "온카스터디 스토리형 숏츠 (완전자동 v1)",
    "nodes": nodes,
    "connections": connections,
    "settings": {"executionOrder": "v1"}
}


def main():
    print("=" * 60)
    print("온카스터디 스토리형 숏츠 (완전자동 v1) 워크플로우 생성")
    print("=" * 60)

    output_path = '/Users/gimdongseog/n8n-project/story_shorts_v1.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 워크플로우 JSON 생성 완료: {output_path}")
    print(f"  - 이름: {workflow['name']}")
    print(f"  - 노드 수: {len(workflow['nodes'])}개")
    print(f"  - 연결 수: {len(workflow['connections'])}개")

    # Verify connections
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
        print("  - 모든 연결이 유효합니다 ✓")

    # Check for credentials
    print("\n[INFO] 크레덴셜 체크:")
    cred_found = False
    for n in workflow["nodes"]:
        if "credentials" in n:
            print(f"  [FOUND] {n['name']}에 credentials 키 발견")
            cred_found = True
    if not cred_found:
        print("  - 크레덴셜 없음 (n8n GUI에서 수동 설정 필요)")

    # List NCA nodes
    print("\n[INFO] NCA Toolkit 노드:")
    for n in workflow["nodes"]:
        if "NCA" in n["name"]:
            print(f"  - {n['name']} ({n['type']})")

    # Placeholders
    print("\n[INFO] 플레이스홀더 (n8n 설정 후 교체 필요):")
    print("  - STORY_SHORTS_SHEET_ID → Google Sheet 문서 ID")
    print("  - NanumGothicBold 폰트 → NCA 서버에서 경로 확인 필요")

    print("\n" + "=" * 60)
    print("워크플로우 구조:")
    print("  [스케줄 03:00,15:00] → [Gemini: 훅 제목 + 나레이션 + 키워드]")
    print("       → [파싱] → [시트 기록] → [세그먼트 분리 (7~10개)]")
    print("       → 병렬 처리:")
    print("         Path A: [TTS 요청] → [대기] → [결과]")
    print("         Path B: [Pexels 검색 (portrait)] → [URL 추출]")
    print("         Path C: [BGM 생성] → [대기]")
    print("       → [Merge] → [Aggregate] → [NCA 데이터 준비]")
    print("       → [NCA 파트별 트림+crop] → [대기]")
    print("       → [NCA 영상 합치기] → [NCA 배너+자막 오버레이]")
    print("       → [NCA BGM 믹스] → [최종 영상]")
    print("       → [YouTube 업로드] → [댓글] → [발행 완료]")
    print("=" * 60)
    print(f"\n비용: ~$0.10/편 (TTS + BGM만, Pexels 무료)")

    return output_path


if __name__ == "__main__":
    main()
