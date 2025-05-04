# MCP Web Client (NiceGUI 기반)

## 개요
이 프로젝트는 `nicegui` 기반의 MCP Web Client로, `langchain-adapter`를 통해 MCP Server와 통신합니다.

## 주요 기능
- LLM(OpenAI, Ollama) 설정 및 저장
- MCP 서버(STDIO, SSE) 설정 및 도구 관리
- 챗봇 인터페이스(텍스트, 파일, 이미지 응답 지원)

## 설치 및 실행

### 1. 패키지 설치
```bash
uv pip install -r requirements.txt
```

### 2. 앱 실행
```bash
python -m app.main
```

## 개발 규칙
- 패키지 관리는 `uv`를 사용합니다.
- 코딩 컨벤션은 **Google Python Style Guide**를 따릅니다.
- 앱 코드는 `app` 폴더에 위치합니다.
