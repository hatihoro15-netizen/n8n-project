#!/usr/bin/env python3
"""
루믹스 숏폼 v3 워크플로우 - 8개 수정사항 일괄 적용
1. 폰트 변경 (Noto Sans KR Bold)
2. 폰트 사이즈 변경 (96)
3. Ken Burns 효과 (전체 장면, 분할 제거)
4. 단어 반복 방지 (AI 프롬프트)
5. 풀버전 자막 (나레이션 = 자막)
6. (5번과 통합)
7. 줄별 슬라이드업 애니메이션
8. 크로스페이드 장면 전환
+ BGM refinement 60으로 변경
+ 폰트 파일 로딩 방식 수정 (fontsdir=/tmp + -f data)
"""
import json
import requests
import copy

N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"
HEADERS = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}

# ============================================================
# 1. Fetch workflow
# ============================================================
print("1. Fetching workflow...")
resp = requests.get(f"{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}", headers=HEADERS)
resp.raise_for_status()
wf = resp.json()
print(f"   Workflow: {wf['name']}, Nodes: {len(wf['nodes'])}")

# ============================================================
# Helper: find node by name
# ============================================================
def find_node(name_part):
    for node in wf['nodes']:
        if name_part in node.get('name', ''):
            return node
    return None

# ============================================================
# 2. NCA 데이터 준비 - items 3,5,8 (Ken Burns, full subtitle, crossfade)
# ============================================================
print("2. Updating NCA 데이터 준비...")
node = find_node('NCA 데이터 준비')
assert node, "NCA 데이터 준비 node not found!"

