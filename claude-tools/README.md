# Claude 작업 파일

Claude가 작업한 파일들을 보관하는 폴더.

## 파일 목록

### 워크플로우
| 파일 | 설명 | n8n ID |
|------|------|--------|
| `oncastudy_shortform_v1.json` | 꿀팁 숏츠 + 밈 혼합 워크플로우 (19노드) | `itUlZJ2rZfGqkxty` |

### 스크립트
| 파일 | 설명 |
|------|------|
| `restore_and_fix.py` | 워크플로우 git 복구 + 8가지 수정 + n8n 업로드 |
| `update_8fixes.py` | 8가지 영상 품질 수정만 단독 적용 |

## 8가지 수정사항 (2026-02-25)
1. 프롬프트: 25-30초, 8-10장면, 12자 이내 대사
2. TTS: ko-KR-HyunsuNeural, rate +15%
3. 이미지: per_page=3, 랜덤 선택
4. NCA 검은배경: #000000@1.0
5. NCA 제목: fontsize=72
6. NCA 자막: 14자 줄바꿈, y=h-250
7. NCA 밈루프: -stream_loop -1
8. 이미지 URL 추출: photos 랜덤 선택
