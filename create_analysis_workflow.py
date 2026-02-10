#!/usr/bin/env python3
"""
채널 성과 분석 워크플로우 생성
- 매일 06:00 KST에 4채널 순차 분석
- YouTube API로 트렌드 + 우리 영상 통계 수집
- Gemini로 분석 리포트 생성
- Google Sheets 분석리포트 탭에 저장
"""
import json, subprocess, uuid

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"

CRED_GEMINI = {"googlePalmApi": {"id": "IKP349r08J9Hoz5E", "name": "Google Gemini(PaLM) Api account"}}
CRED_SHEETS = {"googleSheetsOAuth2Api": {"id": "CWBUyXUqCU9p5VAg", "name": "Google Sheets account"}}
CRED_YOUTUBE = {"youTubeOAuth2Api": {"id": "kRKBMYWf6cB72qUi", "name": "YouTube account"}}

CHANNELS = [
    {
        "name": "루믹스",
        "channelId": "CHANNEL_ID_LUMIX",  # TODO: 실제 채널 ID로 교체
        "keywords": "카지노 솔루션 온라인카지노 API",
        "niche": "카지노 솔루션/IT 솔루션",
        "docId": "1qPH9TG4M0Hv4V63_LqAb6X2gNl_ksbf2T_oIkJJ06Ag",
    },
    {
        "name": "온카스터디",
        "channelId": "CHANNEL_ID_ONCA",  # TODO: 실제 채널 ID로 교체
        "keywords": "먹튀검증 토토사이트 메이저사이트",
        "niche": "먹튀검증/온라인 안전",
        "docId": "1hnFCo4Mxnr4w57_zAFfYLMAgOsAB43ocgWhJW3szWK8",
    },
    {
        "name": "슬롯",
        "channelId": "CHANNEL_ID_SLOT",  # TODO: 실제 채널 ID로 교체
        "keywords": "슬롯 RTP 배팅전략 카지노게임",
        "niche": "슬롯/카지노 게임",
        "docId": "1cps-88TuhFld4qJlryQh2QHkKvxhQyxLSgeu5burA_A",
    },
    {
        "name": "스포츠",
        "channelId": "CHANNEL_ID_SPORTS",  # TODO: 실제 채널 ID로 교체
        "keywords": "스포츠분석 축구 야구 농구 UFC 배당률",
        "niche": "스포츠 분석/베팅 정보",
        "docId": "1NAVwKXLQOUzBoNckxxesIR_ZS3GoNVGepr8zkBFmz4M",
    },
]

def uid():
    return str(uuid.uuid4())

# ============================================================
# Build nodes
# ============================================================
nodes = []
connections = {}

# 1. Schedule Trigger (매일 06:00 KST = 21:00 UTC 전날)
trigger = {
    "parameters": {
        "rule": {
            "interval": [
                {
                    "field": "cronExpression",
                    "expression": "0 21 * * *"
                }
            ]
        }
    },
    "name": "매일 06시 KST",
    "type": "n8n-nodes-base.scheduleTrigger",
    "typeVersion": 1.3,
    "position": [-1800, 300],
    "id": uid()
}
nodes.append(trigger)

# 2. Webhook Trigger (수동 테스트용)
webhook = {
    "parameters": {
        "path": "analysis-trigger",
        "responseMode": "onReceived",
        "options": {}
    },
    "name": "Webhook 트리거",
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 2,
    "position": [-1800, 100],
    "id": uid(),
    "webhookId": uid()
}
nodes.append(webhook)

# 3. Code: 채널 설정 (4개 채널 정보를 아이템으로 출력)
channel_config_code = """
const channels = CHANNELS_PLACEHOLDER;

const today = new Date();
const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
const publishedAfter = weekAgo.toISOString();

return channels.map(ch => ({
  json: {
    ...ch,
    publishedAfter,
    analysisDate: today.toISOString().split('T')[0]
  }
}));
""".replace("CHANNELS_PLACEHOLDER", json.dumps(CHANNELS, ensure_ascii=False))

config_node = {
    "parameters": {
        "jsCode": channel_config_code
    },
    "name": "채널 설정",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [-1500, 200],
    "id": uid()
}
nodes.append(config_node)

# Connect triggers to config
connections["매일 06시 KST"] = {"main": [[{"node": "채널 설정", "type": "main", "index": 0}]]}
connections["Webhook 트리거"] = {"main": [[{"node": "채널 설정", "type": "main", "index": 0}]]}

