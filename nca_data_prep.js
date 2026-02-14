// NCA 영상 제작 - Ken Burns 전체 + 크로스페이드 + 풀 자막
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

let subtitleTexts = [];
let fullNarrationTexts = [];
try {
    const partItems = $('5파트 분리').all();
    subtitleTexts = partItems.map(item => item.json.subtitle || item.json.text || '');
    fullNarrationTexts = partItems.map(item => item.json.text || '');
} catch (e) {
    console.log('Could not get subtitles:', e.message);
}

function splitToChunks(text, maxLen) {
    if (!text) return [];
    text = text.trim();
    if (!text) return [];
    maxLen = maxLen || 14;
    const MIN_BREAK = 7;
    const nsLen = (s) => s.replace(/\s/g, '').length;
    const segments = text.split(/(?<=[,\.!\?])\s*/);
    const result = [];
    for (const seg of segments) {
        const trimmed = seg.trim();
        if (!trimmed) continue;
        if (nsLen(trimmed) <= maxLen) {
            result.push(trimmed);
            continue;
        }
        const words = trimmed.split(/\s+/);
        const n = words.length;
        const isBreak = (w) => /[은는이가을를에로]$|에서$|으로$|[와과]$|면$/.test(w);
        let start = 0;
        while (start < n) {
            if (start >= n - 1) { result.push(words[start]); break; }
            const remNS = words.slice(start).reduce((a, w) => a + w.length, 0);
            if (remNS <= maxLen) { result.push(words.slice(start).join(' ')); break; }
            let len = 0, lastFit = start, bestBreak = -1;
            for (let e = start; e < n; e++) {
                len += (e > start ? 1 : 0) + words[e].length;
                if (len > maxLen) break;
                lastFit = e;
                if (isBreak(words[e]) && len >= MIN_BREAK) bestBreak = e;
            }
            const endIdx = lastFit >= n - 1 ? n - 1 : bestBreak >= 0 ? bestBreak : lastFit;
            result.push(words.slice(start, endIdx + 1).join(' '));
            start = endIdx + 1;
        }
    }
    return result;
}

const partCount = Math.min(narrations.length, videos.length, 5);
const SOURCE_DURATION = 5;
const SCENE_DURATION = 6;
const MAX_SLOW_SECONDS = 7;
const OUTRO_URL = 'http://76.13.182.180:9000/nca-toolkit/assets/outro_lumix.mp4';
const OUTRO_DURATION = 5;
const XFADE_DUR = 0.15;

console.log('Parts:', partCount, 'Videos:', videos.length, 'Narrations:', narrations.length, 'BGM:', bgmUrl ? 'YES' : 'NO');

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
        kbIndex: i,
        type: 'normal'
    });

    if (dur >= MAX_SLOW_SECONDS) {
        console.log('Part ' + (i+1) + ': dur=' + dur.toFixed(1) + 's, LOOP');
    } else {
        const slow = Math.max(1, dur / SOURCE_DURATION);
        console.log('Part ' + (i+1) + ': dur=' + dur.toFixed(1) + 's, slow=' + slow.toFixed(2) + 'x + Ken Burns');
    }
}

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

let filters = [];
let subtitleData = [];
let currentTime = 0;

function getKenBurnsEffect(index, dur) {
    const KB = 1.12;
    const kbW = Math.round(1080 * KB);
    const kbH = Math.round(1920 * KB);
    const dx = kbW - 1080;
    const dy = kbH - 1920;
    const dxH = Math.round(dx / 2);
    const dyH = Math.round(dy / 2);
    const d = dur.toFixed(2);
    const g = (expr, def) => 'if(isnan(t)\\,' + def + '\\,' + expr + ')';
    const variants = [
        'scale=' + kbW + ':' + kbH + ',crop=w=' + g(kbW + '-' + dx + '*t/' + d, kbW) + ':h=' + g(kbH + '-' + dy + '*t/' + d, kbH) + ':x=' + g(dxH + '*t/' + d, 0) + ':y=' + g(dyH + '*t/' + d, 0) + ',scale=1080:1920',
        'scale=' + kbW + ':' + kbH + ',crop=w=' + g('1080+' + dx + '*t/' + d, 1080) + ':h=' + g('1920+' + dy + '*t/' + d, 1920) + ':x=' + g(dxH + '-' + dxH + '*t/' + d, dxH) + ':y=' + g(dyH + '-' + dyH + '*t/' + d, dyH) + ',scale=1080:1920',
        'scale=' + kbW + ':' + kbH + ',crop=1080:1920:' + g(dxH + '*t/' + d, 0) + ':' + g(dyH + '*t/' + d, 0),
        'scale=' + kbW + ':' + kbH + ',crop=1080:1920:' + g(dx + '-' + dx + '*t/' + d, dx) + ':' + g(dy + '-' + dy + '*t/' + d, dy),
        'scale=' + kbW + ':' + kbH + ',crop=1080:1920:' + g(dx + '*t/' + d, 0) + ':' + dyH,
        'scale=' + kbW + ':' + kbH + ',crop=1080:1920:' + g(dx + '-' + dx + '*t/' + d, dx) + ':' + dyH,
        'scale=' + kbW + ':' + kbH + ',hflip,crop=w=' + g(kbW + '-' + dx + '*t/' + d, kbW) + ':h=' + g(kbH + '-' + dy + '*t/' + d, kbH) + ':x=' + g(dxH + '*t/' + d, 0) + ':y=' + g(dyH + '*t/' + d, 0) + ',scale=1080:1920',
        'scale=' + kbW + ':' + kbH + ',hflip,crop=w=' + g('1080+' + dx + '*t/' + d, 1080) + ':h=' + g('1920+' + dy + '*t/' + d, 1920) + ':x=' + g(dxH + '-' + dxH + '*t/' + d, dxH) + ':y=' + g(dyH + '-' + dyH + '*t/' + d, dyH) + ',scale=1080:1920',
    ];
    return variants[index % variants.length];
}

