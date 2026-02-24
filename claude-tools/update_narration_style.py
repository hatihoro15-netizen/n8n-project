#!/usr/bin/env python3
"""
나레이션 스타일 변경: 팩트 나열 → 설명형 대화체
수정 대상: 프롬프트 생성, NCA 데이터 준비
"""
import json
import subprocess
import sys

N8N_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
WORKFLOW_ID = "itUlZJ2rZfGqkxty"
JSON_PATH = "/Users/gimdongseog/n8n-project/claude-tools/oncastudy_shortform_v1.json"

# ── 새 프롬프트 생성 jsCode ──
NEW_PROMPT_JSCODE = r'''const topic = $input.first().json.topic || $input.first().json['주제'] || '';

if (!topic) {
  throw new Error('topic이 비어있습니다. 시트에 topic 컬럼을 확인하세요.');
}

const prompt = `너는 '온카스터디' 커뮤니티의 YouTube Shorts 콘텐츠 기획자야.
아래 주제로 40~50초 분량의 설명형 숏츠 스크립트를 작성해줘.

## 반드시 지킬 주제
${topic}

위 주제를 중심으로 콘텐츠를 작성하되, 후반부에 '온카스터디'를 자연스럽게 1회 언급해.
모든 scene의 dialogue는 반드시 "${topic}" 주제와 직접 관련된 내용이어야 해.

## 온카스터디 소개
온카스터디는 먹튀검증 및 안전 정보 제공 커뮤니티입니다.
검증 정보 공유, 먹튀 사이트 구별법 안내, 자유게시판, 제휴사이트 후기, 스포츠 분석,
포인트 시스템(복권, 돌림판, 기프티콘 교환) 등의 기능이 있습니다.

## 영상 스타일 (설명형 숏츠)
- 총 40~50초, 9:16 세로 영상
- 정보 이미지 + 밈 영상 번갈아 배치
- 상단: 고정된 훅 제목 (검은 배경, 큰 글씨)
- 중간: 정보 이미지 + 밈 영상
- 하단: 자막
- 오디오: 자연스러운 TTS 나레이션

## 나레이션 스타일 (가장 중요!)
레퍼런스 스타일: 자연스러운 한국어 구어체 설명
- "~한 것 같은", "~한 편이", "~거든", "그래서~", "근데~" 같은 자연스러운 어미
- "첫째", "둘째", "셋째" 같은 순서 구조로 포인트 정리
- 각 포인트마다 이유와 예시를 함께 설명
- 마지막에 자연스러운 마무리 + CTA

예시 (이런 느낌으로):
- "요즘 이런 사이트가 늘고 있는데 뭐가 다른지 비교해봄"
- "첫째, 검증된 사이트는 출금이 빠른 편이거든"
- "근데 사기 사이트는 이 부분에서 확실히 차이가 남"
- "그래서 온카스터디에서 검증 정보 확인해보는 게 좋음"

## 장면 구성 규칙
- 총 8~12개 장면
- 각 장면의 dialogue: 자연스러운 1~2문장 (15~40자)
- 짧은 팩트가 아닌, 설명이 담긴 문장으로!
- visual_type: "image" 또는 "meme"
- image: 주제와 직접 관련된 구체적 이미지
- meme: 밈/리액션 영상 (감정 표현)
- 장면의 25~35%를 meme으로 배치
- meme_mood: thinking, excited, shocked, sad, angry, cool, celebrating 중 택1
- meme dialogue: 리액션 문장 ("실화야 이거?", "이건 좀 심한데", "꿀팁이다 진짜")

## 나레이션 흐름 구조
1. 도입 (1~2장면): 주제 소개 + 관심 유도 ("요즘 ~가 늘고 있는데")
2. 본문 (5~8장면): "첫째/둘째/셋째" 구조로 포인트별 설명
   - 각 포인트: 주장 + 이유 또는 예시
   - 중간중간 밈 리액션으로 감정 표현
3. 마무리 (1~2장면): 정리 + CTA ("온카스터디에서 확인해봐")

## 이미지 키워드 규칙
- keyword는 "${topic}" 주제와 직접 관련된 구체적인 영어 단어
- 너무 추상적인 키워드 금지 (예: "background", "abstract" 금지)
- 주제의 핵심 사물/행동을 직접 묘사하는 키워드 사용

## 출력 (순수 JSON, 코드블록 없이)
{
  "hook_title": "훅 제목 (15자 이내, <y>강조</y>)",
  "scenes": [
    {
      "dialogue": "자연스러운 설명 문장 (15~40자)",
      "image_prompt": "영어 이미지 프롬프트 (meme이면 빈 문자열)",
      "keyword": "구체적 영어 키워드 (meme이면 빈 문자열)",
      "visual_type": "image 또는 meme",
      "meme_mood": "meme인 경우만 감정"
    }
  ],
  "Subject": "영상 제목 #온카스터디 #먹튀검증 + 해시태그",
  "Caption": "영상 설명 #온카스터디 + 해시태그",
  "Comment": "구글에 온카스터디 검색!"
}

주의:
- scenes 8~12개
- dialogue는 설명형 문장 (팩트 나열이 아닌 자연스러운 설명!)
- visual_type, keyword 필수
- 주제와 무관한 내용 금지`;

return [{
  json: {
    prompt,
    topic,
    row_number: $input.first().json.row_number,
    ...$input.first().json
  }
}];'''

