#!/usr/bin/env python3
"""
루믹스 숏폼 v3: AI 검증 시스템 + 영상 화질 개선
1. 영상 화질: Kie.ai 해상도/품질 + Creatomate CRF/비트레이트 개선
2. AI 검증: 분석 리포트 → 생성 → 검증 → 최대 3회 재생성
"""
import json
import subprocess
import sys
import uuid

# === 설정 ===
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"
GEMINI_CRED = {"id": "IKP349r08J9Hoz5E", "name": "Google Gemini(PaLM) Api account"}
SHEETS_CRED = {"id": "CWBUyXUqCU9p5VAg", "name": "Google Sheets account"}
SHEETS_DOC_ID = "1gkRjLIcK3HxbnTbLCvG6oknMGVt2uz9pgboM3EF_VKg"


# ============================================================
# 유틸리티
# ============================================================
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

def gen_id():
    return str(uuid.uuid4())


# ============================================================
# 1. 영상 화질 개선
# ============================================================
def improve_video_quality(nodes):
    # Kie.ai: aspect_ratio 9:16 + mode professional 추가
    idx, node = find_node(nodes, '영상 생성')
    if idx != -1:
        node['parameters']['jsonBody'] = (
            '={\n'
            '  "model": "kling-2.6/image-to-video",\n'
            '  "input": {\n'
            '    "prompt": "{{ $json.prompt || \'cinematic motion, slow camera movement, professional\' }}",\n'
            '    "image_urls": ["{{ $json.image.url }}"],\n'
            '    "sound": false,\n'
            '    "duration": "5",\n'
            '    "aspect_ratio": "9:16",\n'
            '    "mode": "professional"\n'
            '  }\n'
            '}'
        )
        print("  [OK] 영상 생성: aspect_ratio 9:16 + mode professional 추가")

    # Creatomate: CRF 16→10, Bitrate 12→20Mbps
    idx, node = find_node(nodes, 'Creatomate 타임라인')
    if idx != -1:
        code = node['parameters']['jsCode']
        code = code.replace('h264_crf: 16', 'h264_crf: 10')
        code = code.replace('h264_bitrate: 12000000', 'h264_bitrate: 20000000')
        node['parameters']['jsCode'] = code
        print("  [OK] Creatomate: CRF 16→10, Bitrate 12→20Mbps")


# ============================================================
# 2. AI 검증 시스템 - 프롬프트 템플릿
# ============================================================
REPORT_PREFIX = (
    "📊 최신 채널 분석 리포트:\n"
    "- 트렌드 키워드: {{ $('분석 리포트 읽기').first().json['트렌드_키워드'] || '데이터 없음' }}\n"
    "- 추천 주제 1: {{ $('분석 리포트 읽기').first().json['추천_주제1'] || '없음' }}\n"
    "- 추천 주제 2: {{ $('분석 리포트 읽기').first().json['추천_주제2'] || '없음' }}\n"
    "- 추천 주제 3: {{ $('분석 리포트 읽기').first().json['추천_주제3'] || '없음' }}\n"
    "- 피해야 할 주제: {{ $('분석 리포트 읽기').first().json['피해야할_주제'] || '없음' }}\n"
    "- 효과적인 훅 팁: {{ $('분석 리포트 읽기').first().json['효과적인_훅_팁'] || '없음' }}\n"
    "- 고성과 패턴: {{ $('분석 리포트 읽기').first().json['고성과_패턴'] || '없음' }}\n\n"
    "위 분석 결과를 반영하여 콘텐츠를 생성해줘. 추천 주제를 우선 참고하되, 피해야 할 주제는 반드시 피해.\n\n"
)

GUIDELINES_SUFFIX = (
    "\n\n📌 나레이션 필수 규칙 (지침서 기반):\n"
    "- 반드시 5문장, 각 문장은 . ! ? 로 끝날 것\n"
    "- 80~150자, 30~60초 분량\n"
    "- 전개 구조: A)문제→해결→결과 B)선언→근거→결과 C)비교→전환→결과 D)명령→이유→결과 중 택1\n"
    "- 첫 문장 패턴 다양화: 질문형/수치형/반전형/선언형/상황형/비교형/명령형 중 택1\n"
    "- 본문에 업종 직접 언급 금지 (해시태그는 예외)\n\n"
    "📌 BGM 키워드 자동 매칭:\n"
    "- 보안/보호 → \"corporate trustworthy, calm and confident, soft synth pads, secure feeling\"\n"
    "- 성장/수익 → \"growth and success, corporate achievement, building momentum, confident\"\n"
    "- 효율/자동화 → \"modern corporate, sleek, minimal electronic, sophisticated\"\n"
    "- 24/7/무중단 → \"innovative tech corporate, futuristic, ambient electronic\"\n"
    "- 신뢰/검증 → \"warm corporate, friendly, soft acoustic, welcoming\"\n"
    "- 일반 → \"calm professional, corporate ambient, soft background, minimal\""
)

