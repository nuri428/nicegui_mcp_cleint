from nicegui import ui
from app.settings.llm_settings import llm_settings_page
from app.settings.mcp_server_settings import mcp_server_settings_page
from app.chatbot import chatbot_page

# 사이드 메뉴 항목 정의
side_menu = [
    {'label': 'MCP 클라이언트 규칙 수정', 'path': '/'},
    {'label': 'LLM 설정', 'path': '/llm'},
    {'label': 'MCP 서버 설정', 'path': '/mcp'},
    {'label': '챗봇', 'path': '/chat'},
]

def llm_home():
    ui.label('MCP 클라이언트 규칙 관리 홈').classes('text-xl font-bold mb-4')
    ui.markdown('''
- 좌측 메뉴에서 원하는 기능을 선택하세요.
- LLM 설정, MCP 서버 설정, 챗봇 등 다양한 기능을 사용할 수 있습니다.
''').classes('mb-4')
    ui.icon('home').classes('text-5xl text-primary')

def render_layout(page_title, content_func=None):
    with ui.row().classes('h-screen w-full'):
        # --- 사이드바 ---
        with ui.column().classes('bg-gray-100 w-64 h-full p-4 shadow-lg'):
            ui.label('프로젝트').classes('text-xl font-bold mb-4')
            for item in side_menu:
                ui.button(item['label'], 
                          on_click=lambda path=item['path']: ui.navigate.to(path), 
                          color='white', 
                          icon='chevron_right').classes('w-full justify-start mb-2')
            ui.separator()
            ui.label('최근').classes('mt-4 text-sm text-gray-500')
        # --- 메인 콘텐츠 영역 ---
        with ui.column().classes('flex-1 h-full p-6'):
            with ui.row().classes('items-center mb-4'):
                ui.label(page_title).classes('text-2xl font-bold')
            if content_func:
                content_func()

@ui.page('/')
def index_page():
    print("index_page")
    render_layout('MCP 클라이언트 규칙 홈', llm_home)

@ui.page('/llm')
def llm_page():
    print("llm_page")
    render_layout('LLM 설정', llm_settings_page)

@ui.page('/mcp')
def mcp_page():
    print("mcp_page")
    render_layout('MCP 서버 설정', mcp_server_settings_page)

@ui.page('/chat')
def chat_page():
    print("chat_page")
    render_layout('챗봇', chatbot_page)

if __name__ in ('__main__', '__mp_main__'):
    # ui.run(host='0.0.0.0', port=8080,  persist=False)
    ui.run(host='0.0.0.0', port=8080, storage_secret=None)