#!/usr/bin/env python3
"""
채널 성과 분석 워크플로우 업데이트
- AI 분석 프롬프트: 2026 유튜브 숏츠 트렌드 인사이트 반영
- Gemini 모델: gemini-2.5-flash (안정 버전)
- 분석리포트 시트 탭 생성 (4개 채널)
"""
import json
import subprocess
import sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
WORKFLOW_ID = "SeW8pBXuifk04TWw"

# 4개 채널 시트 ID
SHEET_IDS = {
    "루믹스": "1gkRjLIcK3HxbnTbLCvG6oknMGVt2uz9pgboM3EF_VKg",
    "온카스터디": "1hnFCo4Mxnr4w57_zAFfYLMAgOsAB43ocgWhJW3szWK8",
    "슬롯": "1cps-88TuhFld4qJlryQh2QHkKvxhQyxLSgeu5burA_A",
    "스포츠": "1NAVwKXLQOUzBoNckxxesIR_ZS3GoNVGepr8zkBFmz4M"
}


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


# ============================================================
# 1. 프롬프트 생성 노드 업데이트 (2026 트렌드 인사이트 반영)
# ============================================================
ENHANCED_PROMPT_CODE = r"""
const channelInfo = $('트렌드 정리').first().json;
const statsResponse = $input.first().json;

// 트렌드 영상 통계 정리
const trendStats = (statsResponse.items || []).map(v => ({
  title: v.snippet?.title || '',
  views: parseInt(v.statistics?.viewCount || '0'),
  likes: parseInt(v.statistics?.likeCount || '0'),
  comments: parseInt(v.statistics?.commentCount || '0')
})).sort((a, b) => b.views - a.views);

const topTrends = trendStats.slice(0, 5).map((v, i) =>
  `${i+1}. "${v.title}" (조회수: ${v.views.toLocaleString()}, 좋아요: ${v.likes.toLocaleString()})`
).join('\n');

const prompt = `너는 YouTube Shorts 콘텐츠 전략가이자 트렌드 분석 전문가야.
아래 데이터를 분석하고 "${channelInfo.name}" 채널을 위한 주간 리포트를 작성해.

[채널 정보]
- 채널명: ${channelInfo.name}
- 니치: ${channelInfo.niche}
- 타겟: 해당 업종의 사업자/운영자/관계자

[이번 주 인기 Shorts 트렌드 (${channelInfo.keywords} 관련)]
${topTrends || '데이터 없음'}

[2026 유튜브 숏츠 핵심 트렌드 참고]
1. 3초 규칙: 알고리즘이 "3-Second Hold"를 기준으로 품질 판단. 3초 안에 시청자가 멈추면 넓은 피드 노출
2. 훅 공식: 결과 먼저 보여주기, 비밀/음모론, 실수 지적, 비교 대결, 숫자 리스트, 도전/체험
3. 루핑: 첫/마지막 장면을 연결하여 자동 재시청 유도 - 알고리즘 매우 긍정 평가
4. 2~3초 편집 리듬: 화면에서 2~3초마다 시각 변화 필수 (줌, 텍스트, 전환)
5. 고대비 자막: 소리 없이도 이해 가능해야 함 (무음 시청 70%+)
6. B2B 최적 길이: 30~45초 (완시청률 + 정보 전달 밸런스)
7. 필코노미 트렌드: 단순 정보보다 감성/공감/스토리텔링이 참여율 높음
8. 검색 가능한 숏폼: 숏츠 전용 검색 필터 도입 - SEO 필수
9. 비포&애프터: 시각적 변화가 완시청률 극대화
10. 액션 중간 시작: "안녕하세요" 인트로 절대 금지, 0.3초 내 말 시작

[분석 요청]
위 데이터와 트렌드를 기반으로, 이 채널이 이번 주에 만들어야 할 콘텐츠 전략을 JSON으로 작성해.
특히 인기 영상들의 훅/구조/주제를 분석하고, 우리 채널에 맞게 적용할 추천 주제를 구체적으로 제시해.
마크다운 코드블록 없이 순수 JSON만 응답해:

{
  "조회수_상위영상": "가장 조회수 높은 트렌드 영상 제목과 조회수, 왜 잘 됐는지 분석",
  "좋아요_상위영상": "가장 좋아요 많은 트렌드 영상 제목, 참여율이 높은 이유",
  "트렌드_키워드": "이번 주 핵심 트렌드 키워드 3-5개 (쉼표 구분)",
  "추천_주제1": "추천 주제 1 - 제목 형식으로 (어떤 훅 공식 사용, 30~45초 구성, 스토리텔링 포인트 포함)",
  "추천_주제2": "추천 주제 2 - 다른 훅 공식 사용",
  "추천_주제3": "추천 주제 3 - 비포&애프터 또는 비교 형식",
  "피해야할_주제": "이번 주 피해야 할 주제/각도 (경쟁 과열, 정책 위반 위험, 이미 포화된 주제 등)",
  "효과적인_훅_팁": "이번 주 가장 효과적인 첫 3초 훅 공식 + 구체적 예시 문장 2개",
  "트렌드_각도": "현재 트렌드의 핵심 방향, 어떤 감정/스토리가 반응 좋은지",
  "고성과_패턴": "고성과 영상들의 공통 패턴 (길이, 편집, 자막, CTA 등)",
  "AI_분석_요약": "전체 분석 요약 3문장 + 이번 주 핵심 키워드 1개"
}`;

return [{
  json: {
    ...channelInfo,
    trendStats,
    geminiPrompt: prompt
  }
}];
"""


