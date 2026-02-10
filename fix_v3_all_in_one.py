#!/usr/bin/env python3
"""
루믹스 v3 전체 수정사항 일괄 적용 (덮어쓰기 방지)
1. Creatomate 타임라인: Math.max, loop, 1080x1920, T24.duration
2. 이미지 프롬프트 AI: 비즈니스/테크 장르 + 금지 패턴
3. AI 주제 생성: 용어 교체 (엔드-투-엔드 → 올인원)
"""
import json
import subprocess
import sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

# === Creatomate 타임라인 최종 코드 ===
CREATOMATE_CODE = r'''// === Creatomate 타임라인 빌더 ===
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

# === 이미지 장르 교체 ===
OLD_GENRES = "['사이버펑크 네온 — neon glow cyberpunk futuristic dark city', '자연 다큐멘터리 — nature documentary organic earthy warm tones', '미니멀 흑백 — minimal monochrome high contrast black white', '레트로 필름그레인 — retro film grain vintage 70s warm analog', '하이테크 미래 — high-tech futuristic holographic clean blue', '다크 시네마틱 — dark cinematic dramatic shadows moody', '팝아트 컬러풀 — pop art vibrant saturated bold colors', '수중/우주 판타지 — underwater space fantasy ethereal floating', '동양풍 — oriental asian aesthetic ink wash dramatic', '고딕 다크판타지 — gothic dark fantasy mystical ancient']"

NEW_GENRES = "['하이테크 미래 — high-tech futuristic holographic clean blue neon', '다크 시네마틱 — dark cinematic dramatic shadows moody professional', '사이버펑크 네온 — neon glow cyberpunk futuristic dark city digital', '미니멀 모던 — minimal modern clean corporate sleek dark background', '럭셔리 프리미엄 — luxury premium dark gold elegant sophisticated', '디지털 데이터 — digital data visualization tech glow matrix code', '비즈니스 코퍼레이트 — corporate modern glass building conference professional', '테크 서버룸 — tech server room data center blue glow cables', '레트로 네온 — retro neon sign night city urban glow', '모던 UI — modern user interface dashboard dark mode holographic']"

OLD_BAN = "금지 패턴:\n- 창문 앞 인물 실루엣, 골든아워 역광, 양복 남자가 도시 내려다보는 장면\n- 악수 장면, 단순 사무실\n- shield/lock/key, arrow/graph/chart, rocket/lightning, puzzle, hourglass/clock"

NEW_BAN = "금지 패턴:\n- 창문 앞 인물 실루엣, 골든아워 역광, 양복 남자가 도시 내려다보는 장면\n- 악수 장면, 단순 사무실\n- shield/lock/key, arrow/graph/chart, rocket/lightning, puzzle, hourglass/clock\n- 자연 풍경(산, 논, 바다, 꽃), 동양화/수묵화, 판타지/마법, 동물\n- 중세 유럽, 고딕 건축, 판타지 마을\n- 카지노 사업과 관련 없는 비주얼 절대 금지"

# === 용어 교체 ===
TERM_FIXES = {
    "엔드-투-엔드 비즈니스 패키지": "올인원 비즈니스 패키지",
    "엔드-투-엔드": "올인원",
}

TERM_RULE = """
- 나레이션에 어려운 영어 표현 금지. 쉬운 한국어로 표현할 것:
  (엔드-투-엔드 → 올인원, 커스텀 UI/UX → 맞춤 디자인, 풀스택 → 전체, DDoS → 해킹 공격, API → 직접 연결)"""


def fetch_workflow():
    result = subprocess.run([
        'curl', '-sk', '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


def fix_creatomate(nodes):
    for n in nodes:
        if n['name'] == 'Creatomate 타임라인':
            n['parameters']['jsCode'] = CREATOMATE_CODE
            print("  [OK] Creatomate 타임라인 전체 교체")
            print("       - Math.max, loop:true, 1080x1920, T24.duration")
            return 1
    print("  [ERROR] Creatomate 타임라인 노드 없음")
    return 0


def fix_image_genres(nodes):
    for n in nodes:
        if n['name'] == '이미지 프롬프트 AI':
            # chainLlm 타입이면 text 필드
            text = n['parameters'].get('text', '')
            if not text:
                print("  [WARN] 이미지 프롬프트 AI text 필드 없음")
                return 0

            if '럭셔리 프리미엄' in text:
                print("  [SKIP] 이미지 장르 이미 수정됨")
                return 0

            # 장르 교체
            if OLD_GENRES in text:
                text = text.replace(OLD_GENRES, NEW_GENRES)
                print("  [OK] 장르 목록 교체 완료")
            else:
                print("  [WARN] 기존 장르 목록을 찾을 수 없음 - 수동 확인 필요")
                # 부분 매칭 시도
                if '자연 다큐멘터리' in text:
                    text = text.replace(
                        "'자연 다큐멘터리 — nature documentary organic earthy warm tones', ",
                        ""
                    )
                    text = text.replace(
                        "'팝아트 컬러풀 — pop art vibrant saturated bold colors', ",
                        "'럭셔리 프리미엄 — luxury premium dark gold elegant sophisticated', "
                    )
                    text = text.replace(
                        "'수중/우주 판타지 — underwater space fantasy ethereal floating', ",
                        "'디지털 데이터 — digital data visualization tech glow matrix code', "
                    )
                    text = text.replace(
                        "'동양풍 — oriental asian aesthetic ink wash dramatic', ",
                        "'비즈니스 코퍼레이트 — corporate modern glass building conference professional', "
                    )
                    text = text.replace(
                        "'고딕 다크판타지 — gothic dark fantasy mystical ancient'",
                        "'모던 UI — modern user interface dashboard dark mode holographic'"
                    )
                    print("  [OK] 개별 장르 교체 완료")

            # 금지 패턴 교체
            if OLD_BAN in text:
                text = text.replace(OLD_BAN, NEW_BAN)
                print("  [OK] 금지 패턴 강화 완료")
            elif '자연 풍경' not in text and '금지 패턴' in text:
                text = text.replace(
                    "- shield/lock/key, arrow/graph/chart, rocket/lightning, puzzle, hourglass/clock",
                    "- shield/lock/key, arrow/graph/chart, rocket/lightning, puzzle, hourglass/clock\n- 자연 풍경(산, 논, 바다, 꽃), 동양화/수묵화, 판타지/마법, 동물\n- 중세 유럽, 고딕 건축, 판타지 마을\n- 카지노 사업과 관련 없는 비주얼 절대 금지"
                )
                print("  [OK] 금지 패턴 추가 완료")

            n['parameters']['text'] = text
            return 1

    print("  [ERROR] 이미지 프롬프트 AI 노드 없음")
    return 0


def fix_terms(nodes):
    targets = ['AI 주제 생성', 'AI 주제 생성 2차', 'AI 주제 생성 3차']
    fixed = 0
    for n in nodes:
        if n['name'] not in targets:
            continue
        msgs = n.get('parameters', {}).get('messages', {}).get('values', [])
        for m in msgs:
            content = m.get('content', '')
            if not content:
                continue
            changed = False
            for old_term, new_term in TERM_FIXES.items():
                if old_term in content:
                    content = content.replace(old_term, new_term)
                    changed = True
            if '어려운 영어 표현 금지' not in content:
                insert_point = content.find('나레이션 필수 규칙')
                if insert_point != -1:
                    next_section = content.find('\n\n', insert_point + 10)
                    if next_section != -1:
                        content = content[:next_section] + TERM_RULE + content[next_section:]
                        changed = True
            if changed:
                m['content'] = content
                print(f"  [OK] {n['name']}: 용어 교체")
                fixed += 1
            else:
                print(f"  [SKIP] {n['name']}: 변경 없음")
    return fixed


def upload_workflow(workflow_data):
    put_data = {
        "name": workflow_data.get("name"),
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "settings": {
            "executionOrder": workflow_data.get("settings", {}).get("executionOrder", "v1")
        }
    }
    with open('/tmp/v3_all_fixes.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/v3_all_fixes.json',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if 'id' in response:
            print(f"  [OK] 업로드 성공 (노드: {len(response.get('nodes', []))}개)")
            return True
        else:
            print(f"  [ERROR] {json.dumps(response, ensure_ascii=False)[:500]}")
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


def verify():
    result = subprocess.run([
        'curl', '-sk', '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    data = json.loads(result.stdout)

    print("\n  검증 결과:")
    all_ok = True
    for n in data['nodes']:
        if n['name'] == 'Creatomate 타임라인':
            code = n['parameters']['jsCode']
            checks = {
                'Math.max': 'Math.max' in code,
                'loop: true': 'loop' in code,
                'width: 1080': 'width: 1080' in code,
                'height: 1920': 'height: 1920' in code,
                'T24.duration': 'Video-T24.duration' in code,
            }
            for k, v in checks.items():
                status = "OK" if v else "FAIL"
                if not v: all_ok = False
                print(f"    [{status}] Creatomate: {k}")

        if n['name'] == '이미지 프롬프트 AI':
            text = n['parameters'].get('text', '')
            checks = {
                '럭셔리 프리미엄': '럭셔리 프리미엄' in text,
                '자연다큐 제거': '자연 다큐멘터리' not in text,
                '동양풍 제거': '동양풍' not in text,
                '고딕 제거': '고딕' not in text,
                '금지패턴 자연풍경': '자연 풍경' in text,
            }
            for k, v in checks.items():
                status = "OK" if v else "FAIL"
                if not v: all_ok = False
                print(f"    [{status}] 이미지: {k}")

    return all_ok


def main():
    print("=" * 60)
    print("루믹스 v3 전체 수정사항 일괄 적용")
    print("=" * 60)

    print("\n[1/5] 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print("  [ERROR] 실패")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    print("\n[2/5] Creatomate 타임라인 수정...")
    fix_creatomate(workflow['nodes'])

    print("\n[3/5] 이미지 장르 교체...")
    fix_image_genres(workflow['nodes'])

    print("\n[4/5] 용어 교체...")
    fix_terms(workflow['nodes'])

    print("\n[5/5] 업로드 + 재활성화 + 검증...")
    if upload_workflow(workflow):
        reactivate()
        verify()

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