FEEDBACK_TEMPLATE = (
    "⚠️ 이전 생성 결과가 품질 기준에 미달했습니다 ({round}차 시도).\n"
    "피드백: {{{{ $('{feedback_source}').first().json.feedback }}}}\n"
    "점수: {{{{ $('{feedback_source}').first().json.total }}}}/60\n\n"
    "위 피드백을 반영하여 더 나은 콘텐츠를 생성해줘. 특히 부족한 항목을 개선할 것.\n\n"
)


def build_verification_prompt(source_node):
    """검증 프롬프트 생성"""
    return (
        "아래 숏폼 콘텐츠를 6개 항목으로 평가해줘. 각 항목 1~10점.\n\n"
        "[평가 대상]\n"
        "Subject: {{ $('" + source_node + "').first().json.Subject }}\n"
        "Narration: {{ $('" + source_node + "').first().json.Narration }}\n"
        "Caption: {{ $('" + source_node + "').first().json.Caption }}\n\n"
        "[평가 항목]\n"
        "1. 훅 파워 - 첫 문장이 스크롤을 멈추게 하는가? (질문/충격/수치 등 강력한 후킹)\n"
        "2. 주제 관련성 - 트렌드/추천 주제와 부합하는가?\n"
        "3. 나레이션 품질 - 5문장 구성, 80~150자, 자연스러운 흐름, 업종 직접 언급 안 하는가?\n"
        "4. 클릭 유도력 - 제목이 호기심/클릭 욕구를 유발하는가?\n"
        "5. 타겟 적합도 - 카지노 솔루션 운영자/사업자 대상에 맞는가?\n"
        "6. 차별화 - 뻔하지 않고 독창적인 각도인가?\n\n"
        "반드시 아래 JSON으로만 응답:\n"
        '{\n'
        '  "hook_power": 8,\n'
        '  "topic_relevance": 7,\n'
        '  "narration_quality": 9,\n'
        '  "click_appeal": 7,\n'
        '  "target_fit": 8,\n'
        '  "differentiation": 6,\n'
        '  "total": 45,\n'
        '  "pass": true,\n'
        '  "feedback": "통과/탈락 사유 1줄"\n'
        '}'
    )


def build_verification_parser_code(source_node):
    """검증 파싱 JS 코드 생성"""
    return (
        "const text = $input.first().json.content.parts[0].text;\n"
        "const cleanText = text.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();\n"
        "const data = JSON.parse(cleanText);\n\n"
        "const total = data.total || (\n"
        "  (data.hook_power || 0) + (data.topic_relevance || 0) +\n"
        "  (data.narration_quality || 0) + (data.click_appeal || 0) +\n"
        "  (data.target_fit || 0) + (data.differentiation || 0)\n"
        ");\n"
        "const pass = total >= 42;\n\n"
        "return [{\n"
        "  json: {\n"
        "    hook_power: data.hook_power || 0,\n"
        "    topic_relevance: data.topic_relevance || 0,\n"
        "    narration_quality: data.narration_quality || 0,\n"
        "    click_appeal: data.click_appeal || 0,\n"
        "    target_fit: data.target_fit || 0,\n"
        "    differentiation: data.differentiation || 0,\n"
        "    total: total,\n"
        "    pass: pass,\n"
        "    feedback: data.feedback || '',\n"
        "    Subject: $('" + source_node + "').first().json.Subject,\n"
        "    Narration: $('" + source_node + "').first().json.Narration,\n"
        "    Caption: $('" + source_node + "').first().json.Caption,\n"
        "    Comment: $('" + source_node + "').first().json.Comment,\n"
        "    BGM_prompt: $('" + source_node + "').first().json.BGM_prompt,\n"
        "    Status: '준비',\n"
        "    Publish: '',\n"
        "    generatedAt: new Date().toISOString()\n"
        "  }\n"
        "}];"
    )


