// NCA 제작 결과 + ASS 자막 (Noto Sans KR 110pt + 줄별 슬라이드업)
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
const FONT_SIZE = 110;
const LINE_GAP = Math.round(FONT_SIZE * 1.3);
const LINE2_Y = RES_Y - 150;
const LINE1_Y = LINE2_Y - LINE_GAP;
const START_Y = RES_Y + 80;
const SLIDE_MS = 300;
const LINE_DELAY = 1.0;
const CENTER_X = Math.round(RES_X / 2);

let assContent = '[Script Info]\n';
assContent += 'Title: Lumix Subtitle\n';
assContent += 'ScriptType: v4.00+\n';
assContent += 'WrapStyle: 0\n';
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
    if (!sub.text && (!sub.lines || !sub.lines.line1)) continue;

    const lines = sub.lines || { line1: sub.text || '', line2: '' };
    const startTime = sub.start;
    const endTime = sub.end;

    if (lines.line2) {
        const move1 = '{\\an5\\move(' + CENTER_X + ',' + START_Y + ',' + CENTER_X + ',' + LINE1_Y + ',0,' + SLIDE_MS + ')\\fad(0,200)}';
        assContent += 'Dialogue: 0,' + fmt(startTime) + ',' + fmt(endTime) + ',Default,,0,0,0,,' + move1 + lines.line1 + '\n';

        const line2Start = startTime + LINE_DELAY;
        const move2 = '{\\an5\\move(' + CENTER_X + ',' + START_Y + ',' + CENTER_X + ',' + LINE2_Y + ',0,' + SLIDE_MS + ')\\fad(0,200)}';
        assContent += 'Dialogue: 0,' + fmt(line2Start) + ',' + fmt(endTime) + ',Default,,0,0,0,,' + move2 + lines.line2 + '\n';
    } else {
        const singleY = LINE2_Y;
        const move = '{\\an5\\move(' + CENTER_X + ',' + START_Y + ',' + CENTER_X + ',' + singleY + ',0,' + SLIDE_MS + ')\\fad(0,200)}';
        assContent += 'Dialogue: 0,' + fmt(startTime) + ',' + fmt(endTime) + ',Default,,0,0,0,,' + move + lines.line1 + '\n';
    }
}

console.log('ASS content length:', assContent.length);
console.log('Subtitle entries:', subtitleData.filter(s => s.text || (s.lines && s.lines.line1)).length);

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
        has_subtitles: subtitleData.filter(s => s.text || (s.lines && s.lines.line1)).length > 0,
    }
}];