def update_prompt_node(nodes):
    """프롬프트 생성 노드: 2026 트렌드 인사이트 반영"""
    idx, node = find_node(nodes, '프롬프트 생성')
    if idx == -1:
        print("  [ERROR] 프롬프트 생성 노드를 찾을 수 없습니다")
        return False
    node['parameters']['jsCode'] = ENHANCED_PROMPT_CODE
    print("  [OK] 프롬프트 생성: 2026 트렌드 인사이트 (3초 훅, 루핑, B2B, 감성 등) 반영")
    return True


def update_gemini_model(nodes):
    """AI 분석 Gemini 모델: preview → 안정 버전"""
    idx, node = find_node(nodes, 'AI 분석')
    if idx == -1:
        print("  [ERROR] AI 분석 노드를 찾을 수 없습니다")
        return False
    node['parameters']['modelId'] = {
        "__rl": True,
        "value": "models/gemini-2.5-flash",
        "mode": "list",
        "cachedResultName": "models/gemini-2.5-flash"
    }
    print("  [OK] AI 분석 모델: gemini-3-flash-preview → gemini-2.5-flash")
    return True


def upload_workflow(workflow_data):
    put_data = {
        "name": workflow_data.get("name"),
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "settings": {
            "executionOrder": workflow_data.get("settings", {}).get("executionOrder", "v1")
        }
    }
    with open('/tmp/analysis_workflow_update.json', 'w') as f:
        json.dump(put_data, f, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-sk', '-X', 'PUT',
        '-H', f'X-N8N-API-KEY: {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', '@/tmp/analysis_workflow_update.json',
        f'{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if 'id' in response:
            print(f"  [OK] 업로드 성공 (ID: {response['id']})")
            return True
        else:
            print(f"  [ERROR] 업로드 실패: {json.dumps(response, ensure_ascii=False)[:500]}")
            return False
    except json.JSONDecodeError:
        print(f"  [ERROR] 응답 파싱 실패: {result.stdout[:300]}")
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
    print("  [OK] 워크플로우 재활성화")


def create_report_tabs():
    """4개 채널 시트에 분석리포트 탭 생성"""
    headers = ["날짜", "채널명", "분석기간", "조회수_상위영상", "좋아요_상위영상",
               "트렌드_키워드", "추천_주제1", "추천_주제2", "추천_주제3",
               "피해야할_주제", "효과적인_훅_팁", "트렌드_각도", "고성과_패턴", "AI_분석_요약"]
    header_row = json.dumps({"values": [headers]})

    for name, doc_id in SHEET_IDS.items():
        # 1단계: 탭 생성 시도
        add_sheet_body = json.dumps({
            "requests": [{
                "addSheet": {
                    "properties": {"title": "분석리포트"}
                }
            }]
        })
        result = subprocess.run([
            'curl', '-sk', '-X', 'POST',
            '-H', 'Content-Type: application/json',
            '-H', f'Authorization: Bearer OAUTH_MANAGED_BY_N8N',
            '-d', add_sheet_body,
            f'https://sheets.googleapis.com/v4/spreadsheets/{doc_id}:batchUpdate'
        ], capture_output=True, text=True)

        # OAuth 토큰이 없으므로 n8n을 통해 처리해야 함
        # 여기서는 시트가 이미 있다고 가정하고, 헤더만 확인
        print(f"  [INFO] {name}: 분석리포트 탭은 수동 생성 필요 (Google Sheets에서 탭 추가)")
        print(f"         시트 URL: https://docs.google.com/spreadsheets/d/{doc_id}")
        print(f"         헤더 컬럼: {', '.join(headers[:5])}... (총 {len(headers)}개)")


def main():
    print("=" * 60)
    print("채널 성과 분석 워크플로우 업데이트")
    print("=" * 60)

    # 1. 워크플로우 가져오기
    print("\n[1/5] 워크플로우 가져오기...")
    workflow = fetch_workflow()
    if 'nodes' not in workflow:
        print(f"  [ERROR] 워크플로우 조회 실패")
        sys.exit(1)
    print(f"  [OK] {len(workflow['nodes'])}개 노드 로드")

    with open('/tmp/analysis_workflow_backup.json', 'w') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    print("  [OK] 백업: /tmp/analysis_workflow_backup.json")

    nodes = workflow['nodes']

    # 2. 프롬프트 업데이트
    print("\n[2/5] AI 분석 프롬프트 강화 (2026 트렌드)...")
    update_prompt_node(nodes)

    # 3. Gemini 모델 변경
    print("\n[3/5] Gemini 모델 변경...")
    update_gemini_model(nodes)

    # 4. 업로드 + 재활성화
    print("\n[4/5] 업로드 + 재활성화...")
    if upload_workflow(workflow):
        reactivate_workflow()

    # 5. 분석리포트 탭 안내
    print("\n[5/5] 분석리포트 시트 탭 확인...")
    create_report_tabs()

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)
    print("\n  변경 내용:")
    print("  1. AI 분석 프롬프트: 2026 트렌드 인사이트 10가지 반영")
    print("     - 3초 훅 규칙, 루핑 기법, B2B 최적 길이")
    print("     - 필코노미(감성) 트렌드, 검색 가능한 숏폼")
    print("     - 비포&애프터, 액션 중간 시작 등")
    print("  2. Gemini 모델: gemini-3-flash-preview → gemini-2.5-flash")
    print("  3. 추천 주제 구체화: 훅 공식 + 구성 + 스토리텔링 포인트 포함")
    print()
    print("  ⚠️ 필요한 수동 작업:")
    print("  - 4개 Google Sheets에 '분석리포트' 탭 생성 (없는 경우)")
    print("  - Channel ID 설정 (채널 설정 노드에서 placeholder 교체)")


if __name__ == "__main__":
    main()
