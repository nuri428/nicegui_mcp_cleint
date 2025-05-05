import os
import json
from nicegui import ui
from pathlib import Path
import copy

current_dir = Path(__file__).parent

CONFIG_DIR = os.path.join(current_dir.parent.parent, 'app/config')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'mcp_config.json')

DEFAULT_SSE_SERVER = {
    'transport': 'sse',
    'url': 'http://localhost:8080',
    'headers': {},
}
DEFAULT_STDIO_SERVER = {
    'transport': 'stdio',
    'command': 'python',
    'args': ["path1", "path2"],
    'envs': {},
}
MCP_SERVERS_KEY = 'mcpServers'
DEFAULT_SERVER_NAME = 'mcp_server1'
DEFAULT_CONFIG = {
    MCP_SERVERS_KEY: {
        DEFAULT_SERVER_NAME: copy.deepcopy(DEFAULT_STDIO_SERVER)
    }
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print("load default config")
        return copy.deepcopy(DEFAULT_CONFIG)
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def parse_dict_input(input_str):
    d = {}
    for pair in input_str.split(','):
        if '=' in pair:
            k, v = pair.split('=', 1)
            d[k.strip()] = v.strip()
    return d

def dict_to_str(d):
    return ','.join([f'{k}={v}' for k, v in d.items()]) if d else ''

# 상태 객체를 전역으로 유지
state = None
config = None
servers = None
server_names = None
selected_name = None

def mcp_server_settings_page() -> None:
    global state, config, servers, server_names, selected_name
    ui.label('MCP 서버 설정')
    config = load_config()
    servers = config[MCP_SERVERS_KEY]
    server_names = list(servers.keys())
    selected_name = server_names[0] if server_names else DEFAULT_SERVER_NAME

    class State:
        def __init__(self, name, d):
            self.selected = name
            self.edit_name = name
            t = d.get('transport', 'stdio') if d else 'stdio'
            if t == 'sse':
                base = copy.deepcopy(DEFAULT_SSE_SERVER)
                base['url'] = d.get('url', base['url']) if d else base['url']
                base['headers'] = d.get('headers', base['headers']) if d else base['headers']
            else:
                base = copy.deepcopy(DEFAULT_STDIO_SERVER)
                base['command'] = d.get('command', base['command']) if d else base['command']
                base['args'] = d.get('args', base['args']) if d else base['args']
                base['envs'] = d.get('envs', base['envs']) if d else base['envs']
            self.edit = base

    state = State(selected_name, servers[selected_name] if selected_name in servers else copy.deepcopy(DEFAULT_STDIO_SERVER))

    @ui.refreshable
    def render_form():
        with ui.column().classes('w-[900px] max-w-full'):
            if server_names:
                select = ui.select(server_names, value=state.selected, label='서버 선택').on('update:model-value', on_select).classes('w-full')
            else:
                ui.label('서버를 추가하세요.').classes('text-lg text-red-500 mb-4')
            ui.button('서버 추가', on_click=on_add, color='primary').classes('w-full')
            if server_names:
                ui.button('서버 삭제', on_click=on_delete, color='negative').classes('w-full')
            ui.separator()

            name_input = ui.input('MCP 서버명(고유키)', value=state.edit_name).classes('w-full')
            def on_name_change(e):
                new_name = e.value
                print(f"on_name_change: {new_name}")
                # 서버명에 해당하는 설정이 있으면 그 설정을 불러오고, 없으면 기본값
                if new_name in servers:
                    state.edit = copy.deepcopy(servers[new_name])
                else:
                    # 현재 transport에 따라 기본값
                    t = state.edit.get('transport', 'stdio')
                    if t == 'sse':
                        state.edit = copy.deepcopy(DEFAULT_SSE_SERVER)
                    else:
                        state.edit = copy.deepcopy(DEFAULT_STDIO_SERVER)
                state.edit_name = new_name
                render_form.refresh()
            name_input.on('update:model-value', on_name_change)
            def on_transport_change(e):
                print(f"on_transport_change: {e.value}")
                t = e.value
                # transport가 바뀌면 state.edit 전체를 새로 할당
                if t == 'sse':
                    state.edit = copy.deepcopy(DEFAULT_SSE_SERVER)
                else:
                    state.edit = copy.deepcopy(DEFAULT_STDIO_SERVER)
                # 서버명 등은 유지
                state.edit_name = name_input.value
                render_form.refresh()

            transport_radio = ui.radio(['sse', 'stdio'], value=state.edit['transport']).bind_value(state.edit, 'transport').on('update:model-value', on_transport_change).classes('w-full')

            if state.edit['transport'] == 'sse':
                url_input = ui.input('MCP 서버 URL', value=state.edit.get('url', '')).bind_value(state.edit, 'url').classes('w-full')
                headers_str = dict_to_str(state.edit.get('headers', {}))
                headers_input = ui.input('헤더 (key=value,쉼표구분)', value=headers_str).classes('w-full')
            else:
                command_input = ui.input('MCP 서버 실행 명령', value=state.edit.get('command', '')).bind_value(state.edit, 'command').classes('w-full')
                args_str = ','.join(state.edit.get('args', []))
                args_input = ui.input('실행 인자 (쉼표로 구분)', value=args_str).classes('w-full')
                envs_str = dict_to_str(state.edit.get('envs', {}))
                envs_input = ui.input('환경변수 (key=value,쉼표구분)', value=envs_str).classes('w-full')

            def on_save():
                new_name = name_input.value.strip()
                if not new_name:
                    ui.notify('서버명을 입력하세요.', color='negative')
                    return
                if new_name != state.selected and new_name in config[MCP_SERVERS_KEY]:
                    ui.notify('이미 존재하는 서버명입니다.', color='negative')
                    return

                t = state.edit['transport']
                if t == 'sse':
                    state.edit['url'] = url_input.value
                    state.edit['headers'] = parse_dict_input(headers_input.value)
                    save_data = {
                        'transport': 'sse',
                        'url': state.edit['url'],
                        'headers': state.edit['headers'],
                    }
                else:
                    state.edit['command'] = command_input.value
                    state.edit['args'] = [a.strip() for a in args_input.value.split(',')] if args_input.value else []
                    state.edit['envs'] = parse_dict_input(envs_input.value)
                    save_data = {
                        'transport': 'stdio',
                        'command': state.edit['command'],
                        'args': state.edit['args'],
                        'envs': state.edit['envs'],
                    }

                if new_name != state.selected:
                    if state.selected in config[MCP_SERVERS_KEY]:
                        del config[MCP_SERVERS_KEY][state.selected]
                config[MCP_SERVERS_KEY][new_name] = save_data
                save_config(config)
                ui.notify('MCP 서버 설정이 저장되었습니다.')
                render_form.refresh()

            def on_cancel():
                ui.navigate.to('/')

            with ui.row().classes('w-full mt-4'):
                ui.button('저장', on_click=on_save, color='primary').classes('w-1/2')
                ui.button('취소', on_click=on_cancel, color='secondary').classes('w-1/2')

    def on_select(e):
        label = e.args['label'] if 'label' in e.args else None
        if label is None:
            return

        name = label
        state.selected = name
        state.edit_name = name
        state.__init__(name, config[MCP_SERVERS_KEY][name])
        render_form.refresh()

    def on_add():
        idx = 1
        while f"mcp_server{idx}" in config[MCP_SERVERS_KEY]:
            idx += 1
        new_name = f"mcp_server{idx}"
        t = state.edit.get('transport', 'stdio')
        if t == 'sse':
            config[MCP_SERVERS_KEY][new_name] = copy.deepcopy(DEFAULT_SSE_SERVER)
        else:
            config[MCP_SERVERS_KEY][new_name] = copy.deepcopy(DEFAULT_STDIO_SERVER)
        save_config(config)
        ui.notify(f"{new_name} 추가됨")
        render_form.refresh()

    def on_delete():
        if state.selected in config[MCP_SERVERS_KEY]:
            del config[MCP_SERVERS_KEY][state.selected]
            save_config(config)
            ui.notify(f"{state.selected} 삭제됨")
            render_form.refresh()

    render_form()