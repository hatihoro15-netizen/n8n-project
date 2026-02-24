#!/usr/bin/env python3
"""
콘텐츠 파싱 노드: Gemini JSON 파싱 에러 수정
- 문자열 내 이스케이프 안 된 제어문자 처리
- 트레일링 콤마 제거
- 에러 시 cleanText 디버그 정보 포함
"""
import json
import subprocess
import sys

N8N_BASE = "https://n8n.srv1345711.hstgr.cloud/api/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
WORKFLOW_ID = "itUlZJ2rZfGqkxty"
JSON_PATH = "/Users/gimdongseog/n8n-project/claude-tools/oncastudy_shortform_v1.json"

NEW_PARSER_JSCODE = r"""const raw = $input.first().json;
let text = '';
if (raw.content && raw.content.parts) {
  text = raw.content.parts[0].text;
} else if (typeof raw === 'string') {
  text = raw;
} else if (raw.text) {
  text = raw.text;
} else {
  text = JSON.stringify(raw);
}

/**
 * Gemini JSON 출력 정리
 * 1. 코드블록 제거
 * 2. JSON 객체 추출 (첫 { ~ 마지막 })
 * 3. 문자열 내 제어문자(줄바꿈, 탭 등) → 공백 변환
 * 4. 트레일링 콤마 제거
 */
function cleanGeminiJson(raw) {
  // 코드블록 제거
  let s = raw.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();

  // JSON 객체 추출 (첫 { ~ 마지막 })
  const first = s.indexOf('{');
  const last = s.lastIndexOf('}');
  if (first !== -1 && last > first) {
    s = s.substring(first, last + 1);
  }

  // 문자열 내 제어문자 처리 (stateful char-by-char parser)
  // JSON 규격: 문자열 안의 \n, \t, \r 등은 반드시 이스케이프 필요
  // Gemini가 이스케이프 없이 출력하는 경우 → 공백으로 치환
  let result = '';
  let inStr = false;
  let esc = false;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (esc) { result += c; esc = false; continue; }
    if (c === '\\' && inStr) { result += c; esc = true; continue; }
    if (c === '"') { inStr = !inStr; result += c; continue; }
    if (inStr) {
      // 줄바꿈, 캐리지리턴 → 공백
      if (c === '\n' || c === '\r') { result += ' '; continue; }
      // 탭 → 공백
      if (c === '\t') { result += ' '; continue; }
      // 기타 제어문자 (0x00~0x1F) 제거
      if (c.charCodeAt(0) < 0x20) { continue; }
    }
    result += c;
  }

  // 트레일링 콤마 제거: ,} 또는 ,]
  result = result.replace(/,(\s*[}\]])/g, '$1');

  return result;
}

let cleanText = cleanGeminiJson(text);
let data;

try {
  data = JSON.parse(cleanText);
} catch (e1) {
  // 2차 시도: 유니코드 따옴표 → 일반 따옴표, BOM 제거
  try {
    let fixed = cleanText
      .replace(/[\u201C\u201D\u201E\u201F\u2033\u2036]/g, '"')
      .replace(/[\u2018\u2019\u201A\u201B\u2032\u2035]/g, "'")
      .replace(/^\uFEFF/, '');
    data = JSON.parse(fixed);
  } catch (e2) {
    // 에러 위치 주변 텍스트 포함하여 디버그
    const posMatch = e1.message.match(/position (\d+)/);
    const pos = posMatch ? parseInt(posMatch[1]) : 0;
    const start = Math.max(0, pos - 80);
    const end = Math.min(cleanText.length, pos + 80);
    const around = cleanText.substring(start, end);
    const pointer = ' '.repeat(Math.min(pos - start, 80)) + '^^^';
    throw new Error(
      `JSON 파싱 실패: ${e1.message}\n` +
      `--- 에러 위치(${pos}) 주변 ---\n` +
      `${around}\n${pointer}\n` +
      `--- 전체 길이: ${cleanText.length}자 ---\n` +
      `처음 300자: ${cleanText.substring(0, 300)}`
    );
  }
}

if (!data.scenes || data.scenes.length < 5) {
  throw new Error('scenes must have at least 5 items, got: ' + (data.scenes?.length || 0));
}

// visual_type, meme_mood 검증 및 기본값 처리
const VALID_MOODS = ['thinking', 'excited', 'shocked', 'sad', 'angry', 'cool', 'celebrating'];

data.scenes = data.scenes.map((scene, idx) => {
  // visual_type이 없으면 위치 기반 기본값 (매 3번째 = meme)
  if (!scene.visual_type || !['image', 'meme'].includes(scene.visual_type)) {
    scene.visual_type = ((idx + 1) % 3 === 0) ? 'meme' : 'image';
  }

  // meme인데 meme_mood가 없으면 기본값
  if (scene.visual_type === 'meme') {
    if (!scene.meme_mood || !VALID_MOODS.includes(scene.meme_mood)) {
      scene.meme_mood = VALID_MOODS[idx % VALID_MOODS.length];
    }
    scene.image_prompt = scene.image_prompt || '';
    scene.keyword = scene.keyword || '';
  } else {
    scene.meme_mood = '';
    if (!scene.keyword) {
      scene.keyword = scene.image_prompt?.split(',')[0] || 'abstract background';
    }
  }

  return scene;
});

const memeCount = data.scenes.filter(s => s.visual_type === 'meme').length;
const imageCount = data.scenes.filter(s => s.visual_type === 'image').length;

return [{
  json: {
    hook_title: data.hook_title,
    scenes: data.scenes,
    Subject: data.Subject,
    Caption: data.Caption,
    Comment: data.Comment,
    fullDialogue: data.scenes.map(s => s.dialogue).join(' '),
    segmentCount: data.scenes.length,
    memeCount,
    imageCount,
    Status: '생성 중',
    generatedAt: new Date().toISOString(),
    row_number: $('주제 파싱').first().json.row_number
  }
}];"""