NCA_DATA_PREP_CODE = r'''// NCA 영상 제작 - Ken Burns 전체 + 크로스페이드 + 풀 자막
const firstItem = $input.first().json;
const dataArray = firstItem.data || [];

const narrations = [];
const videos = [];
let bgmUrl = '';

for (const item of dataArray) {
    if (item.video && item.video.url) {
        videos.push(item.video.url);
    } else if (item.audio && item.audio.url) {
        if (item.metadata && item.metadata.duration) {
            bgmUrl = item.audio.url;
        } else {
            let duration = 0;
            if (item.audio.duration && typeof item.audio.duration === 'number' && item.audio.duration > 0) {
                duration = item.audio.duration;
            } else if (item.audio.duration && typeof item.audio.duration === 'string') {
                duration = parseFloat(item.audio.duration) || 0;
            }
            if (duration <= 0) {
                const fileSize = item.audio.file_size || 0;
                duration = Math.max(Math.round((fileSize * 8 / 128000) * 100) / 100, 3);
            }
            narrations.push({ url: item.audio.url, duration: duration });
        }
    }
}

// 자막 텍스트 가져오기
let subtitleTexts = [];
let fullNarrationTexts = [];
try {
    const partItems = $('5파트 분리').all();
    subtitleTexts = partItems.map(item => item.json.subtitle || item.json.text || '');
    fullNarrationTexts = partItems.map(item => item.json.text || '');
} catch (e) {
    console.log('Could not get subtitles:', e.message);
}

// 2줄 분리 헬퍼
function splitToTwoLines(text) {
    if (!text || text.length <= 16) return { full: text || '', line1: text || '', line2: '' };
    const mid = Math.floor(text.length / 2);
    let splitIdx = -1;
    for (let offset = 0; offset <= mid; offset++) {
        const fwd = mid + offset;
        const bwd = mid - offset;
        if (fwd < text.length && text[fwd] === ' ') { splitIdx = fwd; break; }
        if (bwd >= 0 && text[bwd] === ' ') { splitIdx = bwd; break; }
    }
    if (splitIdx === -1) return { full: text, line1: text, line2: '' };
    const l1 = text.substring(0, splitIdx).trim();
    const l2 = text.substring(splitIdx).trim();
    return { full: text, line1: l1, line2: l2 };
}

const partCount = Math.min(narrations.length, videos.length, 5);
const SCENE_DURATION = 5;
const MAX_SLOW_SECONDS = 6.5;
const OUTRO_URL = 'http://76.13.182.180:9000/nca-toolkit/assets/outro_lumix.mp4';
const OUTRO_DURATION = 5;
const XFADE_DUR = 0.5;

console.log('Parts:', partCount, 'Videos:', videos.length, 'Narrations:', narrations.length, 'BGM:', bgmUrl ? 'YES' : 'NO');

// === 세그먼트 구성 (분할 없이, 각 장면 유지) ===
const segments = [];
for (let i = 0; i < partCount; i++) {
    const dur = narrations[i].duration;
    const videoUrl = videos[i];
    const audioUrl = narrations[i].url;
    const fullText = fullNarrationTexts[i] || '';
    const sceneDur = Math.max(dur, SCENE_DURATION);

    segments.push({
        videoUrl, audioUrl,
        sceneDuration: sceneDur,
        audioDuration: dur,
        audioStart: 0,
        subtitleText: fullText,
        lines: splitToTwoLines(fullText),
        kbIndex: i,
        type: 'normal'
    });

    if (dur > MAX_SLOW_SECONDS) {
        console.log(`Part ${i+1}: dur=${dur.toFixed(1)}s, LOOP + Ken Burns`);
    } else {
        const slow = Math.max(1, dur / SCENE_DURATION);
        console.log(`Part ${i+1}: dur=${dur.toFixed(1)}s, slow=${slow.toFixed(2)}x + Ken Burns`);
    }
}

// === inputs 구성 ===
const inputs = [];
const segMeta = [];

for (const seg of segments) {
    const vIdx = inputs.length;
    inputs.push({ file_url: seg.videoUrl, options: [] });
    const aIdx = inputs.length;
    inputs.push({ file_url: seg.audioUrl, options: [] });
    segMeta.push({ vIdx, aIdx });
}

if (bgmUrl) {
    inputs.push({ file_url: bgmUrl, options: [{ option: "-stream_loop" }, { option: "-1" }] });
}
inputs.push({ file_url: OUTRO_URL, options: [] });
const outroIdx = inputs.length - 1;

// === filter_complex 구성 ===
let filters = [];
let subtitleData = [];
let currentTime = 0;

// Ken Burns 8가지 변형
function getKenBurnsEffect(index, dur) {
    const KB = 1.12;
    const kbW = Math.round(1080 * KB);
    const kbH = Math.round(1920 * KB);
    const dx = kbW - 1080;
    const dy = kbH - 1920;
    const dxH = Math.round(dx / 2);
    const dyH = Math.round(dy / 2);
    const d = dur.toFixed(2);
    const variants = [
        `scale=${kbW}:${kbH},crop=w=${kbW}-${dx}*t/${d}:h=${kbH}-${dy}*t/${d}:x=${dxH}*t/${d}:y=${dyH}*t/${d},scale=1080:1920`,
        `scale=${kbW}:${kbH},crop=w=1080+${dx}*t/${d}:h=1920+${dy}*t/${d}:x=${dxH}-${dxH}*t/${d}:y=${dyH}-${dyH}*t/${d},scale=1080:1920`,
        `scale=${kbW}:${kbH},crop=1080:1920:${dxH}*t/${d}:${dyH}*t/${d}`,
        `scale=${kbW}:${kbH},crop=1080:1920:${dx}-${dx}*t/${d}:${dy}-${dy}*t/${d}`,
        `scale=${kbW}:${kbH},crop=1080:1920:${dx}*t/${d}:${dyH}`,
        `scale=${kbW}:${kbH},crop=1080:1920:${dx}-${dx}*t/${d}:${dyH}`,
        `scale=${kbW}:${kbH},hflip,crop=w=${kbW}-${dx}*t/${d}:h=${kbH}-${dy}*t/${d}:x=${dxH}*t/${d}:y=${dyH}*t/${d},scale=1080:1920`,
        `scale=${kbW}:${kbH},hflip,crop=w=1080+${dx}*t/${d}:h=1920+${dy}*t/${d}:x=${dxH}-${dxH}*t/${d}:y=${dyH}-${dyH}*t/${d},scale=1080:1920`,
    ];
    return variants[index % variants.length];
}

for (let i = 0; i < segments.length; i++) {
    const seg = segments[i];
    const { vIdx, aIdx } = segMeta[i];
    const dur = seg.sceneDuration;
    const slowFactor = Math.max(1, dur / SCENE_DURATION);
    const kbEffect = getKenBurnsEffect(seg.kbIndex, dur);

    // 비디오 필터 (모든 장면에 Ken Burns 적용)
    if (dur > MAX_SLOW_SECONDS) {
        // Loop + Ken Burns
        inputs[vIdx].options = [{ option: "-stream_loop" }, { option: "-1" }];
        filters.push(`[${vIdx}:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,trim=duration=${dur.toFixed(2)},setpts=PTS-STARTPTS,${kbEffect},setpts=PTS-STARTPTS,fps=24[v${i}]`);
    } else if (slowFactor > 1.01) {
        // Slow + Ken Burns
        filters.push(`[${vIdx}:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setpts=PTS*${slowFactor.toFixed(2)},tpad=stop_mode=clone:stop_duration=10,trim=duration=${dur.toFixed(2)},setpts=PTS-STARTPTS,${kbEffect},setpts=PTS-STARTPTS,fps=24[v${i}]`);
    } else {
        // Normal + Ken Burns
        filters.push(`[${vIdx}:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,${kbEffect},trim=duration=${dur.toFixed(2)},setpts=PTS-STARTPTS,fps=24[v${i}]`);
    }

    // 오디오 필터
    filters.push(`[${aIdx}:a]atrim=duration=${dur.toFixed(2)},apad=whole_dur=${dur.toFixed(2)},asetpts=PTS-STARTPTS[a${i}]`);

    // 자막 데이터 (크로스페이드 고려한 타이밍)
    subtitleData.push({
        text: seg.subtitleText,
        lines: seg.lines,
        start: currentTime,
        end: currentTime + dur - XFADE_DUR,
    });
    currentTime += dur - XFADE_DUR;
}

// 아웃트로
filters.push(`[${outroIdx}:v]scale=1080:2160,crop=1080:1920:0:0,trim=duration=${OUTRO_DURATION},setpts=PTS-STARTPTS,fps=24[voutro]`);
filters.push(`anullsrc=r=44100:cl=mono,atrim=duration=${OUTRO_DURATION}[aoutro]`);

// === 크로스페이드 (xfade + acrossfade) ===
const totalParts = segments.length + 1; // scenes + outro
const allDurations = segments.map(s => s.sceneDuration);
allDurations.push(OUTRO_DURATION);

// Video xfade chain
let prevVLabel = 'v0';
let xfadeOffset = allDurations[0] - XFADE_DUR;
for (let k = 1; k < totalParts; k++) {
    const nextVLabel = k < segments.length ? `v${k}` : 'voutro';
    const isLast = k === totalParts - 1;
    const outVLabel = isLast ? 'outv' : `xfv${k}`;
    filters.push(`[${prevVLabel}][${nextVLabel}]xfade=transition=fade:duration=${XFADE_DUR}:offset=${xfadeOffset.toFixed(2)}[${outVLabel}]`);
    prevVLabel = outVLabel;
    if (!isLast) xfadeOffset += allDurations[k] - XFADE_DUR;
}

// Audio acrossfade chain
let prevALabel = 'a0';
for (let k = 1; k < totalParts; k++) {
    const nextALabel = k < segments.length ? `a${k}` : 'aoutro';
    const isLast = k === totalParts - 1;
    const outALabel = isLast ? 'outa' : `xfa${k}`;
    filters.push(`[${prevALabel}][${nextALabel}]acrossfade=d=${XFADE_DUR}:c1=tri:c2=tri[${outALabel}]`);
    prevALabel = outALabel;
}

if (bgmUrl) {
    const bgmIdx = segments.length * 2;
    filters.push(`[${bgmIdx}:a]volume=0.10[bgm]`);
    filters.push(`[outa][bgm]amix=inputs=2:duration=first:dropout_transition=2[finala]`);
}

const filterComplex = filters.join('; ');
const audioMap = bgmUrl ? '[finala]' : '[outa]';

const outputOptions = [
    { option: "-filter_complex" }, { option: filterComplex },
    { option: "-map" }, { option: "[outv]" },
    { option: "-map" }, { option: audioMap },
    { option: "-c:v" }, { option: "libx264" },
    { option: "-preset" }, { option: "fast" },
    { option: "-crf" }, { option: "23" },
    { option: "-c:a" }, { option: "aac" },
    { option: "-b:a" }, { option: "192k" },
    { option: "-pix_fmt" }, { option: "yuv420p" },
    { option: "-movflags" }, { option: "+faststart" },
];

// 크로스페이드 적용 후 총 시간 = currentTime + OUTRO_DURATION (마지막 xfade에서 이미 빼진 상태)
const totalDuration = currentTime + OUTRO_DURATION;
console.log(`Total segments: ${segments.length}, Duration: ${totalDuration.toFixed(1)}s (incl ${OUTRO_DURATION}s outro)`);

return [{
    json: {
        nca_payload: {
            inputs: inputs,
            outputs: [{ options: outputOptions }],
            global_options: [],
        },
        subtitle_data: subtitleData,
        part_count: partCount,
        segment_count: segments.length,
        has_bgm: !!bgmUrl,
        total_duration: totalDuration,
    }
}];'''