# 4. SplitInBatches (한 채널씩 처리)
split_node = {
    "parameters": {
        "batchSize": 1,
        "options": {}
    },
    "name": "채널별 처리",
    "type": "n8n-nodes-base.splitInBatches",
    "typeVersion": 3,
    "position": [-1200, 200],
    "id": uid()
}
nodes.append(split_node)
connections["채널 설정"] = {"main": [[{"node": "채널별 처리", "type": "main", "index": 0}]]}

# 5. YouTube 트렌드 검색 (HTTP Request)
trend_search = {
    "parameters": {
        "method": "GET",
        "url": "https://www.googleapis.com/youtube/v3/search",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "youTubeOAuth2Api",
        "sendQuery": True,
        "queryParameters": {
            "parameters": [
                {"name": "part", "value": "snippet"},
                {"name": "type", "value": "video"},
                {"name": "videoDuration", "value": "short"},
                {"name": "order", "value": "viewCount"},
                {"name": "maxResults", "value": "10"},
                {"name": "q", "value": "={{ $json.keywords }}"},
                {"name": "publishedAfter", "value": "={{ $json.publishedAfter }}"},
                {"name": "regionCode", "value": "KR"},
                {"name": "relevanceLanguage", "value": "ko"}
            ]
        },
        "options": {}
    },
    "name": "트렌드 검색",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [-900, 200],
    "id": uid(),
    "credentials": CRED_YOUTUBE
}
nodes.append(trend_search)

# SplitInBatches output 1 (loop body) → 트렌드 검색
connections["채널별 처리"] = {
    "main": [
        [],  # output 0: done (empty, will connect later)
        [{"node": "트렌드 검색", "type": "main", "index": 0}]  # output 1: loop body
    ]
}

# 6. Code: 트렌드 데이터 정리 + 영상 ID 추출
trend_parse_code = """
const input = $input.first().json;
const trendItems = (input.items || []).map(item => ({
  title: item.snippet?.title || '',
  channelTitle: item.snippet?.channelTitle || '',
  publishedAt: item.snippet?.publishedAt || '',
  videoId: item.id?.videoId || ''
}));

const videoIds = trendItems.map(t => t.videoId).filter(Boolean).join(',');

// 이전 노드의 채널 정보 유지
const channelInfo = $('채널별 처리').first().json;

return [{
  json: {
    ...channelInfo,
    trendVideos: trendItems,
    trendVideoIds: videoIds
  }
}];
"""
trend_parse = {
    "parameters": {"jsCode": trend_parse_code},
    "name": "트렌드 정리",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [-600, 200],
    "id": uid()
}
nodes.append(trend_parse)
connections["트렌드 검색"] = {"main": [[{"node": "트렌드 정리", "type": "main", "index": 0}]]}

# 7. YouTube 트렌드 영상 통계 (조회수/좋아요)
trend_stats = {
    "parameters": {
        "method": "GET",
        "url": "https://www.googleapis.com/youtube/v3/videos",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "youTubeOAuth2Api",
        "sendQuery": True,
        "queryParameters": {
            "parameters": [
                {"name": "part", "value": "statistics,snippet"},
                {"name": "id", "value": "={{ $json.trendVideoIds }}"}
            ]
        },
        "options": {}
    },
    "name": "트렌드 통계",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [-300, 200],
    "id": uid(),
    "credentials": CRED_YOUTUBE
}
nodes.append(trend_stats)
connections["트렌드 정리"] = {"main": [[{"node": "트렌드 통계", "type": "main", "index": 0}]]}