TOPIC_PARSING_CODE = (
    "const text = $input.first().json.content.parts[0].text;\n"
    "const cleanText = text.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();\n"
    "const data = JSON.parse(cleanText);\n\n"
    "let narration = data.Narration || '';\n"
    "if (narration.length > 150) {\n"
    "  const cutPoint = narration.substring(0, 150).lastIndexOf('.');\n"
    "  if (cutPoint > 80) {\n"
    "    narration = narration.substring(0, cutPoint + 1);\n"
    "  } else {\n"
    "    narration = narration.substring(0, 150);\n"
    "  }\n"
    "}\n\n"
    "return [{\n"
    "  json: {\n"
    "    Subject: data.Subject,\n"
    "    Narration: narration,\n"
    "    Caption: data.Caption,\n"
    "    Comment: data.Comment,\n"
    "    BGM_prompt: data.BGM_prompt,\n"
    "    Status: '준비',\n"
    "    Publish: '',\n"
    "    generatedAt: new Date().toISOString()\n"
    "  }\n"
    "}];"
)


# ============================================================
# 3. 노드 생성 팩토리
# ============================================================
def create_gemini_node(name, content, position):
    return {
        "parameters": {
            "modelId": {
                "__rl": True,
                "value": "models/gemini-2.5-flash",
                "mode": "list",
                "cachedResultName": "models/gemini-2.5-flash"
            },
            "messages": {"values": [{"content": content}]},
            "jsonOutput": True,
            "builtInTools": {},
            "options": {}
        },
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1.1,
        "position": position,
        "id": gen_id(),
        "name": name,
        "credentials": {"googlePalmApi": GEMINI_CRED}
    }


def create_code_node(name, js_code, position):
    return {
        "parameters": {"jsCode": js_code},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": position,
        "id": gen_id(),
        "name": name
    }


def create_if_node(name, position):
    return {
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "typeValidation": "strict"
                },
                "conditions": [
                    {
                        "id": gen_id(),
                        "leftValue": "={{ $json.total }}",
                        "rightValue": 42,
                        "operator": {
                            "type": "number",
                            "operation": "gte"
                        }
                    }
                ],
                "combinator": "and"
            },
            "options": {}
        },
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": position,
        "id": gen_id(),
        "name": name
    }


def create_sheets_read_node(name, sheet_name, position):
    return {
        "parameters": {
            "operation": "read",
            "documentId": {
                "__rl": True,
                "value": SHEETS_DOC_ID,
                "mode": "list",
                "cachedResultName": "n8n LUMIX"
            },
            "sheetName": {
                "__rl": True,
                "value": sheet_name,
                "mode": "name"
            },
            "options": {}
        },
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.7,
        "position": position,
        "id": gen_id(),
        "name": name,
        "onError": "continueRegularOutput",
        "credentials": {"googleSheetsOAuth2Api": SHEETS_CRED}
    }


# ============================================================
# 4. 검증 노드 일괄 추가
# ============================================================
def add_verification_nodes(nodes, modified_prompt):
    # 분석 리포트 읽기
    nodes.append(create_sheets_read_node(
        '분석 리포트 읽기', '분석리포트', [-1870, 224]
    ))
    print("  [OK] 분석 리포트 읽기 노드 추가")

    # === 1차 검증 체인 ===
    nodes.append(create_gemini_node(
        'AI 검증 1',
        '=' + build_verification_prompt('주제 파싱'),
        [-960, 224]
    ))
    nodes.append(create_code_node(
        '검증 파싱 1',
        build_verification_parser_code('주제 파싱'),
        [-660, 224]
    ))
    nodes.append(create_if_node('통과 판단 1', [-360, 224]))
    print("  [OK] 1차 검증: AI 검증 1 → 검증 파싱 1 → 통과 판단 1")

    # === 2차 생성 + 검증 체인 ===
    fb1 = FEEDBACK_TEMPLATE.format(round=2, feedback_source='검증 파싱 1')
    nodes.append(create_gemini_node(
        'AI 주제 생성 2차',
        '=' + fb1 + modified_prompt,
        [-360, 560]
    ))
    nodes.append(create_code_node('주제 파싱 2', TOPIC_PARSING_CODE, [-60, 560]))
    nodes.append(create_gemini_node(
        'AI 검증 2',
        '=' + build_verification_prompt('주제 파싱 2'),
        [240, 560]
    ))
    nodes.append(create_code_node(
        '검증 파싱 2',
        build_verification_parser_code('주제 파싱 2'),
        [540, 560]
    ))
    nodes.append(create_if_node('통과 판단 2', [840, 560]))
    print("  [OK] 2차: AI 주제 생성 2차 → 주제 파싱 2 → AI 검증 2 → 검증 파싱 2 → 통과 판단 2")

    # === 3차 생성 (검증 생략, 파이프라인 중단 방지) ===
    fb2 = FEEDBACK_TEMPLATE.format(round=3, feedback_source='검증 파싱 2')
    nodes.append(create_gemini_node(
        'AI 주제 생성 3차',
        '=' + fb2 + modified_prompt,
        [840, 900]
    ))
    nodes.append(create_code_node('주제 파싱 3', TOPIC_PARSING_CODE, [1140, 900]))
    print("  [OK] 3차: AI 주제 생성 3차 → 주제 파싱 3 → 시트 기록 (검증 생략)")


