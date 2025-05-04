import os
import json
from nicegui import ui

CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'mcp_config.json')

# 기본 구조 생성
DEFAULT_CONFIG = {
    "mcp_servers": {}
}

# 서버 설정 기본값
DEFAULT_SERVER = {
    'transport': 'sse',
    'name': '',
    'url': '',
    'command': '',
    'path': [],
    'envs': [],
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def mcp_server_settings_page() -> None:
    ui.label('MCP 서버 설정')
    config = load_config()
    servers = config["mcp_servers"]
    server_names = list(servers.keys())
    selected_name = server_names[0] if server_names else ''

    class State:
        def __init__(self, d, selected):
            self.selected = selected
            self.edit = d.copy() if d else DEFAULT_SERVER.copy()
    state = State(servers[selected_name] if selected_name else DEFAULT_SERVER, selected_name)

    def reload_page():
        ui.navigate.to('/mcp')

    def on_select(e):
        name = e.value
        state.selected = name
        state.edit = config["mcp_servers"][name].copy()
        reload_page()

    def on_add():
        idx = 1
        while f"server{idx}" in config["mcp_servers"]:
            idx += 1
        new_name = f"server{idx}"
        config["mcp_servers"][new_name] = DEFAULT_SERVER.copy()
        save_config(config)
        ui.notify(f"{new_name} 추가됨")
        reload_page()

    def on_delete():
        if state.selected in config["mcp_servers"]:
            del config["mcp_servers"][state.selected]
            save_config(config)
            ui.notify(f"{state.selected} 삭제됨")
            reload_page()

    if server_names:
        select = ui.select(server_names, value=state.selected, label='서버 선택').on('update:model-value', on_select)
    ui.button('서버 추가', on_click=on_add, color='primary')
    if server_names:
        ui.button('서버 삭제', on_click=on_delete, color='negative')
    ui.separator()

    if not server_names:
        ui.label('서버를 추가하세요.')
        return

    name_input = ui.input('MCP 서버 명칭', value=state.edit['name']).bind_value(state.edit, 'name')
    transport_radio = ui.radio(['sse', 'stdio'], value=state.edit['transport']).bind_value(state.edit, 'transport')
    url_input = ui.input('MCP 서버 URL', value=state.edit['url']).bind_value(state.edit, 'url')
    command_input = ui.input('MCP 서버 실행 명령', value=state.edit['command']).bind_value(state.edit, 'command')
    path_input = ui.input('실행 경로 (쉼표로 구분)', value=','.join(state.edit['path']))
    envs_input = ui.input('서버 환경변수 (쉼표로 구분)', value=','.join(state.edit['envs']))

    def update_visible():
        if state.edit['transport'] == 'sse':
            url_input.visible = True
            command_input.visible = False
            path_input.visible = False
        else:
            url_input.visible = False
            command_input.visible = True
            path_input.visible = True

    transport_radio.on('update:model-value', lambda e: update_visible())
    update_visible()

    def on_save():
        # 서버명 중복/빈값 체크
        new_name = name_input.value.strip()
        if not new_name:
            ui.notify('서버명을 입력하세요.', color='negative')
            return
        if new_name != state.selected and new_name in config["mcp_servers"]:
            ui.notify('이미 존재하는 서버명입니다.', color='negative')
            return
        # path/envs는 쉼표로 분리하여 리스트로 저장
        state.edit['path'] = [p.strip() for p in path_input.value.split(',')] if path_input.value else []
        state.edit['envs'] = [e.strip() for e in envs_input.value.split(',')] if envs_input.value else []
        # 서버명 변경 시 key도 변경
        if new_name != state.selected:
            del config["mcp_servers"][state.selected]
        config["mcp_servers"][new_name] = state.edit.copy()
        save_config(config)
        ui.notify('MCP 서버 설정이 저장되었습니다.')
        reload_page()

    def on_cancel():
        ui.navigate.to('/')

    with ui.row():
        ui.button('저장', on_click=on_save, color='primary')
        ui.button('취소', on_click=on_cancel, color='secondary') 