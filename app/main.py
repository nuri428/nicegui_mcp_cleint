from nicegui import ui
from app.llm_settings import llm_settings_page
from app.mcp_server_settings import mcp_server_settings_page
from app.chatbot import chatbot_page


@ui.page('/')
def index_page() -> None:
    with ui.header():
        ui.button('LLM 설정', on_click=lambda: ui.navigate.to(llm_page))
        ui.button('MCP 서버 설정', on_click=lambda: ui.navigate.to('/mcp'))
        ui.button('챗봇', on_click=lambda: ui.navigate.to('/chat'))
    ui.label('MCP Web Client에 오신 것을 환영합니다!')
    # 추후: LLM 설정, MCP 서버 설정, 챗봇 인터페이스 등 라우팅 추가 예정

@ui.page('/llm')
def llm_page():
    llm_settings_page()

@ui.page('/mcp')
def mcp_page():
    mcp_server_settings_page()

@ui.page('/chat')
def chat_page():
    chatbot_page()

if __name__ in ('__main__', '__mp_main__'):
    ui.run() 