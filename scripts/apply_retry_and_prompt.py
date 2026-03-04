#!/usr/bin/env python3
"""
AI 주제 생성 프롬프트 강화 + 리트라이 판단 노드 추가
- 수정 1: AI 주제 생성 프롬프트에 subtopic 주입, 해당 카테고리만 설명
- 수정 2: 리트라이 판단 노드 추가 + 연결 변경 (주제 파싱 에러 → 리트라이 → AI 주제 생성 루프)
"""
import json
import copy

FILE = 'claude-tools/onca_shortform_v16.json'

# === 1. 새 프롬프트 (n8n expression 문법 사용) ===
NEW_PROMPT = """너는 '온카스터디' 커뮤니티의 YouTube Shorts 주제 기획자야.

**{{ $json.category }}번 카테고리**, 소재: '{{ $json.subtopic }}'

이 소재 범위 안에서만 주제(topic) 1개를 만들어.
소재와 무관한 키워드는 절대 넣지 마.

카테고리별 톤 ({{ $json.category }}번만 참고)
{{ $json.category == 1 ? '1) 안전/먹튀검증 썰 → 경고/분노/충격 가능' : $json.category == 2 ? '2) 무료 혜택/앱테크 → 공짜/이득/꿀팁만' : $json.category == 3 ? '3) 잭팟/후기 → 대박/부러움/인증만' : $json.category == 4 ? '4) 방송 하이라이트 → 재미/반전/현장감만' : '5) 스포츠/카지노 뉴스·분석 → 이슈 1개만' }}

절대 금지:
{{ $json.category != 1 ? '- "먹튀", "사기", "잃", "날리", "증발", "피해", "털렸" 같은 손실/범죄 단어 사용 금지' : '' }}
{{ $json.category != 3 ? '- "잭팟", "대박", "당첨" 같은 잭팟 단어 사용 금지' : '' }}
- 소재('{{ $json.subtopic }}')와 무관한 다른 카테고리 키워드 혼합 금지
- "이거 실화냐/이거 가능해/이거 알아" 같은 패턴 금지
- "/" "등" "그리고" 같은 나열 표현 금지

제목(Topic) 규칙
- 20~40자, 클릭을 부르는 후킹 문장 1개
- topic 문장 안에 '온카스터디'를 자연스럽게 1회 포함

출력 형식 (순수 JSON만, 코드블록 없이):
- JSON 값 안에 쌍따옴표(")나 줄바꿈 문자를 절대 넣지 마!
{"topic": ""}"""

# === 2. 리트라이 판단 Code 노드 ===
RETRY_NODE = {
    "parameters": {
        "mode": "runOnceForEachItem",
        "jsCode": """/**
 * 리트라이 판단
 * 주제 파싱 검증 실패 시 최대 2회 재시도, 이후 에러 경로
 * @returns {Array} output[0]=retry, output[1]=give up
 */
const input = $input.first().json;
const catData = $('카테고리 결정').first().json;
const prevRetry = catData.topicRetryCount || 0;
const maxRetries = 2;

if (prevRetry < maxRetries) {
  // 재시도: 카테고리 결정 데이터를 다시 AI 주제 생성으로 전달
  const retryData = {
    category: catData.category,
    outroFile: catData.outroFile,
    outroCta: catData.outroCta,
    subtopic: catData.subtopic,
    outroDuration: catData.outroDuration,
    sequenceInfo: catData.sequenceInfo,
    topicRetryCount: prevRetry + 1
  };
  return [[{ json: retryData }], []];
} else {
  // 포기: 에러 데이터를 주제 파싱 에러 준비로 전달
  return [[], [{ json: input }]];
}"""
    },
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1960, 460],
    "id": "retry-judge-node-001",
    "name": "리트라이 판단",
    "onError": "continueRegularOutput"
}

def find_node(nodes, name):
    """노드 리스트에서 이름으로 노드 찾기"""
    for i, n in enumerate(nodes):
        if n['name'] == name:
            return i, n
    return None, None

def update_prompt(nodes):
    """AI 주제 생성 노드의 프롬프트 업데이트"""
    idx, node = find_node(nodes, 'AI 주제 생성')
    if idx is None:
        print("  WARNING: AI 주제 생성 노드를 찾을 수 없음")
        return False
    node['parameters']['messages']['values'][0]['content'] = NEW_PROMPT
    print(f"  AI 주제 생성 프롬프트 업데이트 완료 (index {idx})")
    return True

def add_retry_node(nodes):
    """리트라이 판단 노드 추가 (이미 있으면 스킵)"""
    idx, node = find_node(nodes, '리트라이 판단')
    if idx is not None:
        print(f"  리트라이 판단 노드 이미 존재 (index {idx})")
        return True
    nodes.append(copy.deepcopy(RETRY_NODE))
    print(f"  리트라이 판단 노드 추가 완료 (index {len(nodes)-1})")
    return True

def update_connections(connections, has_error_prep=True):
    """
    주제 파싱 연결 변경:
    - output[1] (에러) → 리트라이 판단 (기존: 주제 파싱 에러 준비)
    리트라이 판단 연결 추가:
    - output[0] (retry) → AI 주제 생성
    - output[1] (give up) → 주제 파싱 에러 준비
    """
    # 주제 파싱 connections 업데이트
    tp = connections.get('주제 파싱', {})
    tp_main = tp.get('main', [])

    # output[1]이 없으면 추가
    while len(tp_main) < 2:
        tp_main.append([])

    # output[1] → 리트라이 판단
    tp_main[1] = [{"node": "리트라이 판단", "type": "main", "index": 0}]
    tp['main'] = tp_main
    connections['주제 파싱'] = tp
    print(f"  주제 파싱 output[1] → 리트라이 판단 연결 완료")

    # 리트라이 판단 connections 추가
    connections['리트라이 판단'] = {
        "main": [
            # output[0] (retry) → AI 주제 생성
            [{"node": "AI 주제 생성", "type": "main", "index": 0}],
            # output[1] (give up) → 주제 파싱 에러 준비
            [{"node": "주제 파싱 에러 준비", "type": "main", "index": 0}] if has_error_prep else []
        ]
    }
    if has_error_prep:
        print(f"  리트라이 판단 output[0] → AI 주제 생성, output[1] → 주제 파싱 에러 준비 연결 완료")
    else:
        print(f"  리트라이 판단 output[0] → AI 주제 생성 연결 완료 (에러 준비 노드 없음)")

def main():
    with open(FILE) as f:
        data = json.load(f)

    # === Top-level 수정 ===
    print("=== Top-level 수정 ===")
    update_prompt(data['nodes'])
    add_retry_node(data['nodes'])
    update_connections(data['connections'], has_error_prep=True)
    print(f"  총 노드 수: {len(data['nodes'])}")

    # === activeVersion 수정 ===
    print("\n=== activeVersion 수정 ===")
    av = data['activeVersion']
    update_prompt(av['nodes'])
    add_retry_node(av['nodes'])

    # activeVersion에 주제 파싱 에러 준비가 있는지 확인
    _, err_prep = find_node(av['nodes'], '주제 파싱 에러 준비')
    has_err_prep = err_prep is not None
    print(f"  주제 파싱 에러 준비 존재: {has_err_prep}")
    update_connections(av['connections'], has_error_prep=has_err_prep)
    print(f"  총 노드 수: {len(av['nodes'])}")

    # === 저장 ===
    with open(FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n파일 저장 완료: {FILE}")

if __name__ == '__main__':
    main()
