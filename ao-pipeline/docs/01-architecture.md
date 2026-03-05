# 01-architecture.md — AO Pipeline 시스템 구조

## 개요
"프롬프트 100% 반영" AI 영상 자동화 파이프라인.
프롬프트(P1)를 원문 보존한 채 변수 슬롯만 주입 → 씨덴스로 영상 생성 → 업로드.

## 아키텍처: Producer / Worker / Queue

```
[웹훅/폼] → Producer → [Queue] → Worker → [씨덴스] → [업로드]
                ↓                    ↓
             [DB: jobs]          [DB: job_logs]
```

### Producer (작업 등록, 병렬 가능)
1. 입력 수신 (웹훅/폼)
2. 필수값 검사 (prompt_p1, topic, keywords, category, use_media, upload_target)
3. Job 생성 (job_id, status=queued)
4. Queue에 Push
5. 응답 (job_id 반환)

### Worker (작업 처리, 1건씩)
1. Queue에서 Pop (1건)
2. AO 프롬프트 조립 → 최종 실행 프롬프트
3. 씨덴스 실행 (모드에 따라 미디어 첨부)
4. 결과 저장 (video_out)
5. 업로드 실행 (프록시 적용)
6. 상태 업데이트
7. 로그 기록

### Job 상태 흐름
```
queued → processing → generated → uploading → uploaded
                ↘ failed (retrying → processing)
```

## AO 프롬프트 조립기
P1을 재작성하지 않음. P1 100% 유지 + 변수 슬롯 주입:
- {TOPIC}, {KEYWORDS}, {CATEGORY}
- {IMG_1}~{IMG_4}, {REF_VIDEO}
- (선택) {LANG}, {TONE}, {DURATION}, {ASPECT_RATIO}

## use_media 모드
| 모드 | 동작 |
|------|------|
| auto | 이미지/영상 있으면 활용, 없으면 프롬프트만 |
| forced | 제공된 미디어 반드시 사용 |
| off | 프롬프트만 사용 (미디어 무시) |

## 기존 인프라 (공유)
- n8n: https://n8n.srv1345711.hstgr.cloud
- VPS: root@76.13.182.180
- MinIO: 76.13.182.180:9000
- Postgres: n8n-postgres (docker exec n8n-postgres psql -U n8n -d n8ndb)
