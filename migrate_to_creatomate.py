#!/usr/bin/env python3
"""
루믹스 숏폼 v3: Shotstack → Creatomate 마이그레이션 + 나레이션 길이 제어
- "전용" 워크플로우의 Creatomate 연동 패턴 참고 (기술적 구조만)
- 프롬프트는 기존 v3 유지, 글자수만 조정
"""
import json
import subprocess
import sys
import copy

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "9YOHS8N1URWlzGWj"

# Creatomate 설정 (전용 워크플로우에서 가져옴)
CREATOMATE_CRED_ID = "8MwB6jdj2a2b3OV7"
CREATOMATE_CRED_NAME = "Header Auth account 4"
CREATOMATE_TEMPLATE_ID = "056a9082-710f-4345-b964-c6384103fbf6"

def fetch_workflow():
    """n8n API에서 현재 워크플로우 가져오기"""
    result = subprocess.run([
        'curl', '-sk',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)

def find_node(nodes, name):
    """이름으로 노드 찾기"""
    for i, n in enumerate(nodes):
        if n['name'] == name:
            return i, n
    return -1, None

def modify_ai_topic_prompt(nodes):
    """AI 주제 생성 프롬프트 수정 - 나레이션 80~150자 제한"""
    idx, node = find_node(nodes, 'AI 주제 생성')
    if idx == -1:
        print("  [ERROR] AI 주제 생성 노드를 찾을 수 없습니다")
        return False

    messages = node['parameters']['messages']['values']
    for msg in messages:
        content = msg.get('content', '')

        # 나레이션 글자수 변경: 200~350자 → 80~150자
        content = content.replace('200~350자', '80~150자')

        # 30~50초 → 30~60초
        content = content.replace('30~50초', '30~60초')

        # JSON 출력 형식 안의 설명도 변경
        content = content.replace(
            '30~50초 분량, 200~350자',
            '30~60초 분량, 80~150자'
        )

        msg['content'] = content

    print("  [OK] AI 주제 생성 프롬프트: 나레이션 80~150자, 30~60초로 변경")
    return True

def modify_narration_split_prompt(nodes):
    """나레이션 분할 프롬프트 수정 - 각 파트 15~30자"""
    idx, node = find_node(nodes, '나레이션 분할')
    if idx == -1:
        print("  [ERROR] 나레이션 분할 노드를 찾을 수 없습니다")
        return False

    messages = node['parameters']['messages']['values']
    for msg in messages:
        content = msg.get('content', '')

        # "5개 문장으로 나눠줘" → "5개 짧은 문장으로 나눠줘, 각 문장 15~30자"
        content = content.replace(
            '다음 나레이션을 5개 문장으로 나눠줘.',
            '다음 나레이션을 5개 짧은 문장으로 나눠줘. 각 문장은 15~30자 이내로.'
        )

        # 규칙에 글자수 제한 추가
        content = content.replace(
            '2. 각 문장은 비슷한 길이로 균등하게 배분해',
            '2. 각 문장은 비슷한 길이로 균등하게 배분해 (15~30자)'
        )

        msg['content'] = content

    print("  [OK] 나레이션 분할 프롬프트: 각 파트 15~30자 제한 추가")
    return True

def modify_topic_parsing(nodes):
    """주제 파싱 코드에 글자수 검증 추가"""
    idx, node = find_node(nodes, '주제 파싱')
    if idx == -1:
        print("  [ERROR] 주제 파싱 노드를 찾을 수 없습니다")
        return False

    node['parameters']['jsCode'] = """const text = $input.first().json.content.parts[0].text;
// Remove potential markdown code blocks
const cleanText = text.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();
const data = JSON.parse(cleanText);

// 나레이션 글자수 검증 (150자 초과 시 잘라내기)
let narration = data.Narration || '';
if (narration.length > 150) {
  // 150자 근처에서 문장 끝(마침표/물음표/느낌표)에서 자르기
  const cutPoint = narration.substring(0, 150).lastIndexOf('.');
  if (cutPoint > 80) {
    narration = narration.substring(0, cutPoint + 1);
  } else {
    narration = narration.substring(0, 150);
  }
}

return [{
  json: {
    Subject: data.Subject,
    Narration: narration,
    Caption: data.Caption,
    Comment: data.Comment,
    BGM_prompt: data.BGM_prompt,
    Status: '준비',
    Publish: '',
    generatedAt: new Date().toISOString()
  }
}];"""

    print("  [OK] 주제 파싱: 나레이션 150자 초과 시 자동 절삭 추가")
    return True

def replace_shotstack_with_creatomate(nodes):
    """Shotstack 타임라인 → Creatomate 타임라인 교체"""
    idx, node = find_node(nodes, 'Shotstack 타임라인')
    if idx == -1:
        print("  [ERROR] Shotstack 타임라인 노드를 찾을 수 없습니다")
        return False

    # 노드 이름 변경 + 코드 교체 (전용 패턴 기반)
    node['name'] = 'Creatomate 타임라인'
    node['parameters']['jsCode'] = """// === Creatomate 타임라인 빌더 ===
// "전용" 워크플로우 패턴 기반 - 템플릿 + modifications 방식
const bgmUrl = $('BGM 대기').first().json.audio?.url || '';
const videoDuration = 5;
const bitrate = 128000;
let totalDuration = 0;

const modifications = {};

for (let i = 0; i < 5; i++) {
  const n = i + 1;

  // TTS 결과
  const ttsResult = $('TTS 결과').all()[i]?.json;
  const narrationUrl = ttsResult?.audio?.url || '';
  const fileSize = ttsResult?.audio?.file_size || 40000;

  // 오디오 파일 크기로 duration 추정
  let duration = Math.round((fileSize * 8 / bitrate) * 100) / 100;
  if (duration < 3) duration = 5;

  // 영상 speed 계산 (5초 영상을 나레이션 길이에 맞게)
  let speed = "100" + String.fromCharCode(37);
  if (duration > videoDuration) {
    speed = Math.round((videoDuration / duration) * 100) + String.fromCharCode(37);
  }

  // 영상 URL
  const videoResult = $('영상 URL 정리').all()[i]?.json;
  const videoUrl = videoResult?.video?.url || '';

  // 자막 텍스트
  const subtitleText = ($('5파트 분리').all()[i]?.json?.text || '').replace(/\\n/g, '\\\\n');

  // Creatomate modifications
  modifications[`Composition-${n}.duration`] = String(duration);
  modifications[`Video-${n}.source`] = videoUrl;
  modifications[`Video-${n}.speed`] = speed;
  modifications[`Narration-${n}.source`] = narrationUrl;
  modifications[`Text-${n}.text`] = subtitleText;

  totalDuration += duration;
}

// BGM
modifications['BGM.source'] = bgmUrl;

// 엔딩카드 시작점
modifications['Video-T24.time'] = String(totalDuration);

const payload = {
  template_id: "TMPL_ID_PLACEHOLDER",
  output_format: "mp4",
  h264_profile: "high",
  h264_level: "5.2",
  h264_crf: 16,
  h264_bitrate: 12000000,
  frame_rate: 30,
  duration: String(totalDuration + 8),
  modifications: modifications
};

return [{
  json: {
    creatomate_payload: payload,
    modifications: modifications,
    subject: $('주제 파싱').first().json.Subject,
    caption: $('주제 파싱').first().json.Caption,
    comment: $('주제 파싱').first().json.Comment
  }
}];""".replace('TMPL_ID_PLACEHOLDER', CREATOMATE_TEMPLATE_ID)

    print("  [OK] Shotstack 타임라인 → Creatomate 타임라인 코드 교체")
    return True

def replace_shotstack_render(nodes):
    """Shotstack 렌더 → Creatomate 렌더 교체"""
    idx, node = find_node(nodes, 'Shotstack 렌더')
    if idx == -1:
        print("  [ERROR] Shotstack 렌더 노드를 찾을 수 없습니다")
        return False

    node['name'] = 'Creatomate 렌더'
    node['parameters'] = {
        "method": "POST",
        "url": "https://api.creatomate.com/v1/renders",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json.creatomate_payload) }}",
        "options": {
            "timeout": 600000
        }
    }
    node['credentials'] = {
        "httpHeaderAuth": {
            "id": CREATOMATE_CRED_ID,
            "name": CREATOMATE_CRED_NAME
        }
    }

    print("  [OK] Shotstack 렌더 → Creatomate 렌더 (동기 호출, timeout 10분)")
    return True

