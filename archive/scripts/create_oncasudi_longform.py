#!/usr/bin/env python3
"""
온카스터디 롱폼 (완전자동 v1) - n8n workflow generator
Based on 루믹스 솔루션 롱폼 (완전자동 v1) template
"""

import json
import uuid
import subprocess
import sys


def gen_id():
    return str(uuid.uuid4())


def gen_webhook_id():
    return str(uuid.uuid4())


def build_workflow():
    workflow_name = "온카스터디 롱폼 (완전자동 v1)"

    ai_prompt = "너는 온카스터디(온라인 카지노 정보 및 먹튀 검증 플랫폼)의 콘텐츠 기획자이자 영상 대본 작가야.\nYouTube 롱폼 영상(2~3분)용 대본을 작성해줘.\n\n온카스터디 소개: 먹튀 검증, 안전한 사이트 정보, 카지노 가이드, 배팅 전략, 환전 안전 정보를 제공하는 전문 플랫폼\n\n타겟: 안전한 온라인 카지노 정보를 찾는 사용자, 먹튀 피해를 예방하고 싶은 이용자\n톤: 신뢰감 있고 전문적이면서 친근한 안내자 톤, 시청자가 끝까지 보게 만드는 스토리텔링\n구조: 훅(위기감/호기심) → 문제 제기 → 해결책(온카스터디) → 사례/근거 → CTA\n\n아래 주제 카테고리 중 하나를 랜덤으로 골라서 구체적인 주제를 만들어:\n1. 온카스터디가 왜 필요한지 - 먹튀 피해 실태와 예방의 중요성\n2. 안전한 온라인 카지노 사이트 고르는 5가지 기준\n3. 먹튀 사이트 구별하는 방법 - 실제 사례 분석\n4. 온카스터디 먹튀 검증 시스템이 작동하는 원리\n5. 초보자를 위한 온라인 카지노 안전 이용 가이드\n6. 환전 사고 예방법 - 온카스터디가 알려주는 안전한 환전 절차\n7. 온카스터디 사용자 후기 - 먹튀 피해를 막은 실제 경험담\n8. 배팅 전략 기초 - 감이 아닌 데이터로 접근하는 법\n9. 온라인 카지노 사기 유형 TOP 5와 대처법\n10. 2026년 온라인 카지노 트렌드와 안전하게 즐기는 법\n\n대본 규칙:\n- 자연스러운 구어체 (방송 진행자 톤)\n- 총 800~1200자 (한국어 기준, 2~3분 분량)\n- 10개 파트로 나눠서 작성 (각 파트 80~120자)\n- 각 파트에 Pexels 스톡영상 검색용 영어 키워드 포함\n- 온카스터디의 가치와 신뢰성을 자연스럽게 강조\n- CTA는 온카스터디 방문/구독 유도\n\n반드시 아래 JSON 형식으로만 응답해. 마크다운 코드블록 없이 순수 JSON만:\n{\n  \"Subject\": \"영상 제목 (호기심 유발, 20자 이내)\",\n  \"Caption\": \"YouTube 설명 (해시태그 포함, 5줄)\",\n  \"Comment\": \"첫 번째 댓글 (질문 유도)\",\n  \"BGM_prompt\": \"BGM 분위기 영어 설명 (dramatic, suspenseful, trust-building 등 15~25단어)\",\n  \"parts\": [\n    {\"text\": \"나레이션 텍스트 (80~120자)\", \"keyword\": \"pexels search keyword in english (2~4 words)\"},\n    {\"text\": \"...\", \"keyword\": \"...\"},\n    {\"text\": \"...\", \"keyword\": \"...\"},\n    {\"text\": \"...\", \"keyword\": \"...\"},\n    {\"text\": \"...\", \"keyword\": \"...\"},\n    {\"text\": \"...\", \"keyword\": \"...\"},\n    {\"text\": \"...\", \"keyword\": \"...\"},\n    {\"text\": \"...\", \"keyword\": \"...\"},\n    {\"text\": \"...\", \"keyword\": \"...\"},\n    {\"text\": \"...\", \"keyword\": \"...\"}\n  ]\n}"

    shotstack_code = "// === Shotstack 롱폼 타임라인 빌더 (1920x1080 가로) ===\nconst bgmUrl = $('BGM 대기').first().json.audio?.url || '';\nconst bitrate = 128000;\nconst PART_COUNT = 10;\n\nlet scenes = [];\nlet currentStart = 0;\n\nfor (let i = 0; i < PART_COUNT; i++) {\n  // TTS 결과\n  const ttsResult = $('TTS 결과').all()[i]?.json;\n  const narrationUrl = ttsResult?.audio?.url || '';\n  const fileSize = ttsResult?.audio?.file_size || 50000;\n\n  // Duration from audio file size\n  let duration = Math.round((fileSize * 8 / bitrate) * 100) / 100;\n  if (duration < 5) duration = 10;\n\n  // Stock video URL\n  const stockResult = $('영상 URL 추출').all()[i]?.json;\n  const videoUrl = stockResult?.videoUrl || '';\n\n  // Subtitle\n  const subtitleText = $('파트 분리').all()[i]?.json?.text || '';\n\n  scenes.push({\n    start: currentStart,\n    duration: duration,\n    videoUrl: videoUrl,\n    narrationUrl: narrationUrl,\n    subtitleText: subtitleText\n  });\n\n  currentStart += duration;\n}\n\nconst totalDuration = currentStart;\n\n// === Shotstack Timeline (Landscape 1920x1080) ===\nconst timeline = {\n  soundtrack: {\n    src: bgmUrl,\n    effect: \"fadeOut\",\n    volume: 0.15\n  },\n  background: \"#000000\",\n  tracks: [\n    // Track 1: Stock video clips with transitions\n    {\n      clips: scenes.map((s, i) => ({\n        asset: {\n          type: \"video\",\n          src: s.videoUrl,\n          volume: 0,\n          trim: 0\n        },\n        start: s.start,\n        length: s.duration,\n        fit: \"cover\",\n        transition: i > 0 ? {\n          in: \"fade\",\n          out: i < scenes.length - 1 ? \"fade\" : undefined\n        } : undefined\n      }))\n    },\n    // Track 2: Narration audio\n    {\n      clips: scenes.map(s => ({\n        asset: {\n          type: \"audio\",\n          src: s.narrationUrl\n        },\n        start: s.start,\n        length: s.duration\n      }))\n    },\n    // Track 3: Subtitles (bottom bar style)\n    {\n      clips: scenes.map(s => ({\n        asset: {\n          type: \"html\",\n          html: '<div class=\"sub\"><p>' + s.subtitleText.replace(/'/g, \"\\\\\\\\'\" ) + '</p></div>',\n          css: \".sub { background: linear-gradient(transparent, rgba(0,0,0,0.7)); padding: 30px 60px 20px; } p { font-family: 'Noto Sans KR', sans-serif; font-size: 36px; color: #ffffff; text-align: center; line-height: 1.5; font-weight: 600; text-shadow: 1px 1px 4px rgba(0,0,0,0.8); }\",\n          width: 1920,\n          height: 200\n        },\n        start: s.start,\n        length: s.duration,\n        position: \"bottom\",\n        offset: { y: 0 }\n      }))\n    },\n    // Track 4: 채널 로고/워터마크\n    {\n      clips: [{\n        asset: {\n          type: \"html\",\n          html: \"<p>온카스터디</p>\",\n          css: \"p { font-family: 'Noto Sans KR', sans-serif; font-size: 18px; color: rgba(255,255,255,0.5); letter-spacing: 2px; }\",\n          width: 300,\n          height: 40\n        },\n        start: 0,\n        length: totalDuration,\n        position: \"topRight\",\n        offset: { x: -0.02, y: 0.02 }\n      }]\n    }\n  ]\n};\n\n// Intro fade-in (first scene)\nif (timeline.tracks[0].clips.length > 0) {\n  timeline.tracks[0].clips[0].transition = { in: \"fade\" };\n}\n\nconst payload = {\n  timeline: timeline,\n  output: {\n    format: \"mp4\",\n    resolution: \"hd\",\n    aspectRatio: \"16:9\",\n    fps: 30,\n    quality: \"high\"\n  }\n};\n\nreturn [{\n  json: {\n    shotstack_payload: payload,\n    totalDuration: totalDuration,\n    sceneCount: scenes.length,\n    subject: $('대본 파싱').first().json.Subject,\n    caption: $('대본 파싱').first().json.Caption,\n    comment: $('대본 파싱').first().json.Comment\n  }\n}];"

    nodes = []

    # [0] 스케줄 트리거
    nodes.append({
        "parameters": {"rule": {"interval": [{}]}},
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.3,
        "position": [-2400, 304],
        "id": gen_id(),
        "name": "스케줄 트리거"
    })

    # [1] AI 대본 생성
    nodes.append({
        "parameters": {
            "modelId": {"__rl": True, "value": "models/gemini-2.5-flash", "mode": "list", "cachedResultName": "models/gemini-2.5-flash"},
            "messages": {"values": [{"content": ai_prompt}]},
            "jsonOutput": True,
            "builtInTools": {},
            "options": {}
        },
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1.1,
        "position": [-2096, 304],
        "id": gen_id(),
        "name": "AI 대본 생성"
    })

    # [2] 대본 파싱
    nodes.append({
        "parameters": {
            "jsCode": "const text = $input.first().json.content.parts[0].text;\nconst cleanText = text.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();\nconst data = JSON.parse(cleanText);\n\nreturn [{\n  json: {\n    Subject: data.Subject,\n    Caption: data.Caption,\n    Comment: data.Comment,\n    BGM_prompt: data.BGM_prompt,\n    parts: data.parts,\n    fullNarration: data.parts.map(p => p.text).join(' '),\n    Status: '준비',\n    generatedAt: new Date().toISOString()\n  }\n}];"
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-1808, 304],
        "id": gen_id(),
        "name": "대본 파싱"
    })

    # [3] 시트 기록
    nodes.append({
        "parameters": {
            "operation": "append",
            "documentId": {"__rl": True, "value": "ONCASUDI_SHEET_ID", "mode": "list", "cachedResultName": "온카스터디 시트", "cachedResultUrl": ""},
            "sheetName": {"__rl": True, "value": "gid=0", "mode": "list", "cachedResultName": "온카스터디", "cachedResultUrl": ""},
            "columns": {
                "mappingMode": "defineBelow",
                "value": {"Subject": "={{ $json.Subject }}", "Narration": "={{ $json.fullNarration }}", "Caption": "={{ $json.Caption }}", "댓글": "={{ $json.Comment }}", "BGM prompt": "={{ $json.BGM_prompt }}", "Status": "준비"},
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
        "position": [-1504, 304],
        "id": gen_id(),
        "name": "시트 기록"
    })

    # [4] 파트 분리
    nodes.append({
        "parameters": {
            "jsCode": "const data = $('대본 파싱').first().json;\n\nconst items = data.parts.map((part, i) => ({\n  json: {\n    text: part.text,\n    keyword: part.keyword,\n    index: i + 1,\n    subject: data.Subject,\n    bgmPrompt: data.BGM_prompt\n  }\n}));\n\nreturn items;"
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-1200, 304],
        "id": gen_id(),
        "name": "파트 분리"
    })

    # [5] TTS 요청
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
        "position": [-896, 112],
        "id": gen_id(),
        "name": "TTS 요청"
    })

    # [6] TTS 대기
    nodes.append({
        "parameters": {"amount": 30},
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [-608, 112],
        "id": gen_id(),
        "name": "TTS 대기",
        "webhookId": gen_webhook_id()
    })

    # [7] TTS 결과
    nodes.append({
        "parameters": {
            "url": "=https://queue.fal.run/fal-ai/elevenlabs/requests/{{ $json.request_id }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-304, 112],
        "id": gen_id(),
        "name": "TTS 결과"
    })

    # [8] Pexels 검색
    nodes.append({
        "parameters": {
            "url": "=https://api.pexels.com/videos/search?query={{ encodeURIComponent($json.keyword) }}&per_page=3&orientation=landscape&size=medium",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-896, 512],
        "id": gen_id(),
        "name": "Pexels 검색"
    })

    # [9] 영상 URL 추출
    nodes.append({
        "parameters": {
            "jsCode": "const result = $input.first().json;\nconst videos = result.videos || [];\n\nlet videoUrl = '';\nlet videoDuration = 0;\n\nif (videos.length > 0) {\n  // Pick a random video from top 3 results for variety\n  const video = videos[Math.floor(Math.random() * Math.min(3, videos.length))];\n  videoDuration = video.duration || 10;\n\n  // Find HD quality file (prefer 1920x1080)\n  const files = video.video_files || [];\n  const hdFile = files.find(f => f.width >= 1920 && f.quality === 'hd')\n    || files.find(f => f.width >= 1280)\n    || files.find(f => f.quality === 'hd')\n    || files[0];\n\n  if (hdFile) {\n    videoUrl = hdFile.link;\n  }\n}\n\n// Fallback: generic business/technology video\nif (!videoUrl) {\n  videoUrl = 'https://cdn.pixabay.com/video/2024/02/14/200717-913266610_large.mp4';\n  videoDuration = 15;\n}\n\nreturn [{\n  json: {\n    videoUrl: videoUrl,\n    videoDuration: videoDuration,\n    keyword: $('파트 분리').item.json.keyword,\n    index: $('파트 분리').item.json.index\n  }\n}];"
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-608, 512],
        "id": gen_id(),
        "name": "영상 URL 추출"
    })

    # [10] BGM 생성
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://fal.run/beatoven/music-generation",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\n  \"prompt\": \"{{ $json.bgmPrompt || 'dramatic suspenseful trust-building cinematic background music' }}\",\n  \"duration\": 200,\n  \"refinement\": 100,\n  \"creativity\": 16\n}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-896, -96],
        "id": gen_id(),
        "name": "BGM 생성"
    })

    # [11] BGM 대기
    nodes.append({
        "parameters": {"amount": 60},
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [-608, -96],
        "id": gen_id(),
        "name": "BGM 대기",
        "webhookId": gen_webhook_id()
    })

    # [12] Merge
    nodes.append({
        "parameters": {"numberInputs": 3},
        "type": "n8n-nodes-base.merge",
        "typeVersion": 3.2,
        "position": [0, 304],
        "id": gen_id(),
        "name": "Merge"
    })

    # [13] Aggregate
    nodes.append({
        "parameters": {"aggregate": "aggregateAllItemData", "options": {}},
        "type": "n8n-nodes-base.aggregate",
        "typeVersion": 1,
        "position": [320, 320],
        "id": gen_id(),
        "name": "Aggregate"
    })

    # [14] Shotstack 타임라인
    nodes.append({
        "parameters": {"jsCode": shotstack_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [608, 320],
        "id": gen_id(),
        "name": "Shotstack 타임라인"
    })

    # [15] Shotstack 렌더
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
        "position": [0, 608],
        "id": gen_id(),
        "name": "Shotstack 렌더"
    })

    # [16] 렌더 대기
    nodes.append({
        "parameters": {"amount": 180},
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [304, 608],
        "id": gen_id(),
        "name": "렌더 대기",
        "webhookId": gen_webhook_id()
    })

    # [17] 렌더 결과
    nodes.append({
        "parameters": {
            "url": "=https://api.shotstack.io/edit/stage/render/{{ $json.response.id }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [608, 608],
        "id": gen_id(),
        "name": "렌더 결과"
    })

    # [18] 렌더 완료 확인
    nodes.append({
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [{"id": gen_id(), "leftValue": "={{ $json.response.status }}", "rightValue": "done", "operator": {"type": "string", "operation": "equals"}}]
            },
            "options": {}
        },
        "type": "n8n-nodes-base.if",
        "typeVersion": 2.2,
        "position": [960, 608],
        "id": gen_id(),
        "name": "렌더 완료 확인"
    })

    # [19] 추가 대기
    nodes.append({
        "parameters": {"amount": 60},
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1,
        "position": [1008, 816],
        "id": gen_id(),
        "name": "추가 대기",
        "webhookId": gen_webhook_id()
    })

    # [20] 렌더 재확인
    nodes.append({
        "parameters": {
            "url": "=https://api.shotstack.io/edit/stage/render/{{ $('Shotstack 렌더').first().json.response.id }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [1264, 816],
        "id": gen_id(),
        "name": "렌더 재확인"
    })

    # [21] 상태 업데이트
    nodes.append({
        "parameters": {
            "operation": "update",
            "documentId": {"__rl": True, "value": "ONCASUDI_SHEET_ID", "mode": "list", "cachedResultName": "온카스터디 시트"},
            "sheetName": {"__rl": True, "value": "gid=0", "mode": "list", "cachedResultName": "온카스터디"},
            "columns": {
                "mappingMode": "defineBelow",
                "value": {"row_number": "={{ $('시트 기록').first().json.row_number }}", "Status": "생성 완료", "업로드 URL": "={{ $json.response.url }}"},
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
        "position": [1264, 512],
        "id": gen_id(),
        "name": "상태 업데이트"
    })

    # [22] 영상 다운로드
    nodes.append({
        "parameters": {
            "url": "={{ $json.response.url }}",
            "options": {"response": {"response": {"responseFormat": "file"}}}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [1264, 704],
        "id": gen_id(),
        "name": "영상 다운로드"
    })

    # [23] YouTube 업로드
    nodes.append({
        "parameters": {
            "resource": "video",
            "operation": "upload",
            "title": "={{ $('대본 파싱').first().json.Subject }}",
            "regionCode": "KR",
            "categoryId": "28",
            "options": {"description": "={{ $('대본 파싱').first().json.Caption }}", "privacyStatus": "public"}
        },
        "type": "n8n-nodes-base.youTube",
        "typeVersion": 1,
        "position": [1600, 688],
        "id": gen_id(),
        "name": "YouTube 업로드"
    })

    # [24] 첫 댓글
    nodes.append({
        "parameters": {
            "method": "POST",
            "url": "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "youTubeOAuth2Api",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\n  \"snippet\": {\n    \"videoId\": \"{{ $json.id }}\",\n    \"topLevelComment\": {\n      \"snippet\": {\n        \"textOriginal\": \"{{ $('대본 파싱').first().json.Comment }}\"\n      }\n    }\n  }\n}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [1904, 688],
        "id": gen_id(),
        "name": "첫 댓글"
    })

    # [25] 발행 완료
    nodes.append({
        "parameters": {
            "operation": "update",
            "documentId": {"__rl": True, "value": "ONCASUDI_SHEET_ID", "mode": "list", "cachedResultName": "온카스터디 시트"},
            "sheetName": {"__rl": True, "value": "gid=0", "mode": "list", "cachedResultName": "온카스터디"},
            "columns": {
                "mappingMode": "defineBelow",
                "value": {"row_number": "={{ $('시트 기록').first().json.row_number }}", "Publish": "발행 완료", "업로드 URL": "=https://youtube.com/watch?v={{ $('YouTube 업로드').first().json.id }}"},
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
        "position": [2192, 688],
        "id": gen_id(),
        "name": "발행 완료"
    })

    # Connections
    connections = {
        "스케줄 트리거": {"main": [[{"node": "AI 대본 생성", "type": "main", "index": 0}]]},
        "AI 대본 생성": {"main": [[{"node": "대본 파싱", "type": "main", "index": 0}]]},
        "대본 파싱": {"main": [[{"node": "시트 기록", "type": "main", "index": 0}]]},
        "시트 기록": {"main": [[{"node": "파트 분리", "type": "main", "index": 0}, {"node": "BGM 생성", "type": "main", "index": 0}]]},
        "파트 분리": {"main": [[{"node": "TTS 요청", "type": "main", "index": 0}, {"node": "Pexels 검색", "type": "main", "index": 0}]]},
        "TTS 요청": {"main": [[{"node": "TTS 대기", "type": "main", "index": 0}]]},
        "TTS 대기": {"main": [[{"node": "TTS 결과", "type": "main", "index": 0}]]},
        "TTS 결과": {"main": [[{"node": "Merge", "type": "main", "index": 1}]]},
        "Pexels 검색": {"main": [[{"node": "영상 URL 추출", "type": "main", "index": 0}]]},
        "영상 URL 추출": {"main": [[{"node": "Merge", "type": "main", "index": 2}]]},
        "BGM 생성": {"main": [[{"node": "BGM 대기", "type": "main", "index": 0}]]},
        "BGM 대기": {"main": [[{"node": "Merge", "type": "main", "index": 0}]]},
        "Merge": {"main": [[{"node": "Aggregate", "type": "main", "index": 0}]]},
        "Aggregate": {"main": [[{"node": "Shotstack 타임라인", "type": "main", "index": 0}]]},
        "Shotstack 타임라인": {"main": [[{"node": "Shotstack 렌더", "type": "main", "index": 0}]]},
        "Shotstack 렌더": {"main": [[{"node": "렌더 대기", "type": "main", "index": 0}]]},
        "렌더 대기": {"main": [[{"node": "렌더 결과", "type": "main", "index": 0}]]},
        "렌더 결과": {"main": [[{"node": "렌더 완료 확인", "type": "main", "index": 0}]]},
        "렌더 완료 확인": {"main": [[{"node": "상태 업데이트", "type": "main", "index": 0}, {"node": "영상 다운로드", "type": "main", "index": 0}], [{"node": "추가 대기", "type": "main", "index": 0}]]},
        "추가 대기": {"main": [[{"node": "렌더 재확인", "type": "main", "index": 0}]]},
        "렌더 재확인": {"main": [[{"node": "렌더 완료 확인", "type": "main", "index": 0}]]},
        "영상 다운로드": {"main": [[{"node": "YouTube 업로드", "type": "main", "index": 0}]]},
        "YouTube 업로드": {"main": [[{"node": "첫 댓글", "type": "main", "index": 0}]]},
        "첫 댓글": {"main": [[{"node": "발행 완료", "type": "main", "index": 0}]]}
    }

    workflow = {
        "name": workflow_name,
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"}
    }

    return workflow


def main():
    print("=== 온카스터디 롱폼 (완전자동 v1) Workflow Generator ===")
    print()

    workflow = build_workflow()

    output_path = "/Users/gimdongseog/n8n-project/oncasudi_longform_v1.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)

    print(f"Workflow JSON saved to: {output_path}")
    print(f"  - Name: {workflow['name']}")
    print(f"  - Nodes: {len(workflow['nodes'])}")
    print(f"  - Connections: {len(workflow['connections'])} node links")
    print()

    # Upload to n8n
    print("Uploading to n8n...")
    api_url = "https://n8n.srv1345711.hstgr.cloud/api/v1/workflows"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"

    result = subprocess.run(
        ["curl", "-sk", "-X", "POST", api_url,
         "-H", f"X-N8N-API-KEY: {api_key}",
         "-H", "Content-Type: application/json",
         "-d", f"@{output_path}"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"ERROR: curl failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    response_text = result.stdout
    try:
        response = json.loads(response_text)
        if "id" in response:
            print(f"SUCCESS! Workflow uploaded.")
            print(f"  Workflow ID: {response['id']}")
            print(f"  Name: {response.get('name', 'N/A')}")
            print(f"  URL: https://n8n.srv1345711.hstgr.cloud/workflow/{response['id']}")
        else:
            print(f"Upload response (no ID found):")
            print(json.dumps(response, ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print(f"Raw response: {response_text}")


if __name__ == "__main__":
    main()
