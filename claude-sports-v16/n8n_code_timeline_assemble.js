/**
 * n8n Code Node: 동적 타임라인 조립 (TTS duration 기반)
 * 입력:
 *  - script JSON (v1.2/v1.3)
 *  - tts_results: [{id:'intro', url:'...', duration_sec: 2.4}, ...]
 * 출력:
 *  - render_duration_sec, segment_times, template_B params(HOLD/SCROLL)
 */

const input = $input.item.json;
const ttsResults = input.tts_results || []; // 이전 노드에서 합쳐서 넣어주세요
const padding = Number(input.audio_plan?.timeline_padding_sec ?? 0.5);

const durById = {};
for (const r of ttsResults) {
  if (r && r.id) durById[r.id] = Number(r.duration_sec || 0);
}

// segment 순서 고정
const order = ["intro","body","outro"];
let t = 0;
const segmentTimes = {};
for (const id of order) {
  const d = Math.max(0.2, durById[id] || 0);
  segmentTimes[id] = { start: Number(t.toFixed(3)), dur: Number(d.toFixed(3)) };
  t += d;
}
const totalTts = t;
const renderDuration = Number((totalTts + padding).toFixed(3));

// B형 스크롤 파라미터 계산
let hold = 1.0;
let scrollMin = 6.0;
if (input.visual_plan?.template_b?.hold_sec != null) hold = Number(input.visual_plan.template_b.hold_sec);
if (input.visual_plan?.template_b?.scroll_sec_min != null) scrollMin = Number(input.visual_plan.template_b.scroll_sec_min);

// outro 구간(CTA 포함) 확보를 위해 최소 2초는 남기기
const outroDur = segmentTimes.outro?.dur ?? 2.0;
const reserve = Math.max(2.0, outroDur);
const scroll = Math.max(scrollMin, renderDuration - hold - reserve);

return {
  render_duration_sec: renderDuration,
  segment_times: segmentTimes,
  template_b_params: {
    HOLD: Number(hold.toFixed(3)),
    SCROLL: Number(scroll.toFixed(3))
  }
};
