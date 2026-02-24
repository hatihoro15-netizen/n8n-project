#!/usr/bin/env python3
"""
밈 카탈로그 확장 (21→35개) + 프롬프트 20초 속도감 변경
수정 대상: 이미지 URL 추출, 프롬프트 생성
"""
import json
import subprocess
import sys

N8N_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
WORKFLOW_ID = "itUlZJ2rZfGqkxty"
JSON_PATH = "/Users/gimdongseog/n8n-project/claude-tools/oncastudy_shortform_v1.json"

# ── 새 이미지 URL 추출 jsCode (밈 카탈로그 35개) ──
NEW_IMAGE_URL_JSCODE = r"""// 밈 카탈로그: MinIO에 호스팅된 밈/리액션 영상 URL (35개)
const MEME_CATALOG = {
  thinking: [
    'http://76.13.182.180:9000/memes/thinking/meme_thinking_01.mp4',
    'http://76.13.182.180:9000/memes/thinking/meme_thinking_02.mp4',
    'http://76.13.182.180:9000/memes/thinking/meme_thinking_03.mp4',
    'http://76.13.182.180:9000/memes/thinking/meme_thinking_04.mp4',
    'http://76.13.182.180:9000/memes/thinking/meme_thinking_05.mp4',
  ],
  excited: [
    'http://76.13.182.180:9000/memes/excited/meme_excited_01.mp4',
    'http://76.13.182.180:9000/memes/excited/meme_excited_02.mp4',
    'http://76.13.182.180:9000/memes/excited/meme_excited_03.mp4',
    'http://76.13.182.180:9000/memes/excited/meme_excited_04.mp4',
    'http://76.13.182.180:9000/memes/excited/meme_excited_05.mp4',
  ],
  shocked: [
    'http://76.13.182.180:9000/memes/shocked/meme_shocked_01.mp4',
    'http://76.13.182.180:9000/memes/shocked/meme_shocked_02.mp4',
    'http://76.13.182.180:9000/memes/shocked/meme_shocked_03.mp4',
    'http://76.13.182.180:9000/memes/shocked/meme_shocked_04.mp4',
    'http://76.13.182.180:9000/memes/shocked/meme_shocked_05.mp4',
  ],
  sad: [
    'http://76.13.182.180:9000/memes/sad/meme_sad_01.mp4',
    'http://76.13.182.180:9000/memes/sad/meme_sad_02.mp4',
    'http://76.13.182.180:9000/memes/sad/meme_sad_03.mp4',
    'http://76.13.182.180:9000/memes/sad/meme_sad_04.mp4',
    'http://76.13.182.180:9000/memes/sad/meme_sad_05.mp4',
  ],
  angry: [
    'http://76.13.182.180:9000/memes/angry/meme_angry_01.mp4',
    'http://76.13.182.180:9000/memes/angry/meme_angry_02.mp4',
    'http://76.13.182.180:9000/memes/angry/meme_angry_03.mp4',
    'http://76.13.182.180:9000/memes/angry/meme_angry_04.mp4',
    'http://76.13.182.180:9000/memes/angry/meme_angry_05.mp4',
  ],
  cool: [
    'http://76.13.182.180:9000/memes/cool/meme_cool_01.mp4',
    'http://76.13.182.180:9000/memes/cool/meme_cool_02.mp4',
    'http://76.13.182.180:9000/memes/cool/meme_cool_03.mp4',
    'http://76.13.182.180:9000/memes/cool/meme_cool_04.mp4',
    'http://76.13.182.180:9000/memes/cool/meme_cool_05.mp4',
  ],
  celebrating: [
    'http://76.13.182.180:9000/memes/celebrating/meme_celebrating_01.mp4',
    'http://76.13.182.180:9000/memes/celebrating/meme_celebrating_02.mp4',
    'http://76.13.182.180:9000/memes/celebrating/meme_celebrating_03.mp4',
    'http://76.13.182.180:9000/memes/celebrating/meme_celebrating_04.mp4',
    'http://76.13.182.180:9000/memes/celebrating/meme_celebrating_05.mp4',
  ],
};

const items = $input.all();
const segAll = $('세그먼트 분리').all();

return items.map((item, i) => {
  const data = item.json;
  const segData = segAll[i]?.json || {};
  const visualType = segData.visual_type || data.visual_type || 'image';
  const memeMood = segData.meme_mood || data.meme_mood || 'thinking';

  if (visualType === 'meme') {
    const catalog = MEME_CATALOG[memeMood] || MEME_CATALOG.thinking;
    const randomIdx = Math.floor(Math.random() * catalog.length);
    const memeUrl = catalog[randomIdx];
    return {
      json: {
        ...data,
        visual_type: 'meme',
        meme_mood: memeMood,
        images: [{ url: memeUrl }],
        is_video: true,
      }
    };
  } else {
    const photos = data.photos || [];
    let imageUrl = '';
    if (photos.length > 0) {
      const randPhoto = photos[Math.floor(Math.random() * photos.length)];
      imageUrl = randPhoto.src?.portrait || randPhoto.src?.large || randPhoto.src?.medium || '';
    }
    if (!imageUrl) {
      imageUrl = 'https://images.pexels.com/photos/1229861/pexels-photo-1229861.jpeg?auto=compress&cs=tinysrgb&w=1080';
    }
    return {
      json: {
        ...data,
        visual_type: 'image',
        meme_mood: '',
        images: [{ url: imageUrl }],
        is_video: false,
      }
    };
  }
});"""

