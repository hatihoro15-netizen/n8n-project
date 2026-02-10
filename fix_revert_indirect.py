#!/usr/bin/env python3
"""
간접 광고 관련 표현 원복
- 이모지/텔레그램 제거는 유지
- "간접 광고" 표현 원래대로 되돌리기
- "업종 직접 언급 금지" 규칙 원복
- "직접적 광고 느낌 X" 규칙 원복
"""
import json
import subprocess
import sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"


def fetch_workflow():
    result = subprocess.run([
        'curl', '-sk', '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


def revert_indirect(content):
    """간접 광고 관련 표현 원복"""
    original = content

    # 1. "마케팅 콘텐츠를 만들어줘" → "간접 광고 콘텐츠를 만들어줘"
    content = content.replace('마케팅 콘텐츠를 만들어줘', '간접 광고 콘텐츠를 만들어줘')

    # 2. "효과적인 광고" → "자연스러운 간접 광고"
    content = content.replace('효과적인 광고', '자연스러운 간접 광고')

    # 3. "광고가 효과적인가?" → "간접 광고가 자연스러운가?"
    content = content.replace('광고가 효과적인가?', '간접 광고가 자연스러운가?')

    # 4. "직접적 광고 느낌 X" 규칙 원복 (피드 최적화 필수 규칙 섹션에 추가)
    if '절대 직접적 광고 느낌 X' not in content and '"루믹스 솔루션"은 나레이션 후반부에' in content:
        content = content.replace(
            '- "루믹스 솔루션"은 나레이션 후반부에 1~2회만 자연스럽게 언급',
            '- "루믹스 솔루션"은 나레이션 후반부에 1~2회만 자연스럽게 언급\n- 절대 직접적 광고 느낌 X, 스토리텔링으로 자연스럽게'
        )

    # 5. "업종 직접 언급 금지" 규칙 원복 (나레이션 필수 규칙 섹션에 추가)
    if '업종 직접 언급 금지' not in content and '첫 문장 패턴 다양화' in content:
        content = content.replace(
            '- 첫 문장 패턴 다양화: 질문형/수치형/반전형/선언형/상황형/비교형/명령형 중 택1',
            '- 첫 문장 패턴 다양화: 질문형/수치형/반전형/선언형/상황형/비교형/명령형 중 택1\n- 본문에 업종 직접 언급 금지 (해시태그는 예외)'
        )

    return content, content != original


def fix_all(nodes):
    targets = ['AI 주제 생성', 'AI 주제 생성 2차', 'AI 주제 생성 3차',
               'AI 검증 1', 'AI 검증 2']
    fixed = 0

    for n in nodes:
        if n['name'] not in targets:
            continue

        msgs = n.get('parameters', {}).get('messages', {}).get('values', [])
        for m in msgs:
            content = m.get('content', '')
            if not content:
                continue

            new_content, changed = revert_indirect(content)
            if changed:
                m['content'] = new_content
                print(f"  [OK] {n['name']}: 간접 광고 표현 원복")
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
    with open('/tmp/lumix_v3_revert.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_v3_revert.json',
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
    print("=" * 50)
    print("간접 광고 표현 원복")
    print("=" * 50)

    print("\n[1/3] 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print("  [ERROR] 실패")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    print("\n[2/3] 간접 광고 표현 원복...")
    fixed = fix_all(workflow['nodes'])
    print(f"  총 {fixed}개 노드 수정")

    if fixed == 0:
        print("\n수정할 내용 없음")
        return

    print("\n[3/3] 업로드 + 재활성화...")
    if upload_workflow(workflow):
        reactivate()

    print("\n" + "=" * 50)
    print("원복 완료!")
    print("=" * 50)
    print("\n  유지된 것: 이모지 제거, 텔레그램 제거")
    print("  원복된 것: 간접 광고, 업종 직접 언급 금지, 직접적 광고 느낌 X")


if __name__ == "__main__":
    main()