# 8. Code: 통계 데이터 병합 + Gemini 프롬프트 생성
prepare_prompt_code = """
const channelInfo = $('트렌드 정리').first().json;
const statsResponse = $input.first().json;

// 트렌드 영상 통계 정리
const trendStats = (statsResponse.items || []).map(v => ({
  title: v.snippet?.title || '',
  views: parseInt(v.statistics?.viewCount || '0'),
  likes: parseInt(v.statistics?.likeCount || '0'),
  comments: parseInt(v.statistics?.commentCount || '0')
})).sort((a, b) => b.views - a.views);

const topTrends = trendStats.slice(0, 5).map((v, i) =>
  `${i+1}. "${v.title}" (조회수: ${v.views.toLocaleString()}, 좋아요: ${v.likes.toLocaleString()})`
).join('\\n');

const prompt = `너는 YouTube Shorts 콘텐츠 전략가야.
아래 데이터를 분석하고 "${channelInfo.name}" 채널을 위한 리포트를 작성해.

[채널 정보]
- 채널명: ${channelInfo.name}
- 니치: ${channelInfo.niche}

[이번 주 인기 Shorts 트렌드 (${channelInfo.keywords} 관련)]
${topTrends || '데이터 없음'}

[분석 요청]
위 데이터를 기반으로 아래 JSON 형식으로 분석 리포트를 작성해.
마크다운 코드블록 없이 순수 JSON만 응답해:

{
  "조회수_상위영상": "가장 조회수 높은 트렌드 영상 제목과 조회수",
  "좋아요_상위영상": "가장 좋아요 많은 트렌드 영상 제목",
  "트렌드_키워드": "이번 주 핵심 트렌드 키워드 3-5개 (쉼표 구분)",
  "추천_주제1": "추천 주제 1 (제목 형식, 이유 포함)",
  "추천_주제2": "추천 주제 2",
  "추천_주제3": "추천 주제 3",
  "피해야할_주제": "이번 주 피해야 할 주제/각도",
  "효과적인_훅_팁": "효과적인 첫 3초 훅 팁",
  "트렌드_각도": "현재 트렌드의 핵심 각도/방향",
  "고성과_패턴": "고성과 영상들의 공통 패턴",
  "AI_분석_요약": "전체 분석 요약 (3문장 이내)"
}`;

return [{
  json: {
    ...channelInfo,
    trendStats,
    geminiPrompt: prompt
  }
}];
"""
prepare_prompt = {
    "parameters": {"jsCode": prepare_prompt_code},
    "name": "프롬프트 생성",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [0, 200],
    "id": uid()
}
nodes.append(prepare_prompt)
connections["트렌드 통계"] = {"main": [[{"node": "프롬프트 생성", "type": "main", "index": 0}]]}

# 9. Gemini: 분석 리포트 생성
gemini_analysis = {
    "parameters": {
        "modelId": {
            "__rl": True,
            "value": "models/gemini-3-flash-preview",
            "mode": "list",
            "cachedResultName": "models/gemini-3-flash-preview"
        },
        "messages": {
            "values": [
                {"content": "={{ $json.geminiPrompt }}"}
            ]
        },
        "jsonOutput": True,
        "builtInTools": {},
        "options": {}
    },
    "name": "AI 분석",
    "type": "@n8n/n8n-nodes-langchain.googleGemini",
    "typeVersion": 1.1,
    "position": [300, 200],
    "id": uid(),
    "credentials": CRED_GEMINI
}
nodes.append(gemini_analysis)
connections["프롬프트 생성"] = {"main": [[{"node": "AI 분석", "type": "main", "index": 0}]]}

# 10. Code: 리포트 파싱 + Sheets 데이터 준비
parse_report_code = """
const channelInfo = $('프롬프트 생성').first().json;
const geminiResponse = $input.first().json;

// Gemini 응답에서 JSON 추출
let reportText = '';
if (geminiResponse.content && geminiResponse.content.parts) {
  reportText = geminiResponse.content.parts[0].text || '';
} else if (typeof geminiResponse === 'string') {
  reportText = geminiResponse;
} else {
  reportText = JSON.stringify(geminiResponse);
}

// JSON 추출 ({ ~ } 사이)
let cleanText = reportText.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();
const firstBrace = cleanText.indexOf('{');
const lastBrace = cleanText.lastIndexOf('}');
let report = {};
if (firstBrace !== -1 && lastBrace !== -1) {
  try {
    report = JSON.parse(cleanText.substring(firstBrace, lastBrace + 1));
  } catch(e) {
    report = { AI_분석_요약: "파싱 실패: " + cleanText.substring(0, 200) };
  }
}

return [{
  json: {
    날짜: channelInfo.analysisDate,
    채널명: channelInfo.name,
    분석기간: "최근 7일",
    조회수_상위영상: report.조회수_상위영상 || '',
    좋아요_상위영상: report.좋아요_상위영상 || '',
    트렌드_키워드: report.트렌드_키워드 || '',
    추천_주제1: report.추천_주제1 || '',
    추천_주제2: report.추천_주제2 || '',
    추천_주제3: report.추천_주제3 || '',
    피해야할_주제: report.피해야할_주제 || '',
    효과적인_훅_팁: report.효과적인_훅_팁 || '',
    트렌드_각도: report.트렌드_각도 || '',
    고성과_패턴: report.고성과_패턴 || '',
    AI_분석_요약: report.AI_분석_요약 || '',
    _docId: channelInfo.docId
  }
}];
"""
parse_report = {
    "parameters": {"jsCode": parse_report_code},
    "name": "리포트 파싱",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [600, 200],
    "id": uid()
}
nodes.append(parse_report)
connections["AI 분석"] = {"main": [[{"node": "리포트 파싱", "type": "main", "index": 0}]]}