node['parameters']['jsCode'] = NCA_DATA_PREP_CODE
print("   ✅ Ken Burns (all scenes) + no split + crossfade + full subtitle applied")

# ============================================================
# 3. NCA 제작 결과 - items 1,2,7 (font, size, line-by-line animation)
# ============================================================
print("3. Updating NCA 제작 결과...")
node = find_node('NCA 제작 결과')
assert node, "NCA 제작 결과 node not found!"

NCA_RESULT_CODE = r'''// NCA 제작 결과 + ASS 자막 (Noto Sans KR 96pt + 줄별 슬라이드업)
const result = $input.first().json;
const prevData = $('NCA 데이터 준비').first().json;

let videoUrl = '';
if (Array.isArray(result.response)) {
    videoUrl = result.response[0]?.file_url || '';
} else if (typeof result.response === 'string') {
    videoUrl = result.response;
} else {
    videoUrl = result.output_url || result.url || result.video_url || '';
}

console.log('Video URL:', videoUrl);
if (!videoUrl) {
    throw new Error('영상 제작 실패: ' + JSON.stringify(result).substring(0, 200));
}

const subtitleData = prevData.subtitle_data || [];

const RES_X = 1080;
const RES_Y = 1920;
const FONT_SIZE = 96;
const LINE_GAP = Math.round(FONT_SIZE * 1.3);
const LINE2_Y = RES_Y - 150;
const LINE1_Y = LINE2_Y - LINE_GAP;
const START_Y = RES_Y + 80;
const SLIDE_MS = 300;
const LINE_DELAY = 0.35;
const CENTER_X = Math.round(RES_X / 2);

let assContent = `[Script Info]
Title: Lumix Subtitle
ScriptType: v4.00+
WrapStyle: 0
PlayResX: ${RES_X}
PlayResY: ${RES_Y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans KR,${FONT_SIZE},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,4,1,2,40,40,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
`;

const fmt = (totalSec) => {
    const h = Math.floor(totalSec / 3600);
    const m = Math.floor((totalSec % 3600) / 60);
    const s = totalSec % 60;
    return `${h}:${String(m).padStart(2,'0')}:${s.toFixed(2).padStart(5,'0')}`;
};

for (const sub of subtitleData) {
    if (!sub.text && (!sub.lines || !sub.lines.line1)) continue;

    const lines = sub.lines || { line1: sub.text || '', line2: '' };
    const startTime = sub.start;
    const endTime = sub.end;

    if (lines.line2) {
        // 2줄: 각 줄 별도 Dialogue (줄별 슬라이드업)
        // Line 1: 즉시 슬라이드업
        const move1 = `{\\an5\\move(${CENTER_X},${START_Y},${CENTER_X},${LINE1_Y},0,${SLIDE_MS})\\fad(0,200)}`;
        assContent += `Dialogue: 0,${fmt(startTime)},${fmt(endTime)},Default,,0,0,0,,${move1}${lines.line1}\n`;

        // Line 2: LINE_DELAY초 후 슬라이드업
        const line2Start = startTime + LINE_DELAY;
        const move2 = `{\\an5\\move(${CENTER_X},${START_Y},${CENTER_X},${LINE2_Y},0,${SLIDE_MS})\\fad(0,200)}`;
        assContent += `Dialogue: 0,${fmt(line2Start)},${fmt(endTime)},Default,,0,0,0,,${move2}${lines.line2}\n`;
    } else {
        // 1줄: 단일 Dialogue
        const singleY = LINE2_Y;
        const move = `{\\an5\\move(${CENTER_X},${START_Y},${CENTER_X},${singleY},0,${SLIDE_MS})\\fad(0,200)}`;
        assContent += `Dialogue: 0,${fmt(startTime)},${fmt(endTime)},Default,,0,0,0,,${move}${lines.line1}\n`;
    }
}

console.log('ASS content length:', assContent.length);
console.log('Subtitle entries:', subtitleData.filter(s => s.text || (s.lines && s.lines.line1)).length);

const jobId = result.job_id || Date.now().toString();
const assFileName = `subtitles/sub_${jobId}.ass`;
const assUrl = `http://76.13.182.180:9000/nca-toolkit/${assFileName}`;

try {
    const uploadResp = await this.helpers.httpRequest({
        method: 'PUT',
        url: assUrl,
        headers: { 'Content-Type': 'text/plain; charset=utf-8' },
        body: assContent,
        returnFullResponse: true,
    });
    console.log('ASS upload status:', uploadResp.statusCode);
} catch (e) {
    console.log('ASS upload error:', e.message);
    throw new Error('ASS MinIO upload failed: ' + e.message);
}

return [{
    json: {
        video_url: videoUrl,
        ass_url: assUrl,
        has_subtitles: subtitleData.filter(s => s.text || (s.lines && s.lines.line1)).length > 0,
    }
}];'''

