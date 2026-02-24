#!/usr/bin/env python3
"""
워크플로우 복구 + 8가지 수정사항 적용 + n8n 업로드
"""
import json, subprocess, tempfile, os

BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"

WF_PATH = "/Users/gimdongseog/n8n-project/oncastudy_shortform_v1.json"

def api_request(method, endpoint, data=None):
    url = f"{BASE}{endpoint}"
    cmd = ["curl", "-sk", "-X", method, url,
           "-H", f"X-N8N-API-KEY: {API_KEY}",
           "-H", "Content-Type: application/json"]
    if data:
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(data, tmp, ensure_ascii=False)
        tmp.close()
        cmd += ["-d", f"@{tmp.name}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if data:
        os.unlink(tmp.name)
    try:
        return json.loads(result.stdout)
    except:
        print(f"ERROR: {result.stdout[:500]}")
        return None

# 1. JSON 로드
print("1. 워크플로우 JSON 로드...")
with open(WF_PATH, 'r', encoding='utf-8') as f:
    wf = json.load(f)

nodes = wf["nodes"]
node_map = {n["name"]: i for i, n in enumerate(nodes)}

# ========================================
# 수정 1: 프롬프트 생성 (25-30초, 빠른 전환)
# ========================================
print("2. 프롬프트 생성 수정...")

PROMPT_CODE = r'''const topic = $input.first().json.topic || $input.first().json['주제'] || '';

if (!topic) {
  throw new Error('topic이 비어있습니다. 시트에 topic 컬럼을 확인하세요.');
}

const prompt = `너는 '온카스터디' 커뮤니티의 YouTube Shorts 꿀팁 콘텐츠 기획자야.
아래 주제로 25~30초 분량의 빠른 꿀팁 숏츠 스크립트를 작성해줘.

## 반드시 지킬 주제
${topic}

위 주제를 중심으로 콘텐츠를 작성하되, 후반부에 '온카스터디'를 자연스럽게 1회 언급해.
모든 scene의 dialogue는 반드시 "${topic}" 주제와 직접 관련된 내용이어야 해.

## 온카스터디 소개
온카스터디는 먹튀검증 및 안전 정보 제공 커뮤니티입니다.
검증 정보 공유, 먹튀 사이트 구별법 안내, 자유게시판, 제휴사이트 후기, 스포츠 분석,
포인트 시스템(복권, 돌림판, 기프티콘 교환) 등의 기능이 있습니다.

## 영상 스타일 (빠른 꿀팁 숏츠)
- 총 25~30초, 9:16 세로 영상
- 빠른 이미지/밈 전환 (각 장면 2~4초)
- 상단: 고정된 훅 제목 (검은 배경, 큰 글씨)
- 중간: 정보 이미지 + 밈 영상 번갈아 배치
- 하단: 짧은 자막
- 오디오: 빠른 TTS 나레이션

## 장면 구성 규칙 (핵심!)
- 총 8~10개 장면 (짧고 빠르게!)
- 각 장면에 visual_type: "image" 또는 "meme"
- image: 주제와 직접 관련된 구체적 이미지
- meme: 밈/리액션 영상 (감정 표현)
- 장면의 30~40%를 meme으로 배치
- 매 2~3개 image 뒤에 1개 meme
- meme_mood: thinking, excited, shocked, sad, angry, cool, celebrating 중 택1
- meme dialogue: 짧은 리액션 ("실화?!", "대박!", "미쳤다", "꿀팁이다!")

## 나레이션 규칙 (매우 중요!)
1. 강렬한 hook으로 시작
2. 각 dialogue는 반드시 12자 이내! (빠른 전환에 맞게 짧게)
3. 한국어 구어체 (반말+존댓말 믹스)
4. 핵심만 간결하게
5. CTA: "온카스터디 검색!"

## 이미지 키워드 규칙 (중요!)
- keyword는 "${topic}" 주제와 직접 관련된 구체적인 영어 단어
- 너무 추상적인 키워드 금지 (예: "background", "abstract" 금지)
- 주제의 핵심 사물/행동을 직접 묘사하는 키워드 사용
- 예: 먹튀 주제 → "scam warning sign", "money fraud", "online security"
- 예: 스포츠 주제 → "football stadium", "basketball game", "sports betting"
- image_prompt도 주제와 직접 관련된 구체적 장면 묘사

## 출력 (순수 JSON, 코드블록 없이)
{
  "hook_title": "훅 제목 (12자 이내, <y>강조</y>)",
  "scenes": [
    {
      "dialogue": "나레이션 (12자 이내!)",
      "image_prompt": "영어 이미지 프롬프트 (meme이면 빈 문자열)",
      "keyword": "구체적 영어 키워드 (meme이면 빈 문자열)",
      "visual_type": "image 또는 meme",
      "meme_mood": "meme인 경우만 감정"
    }
  ],
  "Subject": "영상 제목 #온카스터디 #먹튀검증 + 해시태그",
  "Caption": "영상 설명 #온카스터디 + 해시태그",
  "Comment": "구글에 온카스터디 검색!"
}

주의:
- scenes 8~10개
- 각 dialogue 12자 이내 필수!
- visual_type, keyword 필수
- 주제와 무관한 내용 금지`;

return [{
  json: {
    prompt,
    topic,
    row_number: $input.first().json.row_number,
    ...$input.first().json
  }
}];'''

idx = node_map.get("프롬프트 생성")
if idx is not None:
    nodes[idx]["parameters"]["jsCode"] = PROMPT_CODE
    print("  ✓ 25~30초, 12자 이내, 빠른 전환")

# ========================================
# 수정 2: TTS (목소리 + 속도)
# ========================================
print("3. TTS 요청 수정...")
idx = node_map.get("TTS 요청")
if idx is not None:
    nodes[idx]["parameters"]["jsonBody"] = '={\n  "text": {{ JSON.stringify($json.dialogue) }},\n  "voice": "ko-KR-HyunsuNeural",\n  "rate": "+15%"\n}'
    print("  ✓ HyunsuNeural, rate +15%")

# ========================================
# 수정 3: 이미지 검색 (per_page=3)
# ========================================
print("4. 이미지 검색 수정...")
idx = node_map.get("이미지 검색")
if idx is not None:
    nodes[idx]["parameters"]["url"] = "=https://api.pexels.com/v1/search?query={{ encodeURIComponent($json.keyword || $json.image_prompt?.split(',')[0] || 'abstract background') }}&per_page=3&orientation=portrait"
    print("  ✓ per_page=3")

# ========================================
# 수정 4: 이미지 URL 추출 (랜덤 선택)
# ========================================
print("5. 이미지 URL 추출 수정...")

IMG_EXTRACT_CODE = r'''// 밈 카탈로그: MinIO에 호스팅된 밈/리액션 영상 URL
const MEME_CATALOG = {
  thinking: [
    'http://76.13.182.180:9000/memes/thinking/meme_thinking_01.mp4',
    'http://76.13.182.180:9000/memes/thinking/meme_thinking_02.mp4',
    'http://76.13.182.180:9000/memes/thinking/meme_thinking_03.mp4',
  ],
  excited: [
    'http://76.13.182.180:9000/memes/excited/meme_excited_01.mp4',
    'http://76.13.182.180:9000/memes/excited/meme_excited_02.mp4',
    'http://76.13.182.180:9000/memes/excited/meme_excited_03.mp4',
  ],
  shocked: [
    'http://76.13.182.180:9000/memes/shocked/meme_shocked_01.mp4',
    'http://76.13.182.180:9000/memes/shocked/meme_shocked_02.mp4',
    'http://76.13.182.180:9000/memes/shocked/meme_shocked_03.mp4',
  ],
  sad: [
    'http://76.13.182.180:9000/memes/sad/meme_sad_01.mp4',
    'http://76.13.182.180:9000/memes/sad/meme_sad_02.mp4',
    'http://76.13.182.180:9000/memes/sad/meme_sad_03.mp4',
  ],
  angry: [
    'http://76.13.182.180:9000/memes/angry/meme_angry_01.mp4',
    'http://76.13.182.180:9000/memes/angry/meme_angry_02.mp4',
    'http://76.13.182.180:9000/memes/angry/meme_angry_03.mp4',
  ],
  cool: [
    'http://76.13.182.180:9000/memes/cool/meme_cool_01.mp4',
    'http://76.13.182.180:9000/memes/cool/meme_cool_02.mp4',
    'http://76.13.182.180:9000/memes/cool/meme_cool_03.mp4',
  ],
  celebrating: [
    'http://76.13.182.180:9000/memes/celebrating/meme_celebrating_01.mp4',
    'http://76.13.182.180:9000/memes/celebrating/meme_celebrating_02.mp4',
    'http://76.13.182.180:9000/memes/celebrating/meme_celebrating_03.mp4',
  ],
};

const items = $input.all();
const segAll = $('세그먼트 분리').all();

return items.map((item, i) => {
  const data = item.json;
  const segData = segAll[i]?.json || {};
  const visualType = segData.visual_type || data.visual_type || 'image';
  const memeMood = segData.meme_mood || data.meme_mood || 'thinking';

  if (visualType === 'meme') {
    const catalog = MEME_CATALOG[memeMood] || MEME_CATALOG.thinking;
    const randomIdx = Math.floor(Math.random() * catalog.length);
    const memeUrl = catalog[randomIdx];
    return {
      json: {
        ...data,
        visual_type: 'meme',
        meme_mood: memeMood,
        images: [{ url: memeUrl }],
        is_video: true,
      }
    };
  } else {
    const photos = data.photos || [];
    let imageUrl = '';
    if (photos.length > 0) {
      const randPhoto = photos[Math.floor(Math.random() * photos.length)];
      imageUrl = randPhoto.src?.portrait || randPhoto.src?.large || randPhoto.src?.medium || '';
    }
    if (!imageUrl) {
      imageUrl = 'https://images.pexels.com/photos/1229861/pexels-photo-1229861.jpeg?auto=compress&cs=tinysrgb&w=1080';
    }
    return {
      json: {
        ...data,
        visual_type: 'image',
        meme_mood: '',
        images: [{ url: imageUrl }],
        is_video: false,
      }
    };
  }
});'''

idx = node_map.get("이미지 URL 추출")
if idx is not None:
    nodes[idx]["parameters"]["jsCode"] = IMG_EXTRACT_CODE
    print("  ✓ 랜덤 사진 선택")

# ========================================
# 수정 5: NCA 데이터 준비 (핵심)
# ========================================
print("6. NCA 데이터 준비 수정...")

NCA_CODE = r'''// NCA 꿀팁 숏츠: 이미지 + 밈 영상 혼합 합성 페이로드
const hookTitle = $('콘텐츠 파싱').first().json.hook_title;
const segmentCount = $('콘텐츠 파싱').first().json.segmentCount;

const hookClean = hookTitle.replace(/<y>/g, '').replace(/<\/y>/g, '');

function escapeDrawtext(text) {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/'/g, '\u2019')
    .replace(/%/g, '%%')
    .replace(/"/g, '\u201D')
    .replace(/:/g, '\\:');
}

// 자막 줄바꿈: 14자마다 줄바꿈
function wrapSubtitle(text, maxLen) {
  if (text.length <= maxLen) return text;
  let lines = [];
  let current = '';
  for (const ch of text) {
    current += ch;
    if (current.length >= maxLen) {
      lines.push(current);
      current = '';
    }
  }
  if (current) lines.push(current);
  return lines.join('\n');
}

let segments = [];
let currentStart = 0;

for (let i = 0; i < segmentCount; i++) {
  const ttsResult = $('TTS 결과 처리').all()[i]?.json;
  const audioUrl = ttsResult?.audio_url || '';
  const duration = ttsResult?.duration_sec || 3;

  const imageResult = $('이미지 URL 추출').all()[i]?.json;
  const imageUrl = imageResult?.images?.[0]?.url || '';
  const isVideo = imageResult?.is_video || false;
  const visualType = imageResult?.visual_type || 'image';

  const dialogueText = $('세그먼트 분리').all()[i]?.json?.dialogue || '';

  if (!imageUrl) {
    throw new Error(`세그먼트 ${i+1} 미디어 URL 없음`);
  }

  segments.push({
    index: i + 1,
    imageUrl, audioUrl, duration,
    start: currentStart,
    dialogueText,
    isVideo,
    visualType,
  });
  currentStart += duration;
}

const totalDuration = currentStart;

let inputs = [];
let inputIndex = 0;

const mediaInputs = [];
for (const seg of segments) {
  if (seg.isVideo) {
    // 밈 영상: -stream_loop -1 로 무한 루프 (짧은 밈도 duration만큼 재생)
    inputs.push({
      file_url: seg.imageUrl,
      options: [
        { option: "-stream_loop", argument: "-1" }
      ]
    });
  } else {
    inputs.push({
      file_url: seg.imageUrl,
      options: [
        { option: "-loop", argument: "1" },
        { option: "-framerate", argument: "30" },
        { option: "-t", argument: String(seg.duration) }
      ]
    });
  }
  mediaInputs.push({ idx: inputIndex, isVideo: seg.isVideo, duration: seg.duration });
  inputIndex++;
}

// 오디오 입력
const audioInputs = [];
const audioSegmentMap = [];
for (let i = 0; i < segments.length; i++) {
  if (segments[i].audioUrl) {
    inputs.push({ file_url: segments[i].audioUrl, options: [] });
    audioInputs.push(inputIndex);
    audioSegmentMap.push(i);
    inputIndex++;
  }
}

let filterParts = [];

for (let i = 0; i < segments.length; i++) {
  const m = mediaInputs[i];
  if (m.isVideo) {
    filterParts.push(
      `[${m.idx}:v]trim=duration=${m.duration},setpts=PTS-STARTPTS,` +
      `scale=1080:1920:force_original_aspect_ratio=decrease,` +
      `pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,` +
      `setsar=1,fps=30[v${i}]`
    );
  } else {
    filterParts.push(
      `[${m.idx}:v]scale=1080:1920:force_original_aspect_ratio=decrease,` +
      `pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,` +
      `setsar=1,fps=30[v${i}]`
    );
  }
}

// 비디오 concat
const vLabels = segments.map((_, i) => `[v${i}]`).join('');
filterParts.push(`${vLabels}concat=n=${segments.length}:v=1:a=0[vconcat]`);

// 오디오 필터
if (audioInputs.length > 0) {
  for (let i = 0; i < audioInputs.length; i++) {
    const aIdx = audioInputs[i];
    const segIdx = audioSegmentMap[i];
    filterParts.push(
      `[${aIdx}:a]atrim=duration=${segments[segIdx].duration},asetpts=PTS-STARTPTS[a${i}]`
    );
  }
  const aLabels = audioInputs.map((_, i) => `[a${i}]`).join('');
  filterParts.push(`${aLabels}concat=n=${audioInputs.length}:v=0:a=1[aconcat]`);
}

// 상단 제목: 검은 배경 (불투명), 큰 글씨
const escapedTitle = escapeDrawtext(hookClean);

let overlayFilter = `[vconcat]drawbox=y=40:w=1080:h=280:color=#000000@1.0:t=fill,` +
  `drawtext=text='${escapedTitle}':fontsize=72:fontcolor=white:` +
  `fontfile=/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf:` +
  `x=(w-tw)/2:y=120:line_spacing=12`;

// 하단 자막: 줄바꿈 적용, 빠른 전환에 동기화
for (const seg of segments) {
  const wrapped = wrapSubtitle(seg.dialogueText, 14);
  const subText = escapeDrawtext(wrapped);
  const startT = seg.start.toFixed(2);
  const endT = (seg.start + seg.duration).toFixed(2);
  overlayFilter += `,drawtext=text='${subText}':fontsize=48:fontcolor=#CCFF00:` +
    `fontfile=/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf:` +
    `x=(w-tw)/2:y=h-250:borderw=3:bordercolor=black:` +
    `enable='between(t,${startT},${endT})'`;
}
overlayFilter += '[vfinal]';
filterParts.push(overlayFilter);

const filter_complex = filterParts.join(';');

const nca_payload = {
  inputs: inputs,
  filters: [{ filter: filter_complex }],
  outputs: [{
    options: [
      { option: "-map", argument: "[vfinal]" },
      { option: "-map", argument: "[aconcat]" },
      { option: "-c:v", argument: "libx264" },
      { option: "-preset", argument: "fast" },
      { option: "-crf", argument: "23" },
      { option: "-c:a", argument: "aac" },
      { option: "-b:a", argument: "192k" },
      { option: "-pix_fmt", argument: "yuv420p" },
      { option: "-movflags", argument: "+faststart" },
      { option: "-t", argument: String(totalDuration) }
    ],
    file_name: "kkultip_shorts_final.mp4"
  }]
};

return [{
  json: {
    nca_payload,
    totalDuration,
    segmentCount: segments.length,
    hookTitle,
    subject: $('콘텐츠 파싱').first().json.Subject,
    caption: $('콘텐츠 파싱').first().json.Caption,
    comment: $('콘텐츠 파싱').first().json.Comment,
  }
}];'''

idx = node_map.get("NCA 데이터 준비")
if idx is not None:
    nodes[idx]["parameters"]["jsCode"] = NCA_CODE
    print("  ✓ 검은배경, fontsize=72, 줄바꿈, 밈루프")

# ========================================
# JSON 저장
# ========================================
print("\n7. 수정된 JSON 저장...")
# ID 제거 (새로 생성 시 n8n이 부여)
wf_clean = {
    "name": wf["name"],
    "nodes": nodes,
    "connections": wf["connections"],
    "settings": wf.get("settings", {}),
}

# 로컬 파일도 업데이트
wf_local = dict(wf)
wf_local["nodes"] = nodes
with open(WF_PATH, 'w', encoding='utf-8') as f:
    json.dump(wf_local, f, ensure_ascii=False, indent=2)
print(f"  ✓ {WF_PATH} 저장")

# ========================================
# n8n에 업로드 (POST = 새로 생성)
# ========================================
print("\n8. n8n에 새 워크플로우 생성...")
result = api_request("POST", "/workflows", wf_clean)

if result and result.get("id"):
    new_id = result["id"]
    print(f"\n✅ 워크플로우 생성 성공!")
    print(f"   새 ID: {new_id}")
    print(f"   이름: {result['name']}")
    print(f"   노드 수: {len(result['nodes'])}")

    # 로컬 JSON에 새 ID 반영
    wf_local["id"] = new_id
    with open(WF_PATH, 'w', encoding='utf-8') as f:
        json.dump(wf_local, f, ensure_ascii=False, indent=2)
    print(f"   로컬 JSON에 새 ID 반영 완료")

    # 활성화
    print("\n9. 워크플로우 활성화...")
    activate = api_request("PATCH", f"/workflows/{new_id}", {"active": True})
    if activate and activate.get("active"):
        print("   ✅ 활성화 완료")
    else:
        print("   ⚠️ 활성화 실패 (수동 실행은 가능)")
else:
    print(f"\n❌ 생성 실패!")
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