for (let i = 0; i < segments.length; i++) {
    const seg = segments[i];
    const { vIdx, aIdx } = segMeta[i];
    const dur = seg.sceneDuration;
    const slowFactor = Math.max(1, dur / SOURCE_DURATION);
    const useKB = false;
    const kbEffect = '';

    if (dur >= MAX_SLOW_SECONDS) {
        inputs[vIdx].options = [{ option: "-stream_loop" }, { option: "-1" }];
        filters.push('[' + vIdx + ':v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setpts=PTS*1.2,fps=24,trim=duration=' + dur.toFixed(2) + ',setpts=PTS-STARTPTS[v' + i + ']');
    } else if (slowFactor > 1.01) {
        filters.push('[' + vIdx + ':v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setpts=PTS*' + slowFactor.toFixed(2) + ',tpad=stop_mode=clone:stop_duration=10,trim=duration=' + dur.toFixed(2) + ',setpts=PTS-STARTPTS,' + (useKB ? kbEffect + ',setpts=PTS-STARTPTS,' : '') + 'fps=24[v' + i + ']');
    } else {
        filters.push('[' + vIdx + ':v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,' + (useKB ? kbEffect + ',' : '') + 'trim=duration=' + dur.toFixed(2) + ',setpts=PTS-STARTPTS,fps=24[v' + i + ']');
    }

    filters.push('[' + aIdx + ':a]atrim=duration=' + dur.toFixed(2) + ',apad=whole_dur=' + dur.toFixed(2) + ',asetpts=PTS-STARTPTS[a' + i + ']');

    const chunks = splitToChunks(seg.subtitleText, 14);
    const partStart = currentTime;
    const partEnd = currentTime + dur - XFADE_DUR;
    const partDur = partEnd - partStart;
    let t = partStart;
    const MIN_GROUP_DUR = 2.0;
    // Calculate how many chunks per group to guarantee minimum display time
    const maxGroups = Math.max(1, Math.floor(partDur / MIN_GROUP_DUR));
    const linesPerGroup = Math.max(2, Math.ceil(chunks.length / maxGroups));
    const groups = [];
    for (let ci = 0; ci < chunks.length; ci += linesPerGroup) {
        const slice = chunks.slice(ci, Math.min(ci + linesPerGroup, chunks.length));
        groups.push(slice.join('\\N'));
    }
    const groupDur = groups.length > 0 ? partDur / groups.length : partDur;
    for (const grp of groups) {
        subtitleData.push({ text: grp, start: t, end: t + groupDur });
        t += groupDur;
    }
    currentTime += dur - XFADE_DUR;
}

filters.push('[' + outroIdx + ':v]fps=24,scale=1080:2160,crop=1080:1920:0:0,trim=duration=' + OUTRO_DURATION + ',setpts=PTS-STARTPTS,fps=24[voutro]');
filters.push('anullsrc=r=44100:cl=mono,atrim=duration=' + OUTRO_DURATION + '[aoutro]');

const totalParts = segments.length + 1;
const allDurations = segments.map(s => s.sceneDuration);
allDurations.push(OUTRO_DURATION);

let prevVLabel = 'v0';
let xfadeOffset = allDurations[0] - XFADE_DUR;
for (let k = 1; k < totalParts; k++) {
    const nextVLabel = k < segments.length ? 'v' + k : 'voutro';
    const isLast = k === totalParts - 1;
    const outVLabel = isLast ? 'outv' : 'xfv' + k;
    filters.push('[' + prevVLabel + '][' + nextVLabel + ']xfade=transition=fade:duration=' + XFADE_DUR + ':offset=' + xfadeOffset.toFixed(2) + '[' + outVLabel + ']');
    prevVLabel = outVLabel;
    if (!isLast) xfadeOffset += allDurations[k] - XFADE_DUR;
}

let prevALabel = 'a0';
for (let k = 1; k < totalParts; k++) {
    const nextALabel = k < segments.length ? 'a' + k : 'aoutro';
    const isLast = k === totalParts - 1;
    const outALabel = isLast ? 'outa' : 'xfa' + k;
    filters.push('[' + prevALabel + '][' + nextALabel + ']acrossfade=d=' + XFADE_DUR + ':c1=tri:c2=tri[' + outALabel + ']');
    prevALabel = outALabel;
}

if (bgmUrl) {
    const bgmIdx = segments.length * 2;
    filters.push('[' + bgmIdx + ':a]volume=0.25[bgm]');
    filters.push('[outa][bgm]amix=inputs=2:duration=first:dropout_transition=2[finala]');
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

const totalDuration = currentTime + OUTRO_DURATION;
console.log('Total segments: ' + segments.length + ', Duration: ' + totalDuration.toFixed(1) + 's');

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
}];