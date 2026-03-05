# 03-seedance-api.md — 씨덴스 API 조사 결과

> 조사일: 2026-03-05

## 현황 요약

| 항목 | 상태 |
|------|------|
| 공식 API (ByteDance) | 미출시 (2026-02 기준) |
| Dreamina CPP | 초대 전용 |
| 서드파티 (fal.ai) | 2026-02-24부터 지원, Python/JS SDK |
| 서드파티 (ModelsLab) | 사용 가능, seedance-t2v / seedance-i2v |
| 서드파티 (laozhang.ai) | 최저가 ($0.05/req) |

## 모델 스펙: Seedance 2.0
- 최대 20초 클립 생성
- 480p ~ 1080p 해상도
- 물리 시뮬레이션 (중력, 충돌, 변형)
- 멀티샷 스토리텔링 (캐릭터/씬 일관성 유지)
- 오디오 싱크 지원

## API 엔드포인트 패턴

### 인증
```
Authorization: Bearer {API_KEY}
Content-Type: application/json
```

### Text-to-Video
```http
POST /v2/generate/text
{
  "model": "seedance-2.0",
  "prompt": "A cat playing piano in a jazz bar",
  "aspect_ratio": "9:16",
  "duration": 10
}
```

### Image-to-Video
```http
POST /v2/generate/image
{
  "model": "seedance-2.0",
  "image_url": "https://...",
  "prompt": "The person starts dancing",
  "duration": 10
}
```

### 상태 폴링
```http
GET /v2/tasks/{task_id}
→ { "status": "success", "output": [{ "url": "https://...", "width": 1080, "height": 1920 }] }
```

## 비동기 처리 흐름
1. POST 요청 → task_id 반환 (생성 시작, 완료 아님)
2. GET /tasks/{task_id} 폴링 (5~10초 간격 권장)
3. status=success → output[].url에서 영상 다운로드

## 서드파티별 엔드포인트

### ModelsLab
```
POST https://modelslab.com/api/v6/video/text2video
model_id: "seedance-t2v" 또는 "seedance-i2v"
```

### fal.ai
```
Python: fal.submit("seedance-2.0", ...)
JS: fal.subscribe("seedance-2.0", ...)
```

## 가격 비교
| 프로바이더 | 5초 720p 기준 | 비고 |
|-----------|-------------|------|
| BytePlus (공식) | $0.49~$0.99 | 미출시 |
| ModelsLab | ~$0.15 | 사용 가능 |
| fal.ai | ~$0.10 | SDK 지원 |
| laozhang.ai | ~$0.05 | 최저가 |

## 결론 및 권장사항
1. **1차 추천: fal.ai** — SDK 지원, 안정적, 합리적 가격
2. **2차 추천: ModelsLab** — REST API 직접 호출, n8n HTTP Request 노드 호환
3. API 키 확보 후 테스트 필요 (n8n HTTP Request 노드로 호출)
4. 비동기 폴링 → n8n Wait 노드 또는 Loop 활용

## 출처
- https://modelslab.com/blog/video-generation/seedance-2-api-developer-guide-2026
- https://www.aifreeapi.com/en/posts/seedance-2-api-integration-guide
- https://seedanceapi.org/docs
- https://help.apiyi.com/en/seedance-2-how-to-use-guide-en.html
- https://evolink.ai/blog/seedance-2-api-access-guide-international-developers
