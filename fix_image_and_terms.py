#!/usr/bin/env python3
"""
1. 이미지 프롬프트 AI: 비주얼 장르를 비즈니스/테크 관련으로 교체
2. AI 주제 생성 1차/2차/3차: 어려운 영어 용어 → 쉬운 한국어로
"""
import json
import subprocess
import sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

# 기존 랜덤 장르 (카지노 사업과 관련 없는 것들 포함)
OLD_GENRES = "['사이버펑크 네온 — neon glow cyberpunk futuristic dark city', '자연 다큐멘터리 — nature documentary organic earthy warm tones', '미니멀 흑백 — minimal monochrome high contrast black white', '레트로 필름그레인 — retro film grain vintage 70s warm analog', '하이테크 미래 — high-tech futuristic holographic clean blue', '다크 시네마틱 — dark cinematic dramatic shadows moody', '팝아트 컬러풀 — pop art vibrant saturated bold colors', '수중/우주 판타지 — underwater space fantasy ethereal floating', '동양풍 — oriental asian aesthetic ink wash dramatic', '고딕 다크판타지 — gothic dark fantasy mystical ancient']"

# 비즈니스/테크/카지노 관련 장르만
NEW_GENRES = "['하이테크 미래 — high-tech futuristic holographic clean blue neon', '다크 시네마틱 — dark cinematic dramatic shadows moody professional', '사이버펑크 네온 — neon glow cyberpunk futuristic dark city digital', '미니멀 모던 — minimal modern clean corporate sleek dark background', '럭셔리 프리미엄 — luxury premium dark gold elegant sophisticated', '디지털 데이터 — digital data visualization tech glow matrix code', '비즈니스 코퍼레이트 — corporate modern glass building conference professional', '테크 서버룸 — tech server room data center blue glow cables', '레트로 네온 — retro neon sign night city urban glow', '모던 UI — modern user interface dashboard dark mode holographic']"

OLD_GENRE_COUNT = "[Math.floor(Math.random() * 10)]"
NEW_GENRE_COUNT = "[Math.floor(Math.random() * 10)]"

# AI 주제 생성에서 바꿀 용어들
TERM_FIXES = {
    "엔드-투-엔드 비즈니스 패키지": "올인원 비즈니스 패키지",
    "엔드-투-엔드": "올인원",
}

# AI 주제 생성에 추가할 용어 규칙
TERM_RULE = """
- 나레이션에 어려운 영어 표현 금지. 쉬운 한국어로 표현할 것:
  (엔드-투-엔드 → 올인원, 커스텀 UI/UX → 맞춤 디자인, 풀스택 → 전체, DDoS → 해킹 공격, API → 직접 연결)"""


def fetch_workflow():
    result = subprocess.run([
        'curl', '-sk', '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


def fix_image_prompt(nodes):
    """이미지 프롬프트 AI 비주얼 장르 교체"""
    for n in nodes:
        if n['name'] == '이미지 프롬프트 AI':
            text = n['parameters'].get('text', '')
            if '럭셔리 프리미엄' in text:
                print("  [SKIP] 이미지 프롬프트 AI: 이미 수정됨")
                return 0

            text = text.replace(OLD_GENRES, NEW_GENRES)

            # 금지 패턴에 자연/풍경 관련 추가
            old_ban = "금지 패턴:\n- 창문 앞 인물 실루엣, 골든아워 역광, 양복 남자가 도시 내려다보는 장면\n- 악수 장면, 단순 사무실\n- shield/lock/key, arrow/graph/chart, rocket/lightning, puzzle, hourglass/clock"
            new_ban = "금지 패턴:\n- 창문 앞 인물 실루엣, 골든아워 역광, 양복 남자가 도시 내려다보는 장면\n- 악수 장면, 단순 사무실\n- shield/lock/key, arrow/graph/chart, rocket/lightning, puzzle, hourglass/clock\n- 자연 풍경(산, 논, 바다, 꽃), 동양화/수묵화, 판타지/마법, 동물\n- 카지노 사업과 관련 없는 비주얼 절대 금지"

            text = text.replace(
                "금지 패턴:\n- 창문 앞 인물 실루엣, 골든아워 역광, 양복 남자가 도시 내려다보는 장면\n- 악수 장면, 단순 사무실\n- shield/lock/key, arrow/graph/chart, rocket/lightning, puzzle, hourglass/clock",
                new_ban
            )

            n['parameters']['text'] = text
            print("  [OK] 이미지 프롬프트 AI: 비주얼 장르 교체 + 금지패턴 강화")
            return 1

    print("  [ERROR] 이미지 프롬프트 AI 노드 없음")
    return 0


def fix_terms(nodes):
    """AI 주제 생성 1차/2차/3차에서 어려운 용어 교체 + 규칙 추가"""
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

            # 용어 교체
            for old_term, new_term in TERM_FIXES.items():
                if old_term in content:
                    content = content.replace(old_term, new_term)
                    changed = True

            # 용어 규칙 추가 (나레이션 필수 규칙 섹션에)
            if '어려운 영어 표현 금지' not in content:
                # 피드 최적화 필수 규칙 다음에 추가
                insert_point = content.find('나레이션 필수 규칙')
                if insert_point != -1:
                    # 나레이션 필수 규칙 섹션 끝에 추가
                    next_section = content.find('\n\n', insert_point + 10)
                    if next_section != -1:
                        content = content[:next_section] + TERM_RULE + content[next_section:]
                        changed = True

            if changed:
                m['content'] = content
                print(f"  [OK] {n['name']}: 용어 교체 + 규칙 추가")
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
    with open('/tmp/lumix_v3_image_terms.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_v3_image_terms.json',
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


def main():
    print("=" * 55)
    print("이미지 장르 교체 + 나레이션 용어 수정")
    print("=" * 55)

    print("\n[1/4] 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print("  [ERROR] 실패")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    print("\n[2/4] 이미지 프롬프트 AI 수정...")
    fix1 = fix_image_prompt(workflow['nodes'])

    print("\n[3/4] AI 주제 생성 용어 수정...")
    fix2 = fix_terms(workflow['nodes'])

    if fix1 + fix2 == 0:
        print("\n수정할 내용 없음")
        return

    print("\n[4/4] 업로드 + 재활성화...")
    if upload_workflow(workflow):
        reactivate()

    print("\n" + "=" * 55)
    print("수정 완료!")
    print("=" * 55)
    print("\n  이미지 장르 변경:")
    print("  제거: 자연 다큐, 수중/우주 판타지, 동양풍, 고딕 다크판타지, 팝아트")
    print("  추가: 럭셔리 프리미엄, 디지털 데이터, 비즈니스 코퍼레이트, 테크 서버룸, 모던 UI")
    print("\n  용어 변경:")
    print("  엔드-투-엔드 → 올인원")
    print("  커스텀 UI/UX → 맞춤 디자인 (프롬프트 규칙)")
    print("  DDoS → 해킹 공격 (프롬프트 규칙)")
    print("  API → 직접 연결 (프롬프트 규칙)")


if __name__ == "__main__":
    main()