node['parameters']['jsCode'] = NCA_RESULT_CODE
print("   ✅ Noto Sans KR + 96pt + line-by-line slide-up animation applied")

# ============================================================
# 4. NCA 자막 추가 - font file + fontsdir
# ============================================================
print("4. Updating NCA 자막 추가...")
node = find_node('NCA 자막 추가')
assert node, "NCA 자막 추가 node not found!"

# New jsonBody with font file input and fontsdir
NCA_SUB_BODY = """={{ JSON.stringify({
  "inputs": [
    { "file_url": $json.video_url, "options": [] },
    { "file_url": "http://76.13.182.180:9000/nca-toolkit/fonts/NotoSansKR-Bold.ttf", "options": [{"option": "-f"}, {"option": "data"}] }
  ],
  "filters": [{ "filter": "ass='" + $json.ass_url + "':fontsdir=/tmp" }],
  "outputs": [{
    "options": [
      { "option": "-c:v" },
      { "option": "libx264" },
      { "option": "-preset" },
      { "option": "fast" },
      { "option": "-crf" },
      { "option": "23" },
      { "option": "-c:a" },
      { "option": "copy" },
      { "option": "-movflags" },
      { "option": "+faststart" }
    ]
  }],
  "global_options": []
}) }}"""

node['parameters']['jsonBody'] = NCA_SUB_BODY
print("   ✅ Font file (-f data) + fontsdir=/tmp applied")

