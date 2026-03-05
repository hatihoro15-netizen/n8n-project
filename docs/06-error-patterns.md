# 06-error-patterns.md — 에러 패턴 / 금지 패턴 (정본)

## 새 실수 발생 시 즉시 추가 규칙
- 실수 발생 → 이 파일에 아래 형식으로 패턴 추가
형식:
### [YYYY-MM-DD] 증상 한 줄
- 증상:
- 잘못된 접근:
- 올바른 접근:
- 재발 방지:

## 절대 금지 패턴
- IP/비밀번호/토큰 하드코딩 (모든 비밀값은 ENV/설정 파일에서만)
- 임시방편 조치 (슬롯 수 임의 증가, 서버 임의 비활성화 등)
- 근본 원인 없이 재시도
- 파일 전체 교체 (필요한 부분만 수정)
- 동작 중인 기능 무단 수정
- 여러 파일 동시 수정 (1파일 단위로)
- 커밋 없이 수정 시작

## 등록된 에러 패턴

### n8n API 업로드 후 덮어쓰기 사고
- 증상: API로 업로드한 변경사항이 에디터 저장 시 덮어써짐
- 잘못된 접근: API 업로드 후 에디터에서 바로 작업 계속
- 올바른 접근: API 업로드 후 반드시 에디터 F5 새로고침 → 반영 확인 후 작업
- 재발 방지: 배포 절차에 "F5 새로고침" 단계 필수 포함

### n8n 직렬 노드 삽입 시 $json 체인 끊김
- 증상: 직렬로 HTTP Request 삽입 후 이후 노드에서 $json이 엉뚱한 값 참조
- 잘못된 접근: $json 그대로 참조
- 올바른 접근: `$('원본노드명').first().json.xxx`로 명시적 참조
- 재발 방지: 직렬 삽입 시 이후 노드 $json 참조 전수 확인

### n8n Google Sheets update 이후 노드 미실행
- 증상: 매칭 행 없을 때 이후 노드가 실행 안 됨
- 잘못된 접근: alwaysOutputData 없이 사용
- 올바른 접근: Google Sheets update 노드에 alwaysOutputData: true 설정
- 재발 방지: Sheets update 노드 추가 시 항상 alwaysOutputData 확인

### n8n top-level / activeVersion 불일치
- 증상: 워크플로우 수정 후 실행 시 구버전이 실행됨
- 잘못된 접근: top-level nodes만 수정
- 올바른 접근: top-level nodes와 activeVersion.nodes 양쪽 다 수정
- 재발 방지: n8n 수정 작업 시 양쪽 확인 체크리스트 포함
