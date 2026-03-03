/**
 * n8n Code Node: SFX 안전 매핑 + 폴백
 * - 입력: script JSON (v1.2/v1.3)
 * - 출력: sfx_urls[] (세그먼트/이벤트별), bgm_url (optional)
 *
 * 전제:
 * - MINIO_BASE_URL은 내부 접근 가능한 base (예: http://minio:9000)
 * - 혹은 presigned URL을 미리 만들어두고 manifest에 넣어도 됨.
 */

const MINIO_BASE_URL = $env.MINIO_BASE_URL || "http://76.13.182.180:9000";
const BUCKET = $env.MINIO_BUCKET || "arubto";

// 실제 MinIO에 존재하는 SFX 파일 매핑
const SFX_KEY = {
  whoosh: "audio/sfx_whoosh1.mp3",
  swoosh: "audio/sfx_whoosh1.mp3",
  pop:    "audio/sfx_pop_user.mp3",
  ding:   "audio/sfx_ding1.mp3",
  ding2:  "audio/sfx_ding2.mp3",
  ppook:  "audio/sfx_ppook.wav",
  wow:    "audio/sfx_wow.wav",
};

// 아직 전용 파일이 없는 키 — 기존 SFX로 폴백
const OPTIONAL_SFX_ALIAS = {
  cash: "ding",
  cheer: "pop",
};

/**
 * MinIO 오브젝트 키를 전체 URL로 변환
 * @param {string} keyPath - MinIO 오브젝트 키
 * @returns {string} 전체 URL
 */
function toUrl(keyPath) {
  return `${MINIO_BASE_URL}/${BUCKET}/${keyPath}`;
}

/**
 * SFX 타입을 안전하게 해석 (존재하지 않으면 alias → 최후 폴백)
 * @param {string} t - 요청된 SFX 타입
 * @returns {string} 유효한 SFX 키
 */
function safeSfxType(t) {
  if (SFX_KEY[t]) return t;
  if (OPTIONAL_SFX_ALIAS[t] && SFX_KEY[OPTIONAL_SFX_ALIAS[t]]) return OPTIONAL_SFX_ALIAS[t];
  // 최후 폴백
  return "whoosh";
}

// 1) v1.3 audio_plan.sfx_events 우선, 없으면 v1.2 segments[].sfx 사용
const input = $input.item.json;
const sfxEvents = input.audio_plan?.sfx_events ?? null;

let resolved = [];

if (Array.isArray(sfxEvents) && sfxEvents.length) {
  resolved = sfxEvents.map(ev => {
    const t = safeSfxType(ev.type);
    return { anchor: ev.anchor, type: t, url: toUrl(SFX_KEY[t]) };
  });
} else if (Array.isArray(input.segments)) {
  // segments[].sfx (세그먼트 시작 기준으로만 처리)
  resolved = input.segments.flatMap(seg => {
    const list = Array.isArray(seg.sfx) ? seg.sfx : [];
    return list.map(t0 => {
      const t = safeSfxType(t0);
      return { anchor: `${seg.id}_start`, type: t, url: toUrl(SFX_KEY[t]) };
    });
  });
}

return { sfx_events_resolved: resolved };