# ── 새 프롬프트 생성 jsCode (20초 + 속도감) ──
NEW_PROMPT_JSCODE = r'''const topic = $input.first().json.topic || $input.first().json['주제'] || '';

if (!topic) {
  throw new Error('topic이 비어있습니다. 시트에 topic 컬럼을 확인하세요.');
}

const prompt = `너는 '온카스터디' 커뮤니티의 YouTube Shorts 콘텐츠 기획자야.
아래 주제로 20초 분량의 빠른 속도감 있는 숏츠 스크립트를 작성해줘.

## 반드시 지킬 주제
${topic}

위 주제를 중심으로 콘텐츠를 작성하되, 후반부에 '온카스터디'를 자연스럽게 1회 언급해.
모든 scene의 dialogue는 반드시 "${topic}" 주제와 직접 관련된 내용이어야 해.

## 온카스터디 소개
온카스터디는 먹튀검증 및 안전 정보 제공 커뮤니티입니다.
검증 정보 공유, 먹튀 사이트 구별법 안내, 자유게시판, 제휴사이트 후기, 스포츠 분석,
포인트 시스템(복권, 돌림판, 기프티콘 교환) 등의 기능이 있습니다.

## 영상 스타일 (20초 속도감 숏츠)
- 총 20초! 짧고 빠르게!
- 9:16 세로 영상
- 빠른 이미지/밈 전환 (각 장면 1.5~3초)
- 상단: 고정된 훅 제목 (검은 배경, 큰 글씨)
- 중간: 정보 이미지 + 밈 영상 빠르게 번갈아
- 하단: 짧은 자막
- 오디오: 빠른 TTS 나레이션

## 나레이션 스타일 (핵심!)
빠르고 임팩트 있는 설명체:
- 짧지만 설명이 있는 문장 (팩트 나열이 아닌 자연스러운 한 문장)
- "~거든", "~한 편이야", "근데~", "그래서~" 같은 구어체 사용
- 핵심 포인트 2~3개만 빠르게 전달
- 각 장면 dialogue: 10~25자 (한 문장으로 핵심만!)

예시 (이런 느낌으로):
- "요즘 이런 사이트 엄청 늘고 있거든"
- "근데 여기서 중요한 게 있어"
- "출금이 빠른 사이트가 안전한 편이야"
- "온카스터디에서 검증 정보 확인해봐"

## 장면 구성 규칙
- 총 7~9개 장면 (20초에 맞게!)
- 각 장면 1.5~3초 (빠른 전환!)
- visual_type: "image" 또는 "meme"
- image: 주제와 직접 관련된 구체적 이미지
- meme: 밈/리액션 영상 (감정 표현)
- 장면의 30~40%를 meme으로 배치 (속도감!)
- meme_mood: thinking, excited, shocked, sad, angry, cool, celebrating 중 택1
- meme dialogue: 짧은 리액션 ("실화?!", "대박!", "ㄹㅇ?", "꿀팁이다!")

## 나레이션 흐름 (20초 구조)
1. 훅 (1~2장면, 3초): 강렬한 시작 ("이거 모르면 진짜 손해야")
2. 핵심 (4~5장면, 12초): 포인트 2~3개 빠르게 전달 + 밈 리액션
3. 마무리 (1~2장면, 5초): 정리 + CTA ("온카스터디 검색!")

## 이미지 키워드 규칙
- keyword는 "${topic}" 주제와 직접 관련된 구체적인 영어 단어
- 너무 추상적인 키워드 금지 (예: "background", "abstract" 금지)
- 주제의 핵심 사물/행동을 직접 묘사하는 키워드 사용

## 출력 (순수 JSON, 코드블록 없이)
{
  "hook_title": "훅 제목 (12자 이내, <y>강조</y>)",
  "scenes": [
    {
      "dialogue": "빠른 설명 문장 (10~25자)",
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
- scenes 7~9개 (20초!)
- dialogue는 10~25자 설명 문장 (속도감!)
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


def main():
    print("1. 로컬 워크플로우 JSON 로드...")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    nodes = workflow.get("nodes", [])
    modified = []

    for node in nodes:
        name = node.get("name", "")

        if name == "프롬프트 생성":
            node["parameters"]["jsCode"] = NEW_PROMPT_JSCODE
            modified.append("프롬프트 생성")
            print("   ✅ 프롬프트 생성: 20초 + 속도감 스타일로 변경")

        elif name == "이미지 URL 추출":
            node["parameters"]["jsCode"] = NEW_IMAGE_URL_JSCODE
            modified.append("이미지 URL 추출")
            print("   ✅ 이미지 URL 추출: MEME_CATALOG 21→35개로 확장")

    if not modified:
        print("❌ 수정할 노드를 찾지 못했습니다")
        sys.exit(1)

    print(f"\n2. 수정된 노드: {', '.join(modified)}")

    # 로컬 저장
    print("3. 로컬 JSON 저장...")
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    print(f"   ✅ {JSON_PATH}")

    # n8n API 업로드
    print("4. n8n API 업로드...")
    upload_data = {
        "name": workflow.get("name", ""),
        "nodes": workflow.get("nodes", []),
        "connections": workflow.get("connections", {}),
        "settings": workflow.get("settings", {}),
    }

    tmp_path = "/tmp/n8n_upload_memes_speed.json"
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

    # 검증
    print("\n5. 변경 검증...")
    for node in resp.get("nodes", []):
        name = node.get("name", "")
        code = node.get("parameters", {}).get("jsCode", "")

        if name == "프롬프트 생성":
            ok_20sec = "20초" in code
            ok_speed = "속도감" in code
            ok_7_9 = "7~9개" in code
            ok_no_40 = "40~50초" not in code
            print(f"   프롬프트 생성:")
            print(f"     20초 분량: {'✅' if ok_20sec else '❌'}")
            print(f"     속도감 스타일: {'✅' if ok_speed else '❌'}")
            print(f"     7~9개 장면: {'✅' if ok_7_9 else '❌'}")
            print(f"     40~50초 제거: {'✅' if ok_no_40 else '❌'}")

        elif name == "이미지 URL 추출":
            cnt_04 = code.count("_04.mp4")
            cnt_05 = code.count("_05.mp4")
            print(f"   이미지 URL 추출:")
            print(f"     04번 밈 추가: {'✅' if cnt_04 == 7 else '❌'} ({cnt_04}/7)")
            print(f"     05번 밈 추가: {'✅' if cnt_05 == 7 else '❌'} ({cnt_05}/7)")

    print("\n🎉 업데이트 완료!")
    print("   - 밈 카탈로그: 21개 → 35개 (카테고리당 5개)")
    print("   - 프롬프트: 20초 + 속도감 있는 스타일")
    print("   - 장면: 7~9개, 각 1.5~3초")


if __name__ == "__main__":
    main()
