#!/usr/bin/env python3
"""
숏폼 가이드 핵심 내용을 루믹스 v3 프롬프트에 반영
1. AI 주제 생성: 루프 구조, 완주율 최적화, 재사용 콘텐츠 방지
2. AI 검증: 평가 항목 강화 (루프/완주율/독창성)
3. AI 주제 생성 2차/3차도 동일 반영
"""
import json
import subprocess
import sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

# === 숏폼 가이드에서 추가할 규칙 ===
SHORTFORM_RULES = """
📌 숏폼 가이드 핵심 (완주율·재시청 극대화):
- 루프 구조 필수: 마지막 문장이 첫 문장과 자연스럽게 연결되어 재시청을 유도할 것 (예: 마지막 "그래서 결국..." → 첫 문장의 주제로 돌아오는 구조)
- 나레이션 흐름: 1~3초 훅(결론/충격/수치) → 약속(이 영상에서 알 수 있는 것) → 본문(정보 밀도 높게, 빈 구간 없이) → 마지막(루프 연결 or CTA)
- 매 문장마다 새로운 정보 또는 감정 변화를 넣어 이탈 방지
- 재사용 콘텐츠 방지: 매번 다른 각도, 다른 전개 방식, 독창적 표현 사용. 뻔한 패턴 반복 금지
- 제목: 30자 이내, 숫자/질문형/궁금증 유발, 이모지 1~2개 허용"""

# === 강화된 AI 검증 프롬프트 ===
ENHANCED_VERIFICATION = """아래 숏폼 콘텐츠를 6개 항목으로 평가해줘. 각 항목 1~10점.

[평가 대상]
Subject: {{{{ $('{source}').first().json.Subject }}}}
Narration: {{{{ $('{source}').first().json.Narration }}}}
Caption: {{{{ $('{source}').first().json.Caption }}}}

[평가 항목]
1. 훅 파워 - 첫 문장 1~3초 안에 스크롤을 멈추게 하는가? (결론 먼저/충격/수치/강한 질문. "안녕하세요" 류 인트로 절대 금지)
2. 루프·완주율 - 마지막 문장이 첫 문장과 자연 연결되는 루프 구조인가? 빈 구간 없이 매 문장 정보 밀도가 높은가?
3. 나레이션 품질 - 5문장 구성, 80~150자, 자연스러운 말투, 감정 흐름(불안→공감→해결→안도)이 있는가?
4. 클릭 유도력 - 제목이 30자 이내로 호기심/클릭 욕구를 유발하는가? (숫자/질문/비밀/방법 활용)
5. 타겟 적합도 - 카지노 솔루션 운영자/사업자 대상에 맞고, 간접 광고가 자연스러운가?
6. 독창성·차별화 - 뻔하지 않은 독창적 각도인가? 재사용 콘텐츠 판정 리스크 없이 고유한가?

반드시 아래 JSON으로만 응답:
{{
  "hook_power": 8,
  "topic_relevance": 7,
  "narration_quality": 9,
  "click_appeal": 7,
  "target_fit": 8,
  "differentiation": 6,
  "total": 45,
  "pass": true,
  "feedback": "통과/탈락 사유 1줄"
}}"""


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


def update_topic_generation(nodes):
    """AI 주제 생성 1차: 숏폼 가이드 규칙 추가"""
    idx, node = find_node(nodes, 'AI 주제 생성')
    if idx == -1:
        print("  [ERROR] AI 주제 생성 노드 없음")
        return

    content = node['parameters']['messages']['values'][0]['content']

    # 기존 "📌 나레이션 필수 규칙" 앞에 숏폼 가이드 규칙 삽입
    if '숏폼 가이드 핵심' in content:
        print("  [SKIP] AI 주제 생성: 이미 숏폼 가이드 반영됨")
        return

    # "📌 나레이션 필수 규칙" 앞에 삽입
    insert_point = content.find('📌 나레이션 필수 규칙')
    if insert_point == -1:
        # fallback: 끝에 추가
        content = content + SHORTFORM_RULES
    else:
        content = content[:insert_point] + SHORTFORM_RULES + '\n' + content[insert_point:]

    # 제목 길이 업데이트: "15자 이내" → "30자 이내"
    content = content.replace('15자 이내', '30자 이내')

    node['parameters']['messages']['values'][0]['content'] = content
    print("  [OK] AI 주제 생성 1차: 루프 구조 + 완주율 + 재사용방지 + 제목 30자")


