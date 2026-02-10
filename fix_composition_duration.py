#!/usr/bin/env python3
"""
컴포지션 duration과 영상 speed 로직 수정
- 나레이션 < 영상 → speed 100%, duration = videoDuration (영상 끝까지)
- 나레이션 > 영상 → speed = (videoDuration/narrationDuration)*100%, duration = narrationDuration
- 즉, compositionDuration = Math.max(narrationDuration, videoDuration)
"""
import json
import subprocess
import sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

NEW_CODE = r'''// === Creatomate 타임라인 빌더 ===
// 템플릿 + modifications 방식
const bgmUrl = $('BGM 대기').first().json.audio?.url || '';
const videoDuration = 5; // Kling 영상 생성 길이 (초)
const bitrate = 128000;
let totalDuration = 0;

const modifications = {};

for (let i = 0; i < 5; i++) {
  const n = i + 1;

  // TTS 결과
  const ttsResult = $('TTS 결과').all()[i]?.json;
  const narrationUrl = ttsResult?.audio?.url || '';
  const fileSize = ttsResult?.audio?.file_size || 40000;

  // 오디오 파일 크기로 narration duration 추정
  let narrationDuration = Math.round((fileSize * 8 / bitrate) * 100) / 100;
  if (narrationDuration < 3) narrationDuration = 5;

  // === 핵심 로직: duration과 speed 계산 ===
  let speed;
  let compositionDuration;

  if (narrationDuration > videoDuration) {
    // 나레이션이 영상보다 길면 → 영상 슬로우모션, duration = 나레이션 길이
    speed = Math.round((videoDuration / narrationDuration) * 100) + String.fromCharCode(37);
    compositionDuration = narrationDuration;
  } else {
    // 나레이션이 영상보다 짧으면 → speed 100%, duration = 영상 길이 (영상 끝까지)
    speed = "100" + String.fromCharCode(37);
    compositionDuration = videoDuration;
  }

  // 영상 URL
  const videoResult = $('영상 URL 정리').all()[i]?.json;
  const videoUrl = videoResult?.video?.url || '';

  // 자막 텍스트
  const subtitleText = ($('5파트 분리').all()[i]?.json?.text || '').replace(/\n/g, '\\n');

  // Creatomate modifications
  modifications[`Composition-${n}.duration`] = String(compositionDuration);
  modifications[`Video-${n}.source`] = videoUrl;
  modifications[`Video-${n}.speed`] = speed;
  modifications[`Video-${n}.playback_rate`] = speed;
  modifications[`Narration-${n}.source`] = narrationUrl;
  modifications[`Text-${n}.text`] = subtitleText;

  totalDuration += compositionDuration;
}

// BGM
modifications['BGM.source'] = bgmUrl;

// 엔딩카드 시작점
modifications['Video-T24.time'] = String(totalDuration);

const payload = {
  template_id: "056a9082-710f-4345-b964-c6384103fbf6",
  output_format: "mp4",
  h264_profile: "high",
  h264_level: "5.2",
  h264_crf: 10,
  h264_bitrate: 20000000,
  frame_rate: 30,
  duration: String(totalDuration + 8),
  modifications: modifications
};

return [{
  json: {
    creatomate_payload: payload,
    modifications: modifications,
    subject: $('시트 기록').first().json.Subject,
    caption: $('시트 기록').first().json.Caption,
    comment: $('시트 기록').first().json.Comment
  }
}];'''


def fetch_workflow():
    result = subprocess.run([
        'curl', '-sk', '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


def fix_timeline_node(nodes):
    for n in nodes:
        if n['name'] == 'Creatomate 타임라인':
            old_code = n['parameters'].get('jsCode', '')

            if 'compositionDuration' in old_code:
                print("  [SKIP] 이미 compositionDuration 로직 적용됨")
                return 0

            n['parameters']['jsCode'] = NEW_CODE
            print("  [OK] Creatomate 타임라인: duration/speed 로직 수정")
            print("       - 나레이션 < 영상 → speed 100%, duration = videoDuration")
            print("       - 나레이션 > 영상 → speed 감소, duration = narrationDuration")
            print("       - compositionDuration = Math.max(narration, video)")
            return 1

    print("  [ERROR] Creatomate 타임라인 노드를 찾을 수 없음")
    return 0


def upload_workflow(workflow_data):
    put_data = {
        "name": workflow_data.get("name"),
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "settings": {
            "executionOrder": workflow_data.get("settings", {}).get("executionOrder", "v1")
        }
    }
    with open('/tmp/lumix_v3_fix_duration.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_v3_fix_duration.json',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if 'id' in response:
            print(f"  [OK] 업로드 성공 (노드: {len(response.get('nodes', []))}개)")
            return True
        else:
            print(f"  [ERROR] {json.dumps(response, ensure_ascii=False)[:300]}")
            return False
    except json.JSONDecodeError:
        print(f"  [ERROR] 파싱 실패: {result.stdout[:300]}")
        return False


def reactivate():
    subprocess.run([
        'curl', '-sk', '-X', 'POST',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}/deactivate'
    ], capture_output=True, text=True)
    result = subprocess.run([
        'curl', '-sk', '-X', 'POST',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}/activate'
    ], capture_output=True, text=True)
    try:
        response = json.loads(result.stdout)
        print(f"  [OK] 재활성화: active={response.get('active')}")
    except Exception:
        print("  [WARN] 재활성화 응답 확인 필요")


def main():
    print("=" * 55)
    print("컴포지션 duration + 영상 speed 로직 수정")
    print("=" * 55)

    print("\n[1/3] 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print("  [ERROR] 실패")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    print("\n[2/3] Creatomate 타임라인 코드 수정...")
    fixed = fix_timeline_node(workflow['nodes'])

    if fixed == 0:
        print("\n수정할 내용 없음")
        return

    print("\n[3/3] 업로드 + 재활성화...")
    if upload_workflow(workflow):
        reactivate()

    print("\n" + "=" * 55)
    print("수정 완료!")
    print("=" * 55)
    print("\n  변경 내용:")
    print("  기존: duration = 항상 나레이션 길이 (영상 잘릴 수 있음)")
    print("  수정: duration = Math.max(나레이션, 영상)")
    print("        나레이션 짧으면 → 영상 5초 풀재생, speed 100%")
    print("        나레이션 길면 → 영상 슬로우, speed 자동 조절")


if __name__ == "__main__":
    main()
