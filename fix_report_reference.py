#!/usr/bin/env python3
"""
분석 리포트 읽기 참조 에러 수정
- 분석리포트 시트가 없어도 워크플로우 정상 동작
- $('분석 리포트 읽기') 참조 → $if 안전장치 적용
"""
import json
import subprocess
import sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

# 안전한 참조 패턴: $if(노드.isExecuted, 값, 기본값)
SAFE_REPORT_BLOCK = """📊 최신 채널 분석 리포트:
- 트렌드 키워드: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['트렌드_키워드'], '데이터 없음') }}
- 추천 주제 1: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['추천_주제1'], '없음') }}
- 추천 주제 2: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['추천_주제2'], '없음') }}
- 추천 주제 3: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['추천_주제3'], '없음') }}
- 피해야 할 주제: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['피해야할_주제'], '없음') }}
- 효과적인 훅 팁: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['효과적인_훅_팁'], '없음') }}
- 고성과 패턴: {{ $if($('분석 리포트 읽기').isExecuted, $('분석 리포트 읽기').first().json['고성과_패턴'], '없음') }}

위 분석 결과를 반영하여 콘텐츠를 생성해줘. 추천 주제를 우선 참고하되, 피해야 할 주제는 반드시 피해.

"""

# 기존 안전하지 않은 참조 패턴
UNSAFE_REPORT_BLOCK_START = "📊 최신 채널 분석 리포트:"
UNSAFE_REPORT_BLOCK_END = "위 분석 결과를 반영하여 콘텐츠를 생성해줘. 추천 주제를 우선 참고하되, 피해야 할 주제는 반드시 피해.\n\n"


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


def fix_report_references(nodes):
    """모든 분석 리포트 읽기 참조를 $if 안전장치로 교체"""
    fixed = 0
    for n in nodes:
        if 'messages' not in n.get('parameters', {}):
            continue

        values = n['parameters']['messages'].get('values', [])
        for val in values:
            content = val.get('content', '')
            if UNSAFE_REPORT_BLOCK_START in content and "$if($('분석 리포트 읽기')" not in content:
                # 기존 안전하지 않은 블록 찾기
                start = content.find(UNSAFE_REPORT_BLOCK_START)
                end = content.find(UNSAFE_REPORT_BLOCK_END)
                if start != -1 and end != -1:
                    end += len(UNSAFE_REPORT_BLOCK_END)
                    new_content = content[:start] + SAFE_REPORT_BLOCK + content[end:]
                    val['content'] = new_content
                    print(f"  [OK] {n['name']}: $if 안전장치 적용")
                    fixed += 1
            elif "$if($('분석 리포트 읽기')" in content:
                print(f"  [SKIP] {n['name']}: 이미 안전장치 적용됨")

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
    with open('/tmp/lumix_v3_fix_report.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_v3_fix_report.json',
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
    print("분석 리포트 참조 에러 수정")
    print("=" * 50)

    print("\n[1/3] 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print("  [ERROR] 실패")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    nodes = workflow['nodes']

    print("\n[2/3] 분석 리포트 참조 안전장치 적용...")
    fixed = fix_report_references(nodes)
    print(f"  총 {fixed}개 노드 수정")

    print("\n[3/3] 업로드 + 재활성화...")
    if upload_workflow(workflow):
        reactivate()

    print("\n" + "=" * 50)
    print("수정 완료!")
    print("=" * 50)
    print("\n  변경: $('분석 리포트 읽기').first().json[...]")
    print("  → $if($('분석 리포트 읽기').isExecuted, ..., '기본값')")
    print("  분석리포트 시트가 없어도 워크플로우 정상 동작")


if __name__ == "__main__":
    main()
