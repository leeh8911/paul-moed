# PAUL MOED: Personal Assist Universal Language Model On Edge Device  

PAUL MOED는 개인 기기를 기반으로 동작하는 AI 비서 및 노트 관리 시스템입니다.  
이 프로젝트는 사용자의 데이터 프라이버시를 보장하면서도, LLM(대규모 언어 모델)의 지능적인 상호작용 기능을 활용하여 개인 생산성을 극대화하는 것을 목표로 합니다.

---

## 주요 기능

1. **노트 관리**
   - 메모, 이벤트, 할 일을 작성, 수정, 삭제 가능
   - 노트를 카테고리별로 관리하고 태그로 분류

2. **지능형 상호작용**
   - LLM을 활용해 노트를 요약, 분석, 추천
   - 이벤트의 위치 기반 소요 시간 예측
   - 할 일에 예상 소요 시간 계산 및 우선순위 추천

3. **지속적 학습**
   - 인터넷 크롤링을 통해 필요한 학습 데이터를 자동 업데이트
   - 개인 데이터와 학습 자료를 활용해 점진적으로 지능 향상

4. **엣지 디바이스 호환**
   - 모든 데이터는 개인 서버에서 관리
   - 경량화된 LLM을 통해 엣지 디바이스에서도 효율적으로 작동

---

## 시스템 구성

### 1. 클라이언트

- 사용자가 노트를 작성하거나 관리할 수 있는 인터페이스
- Python 기반의 크로스 플랫폼 앱 (예: Kivy)

### 2. 서버

- 노트를 데이터베이스에 저장 및 관리
- LLM을 통해 노트를 분석하고 유용한 정보를 제공
- Python으로 구현된 REST API 서버 (예: FastAPI)

### 3. LLM (Language Model)

- 로컬에서 실행 가능한 경량 LLM (예: Llama2, Qwen)
- 지속적인 학습과 인터넷 크롤링을 통한 지식 갱신

---

## 기술 스택

- **백엔드**: Python, SQLite
- **프론트엔드**: Python 기반 UI (Kivy) 또는 웹 프론트엔드 (React)
- **AI 모델**: PyTorch, Transformers (HuggingFace)
- **기타 도구**: Docker, Celery (백그라운드 작업 관리), OpenCV (OCR 등)

---

## 설치 및 실행

### 1. 프로젝트 복제

```bash
git clone https://github.com/yourusername/paul-moed.git
cd paul-moed
```

### 2. Python 환경 설정

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
cd server
python main.py
```

### 4. 클라이언트 실행

```bash
cd client
python main.py
```

### 5. 테스트 코드

```bash
cd test
pytest test_server.py
```

---

## 사용 방법

클라이언트 앱에서 메모, 이벤트, 할 일을 작성합니다.
서버로 데이터를 전송하면, LLM이 메모를 분석하고 유용한 정보를 제공합니다.
사용자는 업데이트된 데이터를 클라이언트에서 확인할 수 있습니다.

## 향후 계획

1. 추가 기능

    - 음성 명령과 자연어 처리 기반의 상호작용
    - 다국어 지원

2. 최적화

    - 엣지 디바이스에서의 성능 최적화
    - 데이터 전송 및 처리 속도 개선

3. 지속적 학습

    - 인터넷에서 학습 자료를 크롤링해 LLM의 지식을 점진적으로 확장

## 라이선스

이 프로젝트는 **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** 라이선스를 따릅니다.  
이 프로젝트는 비상업적 목적에서만 사용할 수 있으며, 상업적 용도로는 사용할 수 없습니다.  
자세한 내용은 [LICENSE.md](./LICENSE.md)를 참고하세요.
