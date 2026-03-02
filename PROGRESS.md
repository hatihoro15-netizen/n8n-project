# n8n 워크플로우 프로젝트 - 진행 상황

## 프로젝트 현재 상태
- **단계**: 아럽토 3단계 - 이미지 캡처 자동화 구현 완료
- **마지막 업데이트**: 2026-03-03
- **활성 워크플로우**: 스포츠 픽 숏츠 v16 (ID: vdl0YHQCpt9cXI2f)

## 완료된 작업
- [x] 프로젝트 초기 설정 시스템 구축 (2026-02-24)
- [x] 꿀팁 숏츠 + 밈 혼합 워크플로우 개편 (2026-02-25)
- [x] MinIO 밈 라이브러리 구축 - Pepe 밈 21개 (2026-02-25)
- [x] 8가지 영상 품질 이슈 수정 (2026-02-25)
- [x] 프로젝트 매뉴얼 시스템 재구축 (2026-02-25)
- [x] 3단계: 이미지 캡처 자동화 구현 (2026-03-03)

## 미완료 작업
- [ ] 캡처 서비스 Docker 빌드 및 배포 (docker build + 서버 실행)
- [ ] MinIO captures 버킷 생성 (mc mb myminio/captures)
- [ ] 캡처 서비스 단독 테스트 (POST /capture { capture_id: "home_full_page" })
- [ ] n8n 수동 테스트 (카테고리 7 사이트 기능 소개 워크플로우)
- [ ] 최종 영상에 라이브365 캡처 화면 정상 표시 확인

---

## 컨텍스트 압축 규칙
- 대화가 길어지면 PROGRESS.md를 요약본으로 압축
- 핵심 결정사항, 아키텍처 변경, 주요 버그 수정만 남기기
- 단순 작업 기록은 삭제하고 결과만 유지
- 새 세션 시작 시 PROGRESS.md만 읽어도 전체 파악 가능하게 유지
- 압축 기준: 동일 주제 반복 기록은 최신 1개만 유지

---

## 작업 기록

### [2026-03-03] 3단계: 이미지 캡처 자동화 구현
- **작업 배경**: 아럽토 유튜브 숏츠 자동화 3단계. AI가 visual_type: "capture"로 지정한 이미지를 라이브365 사이트에서 Puppeteer로 캡처하는 서비스 구축 및 n8n 워크플로우 연동
- **수정 내용**:
  - capture-service 신규 작성 (8파일): Express 서버 + Puppeteer 싱글턴 + MinIO 업로드 + Sharp 이미지 처리
  - 프리셋 시스템 20개 (home/analysis/proto/community 페이지별 5종)
  - Dockerfile + .env.example 배포 설정
  - sports_shortform_v16.json 워크플로우 수정:
    - 세그먼트 분리 노드: capture_id/capture_params/description 필드 추가
    - IF캡처분기 노드: visual_type === 'capture' 분기
    - 캡처 요청 노드: HTTP POST → 캡처 서비스
    - 캡처 URL 정리 노드: 응답 스키마 정규화
    - Merge2 노드: 캡처/비캡처 결과 합침
    - NCA 데이터 준비: capture 타입은 1080x1920 전체 표시 (크롭 없음)
    - 콘텐츠 파싱: capture visual_type 검증 추가
    - 프롬프트 생성: capture 옵션 안내 추가
- **판단 근거**: 사이트 기능 소개 카테고리(7) 영상에 실제 스크린샷 필요
- **수정된 파일**: capture-service/* (8파일 신규), sports_shortform_v16.json
- **검증 결과**: quality-check.sh ALL PASS (JSON 유효, IP 하드코딩 없음)
- **다음 권장 작업**: Docker 빌드 → captures 버킷 생성 → 단독 테스트 → n8n 수동 테스트


### [2026-02-25 05:00] 프로젝트 매뉴얼 시스템 재구축
- **작업 배경**: 프로젝트 관리 시스템 전면 재구축 요청
- **발견한 문제**: 없음 (재구축)
- **수정 내용**: CLAUDE.md, docs/ 7개, PROGRESS.md, quality-check.sh, start.md, settings.json 전체 재작성
- **판단 근거**: 사용자 요청에 따른 체계적 프로젝트 관리 시스템 구축
- **수정된 파일**: CLAUDE.md, docs/01~07, PROGRESS.md, scripts/quality-check.sh, .claude/commands/start.md
- **검증 결과**: quality-check.sh 통과
- **다음 권장 작업**: 워크플로우 수동 실행 테스트

### [2026-02-25 04:30] 8가지 영상 품질 이슈 수정
- **작업 배경**: 워크플로우 실행 결과 영상에서 8가지 이슈 발견
- **발견한 문제**: 밈 짧음, 무관한 이미지, 자막 짤림, 제목 반투명, 글씨 작음, 목소리 부적합, 영상 길이, 자막 동기화
- **수정 내용**:
  - 프롬프트: 25-30초, 8-10장면, 12자 이내 대사
  - NCA: 검은배경(#000000@1.0), fontsize=72, 자막 줄바꿈(14자), 밈 루프(-stream_loop)
  - TTS: HyunsuNeural, rate +15%
  - 이미지: per_page=3, 랜덤 선택
- **판단 근거**: 사용자 피드백 기반 수정
- **수정된 파일**: update_8fixes.py (n8n API로 5개 노드 업데이트)
- **검증 결과**: 8/8 항목 API 적용 확인
- **다음 권장 작업**: 워크플로우 수동 실행 후 영상 확인

### [2026-02-25 03:00] 꿀팁 숏츠 + 밈 혼합 워크플로우 개편
- **작업 배경**: 인기 꿀팁 숏츠 스타일로 워크플로우 전환 (이미지 + 밈 혼합)
- **수정 내용**:
  - MinIO에 밈 라이브러리 구축 (Pepe 밈 21개, 7카테고리)
  - 프롬프트 생성: 밈 혼합 지시, visual_type/meme_mood 출력
  - 콘텐츠 파싱: visual_type/meme_mood 검증
  - 이미지 URL 추출: meme→카탈로그, image→Pexels 분기
  - NCA 데이터 준비: 이미지/영상 FFmpeg 분기 처리
- **검증 결과**: 워크플로우 정상 실행, 영상 생성 성공
- **다음 권장 작업**: 영상 품질 개선 (→ 완료)