def update_topic_generation_retry(nodes, name, round_num):
    """AI 주제 생성 2차/3차: 동일 규칙 추가"""
    idx, node = find_node(nodes, name)
    if idx == -1:
        print(f"  [SKIP] {name} 노드 없음")
        return

    content = node['parameters']['messages']['values'][0]['content']

    if '숏폼 가이드 핵심' in content:
        print(f"  [SKIP] {name}: 이미 반영됨")
        return

    insert_point = content.find('📌 나레이션 필수 규칙')
    if insert_point == -1:
        content = content + SHORTFORM_RULES
    else:
        content = content[:insert_point] + SHORTFORM_RULES + '\n' + content[insert_point:]

    content = content.replace('15자 이내', '30자 이내')

    node['parameters']['messages']['values'][0]['content'] = content
    print(f"  [OK] {name}: 숏폼 가이드 규칙 반영")


def update_verification(nodes, name, source):
    """AI 검증 프롬프트 강화"""
    idx, node = find_node(nodes, name)
    if idx == -1:
        print(f"  [SKIP] {name} 없음")
        return

    new_content = '=' + ENHANCED_VERIFICATION.format(source=source)
    node['parameters']['messages']['values'][0]['content'] = new_content
    print(f"  [OK] {name}: 루프·완주율·독창성 평가 강화")


def upload_workflow(workflow_data):
    put_data = {
        "name": workflow_data.get("name"),
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "settings": {
            "executionOrder": workflow_data.get("settings", {}).get("executionOrder", "v1")
        }
    }
    with open('/tmp/lumix_v3_shortform_guide.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_v3_shortform_guide.json',
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
    print("숏폼 가이드 반영: 루프 구조 + 완주율 + 독창성")
    print("=" * 55)

    # 1. 가져오기
    print("\n[1/5] 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print("  [ERROR] 실패")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드")

    with open('/tmp/lumix_v3_pre_guide.json', 'w') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)

    nodes = workflow['nodes']

    # 2. AI 주제 생성 프롬프트 업데이트
    print("\n[2/5] AI 주제 생성 프롬프트 (1차/2차/3차)...")
    update_topic_generation(nodes)
    update_topic_generation_retry(nodes, 'AI 주제 생성 2차', 2)
    update_topic_generation_retry(nodes, 'AI 주제 생성 3차', 3)

    # 3. AI 검증 프롬프트 업데이트
    print("\n[3/5] AI 검증 프롬프트 (1차/2차)...")
    update_verification(nodes, 'AI 검증 1', '주제 파싱')
    update_verification(nodes, 'AI 검증 2', '주제 파싱 2')

    # 4. 업로드
    print("\n[4/5] 업로드...")
    if upload_workflow(workflow):
        # 5. 재활성화
        print("\n[5/5] 재활성화...")
        reactivate()

    print("\n" + "=" * 55)
    print("반영 완료!")
    print("=" * 55)
    print("\n  추가된 숏폼 가이드 규칙:")
    print("  1. 루프 구조 필수 (마지막→첫 문장 자연 연결, 재시청 유도)")
    print("  2. 완주율 최적화 (빈 구간 금지, 매 문장 정보 밀도)")
    print("  3. 재사용 콘텐츠 방지 (매번 다른 각도·전개·표현)")
    print("  4. 제목 30자 이내 (숫자/질문형/궁금증)")
    print("  5. AI 검증 항목 강화:")
    print("     - '주제 관련성' → '루프·완주율' 평가로 변경")
    print("     - '차별화' → '독창성·재사용콘텐츠 리스크' 평가로 강화")
    print("     - 훅 평가: 인트로 금지 명시")
    print("     - 제목 평가: 30자 기준 + 구체적 패턴 명시")


if __name__ == "__main__":
    main()
