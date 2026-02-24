# 02. 인프라/서버 규칙

## 서버 접속
- SSH: `sshpass -p "$NCA_PASSWORD" ssh root@$NCA_HOST`
- 비밀번호, IP는 환경변수 또는 설정 파일에서 읽기
- **하드코딩 절대 금지**

## Docker 환경
- 모든 서비스는 Docker 컨테이너로 운영
- 컨테이너 직접 수정 금지 → docker-compose.yml 수정 후 재배포
- 컨테이너 재시작 전 반드시 현재 상태 확인 (`docker ps`)

## 인프라 규칙
1. IP 하드코딩 절대 금지 - 모든 IP는 설정 파일 또는 환경변수에서 읽기
2. 서버 직접 수정 금지 - 반드시 로컬에서 테스트 후 배포
3. 설정값 변경 시 백업 필수 - 변경 전 상태 기록
4. 슬롯 수 임의 증가 금지 - 근본 원인 파악 후 조치
5. 서버 임의 비활성화 금지 - 반드시 사유 기록 후 승인받기

## n8n API 사용 규칙
- 엔드포인트: `$N8N_BASE_URL/api/v1`
- API 키는 환경변수로 관리 (`$N8N_API_KEY`)
- PUT body에 `pinData` 포함 금지 (HTTP 400 발생)
- 대용량 JSON은 파일 기반 curl 사용: `curl -d @file.json`
- API 업로드 후 반드시 n8n 에디터 F5 새로고침

## MinIO (S3 호환 스토리지)
- 포트: 9000 (API), 9001 (콘솔)
- 버킷 정책: `mc anonymous set download`으로 퍼블릭 설정
- URL 형식: `http://$NCA_HOST:9000/<버킷>/<경로>/<파일명>`

## NCA Toolkit (FFmpeg API)
- 엔드포인트: `http://$NCA_HOST:8080/v1/ffmpeg/compose`
- 이미지 입력: `-loop 1 -framerate 30 -t <duration>`
- 영상 입력: `-stream_loop -1` + `trim=duration=<duration>`
- 출력: `-c:v libx264 -pix_fmt yuv420p -movflags +faststart`

## TTS (edge-tts API)
- 내부 주소: `http://172.17.0.1:5100/tts` (Docker 네트워크)
- 요청: `{ "text": "...", "voice": "ko-KR-HyunsuNeural", "rate": "+15%" }`

## 환경 변수 관리
- 하드코딩 금지
- 환경별 설정 파일 분리
- 민감 정보는 .env 파일로 관리 (.gitignore 필수)

## 배포 절차
1. git commit (현재 상태 백업)
2. 변경사항 적용
3. quality-check.sh 실행 및 통과
4. n8n API로 워크플로우 업데이트
5. **n8n 에디터 F5 새로고침** (필수!)
6. 워크플로우 수동 실행 테스트
7. 결과 확인 후 git commit + PROGRESS.md 기록

## 장애 대응
1. 즉시 작업 중단
2. 현재 상태 스크린샷/로그 저장
3. 원인 파악
4. 롤백 또는 수정
5. docs/06-error-patterns.md에 패턴 기록
