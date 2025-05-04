import os
import json
from nicegui import ui
from pathlib import Path
import copy
current_dir = Path(__file__).parent

CONFIG_DIR = os.path.join(current_dir.parent.parent, 'app/config')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'mcp_config.json')

# DEFAULT_CONFIG = {"mcp_servers": {}}
DEFAULT_SERVER = {
    'transport': 'sse',    
    'url': 'http://localhost:8080',
    'command': 'python',
    'path': ["path1", "path2"],
    'envs': ["env1=value1"],
}
DEFAULT_SERVER_NAME = 'mcp_server1'
# DEFAULT_CONFIG = {"mcp_servers": {}}  
DEFAULT_CONFIG = {
    "mcp_servers": {
        DEFAULT_SERVER_NAME: copy.deepcopy(DEFAULT_SERVER)
    }
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"load default config")
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
    print(f"server_names: {server_names}")
    selected_name = server_names[0] if server_names else DEFAULT_SERVER_NAME

    class State:
        def __init__(self, name, d):
            self.selected = name
            self.edit_name = name
            # transport 타입에 따라 필요한 필드만 채움
            base = copy.deepcopy(DEFAULT_SERVER)
            if d:
                t = d.get('transport', 'sse')
                base['transport'] = t
                if t == 'sse':
                    base['url'] = d.get('url', base['url'])
                    base['envs'] = d.get('envs', base['envs'])
                else:  # stdio
                    base['command'] = d.get('command', base['command'])
                    base['path'] = d.get('path', base['path'])
                    base['envs'] = d.get('envs', base['envs'])
            self.edit = base
    state = State(selected_name, servers[selected_name] if selected_name in servers else copy.deepcopy(DEFAULT_SERVER))
    print(f"state: {state.edit}")
    def reload_page():
        ui.navigate.to('/mcp')

    def on_select(e):
        name = e.value
        state.selected = name
        state.edit_name = name
        state.edit = copy.deepcopy(config["mcp_servers"][name])
        reload_page()

    def on_add():
        idx = 1
        while f"mcp_server{idx}" in config["mcp_servers"]:
            idx += 1
        new_name = f"mcp_server{idx}"
        config["mcp_servers"][new_name] = copy.deepcopy(DEFAULT_SERVER)
        save_config(config)
        ui.notify(f"{new_name} 추가됨")
        reload_page()

    def on_delete():
        if state.selected in config["mcp_servers"]:
            del config["mcp_servers"][state.selected]
            save_config(config)
            ui.notify(f"{state.selected} 삭제됨")
            reload_page()

    with ui.column().classes('w-[900px] max-w-full'):
        print("on list server")
        if server_names:
            select = ui.select(server_names, value=state.selected, label='서버 선택').on('update:model-value', on_select).classes('w-full')
        else:
            ui.label('서버를 추가하세요.').classes('text-lg text-red-500 mb-4')
        ui.button('서버 추가', on_click=on_add, color='primary').classes('w-full')
        if server_names:
            ui.button('서버 삭제', on_click=on_delete, color='negative').classes('w-full')
        ui.separator()

        # 서버명(키) 입력 필드
        name_input = ui.input('MCP 서버명(고유키)', value=state.edit_name).classes('w-full')
        print(f"name_input: {name_input.value}")
        # 서버 정보 입력 필드
        print(f"state.edit: {state.edit}")
        transport_radio = ui.radio(['sse', 'stdio']).bind_value(state.edit, 'transport').classes('w-full')
        url_input = ui.input('MCP 서버 URL').bind_value(state.edit, 'url').classes('w-full')
        command_input = ui.input('MCP 서버 실행 명령').bind_value(state.edit, 'command').classes('w-full')
        path_str = ','.join(state.edit['path']) if state.edit['path'] else ''
        path_input = ui.input('실행 경로 (쉼표로 구분)', value=path_str).classes('w-full')
        envs_str = ','.join(state.edit['envs']) if state.edit['envs'] else ''
        envs_input = ui.input('서버 환경변수 (쉼표로 구분)', value=envs_str).classes('w-full')
        print(f"envs_input: {envs_input.value}")
        def update_visible():
            print(f"update_visible: {state.edit['transport']}")
            if state.edit['transport'] == 'sse':
                url_input.visible = True
                command_input.visible = False
                path_input.visible = False
            else:
                url_input.visible = False
                command_input.visible = True
                path_input.visible = True
        print("update_visible")
        transport_radio.on('update:model-value', lambda e: update_visible())
        update_visible()

        def on_save():
            new_name = name_input.value.strip()
            if not new_name:
                ui.notify('서버명을 입력하세요.', color='negative')
                return
            if new_name != state.selected and new_name in config["mcp_servers"]:
                ui.notify('이미 존재하는 서버명입니다.', color='negative')
                return
            # path/envs는 저장 시 리스트로 변환
            state.edit['path'] = [p.strip() for p in path_input.value.split(',')] if path_input.value else []
            state.edit['envs'] = [e.strip() for e in envs_input.value.split(',')] if envs_input.value else []
            # transport 타입에 따라 저장 필드 분기
            if state.edit['transport'] == 'sse':
                save_data = {
                    'transport': state.edit['transport'],
                    'url': state.edit['url'],
                    'envs': state.edit['envs'],
                }
            else:  # stdio
                save_data = {
                    'transport': state.edit['transport'],
                    'command': state.edit['command'],
                    'path': state.edit['path'],
                    'envs': state.edit['envs'],
                }
            # 서버명(키)이 변경된 경우 기존 키 삭제 후 새 키로 저장
            if new_name != state.selected:
                if state.selected in config["mcp_servers"]:
                    del config["mcp_servers"][state.selected]
            config["mcp_servers"][new_name] = save_data
            save_config(config)
            ui.notify('MCP 서버 설정이 저장되었습니다.')
            reload_page()

        def on_cancel():
            ui.navigate.to('/')

        with ui.row().classes('w-full mt-4'):
            ui.button('저장', on_click=on_save, color='primary').classes('w-1/2')
            ui.button('취소', on_click=on_cancel, color='secondary').classes('w-1/2')