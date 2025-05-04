import os
import json
from nicegui import ui
from pathlib import Path
current_dir = Path(__file__).parent

CONFIG_DIR = os.path.join(current_dir.parent.parent, 'app/config')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'llm_config.json')

global_llm_config = {}

def mask_api_key(api_key: str) -> str:
    if not api_key or len(api_key) < 8:
        return '*' * len(api_key)
    return api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {
            'llm': 'OpenAI',
            'api_key': '',
            'model_name': '',
            'host': ''
        }
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    global_llm_config.clear()
    global_llm_config.update(config)


def llm_settings_page() -> None:
    ui.label('LLM 설정')
    ui.label('언어 모델 선택')

    config = load_config()
    global_llm_config.clear()
    global_llm_config.update(config)

    class LLMConfig:
        def __init__(self, d):
            self.llm = d.get('llm', 'OpenAI')
            self.api_key = d.get('api_key', '')
            self.model_name = d.get('model_name', '')
            self.host = d.get('host', '')
    state = LLMConfig(config)

    llm_radio = ui.radio(['OpenAI', 'Ollama'], value=state.llm).bind_value(state, 'llm')
    api_input = ui.input('OpenAI API Key', password=True, value=state.api_key).bind_value(state, 'api_key')
    model_input = ui.input('모델 이름', value=state.model_name).bind_value(state, 'model_name')
    host_input = ui.input('Host Address (예: 127.0.0.1)', value=state.host or '127.0.0.1').bind_value(state, 'host')

    def update_labels():
        if state.llm == 'OpenAI':
            api_input.label = 'OpenAI API Key'
            model_input.label = '모델 이름 (예: gpt-3.5-turbo)'
            host_input.visible = False
            state.host = ''
        else:
            api_input.label = 'Ollama API Key (필요시)'
            model_input.label = '모델 이름 (예: llama2)'
            host_input.visible = True
            if not state.host:
                state.host = '127.0.0.1'
            host_input.value = state.host
            host_input.label = 'Ollama Host Address (예: 127.0.0.1)'

    llm_radio.on('update:model-value', lambda e: update_labels())
    update_labels()

    if state.api_key:
        ui.label(f"저장된 API Key: {mask_api_key(state.api_key)}")

    def on_save():
        save_config({
            'llm': state.llm,
            'api_key': state.api_key,
            'model_name': state.model_name,
            'host': state.host if state.llm == 'Ollama' else ''
        })
        ui.notify('설정이 저장되었습니다.')

    def on_cancel():
        ui.navigate.to('/')

    with ui.row():
        ui.button('저장', on_click=on_save, color='primary')
        ui.button('취소', on_click=on_cancel, color='secondary') 