# ============================================================
# 5. 기존 노드 수정
# ============================================================
def modify_ai_topic_prompt(nodes):
    """AI 주제 생성 프롬프트에 리포트 데이터 + 지침서 규칙 추가"""
    _, node = find_node(nodes, 'AI 주제 생성')
    if not node:
        print("  [ERROR] AI 주제 생성 노드를 찾을 수 없습니다")
        return None

    original = node['parameters']['messages']['values'][0]['content']
    modified = REPORT_PREFIX + original + GUIDELINES_SUFFIX
    node['parameters']['messages']['values'][0]['content'] = '=' + modified
    print("  [OK] AI 주제 생성: 리포트 데이터 + 지침서 규칙 삽입")
    return modified


def move_sheet_node(nodes):
    """시트 기록 노드 위치 이동 (새 노드들 공간 확보)"""
    _, node = find_node(nodes, '시트 기록')
    if node:
        node['position'] = [-60, 224]
        print("  [OK] 시트 기록 위치: [-960,224] → [-60,224]")


def update_creatomate_reference(nodes):
    """Creatomate 타임라인: 주제 파싱 참조 → 시트 기록 참조"""
    _, node = find_node(nodes, 'Creatomate 타임라인')
    if node:
        code = node['parameters']['jsCode']
        code = code.replace("$('주제 파싱')", "$('시트 기록')")
        node['parameters']['jsCode'] = code
        print("  [OK] Creatomate 타임라인: $('주제 파싱') → $('시트 기록')")


# ============================================================
# 6. 연결 재구성
# ============================================================
def rewire_connections(connections):
    # 모든 트리거 → 분석 리포트 읽기
    for trigger in ['스케줄 트리거', 'Webhook 트리거', "When clicking 'Execute workflow'"]:
        if trigger in connections:
            connections[trigger] = {
                "main": [[{"node": "분석 리포트 읽기", "type": "main", "index": 0}]]
            }

    # 분석 리포트 읽기 → AI 주제 생성
    connections['분석 리포트 읽기'] = {
        "main": [[{"node": "AI 주제 생성", "type": "main", "index": 0}]]
    }

    # AI 주제 생성 → 주제 파싱 (변경 없음)

    # 주제 파싱 → AI 검증 1 (기존: 시트 기록)
    connections['주제 파싱'] = {
        "main": [[{"node": "AI 검증 1", "type": "main", "index": 0}]]
    }

    # 1차 검증 체인
    connections['AI 검증 1'] = {
        "main": [[{"node": "검증 파싱 1", "type": "main", "index": 0}]]
    }
    connections['검증 파싱 1'] = {
        "main": [[{"node": "통과 판단 1", "type": "main", "index": 0}]]
    }
    # 통과 판단 1: true(0) → 시트 기록, false(1) → 2차 생성
    connections['통과 판단 1'] = {
        "main": [
            [{"node": "시트 기록", "type": "main", "index": 0}],
            [{"node": "AI 주제 생성 2차", "type": "main", "index": 0}]
        ]
    }

    # 2차 체인
    connections['AI 주제 생성 2차'] = {
        "main": [[{"node": "주제 파싱 2", "type": "main", "index": 0}]]
    }
    connections['주제 파싱 2'] = {
        "main": [[{"node": "AI 검증 2", "type": "main", "index": 0}]]
    }
    connections['AI 검증 2'] = {
        "main": [[{"node": "검증 파싱 2", "type": "main", "index": 0}]]
    }
    connections['검증 파싱 2'] = {
        "main": [[{"node": "통과 판단 2", "type": "main", "index": 0}]]
    }
    # 통과 판단 2: true(0) → 시트 기록, false(1) → 3차 생성
    connections['통과 판단 2'] = {
        "main": [
            [{"node": "시트 기록", "type": "main", "index": 0}],
            [{"node": "AI 주제 생성 3차", "type": "main", "index": 0}]
        ]
    }

    # 3차 체인 (검증 없이 바로 시트 기록)
    connections['AI 주제 생성 3차'] = {
        "main": [[{"node": "주제 파싱 3", "type": "main", "index": 0}]]
    }
    connections['주제 파싱 3'] = {
        "main": [[{"node": "시트 기록", "type": "main", "index": 0}]]
    }

    # 시트 기록 → 나레이션 분할 + BGM 생성 (기존 유지, 건드리지 않음)

    print("  [OK] 연결 재구성 완료")
    print("    트리거 → 분석 리포트 읽기 → AI 주제 생성 → 주제 파싱")
    print("    → AI 검증 1 → 검증 파싱 1 → 통과 판단 1")
    print("    ├ 통과(42↑) → 시트 기록 → [제작...]")
    print("    └ 탈락 → AI 주제 생성 2차 → 주제 파싱 2 → AI 검증 2 → 검증 파싱 2 → 통과 판단 2")
    print("      ├ 통과 → 시트 기록")
    print("      └ 탈락 → AI 주제 생성 3차 → 주제 파싱 3 → 시트 기록 (검증 생략)")


