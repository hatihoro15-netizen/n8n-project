# Claude 작업 파일

Claude가 작업한 파일들을 보관하는 폴더.

## 파일 목록

### 워크플로우
| 파일 | 설명 | n8n ID |
|------|------|--------|
| `oncastudy_shortform_v1.json` | 원본 워크플로우 (19노드) | `itUlZJ2rZfGqkxty` |
| `test_shortform_v4.json` | 테스트 v4 (3가지 수정) | `vdl0YHQCpt9cXI2f` |
| `test_shortform_v5.json` | 테스트 v5 (6가지 개선 + 30~40초) | `vdl0YHQCpt9cXI2f` |
| `test_shortform_v6.json` | 테스트 v6 (5가지 주제 + 효과음 강화) | `vdl0YHQCpt9cXI2f` |

### 효과음
| 파일 | 용도 | MinIO 키 |
|------|------|----------|
| `Whoosh1.mp3` | 장면 전환 | `sfx_whoosh1.mp3` |
| `효과음/띠링1초.mp3` | 강조 (숫자) | `sfx_ding1.mp3` |
| `효과음/띠링2.mp3` | 강조 (기본) | `sfx_ding2.mp3` |
| `효과음/뽀옥1.wav` | 밈 등장 | `sfx_ppook.wav` |
| `효과음/와우.wav` | 리액션 | `sfx_wow.wav` |
| `효과음/키보드타이핑.mp3` | 타이핑 효과 | `sfx_typing.mp3` |
| `효과음/팝.mp3` | 강조 포인트 | `sfx_pop_user.mp3` |

### 스크립트
| 파일 | 설명 |
|------|------|
| `restore_and_fix.py` | 워크플로우 git 복구 + 8가지 수정 + n8n 업로드 |
| `update_8fixes.py` | 8가지 영상 품질 수정만 단독 적용 |
| `update_narration_style.py` | 나레이션 스타일 변경 (팩트→설명형 대화체) |
| `update_memes_and_speed.py` | 밈 카탈로그 확장 + 속도 변경 |
| `update_parser_fix.py` | Gemini JSON 파싱 에러 수정 |

## v6 개선 (2026-02-27) - 현재 테스트 워크플로우

### 주제/프롬프트 개편
- AI 주제 생성: 5가지 핵심 카테고리 랜덤 선택
  1. 내 돈 지키는 꿀팁 (안전/먹튀검증)
  2. 돈 안 쓰고 돈 버는 법 (무료 혜택/앱테크)
  3. 대박 터진 썰 (잭팟/후기)
  4. 레전드 방송 하이라이트 (엔터)
  5. 오늘의 픽 & 정보 요약 (뉴스)
- 프롬프트: 온카스터디 특화 + 빠른 템포 입말체
- 7~8장면, 20~25초, 8~15자 대사
- 밈 최대 2개 (20~25%)

### 효과음 강화
- 사용자 커스텀 효과음 7종 (MinIO 업로드)
- 장면 전환 SFX: whoosh(기본), ppook(밈 등장), ding(숫자)
- 강조 포인트 SFX: `<em>` 태그 있는 세그먼트에 0.3초 후 ding2/pop 추가
- 전환(~7개) + 강조(~6개) = 총 ~13개 효과음

### 자막 수정
- `expansion=none` 추가 → `%` 문자 자막 깨짐 해결
- escapeDrawtext: `;` `,` `[` `]` `\n` 이스케이프 추가
- 자막 크기 fontsize=52, borderw=4, y=h-280

## v5 개선 (2026-02-26)
- 영상 길이: 30~40초 (14~16장면) → v6에서 20~25초로 변경
- 첫 장면 밈 강제 (움직임으로 후킹)
- 밈 비율 40% (최대 5개) → v6에서 25% 최대 2개로 변경
- Ken Burns 줌 효과 → 제거 (무한 반복 버그)

## v4 수정 (2026-02-26)
1. silenceremove 제거 → 나레이션 끊김 해결
2. 노란색 em 강조 제거 → 흰색 자막만
3. 효과음 asplit → 정상 재생

## v3 수정 (2026-02-25)
1. 시각자료-내용 일치: keyword를 dialogue 기반으로
2. `<y>` 태그 노출 수정
3. 밈 일관성: 최대 2개 제한
4. 구체적 수치 필수
5. TTS `<em>` 태그 읽기 방지 (dialogue_tts 분리)
