# 🦎 Gekkota - loT & Al 활용 파충류 사육·관리·관찰 어플리케이션

![Image](https://github.com/user-attachments/assets/0811ef0a-21b4-49ec-a462-c95f132a0bb2)

<br>

> 급성장 중인 파충류 시장에서 사육자들은 최적의 환경 조성과 지속적인 관리에 어려움을 겪고 있으며, <br>
> 이로 인해 높은 폐사율과 건강 문제가 발생하고 있습니다. <br>
> 
> 이를 해결하기 위한 솔루션으로 IoT와 AI를 결합한 스마트 사육 관리 시스템을 제안합니다. <br>
> RADXA 기반 카메라로 실시간 모니터링, 영상 분석을 통한 행동/활동량 파악이 가능합니다. <br>
> sLLM 기반 챗봇을 통해 즉각적으로 맞춤형 사육 정보도 제공받을 수 있습니다. <br>
> 캐릭터 기반 UI의 모바일 앱은 복잡한 데이터를 직관적으로 시각화하며, 기록 관리도 지원합니다. <br>
>
> 본 솔루션을 통해 파충류 시장의 지속적인 성장과 효율적인 사육 문화 정착에 기여할 수 있을 것으로 기대합니다.

<br>

### ✨ 시스템 아키텍쳐
<img width="1378" alt="Image" src="https://github.com/user-attachments/assets/89776670-b5d6-4f0f-bffa-297cb73ce135" />

<br><br>
<hr>

# 📌 Gekkota Back-end Repository

### ✨ 주요 기능

<img width="860" alt="Image" src="https://github.com/user-attachments/assets/521daca5-e9d4-45e5-b895-4c9f56d936d3" />

<br><br>

### ✨ 프로젝트 구조

```
Gekkota-BE/
├── crontab/          # 행동 분석 및 시각화 기능을 담당하는 파충류 행동 데이터 처리 모듈 디렉토리
│   ├── __init__.py
│   ├── active_create.py
│   ├── heatmap_create.py
│   └── hiding_detector.py
│
├── db/               # 데이터베이스 연결 및 외부 저장소 연동을 위한 인프라 유틸리티 디렉토리
│   ├── __init__.py
│   ├── database.py
│   ├── session.py
│   └── s3_utils.py
│
├── llm_api/          # RAG 기반 질문응답을 위한 파충류 사육 지식 데이터 인덱스 및 프롬프트 관리 디렉토리
│   ├── __init__.py
│   ├── rag_chunks.json
│   ├── rag_faiss.index
│   ├── rag_metadata.json
│   └── rag_qa_prompt.py
│
├── repository/       # 엔티티 모델을 기반으로 실제 데이터베이스에 접근하여 CRUD 로직을 처리하는 저장소 계층 디렉토리
│   ├── __init__.py
│   ├── entity/       # 도마뱀 사육 데이터를 위한 데이터베이스 테이블 구조를 정의한 ORM 엔티티 모델 디렉토리
│   │   ├── __init__.py
│   │   ├── active_report_entity.py
│   │   ├── chat_entity.py
│   │   ├── device_entity.py
│   │   ├── pet_active_entity.py
│   │   ├── pet_clean_entity.py
│   │   ├── pet_entity.py
│   │   ├── pet_feed_entity.py
│   │   ├── pet_health_entity.py
│   │   └── user_entity.py
│   ├── active_report_repository.py
│   ├── chat_repository.py
│   ├── device_repository.py
│   ├── pet_active_repository.py
│   ├── pet_clean_repository.py
│   ├── pet_feed_repository.py
│   ├── pet_health_repository.py
│   ├── pet_repository.py
│   └── user_repository.py
│
├── router/           # API 요청을 실제 서비스 로직과 연결하는 FastAPI 라우터 정의 디렉토리
│   ├── __init__.py
│   ├── model/        # 각 라우터에서 사용하는 요청/응답 데이터의 구조를 정의하는 Pydantic 모델 디렉토리
│   │   ├── __init__.py
│   │   ├── chat_model.py
│   │   ├── device_model.py
│   │   ├── pet_active_model.py
│   │   ├── pet_clean_model.py
│   │   ├── pet_feed_model.py
│   │   ├── pet_health_model.py
│   │   ├── pet_model.py
│   │   ├── pet_state_model.py
│   │   ├── rtsp_model.py
│   │   └── user_model.py
│   ├── chat_router.py
│   ├── device_router.py
│   ├── heatmap_router.py
│   ├── pet_active_router.py
│   ├── pet_clean_router.py
│   ├── pet_feed_router.py
│   ├── pet_health_router.py
│   ├── pet_router.py
│   ├── rtsp_router.py
│   ├── s3_router.py
│   └── user_router.py
│
├── service/          # 라우터에서 호출되는 핵심 비즈니스 로직을 구현하는 서비스 계층 디렉토리
│   ├── __init__.py
│   ├── active_report_service.py
│   ├── chat_service.py
│   ├── device_service.py
│   ├── heatmap_service.py
│   ├── pet_active_service.py
│   ├── pet_clean_service.py
│   ├── pet_feed_service.py
│   ├── pet_health_service.py
│   ├── pet_service.py
│   ├── pet_state_service.py
│   ├── rtsp_service.py
│   ├── s3_service.py
│   └── user_service.py
│
├── util/             # 공통 기능, 외부 연동, 설정 관리 등을 지원하는 범용 유틸리티 함수 및 모듈 디렉토리
│   │                   예: Firebase 인증 처리, 설정 파일 로딩, Swagger 설정, 스케줄링, 히트맵 생성 등 기능 지원
│   ├── __init__.py
│   ├── active_create.py
│   ├── config_util.py
│   ├── firebase_util.py
│   ├── heatmap_generator.py
│   ├── scheduler.py
│   └── swagger_util.py
│
├── .env.example      # 환경 변수 템플릿 파일
├── .gitignore        # Git에 포함되지 않을 파일/디렉토리 설정
├── Dockerfile        # Docker 이미지 생성을 위한 빌드 명세
├── firebase_admin_key.json     # Firebase 관리자 권한 인증 키 파일
├── main.py                     # FastAPI 앱 진입점
└── requirements.txt            # 프로젝트 의존 패키지 목록
```
<br><br>

### ✨ ERD

> AI서버에서 yolo_results 테이블에 image(파일명), device(시리얼넘버), date, yolo_results(추론값) 넣으면 <br>
> 본 서버에서 해당 테이블을 참고하여 active_reports 테이블을 채움 <br>

![Image](https://github.com/user-attachments/assets/ac5ec525-5ba9-4d8f-8594-25d9ad95e662)

<br><br>

### ✨ API 엔드포인트

<img alt="Image" src="https://github.com/user-attachments/assets/285a7dd1-7079-4a73-8843-e880b5488569" />