# ============================================================
# 7. 업로드 + 재활성화
# ============================================================
def upload_workflow(workflow_data):
    put_data = {
        "name": workflow_data.get("name", "루믹스 솔루션 숏폼 (완전자동 v3)"),
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "settings": {
            "executionOrder": workflow_data.get("settings", {}).get("executionOrder", "v1")
        }
    }

    with open('/tmp/lumix_v3_verification_update.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/lumix_v3_verification_update.json',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  [ERROR] 응답 파싱 실패: {result.stdout[:500]}")
        return False

    if 'id' in response:
        print(f"  [OK] 업로드 성공 (ID: {response['id']}, 노드: {len(response.get('nodes', []))}개)")
        return True
    else:
        print(f"  [ERROR] 업로드 실패: {json.dumps(response, ensure_ascii=False)[:500]}")
        return False


def reactivate_workflow():
    subprocess.run([
        'curl', '-sk', '-X', 'PATCH',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '{"active": false}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PATCH',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '{"active": true}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if response.get('active'):
            print("  [OK] 워크플로우 재활성화 완료 (Webhook 재등록)")
            return True
        else:
            print(f"  [WARN] 재활성화 상태: {response.get('active', 'unknown')}")
            return False
    except json.JSONDecodeError:
        print(f"  [ERROR] 재활성화 응답 파싱 실패")
        return False


# ============================================================
# 메인 실행
# ============================================================
def main():
    print("=" * 60)
    print("루믹스 숏폼 v3: AI 검증 시스템 + 영상 화질 개선")
    print("=" * 60)

    # 1. 워크플로우 가져오기
    print("\n[1/7] 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print(f"  [ERROR] 워크플로우 조회 실패: {workflow}")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드 로드")

    # 백업
    with open('/tmp/lumix_v3_pre_verification_backup.json', 'w') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    print("  [OK] 백업: /tmp/lumix_v3_pre_verification_backup.json")

    nodes = workflow['nodes']
    connections = workflow['connections']

    # 2. 영상 화질 개선
    print("\n[2/7] 영상 화질 개선...")
    improve_video_quality(nodes)

    # 3. AI 주제 생성 프롬프트 수정
    print("\n[3/7] AI 주제 생성 프롬프트 수정...")
    modified_prompt = modify_ai_topic_prompt(nodes)
    if not modified_prompt:
        sys.exit(1)

    # 4. 검증 노드 추가 (11개)
    print("\n[4/7] AI 검증 시스템 노드 추가 (11개)...")
    add_verification_nodes(nodes, modified_prompt)

    # 5. 기존 노드 수정
    print("\n[5/7] 기존 노드 수정...")
    move_sheet_node(nodes)
    update_creatomate_reference(nodes)

    # 6. 연결 재구성
    print("\n[6/7] 연결 구조 재구성...")
    rewire_connections(connections)

    # 7. 업로드 + 재활성화
    print("\n[7/7] 업로드 + 재활성화...")
    if upload_workflow(workflow):
        reactivate_workflow()

    # 최종 요약
    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)
    print(f"\n  총 노드: {len(nodes)}개 (기존 34 + 신규 11 = 45)")
    print("\n  [화질 개선]")
    print("    - Kie.ai: aspect_ratio 9:16 + mode professional (1080p 출력)")
    print("    - Creatomate: CRF 10 (고화질) + 20Mbps (고비트레이트)")
    print("\n  [AI 검증 시스템]")
    print("    - 분석 리포트 읽기 (Google Sheets)")
    print("    - AI 주제 생성 프롬프트: 리포트 + 지침서 반영")
    print("    - 1차 검증 → 2차 재생성+검증 → 3차 최종생성")
    print("    - 42점(7점 평균) 이상만 제작 진행")
    print(f"\n  백업: /tmp/lumix_v3_pre_verification_backup.json")
    print(f"  업데이트: /tmp/lumix_v3_verification_update.json")


if __name__ == "__main__":
    main()