def main():
    print("1. 로컬 워크플로우 JSON 로드...")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    found = False
    for node in workflow.get("nodes", []):
        if node.get("name") == "콘텐츠 파싱":
            old = node["parameters"]["jsCode"]
            node["parameters"]["jsCode"] = NEW_PARSER_JSCODE
            found = True
            print("   ✅ 콘텐츠 파싱 jsCode 교체 완료")
            print("      추가된 기능:")
            print("      - cleanGeminiJson(): 문자열 내 제어문자 stateful 처리")
            print("      - 트레일링 콤마 제거")
            print("      - 유니코드 따옴표 → 일반 따옴표 (2차 시도)")
            print("      - 에러 시 위치+주변 텍스트 포함")
            break

    if not found:
        print("❌ 콘텐츠 파싱 노드를 찾지 못함")
        sys.exit(1)

    # 로컬 저장
    print("\n2. 로컬 JSON 저장...")
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)

    # n8n 업로드
    print("3. n8n API 업로드...")
    upload_data = {
        "name": workflow.get("name", ""),
        "nodes": workflow.get("nodes", []),
        "connections": workflow.get("connections", {}),
        "settings": workflow.get("settings", {}),
    }
    tmp = "/tmp/n8n_upload_parser.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(upload_data, f, ensure_ascii=False)

    result = subprocess.run(
        ["curl", "-s", "-X", "PUT",
         f"{N8N_BASE}/workflows/{WORKFLOW_ID}",
         "-H", f"X-N8N-API-KEY: {API_KEY}",
         "-H", "Content-Type: application/json",
         "-d", f"@{tmp}"],
        capture_output=True, text=True, timeout=30,
    )
    resp = json.loads(result.stdout)
    if "id" in resp:
        print(f"   ✅ 업로드 완료: {resp['id']}")
    else:
        print(f"   ❌ 오류: {result.stdout[:500]}")
        sys.exit(1)

    # 검증
    print("\n4. 검증...")
    for node in resp.get("nodes", []):
        if node.get("name") == "콘텐츠 파싱":
            code = node["parameters"]["jsCode"]
            checks = {
                "cleanGeminiJson 함수": "cleanGeminiJson" in code,
                "제어문자 처리": "charCodeAt(0) < 0x20" in code,
                "트레일링 콤마": "trailing" in code.lower() or ",($1" in code or ",(\\s*[}\\]])" in code,
                "유니코드 따옴표": "\\u201C" in code,
                "에러 디버그 정보": "에러 위치" in code,
            }
            for label, ok in checks.items():
                print(f"   {label}: {'✅' if ok else '❌'}")
            break

    print("\n🎉 콘텐츠 파싱 JSON 정리 강화 완료!")


if __name__ == "__main__":
    main()
