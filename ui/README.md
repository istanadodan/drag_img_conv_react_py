# 프론트엔드 UI

React + TypeScript + Vite 기반의 HEIC to JPG 변환 서비스 프론트엔드입니다.

> **시작하기**: 프로젝트 루트에서 [`run_app.ps1`](../run_app.ps1) 스크립트를 실행하면 자동으로 시작됩니다.
> 자세한 설정 및 실행 방법은 [루트 README.md](../README.md)을 참조하세요.

## 프로젝트 구조

```
ui/
├── public/
│   └── index.html          # 메인 HTML 파일
├── src/
│   ├── components/
│   │   ├── DropZone.tsx    # 파일 업로드 드롭 존
│   │   ├── JobItem.tsx     # 변환 작업 상태 표시
│   │   └── JobList.tsx     # 작업 목록
│   ├── styles/
│   │   ├── App.css         # 메인 앱 스타일
│   │   ├── DropZone.css    # DropZone 스타일
│   │   ├── JobItem.css     # JobItem 스타일
│   │   ├── JobList.css     # JobList 스타일
│   │   └── index.css       # 글로벌 스타일
│   ├── api.ts              # API 호출 유틸리티
│   ├── types.ts            # TypeScript 타입 정의
│   ├── App.tsx             # 메인 App 컴포넌트
│   ├── main.tsx            # 진입점
│   └── index.css           # 글로벌 스타일
├── package.json            # 프로젝트 설정
├── tsconfig.json           # TypeScript 설정
└── README.md               # 이 파일
```

## 주요 기능

### 1. 다중 존 지원
- 각 존별로 독립적인 드롭 존 제공
- 존별로 다른 품질 설정 적용

### 2. 파일 업로드
- Drag & Drop 지원
- 파일 선택 대화상자 지원
- 다중 파일 동시 업로드

### 3. 실시간 진행률 표시
- WebSocket을 통한 실시간 업데이트
- 진행률 바 표시
- 파일별 변환 상태 표시

### 4. 변환 결과
- 변환 완료, 건너뜀, 실패 상태 구분
- 각 파일의 변환 결과 및 에러 메시지 표시
- 완료된 작업 제거 기능

## API 통신

백엔드 API와 통신하는 엔드포인트 목록은 [루트 README.md의 API 섹션](../README.md#-api-엔드포인트)을 참조하세요.

## 개발 가이드

### 컴포넌트 추가
새로운 컴포넌트를 추가할 때:

1. `src/components/` 디렉토리에 `.tsx` 파일 생성
2. 해당 스타일을 `src/styles/` 디렉토리에 `.css` 파일로 생성
3. `App.tsx`에서 컴포넌트 임포트 및 사용

### 타입 확장
새로운 데이터 타입이 필요한 경우 `src/types.ts`에 추가합니다.

### API 메서드 추가
새로운 API 호출이 필요한 경우 `src/api.ts`에 함수를 추가합니다.

## 스타일링

이 프로젝트는 CSS를 사용하여 스타일링합니다. 각 컴포넌트는 독립적인 CSS 파일을 가지고 있습니다.

### 색상 팔레트
- 주 색상: #4CAF50 (초록색)
- 배경색: #f5f5f5
- 텍스트색: #333
- 에러색: #F44336
- 경고색: #FF9800

### 반응형 디자인
모바일, 태블릿, 데스크톱 화면에 대응하는 반응형 디자인을 지원합니다.

## 브라우저 지원

- Chrome/Edge (최신 2개 버전)
- Firefox (최신 2개 버전)
- Safari (최신 2개 버전)

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
