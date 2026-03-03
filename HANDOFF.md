# HANDOFF - 루믹스 숏폼 브랜치 인수인계

## 브랜치 정보
- **브랜치**: `feature/lumix-shortform`
- **마지막 작업일**: 2026-03-03
- **상태**: 폴더 정리 완료, 운영 가능 상태

## 현재 폴더 구조

```
lumix/
├── CLAUDE.md                    # 프로젝트 작업 규칙
├── PROGRESS.md                  # 진행 상황 기록
├── HANDOFF.md                   # 이 파일 (인수인계)
├── .gitignore
├── claude-tools-lumix/          # 루믹스 전용 리소스 + 워크플로우
│   ├── lumix_shortform_v15.json # 루믹스 숏폼 워크플로우 (최신)
│   ├── test_shortform_v15.json  # 테스트용 워크플로우
│   ├── README.md
│   ├── Whoosh1.mp3
│   ├── oncastudy_memes/         # 밈 이미지 (7카테고리)
│   ├── 주제별 영상/              # 주제별 배경 영상 (13개)
│   ├── 짤/                      # 짤 영상
│   ├── 페페/                    # 페페 밈 이미지 (12개)
│   └── 효과음/                  # 효과음/BGM (7개)
├── docs/                        # 프로젝트 문서
│   ├── 01-architecture.md
│   ├── 02-infra-rules.md
│   ├── 03-file-roles.md
│   ├── 04-workflow.md
│   ├── 05-quality-check.md
│   ├── 06-error-patterns.md
│   └── 07-report-template.md
└── scripts/
    └── quality-check.sh         # 품질 검사 스크립트
```

## 최근 작업 이력

| 날짜 | 커밋 | 내용 |
|------|------|------|
| 2026-03-03 | ad0611b | 불필요 파일 정리 (archive, 구버전, 백업, 온카스터디 삭제) |
| 2026-03-01 | 5c5cb87 | v15: 자막 70 + 훅 75 + 2줄 줄바꿈 + 타이밍 조정 |
| 2026-03-01 | 421d81d | 루믹스 전용 설명형 숏츠 워크플로우 v15 수정 |
| 2026-03-01 | 306cd6f | v15: 워크플로우 이름 변경 |
| 2026-03-01 | 9a41afd | 루믹스 숏츠 워크플로우 초기 설정 |

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `claude-tools-lumix/lumix_shortform_v15.json` | 루믹스 전용 숏폼 워크플로우 (최신) |
| `claude-tools-lumix/test_shortform_v15.json` | 온카스터디 테스트 워크플로우 |
| `scripts/quality-check.sh` | JSON/Python/JS 문법 + 하드코딩 검사 |

## 정리 내역 (2026-03-03)

삭제한 항목:
- `archive/` 전체 (구 기획서, 계획, 스크립트 27개)
- `assets/` 전체 (미사용 캐릭터 이미지 3개, ~24MB)
- `claude-tools/` 구버전 (test_shortform v4~v14, 일회성 스크립트 5개)
- `workflows/` 전체 (온카스터디 워크플로우, 백업 9개, 분석 메모)

이동한 항목:
- `claude-tools/` 리소스 → `claude-tools-lumix/`로 통합

## 다음 작업 제안
- [ ] 워크플로우 수동 실행 테스트 (영상 결과 확인)
- [ ] 루믹스 숏폼 v15 실서비스 적용 여부 결정
