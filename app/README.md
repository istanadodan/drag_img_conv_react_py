# 백엔드 API 아키텍처

FastAPI 기반 REST API 서버의 상세 아키텍처 및 처리 절차입니다.
일반적인 설정 및 실행 방법은 [루트 README.md](../README.md)을 참조하세요.

## 📁 디렉토리 구조

```
app/
├── core/                      # 핵심 설정
│   └── config.py             # config.json 로드 및 전역 설정
│
├── routers/                   # HTTP 엔드포인트 (표현 계층)
│   ├── zones.py              # GET /api/zones - 설정된 존 조회
│   ├── uploads.py            # POST /api/upload/{zone_id} - 파일 업로드 및 큐 등록
│   └── jobs.py               # GET /api/jobs/{job_id} - 작업 상태 조회 (폴링)
│                             # WS /api/jobs/ws/{job_id} - 실시간 진행 상황 (웹소켓)
│
├── services/                  # 비즈니스 로직 (애플리케이션 계층)
│   ├── converter.py          # HEIC → JPG 변환 함수 (동기)
│   ├── conversion_queue.py   # 변환 작업 큐 관리 (비동기)
│   └── websocket_manager.py  # 클라이언트별 웹소켓 연결 관리
│
├── schemas/                   # API 요청/응답 데이터 모델
│   ├── zone.py               # ZoneResponse
│   ├── job.py                # EnqueueResponse, JobStatusResponse
│   └── ws.py                 # FileResult, JobUpdate
│
└── main.py                    # FastAPI 앱 팩토리 및 미들웨어 설정
```

## 🔄 처리 절차

### 1️⃣ 파일 업로드 및 작업 등록

```
클라이언트
    ↓
POST /api/upload/{zone_id}  (HEIC 파일)
    ↓
routers.uploads.py
    ├─ zone_id 검증
    ├─ 파일을 임시 디렉토리에 저장
    └─ ConversionQueue.enqueue() 호출
            ↓
        services.conversion_queue.py
        ├─ job_id 생성 (UUID)
        ├─ ConversionJobState 생성
        └─ 백그라운드 작업 시작 (asyncio.create_task)
    ↓
응답: { job_id, total }
```

### 2️⃣ 백그라운드 변환 작업 (병렬 처리)

```
ConversionQueue._process(job_id, quality, file_paths)
    ↓
각 파일에 대해:
    ├─ loop.run_in_executor() 호출
    │  └─ ThreadPoolExecutor에서 convert_with_suffix() 실행 (동기)
    │        ↓
    │     services.converter.py
    │     ├─ HEIC 열기
    │     ├─ EXIF 메타데이터 추출
    │     ├─ ICC 색상 프로파일 추출
    │     ├─ RGB 변환
    │     ├─ JPG 저장 (품질 옵션 적용)
    │     └─ 파일 타임스탐프 보존
    │
    ├─ 결과 수집 (FileResult)
    └─ WebSocket 브로드캐스트
           ↓
        services.websocket_manager.py
        └─ 모든 연결 클라이언트에게 JobUpdate 전송
```

### 3️⃣ 상태 조회 (폴링 또는 웹소켓)

```
클라이언트 옵션 A: 폴링
    ↓
GET /api/jobs/{job_id}
    ↓
routers.jobs.py
    └─ ConversionQueue.get_state(job_id) 조회
            ↓
        services.conversion_queue.py
        └─ ConversionJobState 반환
    ↓
응답: JobStatusResponse

클라이언트 옵션 B: 웹소켓 (실시간)
    ↓
WS /api/jobs/ws/{job_id}
    ↓
routers.jobs.py
    └─ WebSocketManager.connect() 등록
            ↓
        services.websocket_manager.py
        ├─ 연결 저장 (active_connections)
        └─ 변환 진행 중 JobUpdate 수신
```

## 📊 주요 모듈 설명

### `core/config.py`
- **역할**: 설정 파일(config.json) 로드
- **제공**: `settings` 객체 (전역 변수)
  - `zones`: 존 목록 (id, label, quality)
  - `max_workers`: 스레드풀 워커 수

### `services/converter.py`
- **함수**: `convert_with_suffix(heic_path, quality) -> dict`
- **기능**: 단일 HEIC 파일을 JPG로 변환
- **특징**: 
  - 동기 함수 (ThreadPoolExecutor에서 실행)
  - EXIF 메타데이터 및 ICC 색상 프로파일 보존
  - 4:4:4 크로마 서브샘플링 (손실 최소화)

### `services/conversion_queue.py`
- **클래스**: `ConversionQueue`
- **역할**: 변환 작업 큐 관리 (비동기)
- **주요 메서드**:
  - `enqueue(zone_id, quality, file_paths)`: 작업 등록 및 반환
  - `_process()`: 백그라운드에서 파일 변환 실행
  - `get_state(job_id)`: 작업 상태 조회

### `services/websocket_manager.py`
- **클래스**: `WebSocketManager`
- **역할**: WebSocket 연결을 job_id별로 관리
- **주요 메서드**:
  - `connect()`: 웹소켓 연결 등록
  - `broadcast()`: 해당 job의 모든 클라이언트에게 메시지 전송
  - `disconnect()`: 연결 해제

## 🚀 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/zones` | 설정된 모든 존 조회 |
| POST | `/api/upload/{zone_id}` | HEIC 파일 업로드 및 변환 작업 등록 |
| GET | `/api/jobs/{job_id}` | 작업 상태 조회 (폴링용) |
| WS | `/api/jobs/ws/{job_id}` | 작업 실시간 진행 상황 스트림 |

## ⚙️ 동작 특징

- **비동기 처리**: FastAPI + asyncio를 통한 비블로킹 I/O
- **병렬 변환**: ThreadPoolExecutor를 통한 다중 파일 동시 변환
- **실시간 업데이트**: WebSocket을 통한 진행 상황 브로드캐스트
- **품질 보존**: EXIF/ICC 프로파일 보존, 크로마 서브샘플링 최소화
- **안정성**: 변환 실패 시 불완전 파일 자동 정리
