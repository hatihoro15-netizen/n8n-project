#!/usr/bin/env python3
"""
루믹스 v3 버그 수정:
1. YouTube 업로드/첫 댓글: $('주제 파싱') → $('시트 기록') (AI 검증 통과 콘텐츠 사용)
2. 스케줄: 12시간 간격 → 크론 표현식 (정시 실행)
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


def find_node(nodes, name):
    for i, n in enumerate(nodes):
        if n['name'] == name:
            return i, n
    return -1, None


def fix_youtube_upload(nodes):
    """YouTube 업로드: 주제 파싱 → 시트 기록 참조 변경"""
    idx, node = find_node(nodes, 'YouTube 업로드')
    if idx == -1:
        print("  [SKIP] YouTube 업로드 노드 없음")
        return

    params = node['parameters']
    changed = False

    # title
    if "주제 파싱" in str(params.get('title', '')):
        params['title'] = "={{ $('시트 기록').first().json.Subject }}"
        changed = True

    # description in options
    opts = params.get('options', {})
    if "주제 파싱" in str(opts.get('description', '')):
        opts['description'] = "={{ $('시트 기록').first().json.Caption }}"
        changed = True

    if changed:
        print("  [OK] YouTube 업로드: $('주제 파싱') → $('시트 기록') 참조 수정")
    else:
        print("  [INFO] YouTube 업로드: 이미 시트 기록 참조 중")


def fix_first_comment(nodes):
    """첫 댓글: 주제 파싱 → 시트 기록 참조 변경"""
    idx, node = find_node(nodes, '첫 댓글')
    if idx == -1:
        print("  [SKIP] 첫 댓글 노드 없음")
        return

    params = node['parameters']
    body = params.get('jsonBody', '')
    if "주제 파싱" in body:
        new_body = body.replace("$('주제 파싱')", "$('시트 기록')")
        params['jsonBody'] = new_body
        print("  [OK] 첫 댓글: $('주제 파싱') → $('시트 기록') 참조 수정")
    else:
        print("  [INFO] 첫 댓글: 이미 시트 기록 참조 중")


def fix_schedule(nodes):
    """스케줄 트리거: 12시간 간격 → 매일 12:00, 00:00 KST"""
    idx, node = find_node(nodes, '스케줄 트리거')
    if idx == -1:
        print("  [SKIP] 스케줄 트리거 없음")
        return

    # 12시간 간격 → 크론 (매일 03:00, 15:00 UTC = 12:00, 00:00 KST)
    node['parameters']['rule'] = {
        "interval": [{
            "field": "cronExpression",
            "expression": "0 3,15 * * *"
        }]
    }
    print("  [OK] 스케줄: 12시간 간격 → 크론 (매일 12:00, 00:00 KST)")


def upload_workflow(workflow_data):
    put_data = {
        "name": workflow_data.get("name"),
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "settings": {
            "executionOrder": workflow_data.get("settings", {}).get("executionOrder", "v1")
        }
    }

    with open('/tmp/lumix_v3_bugfix.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_v3_bugfix.json',
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
        active = response.get('active', '?')
        print(f"  [OK] 재활성화: active={active}")
    except Exception:
        print(f"  [WARN] 재활성화 응답 확인 필요")


def main():
    print("=" * 50)
    print("루믹스 v3 버그 수정")
    print("=" * 50)

    print("\n[1/4] 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print(f"  [ERROR] 실패")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    # 백업
    with open('/tmp/lumix_v3_pre_bugfix.json', 'w') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)

    nodes = workflow['nodes']

    print("\n[2/4] 참조 버그 수정...")
    fix_youtube_upload(nodes)
    fix_first_comment(nodes)

    print("\n[3/4] 스케줄 수정...")
    fix_schedule(nodes)

    print("\n[4/4] 업로드 + 재활성화...")
    if upload_workflow(workflow):
        reactivate()

    print("\n" + "=" * 50)
    print("수정 완료!")
    print("=" * 50)
    print("\n  변경 내용:")
    print("  1. YouTube 업로드 제목/설명: 검증 통과 콘텐츠 사용")
    print("  2. 첫 댓글: 검증 통과 콘텐츠 사용")
    print("  3. 스케줄: 매일 12:00, 00:00 KST 실행")


if __name__ == "__main__":
    main()
