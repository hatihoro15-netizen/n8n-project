#!/usr/bin/env python3
"""
온카스터디 숏폼 (완전자동 v1) 워크플로우 생성기

Based on: 루믹스 솔루션 숏폼 (완전자동 v3) template
Output: oncasudi_shortform_v1.json
Uploaded workflow ID: Rn7dlQMowuMGQ72g

Changes from template:
  - AI 주제 생성: 온카스터디 간접 광고 프롬프트 (대화/후기/정보/비교형)
  - 나레이션 분할: 대화체 흐름 + 감정 전환(불안->해결->안도) 유지 규칙 추가
  - 이미지 프롬프트 AI: 온카스터디 비주얼 (다크/느와르/서스펜스/감성, 카지노 직접 묘사 금지)
  - BGM 생성: 기본 프롬프트를 dark tense dramatic suspenseful로 변경
  - Google Sheets: ONCASUDI_SHEET_ID / 온카스터디 시트명 (3개 노드)
  - 모든 노드: credentials 제거됨 (별도 연결 필요)

Usage:
    python3 create_oncasudi_shortform.py
"""

import json
import uuid
import os


def gen_id():
    return str(uuid.uuid4())


def gen_wh():
    return str(uuid.uuid4())


def build_workflow():
    nodes = []

    # [0] 스케줄 트리거 - 12시간 간격
    nodes.append({
        "parameters": {"rule": {"interval": [{"field": "hours", "hoursInterval": 12}]}},
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.3,
        "position": [-1872, 224],
        "id": gen_id(),
        "name": "스케줄 트리거"
    })

    # [1] AI 주제 생성 - 온카스터디 간접 광고 프롬프트
    ai_topic_prompt = """너는 '온카스터디'(온라인 카지노 정보 검증 및 안전 가이드 플랫폼)의 YouTube Shorts 콘텐츠 기획자야.
YouTube Shorts(30~50초)용 간접 광고 콘텐츠를 기획해줘.

타겟: 온라인 카지노/배팅에 관심 있는 20~40대, 먹튀 피해를 당했거나 안전한 사이트를 찾는 사람들
톤: 공감적이고 친근한 대화체, 정보 전달 + 감정 자극

간접 광고 스타일 (아래 중 하나를 랜덤으로 골라서 사용):
1. 대화형: 친구끼리 대화하듯 "야 나 어제 환전 안 됐어..." -> "온카스터디에서 미리 확인했어야지"
2. 후기형: 실제 경험담처럼 "처음엔 나도 몰랐는데..." -> "온카스터디 보고 나서 달라졌다"
3. 정보형: 유용한 팁 전달 "먹튀 당하기 전에 이것만 확인하세요" -> "온카스터디에 검증 방법 다 나와있어요"
4. 비교형: 안전 vs 위험 비교 "이런 사이트는 절대 가지 마세요" -> "온카스터디 검증 사이트만 이용하세요"

주제 카테고리 (하나를 랜덤으로 골라서 구체적인 주제를 만들어):
1. 먹튀 예방법 & 먹튀 사이트 특징
2. 안전한 온라인 카지노 검증 방법
3. 환전 문제 & 해결 방법
4. 온라인 배팅 초보자 가이드
5. 먹튀 피해 실제 사례 & 교훈
6. 신뢰할 수 있는 사이트 구별법
7. 배팅 전략 & 자금 관리
8. 온라인 카지노 보너스 & 프로모션 주의사항

핵심 규칙:
- 처음 3초 안에 강력한 훅(호기심/충격/공감) 필수
- '온카스터디'라는 이름이 나레이션에 자연스럽게 1~2번 언급되어야 함
- 직접적인 광고가 아닌 자연스러운 정보 전달 속에 온카스터디 언급
- 감정적 스토리텔링: 불안 -> 해결 -> 안도의 흐름
- 클릭 유도: 호기심을 자극하는 제목과 댓글

반드시 아래 JSON 형식으로만 응답해. 마크다운 코드블록 없이 순수 JSON만:
{
  "Subject": "영상 제목 (호기심 유발, 15자 이내)",
  "Narration": "나레이션 전문 (30~50초 분량, 200~350자)",
  "Caption": "YouTube 설명 (해시태그 포함, 3줄)",
  "Comment": "첫 번째 댓글 (질문 유도 또는 공감 유도)",
  "BGM_prompt": "BGM 분위기 영어 설명 (10~20단어)"
}"""

    nodes.append({
        "parameters": {
            "modelId": {"__rl": True, "value": "models/gemini-2.5-flash", "mode": "list", "cachedResultName": "models/gemini-2.5-flash"},
            "messages": {"values": [{"content": ai_topic_prompt}]},
            "jsonOutput": True, "builtInTools": {}, "options": {}
        },
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1.1, "position": [-1568, 224],
        "id": gen_id(), "name": "AI 주제 생성"
    })

    # Additional 32 nodes follow the same pattern as the template...
    # (See oncasudi_shortform_v1.json for the complete generated output)

    return nodes


if __name__ == "__main__":
    output = "/Users/gimdongseog/n8n-project/oncasudi_shortform_v1.json"
    if os.path.exists(output):
        with open(output) as f:
            data = json.load(f)
        print(f"Workflow: {data['name']}")
        print(f"Nodes: {len(data['nodes'])}")
        print(f"Connections: {len(data['connections'])}")
        print(f"File: {output}")
        print(f"n8n Workflow ID: Rn7dlQMowuMGQ72g")
    else:
        print("Workflow JSON not found. Regenerate needed.")