# ── NCA 데이터 준비: 자막 줄바꿈 14→20자, 폰트 48→42 ──
# 기존 NCA jsCode에서 부분 수정만 적용
NCA_SUBTITLE_CHANGES = {
    "wrapSubtitle(seg.dialogueText, 14)": "wrapSubtitle(seg.dialogueText, 20)",
    "fontsize=48": "fontsize=42",
}


def main():
    # 1. 로컬 JSON 로드
    print("1. 로컬 워크플로우 JSON 로드...")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    nodes = workflow.get("nodes", [])
    modified = []

    for node in nodes:
        name = node.get("name", "")

        # ── 프롬프트 생성 수정 ──
        if name == "프롬프트 생성":
            old_code = node["parameters"]["jsCode"]
            node["parameters"]["jsCode"] = NEW_PROMPT_JSCODE
            modified.append("프롬프트 생성")
            print(f"   ✅ 프롬프트 생성: 설명형 대화체로 변경")
            print(f"      - 기존: 25~30초, 12자 이내 팩트")
            print(f"      - 변경: 40~50초, 15~40자 설명형 문장")

        # ── NCA 데이터 준비 수정 ──
        elif name == "NCA 데이터 준비":
            code = node["parameters"]["jsCode"]
            for old, new in NCA_SUBTITLE_CHANGES.items():
                if old in code:
                    code = code.replace(old, new)
                    print(f"   ✅ NCA 데이터 준비: '{old}' → '{new}'")
            node["parameters"]["jsCode"] = code
            modified.append("NCA 데이터 준비")

    if not modified:
        print("❌ 수정할 노드를 찾지 못했습니다")
        sys.exit(1)

    print(f"\n2. 수정된 노드: {', '.join(modified)}")

    # 2. 로컬 JSON 저장
    print("3. 로컬 JSON 저장...")
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    print(f"   ✅ {JSON_PATH}")

    # 3. n8n API로 업로드 (PUT)
    print("4. n8n API 업로드...")

    # pinData 제거 (n8n PUT API 제약)
    upload_data = {
        "name": workflow.get("name", ""),
        "nodes": workflow.get("nodes", []),
        "connections": workflow.get("connections", {}),
        "settings": workflow.get("settings", {}),
    }

    tmp_path = "/tmp/n8n_upload_narration.json"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(upload_data, f, ensure_ascii=False)

    result = subprocess.run(
        [
            "curl", "-s", "-X", "PUT",
            f"{N8N_BASE}/workflows/{WORKFLOW_ID}",
            "-H", f"X-N8N-API-KEY: {API_KEY}",
            "-H", "Content-Type: application/json",
            "-d", f"@{tmp_path}",
        ],
        capture_output=True, text=True, timeout=30,
    )

    if result.returncode != 0:
        print(f"❌ curl 실패: {result.stderr}")
        sys.exit(1)

    resp = json.loads(result.stdout)
    if "id" in resp:
        print(f"   ✅ 워크플로우 업데이트 완료: {resp['id']}")
    else:
        print(f"   ❌ API 응답 오류: {result.stdout[:500]}")
        sys.exit(1)

    # 4. 검증
    print("\n5. 변경 검증...")
    for node in resp.get("nodes", []):
        name = node.get("name", "")
        code = node.get("parameters", {}).get("jsCode", "")

        if name == "프롬프트 생성":
            has_style = "설명형 숏츠" in code
            has_40sec = "40~50초" in code
            has_conversational = "한 것 같은" in code
            no_12char = "12자 이내" not in code
            print(f"   프롬프트 생성:")
            print(f"     설명형 스타일: {'✅' if has_style else '❌'}")
            print(f"     40~50초 분량: {'✅' if has_40sec else '❌'}")
            print(f"     대화체 어미: {'✅' if has_conversational else '❌'}")
            print(f"     12자 제한 제거: {'✅' if no_12char else '❌'}")

        elif name == "NCA 데이터 준비":
            has_20char = "wrapSubtitle(seg.dialogueText, 20)" in code
            has_42font = "fontsize=42" in code
            print(f"   NCA 데이터 준비:")
            print(f"     자막 20자 줄바꿈: {'✅' if has_20char else '❌'}")
            print(f"     폰트 크기 42: {'✅' if has_42font else '❌'}")

    print("\n🎉 나레이션 스타일 변경 완료!")
    print("   - 팩트 나열 (12자) → 설명형 대화체 (15~40자)")
    print("   - 자막 줄바꿈 14자 → 20자")
    print("   - 자막 폰트 48 → 42")


if __name__ == "__main__":
    main()
