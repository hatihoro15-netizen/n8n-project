"""
꿀팁 숏츠 + 밈 영상 혼합 워크플로우 개편 스크립트

수정 대상 노드 (5개 + minor 1개):
1. 프롬프트 생성 - 꿀팁 스타일 + visual_type/meme_mood 출력
2. 콘텐츠 파싱 - visual_type, meme_mood 검증/기본값
3. 세그먼트 분리 - visual_type, meme_mood 패스스루
4. 이미지 URL 추출 - meme→카탈로그 URL / image→Pexels
5. NCA 데이터 준비 - 이미지 vs 영상 FFmpeg 분기
+ 이미지 검색 - fallback 키워드 추가 (minor)
"""
import json
import subprocess
import copy

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
WORKFLOW_ID = "dEtWqwWQPJfwCWiIM0QYd"


import tempfile
import os


def api_request(method, url, data=None):
    """n8n API 요청 공통 함수 - 대용량 데이터는 파일로 전송"""
    cmd = ["curl", "-sk", "-X", method,
           "-H", f"X-N8N-API-KEY: {API_KEY}",
           "-H", "Content-Type: application/json"]

    tmp_file = None
    if data:
        # 대용량 JSON은 파일로 저장 후 @file로 전송
        tmp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False, encoding='utf-8'
        )
        json.dump(data, tmp_file, ensure_ascii=False)
        tmp_file.close()
        cmd += ["-d", f"@{tmp_file.name}"]

    cmd.append(url)

    result = subprocess.run(cmd, capture_output=True, text=True)

    # 임시 파일 정리
    if tmp_file:
        os.unlink(tmp_file.name)

    if result.returncode != 0:
        print(f"[ERROR] curl 실패: {result.stderr[:300]}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"[ERROR] JSON 파싱 실패: {result.stdout[:500]}")
        return None


# ============================================================
# 노드 1: 프롬프트 생성 - 꿀팁 스타일 + visual_type/meme_mood
# ============================================================
PROMPT_CODE = r"""const topic = $input.first().json.topic || $input.first().json['주제'] || '';

if (!topic) {
  throw new Error('topic이 비어있습니다. 시트에 topic 컬럼을 확인하세요.');
}

const prompt = `너는 '온카스터디' 커뮤니티의 YouTube Shorts 꿀팁 콘텐츠 기획자야.
아래 주제로 45~60초 분량의 꿀팁 나레이션 숏츠 스크립트를 작성해줘.

## 반드시 지킬 주제
${topic}

위 주제를 중심으로 콘텐츠를 작성하되, 후반부에 '온카스터디'를 자연스럽게 1~2회 언급해 (광고 티 없이).
모든 scene의 dialogue는 반드시 "${topic}" 주제와 직접 관련된 내용이어야 해.
주제와 무관한 내용(요리, 패션, 여행 등)은 절대 포함하지 마.

## 온카스터디 소개
온카스터디는 먹튀검증 및 안전 정보 제공 커뮤니티입니다.
핵심 기능은 안전한 카지노 사이트를 고를 수 있도록 검증 정보를 공유하고, 먹튀 사이트를 구별하는 방법을 안내하는 것입니다.
커뮤니티 기능으로는 자유게시판, 제휴사이트 후기, 스포츠 분석 게시판, 방송존(동물원, 가디언, 인생역전, 하이라이트) 등이 있고,
포인트 시스템을 통해 복권, 돌림판, 오목, 무료슬롯 같은 활동도 가능하며, 포인트로 기프티콘 교환도 됩니다.

주제에 따라 온카스터디의 적절한 기능을 자연스럽게 연결해:
- 먹튀/안전 관련 주제 → 검증 정보, 안전 사이트 추천
- 스포츠 관련 주제 → 스포츠 분석 게시판
- 커뮤니티/재미 관련 주제 → 포인트 시스템, 미니게임, 방송존
- 일반 정보 주제 → 자유게시판, 커뮤니티 활동

## 영상 스타일 (꿀팁 숏츠 + 밈 혼합)
- 총 45~60초, 9:16 세로 영상
- 상단: 고정된 훅 제목 (핵심 키워드 1~2개는 <y>태그</y>로 감싸기)
- 중간: 정보 이미지 + 밈/리액션 영상 번갈아 배치
- 하단: 나레이션 자막
- 오디오: TTS 나레이션

## 장면 구성 규칙 (핵심!)
- 총 8~12개 장면
- 각 장면에 visual_type을 지정: "image" 또는 "meme"
- image: 주제 관련 정보 이미지 (Pexels에서 검색)
- meme: 밈/리액션 영상 (감정 표현용)
- 장면의 30~40%를 meme으로 지정
- 매 2~3개 image 뒤에 1개 meme 배치 (리듬감)
- meme 장면에는 meme_mood를 지정: thinking, excited, shocked, sad, angry, cool, celebrating 중 택1
- meme 장면의 dialogue는 감정 반응이나 리액션 문장 (예: "이거 실화냐?!", "대박...", "진짜 개꿀팁이다")

## 나레이션 규칙
1. 시청자를 끌어당기는 강렬한 hook으로 시작 (질문 or 충격적 사실)
2. "${topic}" 주제의 핵심 정보를 간결하게 전달
3. 자연스러운 한국어 구어체 (반말+존댓말 믹스, "~거든요", "~잖아요")
4. 후반부에 온카스터디를 해결책으로 자연스럽게 언급
5. CTA로 마무리 ("온카스터디 검색해보세요", "링크 확인" 등)
6. 각 장면은 3~6초 분량 (한 문장, 짧고 임팩트 있게)

## 이미지 프롬프트 규칙 (visual_type이 "image"인 경우만)
- 영어로 작성
- "${topic}" 주제와 직접 관련된 시각적 장면 묘사
- 항상 포함: "photorealistic, cinematic lighting, 4k quality, portrait orientation 9:16"
- 감정/분위기를 강조 (worried, excited, shocked, confident 등)
- visual_type이 "meme"인 경우 image_prompt는 빈 문자열

## 출력 (순수 JSON, 코드블록 없이)
{
  "hook_title": "훅 제목 (15자 이내, 핵심 키워드 <y>태그</y>)",
  "scenes": [
    {
      "dialogue": "나레이션 텍스트 (한 문장)",
      "image_prompt": "영어 이미지 프롬프트 (meme이면 빈 문자열)",
      "keyword": "Pexels 검색용 영어 키워드 (meme이면 빈 문자열)",
      "visual_type": "image 또는 meme",
      "meme_mood": "meme인 경우만: thinking/excited/shocked/sad/angry/cool/celebrating"
    }
  ],
  "Subject": "영상 제목 #온카스터디 #먹튀검증 + 주제관련 해시태그",
  "Caption": "영상 설명 #온카스터디 #먹튀검증 + 주제관련 해시태그",
  "Comment": "구글에 온카스터디 검색!"
}

주의:
- scenes는 8~12개
- visual_type 필수: "image" 또는 "meme"
- meme인 장면은 meme_mood 필수
- image인 장면은 image_prompt, keyword 필수
- 반드시 위 JSON 형식 그대로 출력
- "${topic}" 주제와 무관한 내용 절대 금지`;

return [{
  json: {
    prompt,
    topic,
    row_number: $input.first().json.row_number,
    ...$input.first().json
  }
}];"""


# ============================================================
# 노드 2: 콘텐츠 파싱 - visual_type, meme_mood 검증/기본값
# ============================================================
CONTENT_PARSE_CODE = r"""const raw = $input.first().json;
let text = '';
if (raw.content && raw.content.parts) {
  text = raw.content.parts[0].text;
} else if (typeof raw === 'string') {
  text = raw;
} else if (raw.text) {
  text = raw.text;
} else {
  text = JSON.stringify(raw);
}

const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
const data = JSON.parse(cleanText);

if (!data.scenes || data.scenes.length < 5) {
  throw new Error('scenes must have at least 5 items, got: ' + (data.scenes?.length || 0));
}

// visual_type, meme_mood 검증 및 기본값 처리
const VALID_MOODS = ['thinking', 'excited', 'shocked', 'sad', 'angry', 'cool', 'celebrating'];

data.scenes = data.scenes.map((scene, idx) => {
  // visual_type이 없으면 위치 기반 기본값 (매 3번째 = meme)
  if (!scene.visual_type || !['image', 'meme'].includes(scene.visual_type)) {
    scene.visual_type = ((idx + 1) % 3 === 0) ? 'meme' : 'image';
  }

  // meme인데 meme_mood가 없으면 기본값
  if (scene.visual_type === 'meme') {
    if (!scene.meme_mood || !VALID_MOODS.includes(scene.meme_mood)) {
      scene.meme_mood = VALID_MOODS[idx % VALID_MOODS.length];
    }
    // meme 장면은 image_prompt/keyword 불필요
    scene.image_prompt = scene.image_prompt || '';
    scene.keyword = scene.keyword || '';
  } else {
    // image 장면은 meme_mood 불필요
    scene.meme_mood = '';
    // keyword fallback
    if (!scene.keyword) {
      scene.keyword = scene.image_prompt?.split(',')[0] || 'abstract background';
    }
  }

  return scene;
});

const memeCount = data.scenes.filter(s => s.visual_type === 'meme').length;
const imageCount = data.scenes.filter(s => s.visual_type === 'image').length;

return [{
  json: {
    hook_title: data.hook_title,
    scenes: data.scenes,
    Subject: data.Subject,
    Caption: data.Caption,
    Comment: data.Comment,
    fullDialogue: data.scenes.map(s => s.dialogue).join(' '),
    segmentCount: data.scenes.length,
    memeCount,
    imageCount,
    Status: '생성 중',
    generatedAt: new Date().toISOString(),
    row_number: $('주제 선택').first().json.row_number
  }
}];"""


# ============================================================
# 노드 3: 세그먼트 분리 - visual_type, meme_mood 패스스루
# ============================================================
SEGMENT_SPLIT_CODE = r"""const data = $('콘텐츠 파싱').first().json;
const scenes = data.scenes || [];

return scenes.map((scene, i) => ({
  json: {
    index: i,
    dialogue: scene.dialogue,
    image_prompt: scene.image_prompt,
    keyword: scene.keyword || scene.image_prompt?.split(',')[0] || 'abstract background',
    visual_type: scene.visual_type || 'image',
    meme_mood: scene.meme_mood || '',
  }
}));"""


# ============================================================
# 노드 4: 이미지 URL 추출 - meme→카탈로그 URL / image→Pexels
# ============================================================
IMAGE_URL_CODE = r"""// 밈 카탈로그: MinIO에 호스팅된 밈/리액션 영상 URL
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

const data = $input.first().json;

// 세그먼트 분리에서 visual_type 참조
const segIdx = $input.first().json.index ?? data.index ?? 0;
const segData = $('세그먼트 분리').all()[segIdx]?.json || {};
const visualType = segData.visual_type || data.visual_type || 'image';
const memeMood = segData.meme_mood || data.meme_mood || 'thinking';

if (visualType === 'meme') {
  // 밈 → 카탈로그에서 랜덤 URL 선택
  const catalog = MEME_CATALOG[memeMood] || MEME_CATALOG.thinking;
  const randomIdx = Math.floor(Math.random() * catalog.length);
  const memeUrl = catalog[randomIdx];

  return [{
    json: {
      ...data,
      visual_type: 'meme',
      meme_mood: memeMood,
      images: [{ url: memeUrl }],
      is_video: true,
    }
  }];
} else {
  // 이미지 → 기존 Pexels 처리
  const photos = data.photos || [];
  let imageUrl = '';
  if (photos.length > 0) {
    imageUrl = photos[0].src?.portrait || photos[0].src?.large || photos[0].src?.medium || '';
  }

  if (!imageUrl) {
    imageUrl = 'https://images.pexels.com/photos/1229861/pexels-photo-1229861.jpeg?auto=compress&cs=tinysrgb&w=1080';
  }

  return [{
    json: {
      ...data,
      visual_type: 'image',
      meme_mood: '',
      images: [{ url: imageUrl }],
      is_video: false,
    }
  }];
}"""


# ============================================================
# 노드 5: NCA 데이터 준비 - 이미지 vs 영상 FFmpeg 분기
# ============================================================
NCA_DATA_CODE = r"""// NCA 꿀팁 숏츠: 이미지 + 밈 영상 혼합 합성 페이로드
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

let segments = [];
let currentStart = 0;

for (let i = 0; i < segmentCount; i++) {
  const ttsResult = $('TTS 결과 처리').all()[i]?.json;
  const audioUrl = ttsResult?.audio_url || '';
  const duration = ttsResult?.duration_sec || 4;

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

// 미디어 입력 (이미지 또는 영상)
const mediaInputs = [];
for (const seg of segments) {
  if (seg.isVideo) {
    // 밈 영상: 입력 옵션 없음 (직접 읽기)
    inputs.push({
      file_url: seg.imageUrl,
      options: []
    });
  } else {
    // 정지 이미지: loop + framerate + duration
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

// 비디오 필터: 이미지 vs 영상 분기
for (let i = 0; i < segments.length; i++) {
  const m = mediaInputs[i];
  if (m.isVideo) {
    // 밈 영상: trim → scale → pad
    filterParts.push(
      `[${m.idx}:v]trim=duration=${m.duration},setpts=PTS-STARTPTS,` +
      `scale=1080:1920:force_original_aspect_ratio=decrease,` +
      `pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,` +
      `setsar=1,fps=30[v${i}]`
    );
  } else {
    // 정지 이미지: scale → pad
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

// 자막 오버레이
const escapedTitle = escapeDrawtext(hookClean);

let overlayFilter = `[vconcat]drawbox=y=40:w=1080:h=260:color=#333333@0.80:t=fill,` +
  `drawtext=text='${escapedTitle}':fontsize=54:fontcolor=white:` +
  `fontfile=/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf:` +
  `x=(w-tw)/2:y=110:line_spacing=12`;

for (const seg of segments) {
  const subText = escapeDrawtext(seg.dialogueText);
  const startT = seg.start.toFixed(2);
  const endT = (seg.start + seg.duration).toFixed(2);
  overlayFilter += `,drawtext=text='${subText}':fontsize=44:fontcolor=#CCFF00:` +
    `fontfile=/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf:` +
    `x=(w-tw)/2:y=h-200:borderw=3:bordercolor=black:` +
    `enable='between(t\\\\,${startT}\\\\,${endT})'`;
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
}];"""


# ============================================================
# 이미지 검색 URL 수정 (fallback 키워드 추가)
# ============================================================
# 기존 URL에 fallback 파라미터 추가
IMAGE_SEARCH_URL = (
    "=https://api.pexels.com/v1/search?"
    "query={{ encodeURIComponent($json.keyword || $json.image_prompt?.split(',')[0] || 'abstract background') }}"
    "&per_page=1&orientation=portrait"
)


def main():
    """워크플로우 노드 수정 실행"""
    print("=" * 60)
    print("꿀팁 숏츠 + 밈 영상 혼합 워크플로우 개편")
    print("=" * 60)

    # Step 1: 워크플로우 가져오기
    print("\n--- Step 1: 워크플로우 조회 ---")
    wf = api_request("GET", f"{BASE}/workflows/{WORKFLOW_ID}")
    if not wf:
        print("[ERROR] 워크플로우 조회 실패")
        return False

    print(f"  이름: {wf.get('name')}")
    print(f"  노드 수: {len(wf.get('nodes', []))}")

    # Step 2: 노드 수정
    print("\n--- Step 2: 노드 수정 ---")
    nodes = copy.deepcopy(wf["nodes"])
    modified_count = 0

    for node in nodes:
        name = node.get("name", "")

        if name == "프롬프트 생성":
            node["parameters"]["jsCode"] = PROMPT_CODE
            print(f"  [수정] 프롬프트 생성: 꿀팁 스타일 + visual_type/meme_mood")
            modified_count += 1

        elif name == "콘텐츠 파싱":
            node["parameters"]["jsCode"] = CONTENT_PARSE_CODE
            print(f"  [수정] 콘텐츠 파싱: visual_type/meme_mood 검증/기본값")
            modified_count += 1

        elif name == "세그먼트 분리":
            node["parameters"]["jsCode"] = SEGMENT_SPLIT_CODE
            print(f"  [수정] 세그먼트 분리: visual_type/meme_mood 패스스루")
            modified_count += 1

        elif name == "이미지 URL 추출":
            node["parameters"]["jsCode"] = IMAGE_URL_CODE
            print(f"  [수정] 이미지 URL 추출: meme→카탈로그 / image→Pexels 분기")
            modified_count += 1

        elif name == "NCA 데이터 준비":
            node["parameters"]["jsCode"] = NCA_DATA_CODE
            print(f"  [수정] NCA 데이터 준비: 이미지 vs 영상 FFmpeg 분기")
            modified_count += 1

        elif name == "이미지 검색":
            node["parameters"]["url"] = IMAGE_SEARCH_URL
            print(f"  [수정] 이미지 검색: fallback 키워드 추가")
            modified_count += 1

    print(f"\n  총 {modified_count}개 노드 수정")

    if modified_count < 5:
        print(f"  [WARN] 최소 5개 예상인데 {modified_count}개만 수정됨")

    # Step 3: pinData 정리 (이전 버전 고정 데이터 제거)
    print("\n--- Step 3: pinData 정리 ---")
    pin_data = wf.get("pinData", {})
    if pin_data:
        print(f"  기존 pinData 키: {list(pin_data.keys())}")
        pin_data = {}  # 전부 제거 (새 구조와 호환 안 됨)
        print("  pinData 전부 제거 (새 구조 호환)")

    # Step 4: API PUT으로 업데이트 (파일 기반)
    print("\n--- Step 4: 워크플로우 업데이트 ---")
    update_data = {
        "name": wf.get("name", "설명형 숏츠 - 온카스터디"),
        "nodes": nodes,
        "connections": wf["connections"],
        "settings": wf.get("settings", {"executionOrder": "v1"}),
    }

    # 파일로 저장 후 curl @file로 전송
    update_file = "/tmp/wf_kkultip_update.json"
    with open(update_file, "w", encoding="utf-8") as f:
        json.dump(update_data, f, ensure_ascii=False)

    file_size = os.path.getsize(update_file)
    print(f"  JSON 파일 크기: {file_size:,} bytes")

    put_result = subprocess.run(
        ["curl", "-sk", "-X", "PUT",
         f"{BASE}/workflows/{WORKFLOW_ID}",
         "-H", f"X-N8N-API-KEY: {API_KEY}",
         "-H", "Content-Type: application/json",
         "-d", f"@{update_file}"],
        capture_output=True, text=True
    )

    os.unlink(update_file)

    if put_result.returncode != 0:
        print(f"[ERROR] curl 실패: {put_result.stderr[:300]}")
        return False

    try:
        result = json.loads(put_result.stdout)
        print(f"  업데이트 성공: {result.get('name')}")
        print(f"  버전: {result.get('versionId', 'N/A')}")
    except json.JSONDecodeError:
        print(f"  응답 길이: {len(put_result.stdout)}")
        if len(put_result.stdout) > 100:
            print("  (응답 있음 - 성공으로 판단)")
        else:
            print(f"[ERROR] 응답: {put_result.stdout[:500]}")
            return False

    # Step 5: 검증
    print("\n--- Step 5: 검증 ---")
    verify_result = subprocess.run(
        ["curl", "-sk",
         f"{BASE}/workflows/{WORKFLOW_ID}",
         "-H", f"X-N8N-API-KEY: {API_KEY}"],
        capture_output=True, text=True
    )
    verify_wf = json.loads(verify_result.stdout)
    target_nodes = ["프롬프트 생성", "콘텐츠 파싱", "세그먼트 분리", "이미지 URL 추출", "NCA 데이터 준비"]
    all_ok = True
    for node in verify_wf.get("nodes", []):
        name = node.get("name", "")
        if name in target_nodes:
            code = node.get("parameters", {}).get("jsCode", "")
            has_visual_type = "visual_type" in code
            print(f"  [{name}] visual_type 포함: {has_visual_type}")
            if not has_visual_type:
                all_ok = False

    if not all_ok:
        print("  [WARN] 일부 노드에 visual_type 없음!")

    print("\n" + "=" * 60)
    print("완료! 워크플로우 수동 실행으로 테스트하세요.")
    print(f"  워크플로우 ID: {WORKFLOW_ID}")
    print("=" * 60)
    return True


if __name__ == "__main__":
    main()