def remove_render_wait_and_result(nodes, connections):
    """렌더 대기/렌더 결과 노드 삭제 (Creatomate는 동기 호출이므로 불필요)"""
    removed = []
    for name in ['렌더 대기', '렌더 결과']:
        idx, node = find_node(nodes, name)
        if idx != -1:
            nodes.pop(idx)
            removed.append(name)
            # 연결에서도 삭제
            if name in connections:
                del connections[name]

    print(f"  [OK] 삭제된 노드: {', '.join(removed)}")
    return True

def update_connections(connections):
    """연결 구조 업데이트"""
    # Shotstack 타임라인 → Creatomate 타임라인 이름 변경
    if 'Shotstack 타임라인' in connections:
        connections['Creatomate 타임라인'] = connections.pop('Shotstack 타임라인')

    # Aggregate → Creatomate 타임라인 연결 업데이트
    if 'Aggregate' in connections:
        for output in connections['Aggregate']['main']:
            for target in output:
                if target['node'] == 'Shotstack 타임라인':
                    target['node'] = 'Creatomate 타임라인'

    # Creatomate 타임라인 → Creatomate 렌더 연결 업데이트
    if 'Creatomate 타임라인' in connections:
        for output in connections['Creatomate 타임라인']['main']:
            for target in output:
                if target['node'] == 'Shotstack 렌더':
                    target['node'] = 'Creatomate 렌더'

    # Shotstack 렌더 → Creatomate 렌더 이름 변경
    if 'Shotstack 렌더' in connections:
        connections['Creatomate 렌더'] = connections.pop('Shotstack 렌더')

    # Creatomate 렌더의 출력을 직접 상태 업데이트 + 영상 다운로드로 연결
    # (렌더 대기/렌더 결과 경유하지 않음 - 동기 호출이므로)
    connections['Creatomate 렌더'] = {
        "main": [
            [
                {"node": "상태 업데이트", "type": "main", "index": 0},
                {"node": "영상 다운로드", "type": "main", "index": 0}
            ]
        ]
    }

    print("  [OK] 연결 구조: Aggregate → Creatomate 타임라인 → Creatomate 렌더 → 상태 업데이트 + 영상 다운로드")
    return True

