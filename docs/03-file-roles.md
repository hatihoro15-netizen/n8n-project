# 파일별 역할

## 디렉토리 구조
```
prompt/
├── CLAUDE.md              # 프로젝트 매뉴얼 (작업 규칙)
├── PROGRESS.md            # 작업 진행 기록
├── MEMORY.md              # Claude 프로젝트 메모리
├── characters/            # 캐릭터 참조 이미지
│   ├── Grandma.png
│   ├── Jay.png
│   └── Mike.png
├── docs/                  # 프로젝트 문서
│   ├── 01-architecture.md
│   ├── 02-infra-rules.md
│   ├── 03-file-roles.md
│   ├── 04-workflow.md
│   ├── 05-quality-check.md
│   ├── 06-error-patterns.md
│   ├── 07-report-template.md
│   └── n8n_기획서_최종.xlsx
├── scripts/               # 자동화 스크립트
│   └── quality-check.sh
└── workflows/             # 워크플로우 파일 (v8.4)
    ├── Jay+Mike_v84.json
    ├── 할머니+Mike_v84.json
    ├── 흑형스포츠_v84.json
    ├── v8.4_jay_mike_prompt.md
    ├── v8.4_할머니_mike_prompt.md
    └── v8.4_흑형스포츠_prompt.md
```

## 파일 역할 매핑
| 파일/디렉토리 | 역할 | 담당 에이전트 | 혼용 금지 |
|-------------|------|-------------|----------|
| CLAUDE.md | 작업 규칙/매뉴얼 | 모든 에이전트 (읽기) | 규칙 외 내용 작성 금지 |
| PROGRESS.md | 작업 기록 | 모든 에이전트 (쓰기) | 기록 외 내용 금지 |
| workflows/*.json | n8n 워크플로우 정의 | 워크플로우 에이전트 | 프롬프트 직접 수정 금지 |
| workflows/*_prompt.md | AI 프롬프트 원본 | 콘텐츠 에이전트 | 워크플로우 로직 금지 |
| characters/*.png | 캐릭터 참조 이미지 | 콘텐츠 에이전트 | 이미지 외 파일 금지 |
| docs/*.md | 프로젝트 문서 | 해당 영역 에이전트 | 코드 포함 금지 |
| scripts/*.sh | 자동화 스크립트 | 검증 에이전트 | 비즈니스 로직 금지 |

## 혼용 금지 규칙
- **워크플로우 JSON에 프롬프트 직접 수정 금지**: 프롬프트는 *_prompt.md에서 관리, JSON은 노드 구조만
- **프롬프트 파일에 워크플로우 로직 금지**: 프롬프트 텍스트만 포함
- **docs에 실행 가능 코드 금지**: 문서만 포함
- **scripts에 비즈니스 로직 금지**: 검증/자동화 스크립트만