# 11. Google Sheets: 분석리포트 탭에 저장
# HTTP Request로 append (동적 docId 사용을 위해)
sheets_save = {
    "parameters": {
        "method": "POST",
        "url": "=https://sheets.googleapis.com/v4/spreadsheets/{{ $json._docId }}/values/%EB%B6%84%EC%84%9D%EB%A6%AC%ED%8F%AC%ED%8A%B8:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "googleSheetsOAuth2Api",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={"values": [[{{ JSON.stringify($json.날짜) }}, {{ JSON.stringify($json.채널명) }}, {{ JSON.stringify($json.분석기간) }}, {{ JSON.stringify($json.조회수_상위영상) }}, {{ JSON.stringify($json.좋아요_상위영상) }}, {{ JSON.stringify($json.트렌드_키워드) }}, {{ JSON.stringify($json.추천_주제1) }}, {{ JSON.stringify($json.추천_주제2) }}, {{ JSON.stringify($json.추천_주제3) }}, {{ JSON.stringify($json.피해야할_주제) }}, {{ JSON.stringify($json.효과적인_훅_팁) }}, {{ JSON.stringify($json.트렌드_각도) }}, {{ JSON.stringify($json.고성과_패턴) }}, {{ JSON.stringify($json.AI_분석_요약) }}]]}',
        "options": {}
    },
    "name": "시트 저장",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [900, 200],
    "id": uid(),
    "credentials": CRED_SHEETS
}
nodes.append(sheets_save)
connections["리포트 파싱"] = {"main": [[{"node": "시트 저장", "type": "main", "index": 0}]]}

# 12. Back to SplitInBatches (loop)
connections["시트 저장"] = {"main": [[{"node": "채널별 처리", "type": "main", "index": 0}]]}

# 13. Done node (SplitInBatches output 0 = done)
done_node = {
    "parameters": {
        "jsCode": 'return [{json: {message: "4채널 성과 분석 완료!", timestamp: new Date().toISOString()}}];'
    },
    "name": "분석 완료",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [-900, -100],
    "id": uid()
}
nodes.append(done_node)

# Update SplitInBatches connections - output 0 is "done"
connections["채널별 처리"]["main"][0] = [{"node": "분석 완료", "type": "main", "index": 0}]

# ============================================================
# Build and upload workflow
# ============================================================
workflow = {
    "name": "채널 성과 분석 (매일 06:00)",
    "nodes": nodes,
    "connections": connections,
    "settings": {"executionOrder": "v1"}
}

# Save JSON locally
output_path = "/Users/gimdongseog/n8n-project/workflow_analysis.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)
print(f"워크플로우 JSON 저장: {output_path}")

# Upload to n8n
print("n8n에 워크플로우 업로드 중...")
result = subprocess.run([
    'curl', '-sk', '-X', 'POST', f'{BASE}/workflows',
    '-H', f'X-N8N-API-KEY: {API_KEY}',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(workflow, ensure_ascii=False)
], capture_output=True, text=True)

resp = json.loads(result.stdout)
if resp.get('id'):
    wf_id = resp['id']
    print(f"✅ 워크플로우 생성 완료! ID: {wf_id}")
    print(f"   URL: https://n8n.srv1345711.hstgr.cloud/workflow/{wf_id}")
    print()
    print("⚠️  TODO: YouTube Channel ID 설정 필요!")
    print("   n8n에서 '채널 설정' 노드의 channelId 값을 실제 채널 ID로 변경하세요:")
    print("   - CHANNEL_ID_LUMIX → 루믹스 솔루션 채널 ID")
    print("   - CHANNEL_ID_ONCA → 온카스터디 채널 ID")
    print("   - CHANNEL_ID_SLOT → 슬롯 채널 ID")
    print("   - CHANNEL_ID_SPORTS → 스포츠 채널 ID")

    # Activate
    act_result = subprocess.run([
        'curl', '-sk', '-X', 'POST', f'{BASE}/workflows/{wf_id}/activate',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json'
    ], capture_output=True, text=True)
    act_resp = json.loads(act_result.stdout)
    if act_resp.get('active') or act_resp.get('id'):
        print(f"✅ 활성화 완료 (Webhook + Schedule)")
    else:
        print(f"⚠️  활성화 응답: {act_result.stdout[:200]}")
else:
    print(f"❌ 업로드 실패: {result.stdout[:500]}")
