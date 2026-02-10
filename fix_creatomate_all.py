#!/usr/bin/env python3
"""
Creatomate 타임라인 전체 수정 (한번에 적용)
1. compositionDuration = Math.max(narrationDuration, videoDuration)
2. loop: true (speed 제거)
3. 해상도 1080x1920
4. Video-T24.duration = 4
"""
import json
import subprocess
import sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

FINAL_CODE = r'''// === Creatomate 타임라인 빌더 ===
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

  // 컴포지션 duration = Math.max(나레이션, 영상)
  const compositionDuration = Math.max(narrationDuration, videoDuration);

  // 영상 URL
  const videoResult = $('영상 URL 정리').all()[i]?.json;
  const videoUrl = videoResult?.video?.url || '';

  // 자막 텍스트
  const subtitleText = ($('5파트 분리').all()[i]?.json?.text || '').replace(/\n/g, '\\n');

  // Creatomate modifications
  modifications[`Composition-${n}.duration`] = String(compositionDuration);
  modifications[`Video-${n}.source`] = videoUrl;
  modifications[`Video-${n}.loop`] = true;
  modifications[`Narration-${n}.source`] = narrationUrl;
  modifications[`Text-${n}.text`] = subtitleText;

  totalDuration += compositionDuration;
}

// BGM
modifications['BGM.source'] = bgmUrl;

// 엔딩카드
modifications['Video-T24.time'] = String(totalDuration);
modifications['Video-T24.duration'] = '4';

const payload = {
  template_id: "056a9082-710f-4345-b964-c6384103fbf6",
  output_format: "mp4",
  width: 1080,
  height: 1920,
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


def fix_code(nodes):
    for n in nodes:
        if n['name'] == 'Creatomate 타임라인':
            n['parameters']['jsCode'] = FINAL_CODE
            print("  [OK] Creatomate 타임라인 전체 교체")
            print("       - Math.max(narration, 5초)")
            print("       - loop: true (speed 제거)")
            print("       - 1080x1920 해상도")
            print("       - Video-T24.duration: 4")
            return 1
    print("  [ERROR] 노드 없음")
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
    with open('/tmp/lumix_v3_creatomate_final.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_v3_creatomate_final.json',
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
        print(f"  [ERROR] 파싱 실패")
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


def verify(workflow_id):
    """업로드 후 확인"""
    result = subprocess.run([
        'curl', '-sk', '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{workflow_id}'
    ], capture_output=True, text=True)
    data = json.loads(result.stdout)
    for n in data['nodes']:
        if n['name'] == 'Creatomate 타임라인':
            code = n['parameters']['jsCode']
            checks = {
                'Math.max': 'Math.max' in code,
                'loop: true': 'loop' in code,
                'speed 제거': '.speed' not in code,
                'width: 1080': 'width: 1080' in code,
                'T24.duration': "Video-T24.duration" in code,
            }
            print("\n  검증 결과:")
            all_ok = True
            for k, v in checks.items():
                status = "OK" if v else "FAIL"
                if not v:
                    all_ok = False
                print(f"    [{status}] {k}")
            return all_ok
    return False


def main():
    print("=" * 55)
    print("Creatomate 타임라인 전체 수정 (한번에)")
    print("=" * 55)

    print("\n[1/4] 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print("  [ERROR] 실패")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    print("\n[2/4] 코드 교체...")
    fix_code(workflow['nodes'])

    print("\n[3/4] 업로드 + 재활성화...")
    if upload_workflow(workflow):
        reactivate()

    print("\n[4/4] 업로드 확인...")
    verify(WORKFLOW_ID)

    print("\n" + "=" * 55)
    print("완료!")
    print("=" * 55)


if __name__ == "__main__":
    main()
