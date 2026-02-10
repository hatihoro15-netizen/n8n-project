#!/usr/bin/env python3
"""
프롬프트 정리
1. 이모지 전부 제거 (📊 🏢 🎯 📌 ⚠️)
2. "간접 광고" → 직접 광고로 변경
3. 텔레그램 연락처 제거
"""
import json
import subprocess
import sys
import re

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

# 제거할 이모지 목록
EMOJIS = ['📊', '🏢', '🎯', '📌', '⚠️']


def fetch_workflow():
    result = subprocess.run([
        'curl', '-sk', '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


def clean_content(content):
    """프롬프트 내용 정리"""
    original = content

    # 1. 이모지 제거
    for emoji in EMOJIS:
        content = content.replace(emoji, '')

    # 2. 텔레그램 연락처 라인 제거
    content = re.sub(r'-\s*연락:\s*텔레그램\s*@\w+\n?', '', content)

    # 3. "간접 광고" → "광고" / "마케팅"
    content = content.replace('간접 광고 콘텐츠를 만들어줘', '마케팅 콘텐츠를 만들어줘')
    content = content.replace('자연스러운 간접 광고', '효과적인 광고')
    content = content.replace('간접 광고가 자연스러운가?', '광고가 효과적인가?')
    content = content.replace('간접 광고', '광고')

    # 4. "절대 직접적 광고 느낌 X, 스토리텔링으로 자연스럽게" 제거
    content = content.replace('- 절대 직접적 광고 느낌 X, 스토리텔링으로 자연스럽게\n', '')

    # 5. "본문에 업종 직접 언급 금지 (해시태그는 예외)" 제거
    content = content.replace('- 본문에 업종 직접 언급 금지 (해시태그는 예외)\n', '')

    # 6. 공백 정리 (이모지 제거 후 남는 앞 공백)
    # " 최신 채널" → "최신 채널" 같은 경우
    content = re.sub(r'\n ([가-힣])', r'\n\1', content)

    return content, content != original


def clean_all_prompts(nodes):
    """모든 프롬프트 노드의 내용 정리"""
    targets = ['AI 주제 생성', 'AI 주제 생성 2차', 'AI 주제 생성 3차',
               'AI 검증 1', 'AI 검증 2', '이미지 프롬프트 AI']
    fixed = 0

    for n in nodes:
        if n['name'] not in targets:
            continue

        msgs = n.get('parameters', {}).get('messages', {}).get('values', [])
        for i, m in enumerate(msgs):
            content = m.get('content', '')
            if not content:
                continue

            new_content, changed = clean_content(content)
            if changed:
                m['content'] = new_content
                print(f"  [OK] {n['name']}: 정리 완료")
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
    with open('/tmp/lumix_v3_cleanup.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_v3_cleanup.json',
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
    print("프롬프트 정리: 이모지/텔레그램/간접광고 제거")
    print("=" * 50)

    print("\n[1/3] 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print("  [ERROR] 실패")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    print("\n[2/3] 프롬프트 정리...")
    fixed = clean_all_prompts(workflow['nodes'])
    print(f"  총 {fixed}개 노드 수정")

    if fixed == 0:
        print("\n수정할 내용 없음")
        return

    print("\n[3/3] 업로드 + 재활성화...")
    if upload_workflow(workflow):
        reactivate()

    print("\n" + "=" * 50)
    print("정리 완료!")
    print("=" * 50)
    print("\n  변경 사항:")
    print("  1. 이모지 제거 (📊 🏢 🎯 📌 ⚠️)")
    print("  2. 텔레그램 @conggal20 연락처 제거")
    print("  3. '간접 광고' → '광고/마케팅' 직접 표현으로 변경")
    print("  4. '업종 직접 언급 금지' 규칙 제거")
    print("  5. '직접적 광고 느낌 X' 규칙 제거")


if __name__ == "__main__":
    main()