# ============================================================
# 5. AI 주제 생성 - item 4 (word repetition prevention)
# ============================================================
print("5. Updating AI 주제 생성 prompts...")
WORD_REPEAT_RULE = "\n\n📌 단어 반복 금지: 5문장 내에서 동일한 핵심 단어(명사/동사 어근)를 2회 이상 사용하지 마세요. 동의어나 다른 표현으로 대체하세요."

for node in wf['nodes']:
    name = node.get('name', '')
    if 'AI 주제 생성' in name:
        params = node.get('parameters', {})
        # Check Gemini node types
        if 'text' in params:
            prompt_field = 'text'
        elif 'prompt' in params:
            prompt_field = 'prompt'
        elif 'modelParameters' in params and 'prompt' in params.get('modelParameters', {}):
            prompt_field = None  # nested
        else:
            # Check for message-based prompt
            prompt_field = None
            for key in params:
                if isinstance(params[key], str) and len(params[key]) > 100:
                    prompt_field = key
                    break

        if prompt_field and isinstance(params.get(prompt_field, ''), str):
            current_prompt = params[prompt_field]
            if '단어 반복 금지' not in current_prompt:
                params[prompt_field] = current_prompt + WORD_REPEAT_RULE
                print(f"   ✅ '{name}' - word repetition rule added")
            else:
                print(f"   ⏭️ '{name}' - already has word repetition rule")
        else:
            # Try resource/messages approach (n8n Gemini node)
            if 'messages' in params:
                messages = params['messages']
                if isinstance(messages, dict) and 'values' in messages:
                    for msg in messages['values']:
                        if 'content' in msg and isinstance(msg['content'], str):
                            if '단어 반복 금지' not in msg['content']:
                                msg['content'] += WORD_REPEAT_RULE
                                print(f"   ✅ '{name}' - word repetition rule added (messages)")
                            break
            # Also check promptType/text pattern
            if 'promptType' in params:
                for key in ['text', 'prompt', 'userMessage']:
                    if key in params and isinstance(params[key], str) and len(params[key]) > 50:
                        if '단어 반복 금지' not in params[key]:
                            params[key] += WORD_REPEAT_RULE
                            print(f"   ✅ '{name}' - word repetition rule added ({key})")
                        break

