import json, requests, time

N8N_URL = "https://n8n.srv1345711.hstgr.cloud"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZGRiZmViZC00NjIyLTRjMTAtYWU5ZC1mYjFlZGRjZWU5YjIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiZWNiOTY5ZjQtNzE5NS00MTIxLWE2YWYtMDg2N2NiNjMyMzI3IiwiaWF0IjoxNzcwNDk2NDEzfQ.Zsw3KmO_lsbfomEmMGFUraSPmzM4NIIcfzCpAkB83J4"
WF_ID = "9YOHS8N1URWlzGWj"
HEADERS = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}

# Load code from files
with open('/tmp/nca_data_prep.js') as f:
    NCA_DATA_CODE = f.read()
with open('/tmp/nca_result.js') as f:
    NCA_RESULT_CODE = f.read()

NCA_SUB_BODY = """={{ JSON.stringify({
  "inputs": [
    { "file_url": $json.video_url, "options": [] },
    { "file_url": "http://76.13.182.180:9000/nca-toolkit/fonts/NotoSansKR-Bold.ttf", "options": [{"option": "-f"}, {"option": "data"}] }
  ],
  "filters": [{ "filter": "ass='" + $json.ass_url + "':fontsdir=/tmp" }],
  "outputs": [{
    "options": [
      { "option": "-c:v" },
      { "option": "libx264" },
      { "option": "-preset" },
      { "option": "fast" },
      { "option": "-crf" },
      { "option": "23" },
      { "option": "-c:a" },
      { "option": "copy" },
      { "option": "-movflags" },
      { "option": "+faststart" }
    ]
  }],
  "global_options": []
}) }}"""

# Fetch
print("Fetching workflow...")
resp = requests.get(f"{N8N_URL}/api/v1/workflows/{WF_ID}", headers=HEADERS)
wf = resp.json()

WORD_RULE = "\n\n📌 단어 반복 금지: 5문장 내에서 동일한 핵심 단어(명사/동사 어근)를 2회 이상 사용하지 마세요."

for node in wf['nodes']:
    name = node.get('name', '')
    p = node.get('parameters', {})
    
    if name == 'NCA 데이터 준비':
        p['jsCode'] = NCA_DATA_CODE
        print(f"  Set NCA 데이터 준비: {len(NCA_DATA_CODE)} chars")
    
    elif name == 'NCA 제작 결과':
        p['jsCode'] = NCA_RESULT_CODE
        print(f"  Set NCA 제작 결과: {len(NCA_RESULT_CODE)} chars")
    
    elif name == 'NCA 자막 추가':
        p['jsonBody'] = NCA_SUB_BODY
        print("  Set NCA 자막 추가: jsonBody")
    
    elif name == 'MIME 타입 수정':
        p['jsCode'] = """for (const item of items) {
  if (item.binary && item.binary.data) {
    item.binary.data.mimeType = 'video/mp4';
    item.binary.data.fileName = item.binary.data.fileName || 'video.mp4';
  }
}
return items;"""
        print("  Set MIME 타입 수정: video/mp4")

    elif 'BGM 생성' in name and 'jsonBody' in p:
        old = p['jsonBody']
        p['jsonBody'] = old.replace('"refinement": 100', '"refinement": 60')
        if old != p['jsonBody']:
            print("  Set BGM: refinement 60")
    
    elif 'AI 주제 생성' in name:
        msgs = p.get('messages', {})
        if isinstance(msgs, dict) and 'values' in msgs:
            for m in msgs['values']:
                c = m.get('content', '')
                if isinstance(c, str) and len(c) > 50 and '단어 반복 금지' not in c:
                    m['content'] = c + WORD_RULE
                    print(f"  Set {name}: word rule")
                    break

# Save
print("\nDeactivating...")
requests.post(f"{N8N_URL}/api/v1/workflows/{WF_ID}/deactivate", headers=HEADERS)

payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData", None),
}
print(f"PUT payload: {len(json.dumps(payload))} bytes")
r = requests.put(f"{N8N_URL}/api/v1/workflows/{WF_ID}", headers=HEADERS, json=payload)
print(f"PUT status: {r.status_code}")
if r.status_code != 200:
    print(f"ERROR: {r.text[:500]}")
    exit(1)

print("Activating...")
requests.post(f"{N8N_URL}/api/v1/workflows/{WF_ID}/activate", headers=HEADERS)

# Verify after 1s
time.sleep(1)
print("\n=== VERIFY (1s) ===")
resp = requests.get(f"{N8N_URL}/api/v1/workflows/{WF_ID}", headers=HEADERS)
vwf = resp.json()
ref_str = '"refinement": 60'
for node in vwf['nodes']:
    name = node.get('name','')
    p = node.get('parameters',{})
    if name == 'NCA 데이터 준비':
        code = p.get('jsCode','')
        xf = 'XFADE_DUR' in code
        kb = 'getKenBurns' in code
        ns = 'SPLIT_SECONDS' not in code
        print(f"  {name}: len={len(code)} XFADE={xf} KenBurns={kb} NoSplit={ns}")
    elif name == 'NCA 제작 결과':
        code = p.get('jsCode','')
        noto = 'Noto Sans KR' in code
        s85 = 'FONT_SIZE = 85' in code
        print(f"  {name}: len={len(code)} Noto={noto} Size85={s85}")
    elif name == 'NCA 자막 추가':
        body = p.get('jsonBody','')
        fd = 'fontsdir' in body
        ft = 'NotoSansKR' in body
        print(f"  {name}: fontsdir={fd} font={ft}")
    elif 'BGM 생성' in name:
        body = p.get('jsonBody','')
        r60 = ref_str in body
        print(f"  {name}: ref60={r60}")

# Verify after 10s
time.sleep(10)
print("\n=== VERIFY (11s) ===")
resp = requests.get(f"{N8N_URL}/api/v1/workflows/{WF_ID}", headers=HEADERS)
vwf = resp.json()
for node in vwf['nodes']:
    name = node.get('name','')
    p = node.get('parameters',{})
    if name == 'NCA 데이터 준비':
        code = p.get('jsCode','')
        print(f"  {name}: len={len(code)} XFADE={'XFADE_DUR' in code}")
    elif name == 'NCA 제작 결과':
        code = p.get('jsCode','')
        print(f"  {name}: len={len(code)} Noto={'Noto Sans KR' in code}")
    elif name == 'NCA 자막 추가':
        body = p.get('jsonBody','')
        print(f"  {name}: fontsdir={'fontsdir' in body}")