def update_status_update_node(nodes):
    """상태 업데이트 Expression 수정: response.url → url (Creatomate 동기 응답)"""
    idx, node = find_node(nodes, '상태 업데이트')
    if idx == -1:
        print("  [ERROR] 상태 업데이트 노드를 찾을 수 없습니다")
        return False

    columns = node['parameters']['columns']
    value = columns['value']

    # Shotstack: $json.response.url → Creatomate: $json.url
    if '업로드 URL' in value:
        old_val = value['업로드 URL']
        value['업로드 URL'] = old_val.replace('$json.response.url', '$json.url')
        print(f"  [OK] 상태 업데이트: 업로드 URL expression → $json.url")

    return True

def update_video_download_node(nodes):
    """영상 다운로드 URL Expression 수정"""
    idx, node = find_node(nodes, '영상 다운로드')
    if idx == -1:
        print("  [ERROR] 영상 다운로드 노드를 찾을 수 없습니다")
        return False

    # Shotstack: $json.response.url → Creatomate: $json.url
    url = node['parameters'].get('url', '')
    node['parameters']['url'] = url.replace('$json.response.url', '$json.url')

    print("  [OK] 영상 다운로드: URL expression → $json.url")
    return True

def fix_publish_complete_node(nodes):
    """발행 완료 노드: row_number → Subject 매칭"""
    idx, node = find_node(nodes, '발행 완료')
    if idx == -1:
        print("  [ERROR] 발행 완료 노드를 찾을 수 없습니다")
        return False

    columns = node['parameters']['columns']

    # matchingColumns 변경
    columns['matchingColumns'] = ['Subject']

    # value에서 row_number 제거, Subject 추가
    value = columns['value']
    if 'row_number' in value:
        del value['row_number']
    value['Subject'] = "={{ $('시트 기록').first().json.Subject }}"

    # schema 업데이트 - Subject를 매칭 가능하게
    for s in columns.get('schema', []):
        if s['id'] == 'row_number':
            s['removed'] = True
        if s['id'] == 'Subject':
            s['removed'] = False
            s['canBeUsedToMatch'] = True

    # Subject가 schema에 없으면 추가
    has_subject = any(s['id'] == 'Subject' for s in columns.get('schema', []))
    if not has_subject:
        columns['schema'].insert(0, {
            "id": "Subject",
            "displayName": "Subject",
            "required": False,
            "defaultMatch": False,
            "display": True,
            "type": "string",
            "canBeUsedToMatch": True
        })

    print("  [OK] 발행 완료: matchingColumns row_number → Subject")
    return True