# ============================================================
# 6. BGM 생성 - refinement 100 → 60
# ============================================================
print("6. Updating BGM refinement...")
for node in wf['nodes']:
    name = node.get('name', '')
    if 'BGM' in name:
        params = node.get('parameters', {})
        # Check jsonBody for refinement
        if 'jsonBody' in params:
            body = params['jsonBody']
            if 'refinement' in body:
                old = body
                body = body.replace('"refinement": 100', '"refinement": 60')
                body = body.replace('"refinement":100', '"refinement": 60')
                if body != old:
                    params['jsonBody'] = body
                    print(f"   ✅ '{name}' - refinement 100 → 60")
                else:
                    print(f"   ⏭️ '{name}' - refinement already set or different format")
            else:
                print(f"   ℹ️ '{name}' - no refinement in jsonBody")
        elif 'body' in params:
            body = str(params['body'])
            if 'refinement' in body:
                print(f"   ℹ️ '{name}' - has refinement in body field")

# ============================================================
# 7. Upload workflow
# ============================================================
print("\n7. Preparing upload...")

# Deactivate first
deact_resp = requests.post(
    f"{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}/deactivate",
    headers=HEADERS
)
print(f"   Deactivate: {deact_resp.status_code}")

# Clean payload
payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData", None),
}

update_resp = requests.put(
    f"{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}",
    headers=HEADERS,
    json=payload
)
print(f"   Update: {update_resp.status_code}")
if update_resp.status_code != 200:
    print(f"   ERROR: {update_resp.text[:500]}")
else:
    print("   ✅ Workflow updated successfully!")

# Reactivate
act_resp = requests.post(
    f"{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}/activate",
    headers=HEADERS
)
print(f"   Activate: {act_resp.status_code}")

# ============================================================
# 8. Verify
# ============================================================
print("\n8. Verifying changes...")
verify_resp = requests.get(f"{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}", headers=HEADERS)
vwf = verify_resp.json()

checks = {
    "Font (Noto Sans KR)": False,
    "Font size (96)": False,
    "Ken Burns (all scenes)": False,
    "No SPLIT_SECONDS": True,
    "Crossfade (xfade)": False,
    "Full subtitle (fullText)": False,
    "Line-by-line animation": False,
    "fontsdir=/tmp": False,
    "Font file input": False,
}

for node in vwf['nodes']:
    name = node.get('name', '')
    params = node.get('parameters', {})

    if 'NCA 제작 결과' in name:
        code = params.get('jsCode', '')
        if 'Noto Sans KR' in code:
            checks["Font (Noto Sans KR)"] = True
        if 'FONT_SIZE = 96' in code:
            checks["Font size (96)"] = True
        if 'LINE_DELAY' in code and 'LINE_GAP' in code:
            checks["Line-by-line animation"] = True

    if 'NCA 데이터 준비' in name:
        code = params.get('jsCode', '')
        if 'getKenBurnsEffect' in code:
            checks["Ken Burns (all scenes)"] = True
        if 'SPLIT_SECONDS' in code:
            checks["No SPLIT_SECONDS"] = False
        if 'xfade' in code:
            checks["Crossfade (xfade)"] = True
        if 'fullNarrationTexts[i]' in code or 'fullText' in code:
            checks["Full subtitle (fullText)"] = True

    if 'NCA 자막 추가' in name:
        body = params.get('jsonBody', '')
        if 'fontsdir=/tmp' in body:
            checks["fontsdir=/tmp"] = True
        if 'NotoSansKR-Bold.ttf' in body:
            checks["Font file input"] = True

print("\n   === 검증 결과 ===")
all_pass = True
for item, result in checks.items():
    status = "✅" if result else "❌"
    print(f"   {status} {item}")
    if not result:
        all_pass = False

if all_pass:
    print("\n   🎉 모든 변경사항 적용 완료!")
else:
    print("\n   ⚠️ 일부 항목 확인 필요")
