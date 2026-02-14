// NCA 제작 결과 + ASS 자막 (Noto Sans KR 85pt + 순차 1줄씩 + 왼→오 + 페이드아웃)
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
    throw new Error('Video production failed: ' + JSON.stringify(result).substring(0, 200));
}

const subtitleData = prevData.subtitle_data || [];

const RES_X = 1080;
const RES_Y = 1920;
const FONT_SIZE = 85;
const SUB_Y = RES_Y - 250;
const REVEAL_MS = 400;
const FADE_MS = 300;
const CENTER_X = Math.round(RES_X / 2);

let assContent = '[Script Info]\n';
assContent += 'Title: Lumix Subtitle\n';
assContent += 'ScriptType: v4.00+\n';
assContent += 'WrapStyle: 2\n';
assContent += 'PlayResX: ' + RES_X + '\n';
assContent += 'PlayResY: ' + RES_Y + '\n\n';
assContent += '[V4+ Styles]\n';
assContent += 'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n';
assContent += 'Style: Default,Noto Sans KR,' + FONT_SIZE + ',&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,4,1,2,40,40,120,1\n\n';
assContent += '[Events]\n';
assContent += 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n';

const fmt = (totalSec) => {
    const h = Math.floor(totalSec / 3600);
    const m = Math.floor((totalSec % 3600) / 60);
    const s = totalSec % 60;
    return h + ':' + String(m).padStart(2,'0') + ':' + s.toFixed(2).padStart(5,'0');
};

for (const sub of subtitleData) {
    if (!sub.text) continue;
    const fx = '{\\an5\\pos(' + CENTER_X + ',' + SUB_Y + ')\\clip(0,0,0,' + RES_Y + ')\\t(0,' + REVEAL_MS + ',\\clip(0,0,' + RES_X + ',' + RES_Y + '))\\fad(0,' + FADE_MS + ')}';
    assContent += 'Dialogue: 0,' + fmt(sub.start) + ',' + fmt(sub.end) + ',Default,,0,0,0,,' + fx + sub.text + '\n';
}

console.log('ASS content length:', assContent.length);
console.log('Subtitle entries:', subtitleData.filter(s => s.text).length);

const jobId = result.job_id || Date.now().toString();
const assFileName = 'subtitles/sub_' + jobId + '.ass';
const assUrl = 'http://76.13.182.180:9000/nca-toolkit/' + assFileName;

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
        has_subtitles: subtitleData.filter(s => s.text).length > 0,
    }
}];