def upload_workflow(workflow_data):
    """수정된 워크플로우를 n8n에 업로드"""
    # PUT 요청에 필요한 필드만 포함
    put_data = {
        "name": workflow_data.get("name", "루믹스 솔루션 숏폼 (완전자동 v3)"),
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "settings": {
            "executionOrder": workflow_data.get("settings", {}).get("executionOrder", "v1")
        }
    }

    put_json = json.dumps(put_data, ensure_ascii=False)

    # 임시 파일에 저장
    with open('/tmp/lumix_v3_updated.json', 'w') as f:
        f.write(put_json)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', f'@/tmp/lumix_v3_updated.json',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    response = json.loads(result.stdout)
    if 'id' in response:
        print(f"  [OK] 워크플로우 업로드 성공 (ID: {response['id']})")
        return True
    else:
        print(f"  [ERROR] 업로드 실패: {response}")
        return False

def reactivate_workflow():
    """워크플로우 비활성화 후 재활성화 (Webhook 재등록)"""
    # 비활성화
    result = subprocess.run([
        'curl', '-sk', '-X', 'PATCH',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '{"active": false}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    # 활성화
    result = subprocess.run([
        'curl', '-sk', '-X', 'PATCH',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '{"active": true}',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    response = json.loads(result.stdout)
    if response.get('active') == True:
        print("  [OK] 워크플로우 재활성화 완료")
        return True
    else:
        print(f"  [WARN] 재활성화 상태: {response.get('active', 'unknown')}")
        return False

def main():
    print("=" * 60)
    print("루믹스 숏폼 v3: Shotstack → Creatomate 마이그레이션")
    print("=" * 60)

    # 1. 현재 워크플로우 가져오기
    print("\n[1/8] 현재 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print(f"  [ERROR] 워크플로우 조회 실패: {workflow}")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드 로드")

    # 백업 저장
    with open('/tmp/lumix_v3_backup.json', 'w') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    print("  [OK] 백업 저장: /tmp/lumix_v3_backup.json")

    nodes = workflow['nodes']
    connections = workflow['connections']

    # 2. AI 주제 생성 프롬프트 수정
    print("\n[2/8] AI 주제 생성 프롬프트 수정 (나레이션 80~150자)...")
    modify_ai_topic_prompt(nodes)

    # 3. 나레이션 분할 프롬프트 수정
    print("\n[3/8] 나레이션 분할 프롬프트 수정 (각 파트 15~30자)...")
    modify_narration_split_prompt(nodes)

    # 4. 주제 파싱 글자수 검증 추가
    print("\n[4/8] 주제 파싱 글자수 검증 추가...")
    modify_topic_parsing(nodes)

    # 5. Shotstack → Creatomate 노드 교체
    print("\n[5/8] Shotstack → Creatomate 노드 교체...")
    replace_shotstack_with_creatomate(nodes)
    replace_shotstack_render(nodes)
    remove_render_wait_and_result(nodes, connections)

    # 6. 연결 구조 업데이트
    print("\n[6/8] 연결 구조 업데이트...")
    update_connections(connections)

    # 7. Expression 수정 + 발행 완료 수정
    print("\n[7/8] Expression 수정 + 발행 완료 수정...")
    update_status_update_node(nodes)
    update_video_download_node(nodes)
    fix_publish_complete_node(nodes)

    # 8. 업로드 + 재활성화
    print("\n[8/8] 워크플로우 업로드 + 재활성화...")
    if upload_workflow(workflow):
        reactivate_workflow()

    # 최종 확인
    print("\n" + "=" * 60)
    print("마이그레이션 완료!")
    print("=" * 60)
    print("\n변경 요약:")
    print("  1. AI 주제 생성: 나레이션 200~350자 → 80~150자")
    print("  2. 나레이션 분할: 각 파트 15~30자 제한 추가")
    print("  3. 주제 파싱: 150자 초과 시 자동 절삭 안전장치")
    print("  4. Shotstack 타임라인 → Creatomate 타임라인 (Code)")
    print("  5. Shotstack 렌더 → Creatomate 렌더 (동기 HTTP POST)")
    print("  6. 렌더 대기/렌더 결과 삭제 (동기 호출이므로 불필요)")
    print("  7. 상태 업데이트/영상 다운로드: $json.response.url → $json.url")
    print("  8. 발행 완료: matchingColumns row_number → Subject")
    print(f"\n  Creatomate 크레덴셜: {CREATOMATE_CRED_ID}")
    print(f"  Creatomate 템플릿: {CREATOMATE_TEMPLATE_ID}")
    print(f"\n  수정된 JSON 저장: /tmp/lumix_v3_updated.json")
    print(f"  백업 JSON 저장: /tmp/lumix_v3_backup.json")

if __name__ == "__main__":
    main()
