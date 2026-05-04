# HEIC to JPG Converter

Apple의 HEIC 이미지 형식을 JPG로 변환하는 풀스택 웹 애플리케이션입니다.
품질 보존에 중점을 두고 EXIF 메타데이터, ICC 색상 프로파일, 파일 타임스탐프를 모두 유지합니다.

**주요 특징**: 동적 Profile 관리, 실시간 변환 진행 상황, 메모리 최적화 처리, 리사이징 옵션

## 🚀 빠른 시작 (Quick Start)

### 방법 1: 자동 실행 스크립트 (권장)

PowerShell에서 프로젝트 루트 디렉토리로 이동 후 다음을 실행하세요:

```powershell
.\run_app.ps1
```

**스크립트가 자동으로 수행하는 작업:**

- ✅ Python 가상환경 활성화
- ✅ FastAPI 백엔드 시작 (http://localhost:8000)
- ✅ Vite 프론트엔드 시작 (http://localhost:5173)
- ✅ 60초마다 서비스 상태 모니터링 및 출력
- ✅ Ctrl+C로 모든 서비스 안전 종료 및 정리

**스크립트 옵션:**

```powershell
# 백엔드만 실행
.\run_app.ps1 -NoFrontend

# 프론트엔드만 실행
.\run_app.ps1 -NoBackend

# 포트 변경
.\run_app.ps1 -BackendPort 8001 -FrontendPort 5174
```

---

### 방법 2: 수동 실행 (터미널 분리)

**터미널 1 - 백엔드 (FastAPI):**

```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**터미널 2 - 프론트엔드 (React + Vite):**

```powershell
cd ui
npm install
npm run dev -- --port 5173
```

---

### 방법 3: CLI 도구

폴더의 모든 HEIC 파일을 배치 변환:

```powershell
# 대화형 모드
python cli.py

# 폴더 경로 지정
python cli.py "C:\Users\YourName\Pictures"
```

---

## 📁 프로젝트 구조

```
heicTojpg/
├── app/                          # FastAPI 백엔드
│   ├── main.py                   # 앱 초기화
│   ├── routers/                  # API 엔드포인트
│   │   ├── zones.py              # Zone CRUD 엔드포인트
│   │   ├── uploads.py            # 파일 업로드 엔드포인트
│   │   └── jobs.py               # 작업 상태 엔드포인트
│   ├── services/                 # 비즈니스 로직
│   │   ├── converter.py          # HEIC→JPG 변환 엔진
│   │   ├── conversion_queue.py    # 비동기 작업 큐
│   │   └── websocket_manager.py   # 실시간 통신
│   ├── schemas/                  # 데이터 모델
│   ├── core/                     # 설정 및 열거형
│   └── config.json               # Profile 설정 파일
├── ui/                           # React 프론트엔드
│   ├── src/                      # React 컴포넌트
│   │   ├── components/           # UI 컴포넌트
│   │   │   ├── DropZone.tsx      # 드래그앤드롭 카드
│   │   │   ├── AddZoneModal.tsx  # Profile 생성/수정 모달
│   │   │   └── JobList.tsx       # 변환 작업 목록
│   │   ├── api.ts                # API 함수
│   │   └── types.ts              # TypeScript 타입
│   ├── package.json              # npm 의존성
│   └── tsconfig.json             # TypeScript 설정
├── cli.py                        # 독립형 CLI 도구
├── run_app.ps1                   # 풀스택 실행 스크립트
├── CLAUDE.md                     # 개발자 가이드
└── README.md                     # 이 파일
```

---

## 🎯 주요 기능

### 1. 동적 Conversion Profile 관리

- **Profile 생성**: "+ Add Profile" 버튼으로 새 profile 추가
- **Profile 수정**: 카드 제목 클릭으로 편집
- **Profile 삭제**: 제목의 ✕ 아이콘으로 삭제
- **설정 저장**: 모든 변경사항은 config.json에 자동 저장
- **리사이징 옵션**: 각 profile별로 선택 가능
  - No Resize: 원본 크기 유지
  - Ratio Scale: 비율로 축소 (예: 80%)
  - Max Length: 최대 길이로 고정 (예: 1920px)

### 2. 품질 보존 변환

- **EXIF 메타데이터 유지** - GPS, 카메라 정보, 촬영 방향
- **ICC 색상 프로파일 보존** - 색 정확성 유지
- **크로마 서브샘플링 4:4:4** - 최고 품질 (기본값은 4:2:0)
- **파일 타임스탐프 유지** - 원본 생성/수정일 보존
- **메모리 기반 처리** - UploadFile을 bytes로 변환해서 I/O 성능 최적화

### 3. 실시간 진행 상황 (WebSocket)

- 변환 중 실시간 진행률 업데이트
- 파일별 상태 (진행 중/완료/실패) 표시
- 브라우저에서 즉시 피드백

### 4. UI 개선

- **Color-coded Profiles**: 선택한 색상이 제목 배경에 표시
- **카드 기반 레이아웃**: 각 profile이 독립적인 드래그앤드롭 영역
- **통합 관리 UI**: 생성, 수정, 삭제 모두 한 화면에서 가능
- **Responsive Design**: 모바일부터 데스크톱까지 최적화

### 5. API 엔드포인트

| 메서드 | 경로                   | 설명                          |
| ------ | ---------------------- | ----------------------------- |
| GET    | `/api/zones`           | 모든 profile 목록 조회        |
| POST   | `/api/zones`           | 새 profile 생성               |
| PUT    | `/api/zones/{zone_id}` | Profile 수정                  |
| DELETE | `/api/zones/{zone_id}` | Profile 삭제                  |
| POST   | `/api/upload/{zone_id}`| 파일 업로드 및 변환 작업 생성 |
| GET    | `/api/jobs/{job_id}`   | 작업 상태 조회                |
| WS     | `/api/jobs/ws/{job_id}`| 실시간 진행 상황 스트림       |

---

## 🔧 기술 스택

### 백엔드

- **FastAPI** - REST API 프레임워크
- **Python 3.x** - 메인 언어
- **Pillow + pillow-heif** - HEIC 읽기 및 JPG 변환
- **uvicorn** - ASGI 서버
- **Pydantic v2** - 데이터 검증

### 프론트엔드

- **React 18** - UI 프레임워크
- **TypeScript** - 타입 안정성
- **Vite** - 번들 및 개발 서버
- **WebSocket API** - 실시간 통신
- **CSS Grid** - 반응형 레이아웃

---

## 📋 요구사항

### 필수

- **Python 3.8+** (가상환경 `venv/` 포함)
- **Node.js 14+** (npm 포함)
- **Windows PowerShell 5.1+**

### 선택 (CLI 도구)

- 프로젝트의 `ui/` 폴더가 없어도 백엔드와 CLI는 독립적으로 동작

---

## 🛠️ 개발 가이드

더 자세한 개발 정보는 [CLAUDE.md](CLAUDE.md)를 참조하세요.

- 아키텍처 상세 설명
- 새로운 기능 추가 방법
- 테스트 및 배포
- 자동화된 유지보수
- 최소 변경 원칙 (Minimal Change Principle)

---

## 📝 사용 예시

### 웹 UI를 통한 변환

1. **브라우저 열기**

   ```
   http://localhost:5173
   ```

2. **Profile 관리**

   - **새 Profile 추가**: "+ Add Profile" 버튼
     - ID: unique identifier (예: web-profile)
     - 이름: 표시 이름 (예: Web Upload)
     - 품질: 1-100
     - 색상: 시각적 구분용
     - 리사이징: 선택적 (비율 또는 최대 길이)
   
   - **Profile 수정**: 카드 제목 클릭
   
   - **Profile 삭제**: 제목 오른쪽 ✕ 아이콘

3. **파일 업로드**

   - 원하는 Profile의 카드로 드래그앤드롭
   - 또는 "Browse" 버튼으로 파일 선택
   - 여러 파일 동시 업로드 가능

4. **진행 상황 확인**

   - 실시간 진행률 표시
   - 파일별 상태 업데이트
   - 에러 메시지 표시

5. **완료 및 다운로드**
   - 변환 완료 후 다운로드 가능
   - 실패한 파일 표시 및 오류 메시지

### CLI를 통한 배치 변환

```powershell
# 폴더의 모든 HEIC 파일 변환
python cli.py "C:\Pictures"

# 프롬프트에서:
# 변환할 폴더 경로를 입력하세요: C:\Pictures
# 🔍 N개의 HEIC 파일 발견
# 품질값을 입력하세요 (1-100, 기본값: 90): 95
# ✅변환 완료 : M개
# ⏭️  건너뜀   : K개
# ❌ 실패      : L개
```

---

## 🐛 문제 해결

### 포트가 이미 사용 중인 경우

```powershell
# 포트 변경
.\run_app.ps1 -BackendPort 8001 -FrontendPort 5174
```

### npm 모듈 누락

```powershell
cd ui
npm install
```

### Python 모듈 누락

```powershell
.\venv\Scripts\python -m pip install -r requirements.txt
```

### PowerShell 실행 정책 오류

```powershell
# 현재 사용자에 대해 스크립트 실행 허용
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Profile 관련 오류

- **프로필 생성 실패**: ID가 중복되지 않았는지 확인
- **색상 미표시**: 색상 선택 후 저장 확인
- **리사이징 미적용**: Profile 수정 후 새로운 파일 업로드 필요

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 💡 더 알아보기

- [백엔드 아키텍처](app/README.md)
- [프론트엔드 문서](ui/README.md)
- [개발 가이드](CLAUDE.md)
- [API 명세서](app/API.md) (선택)