# 예시: LLM 설정 dict
llm_config_example_openai = {
    "provider": "openai",
    "api_key": "sk-...",
    "model": "gpt-4",
    "base_url": "https://api.openai.com/v1",
    "temperature": 0.7,  # 온도 추가
}

llm_config_example_ollama = {
    "provider": "ollama",
    "model": "llama2",
    "base_url": "http://localhost:11434",
    "temperature": 0.7,  # 온도 추가
} 