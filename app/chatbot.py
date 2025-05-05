from nicegui import ui
from app.api.react_agent import graph
from app.settings.llm_settings import load_config as load_llm_config
from app.settings.mcp_server_settings import load_config as load_mcp_config
from app.settings.mcp_server_settings import MCP_SERVERS_KEY
from langchain_core.messages import AIMessage

def chatbot_page() -> None:
    messages = []
    chat_column_id = 'chat-column'
    chat_column = ui.column().classes('w-full h-96 bg-gray-100 rounded p-2 overflow-y-auto').style('min-height:300px;').props(f'id={chat_column_id}')

    def add_message(sender, text):
        with chat_column:
            ui.markdown(f'**{sender}:** {text}')
        messages.append({'sender': sender, 'text': text})
        # JS로 스크롤을 가장 아래로 이동
        ui.run_javascript(f"""
            var el = document.getElementById('{chat_column_id}');
            if (el) el.scrollTop = el.scrollHeight;
        """)

    user_input = ui.input('메시지를 입력하세요').classes('w-full')

    async def send_message():
        msg = user_input.value.strip()
        if not msg:
            return
        add_message('나', msg)
        user_input.value = ''
        # LLM/MCP 설정 불러오기
        llm_raw = load_llm_config()
        mcp_raw = load_mcp_config()
        llm_config = {
            'provider': llm_raw.get('llm', '').lower(),
            'api_key': llm_raw.get('api_key', ''),
            'model': llm_raw.get('model_name', ''),
            'base_url': llm_raw.get('host', ''),
            'temperature': llm_raw.get('temperature', 0.7),
        }
        mcp_servers = mcp_raw.get('mcpServers', {})

        client_id = ui.context.client.id
        # AI 메시지용 마크다운 객체 생성 (빈 문자열로)
        ai_md = None
        with chat_column:
            ai_md = ui.markdown('**AI:** ')
        content = ''
        try:
            res = await graph.ainvoke(
                {
                    'messages': [{'role': 'user', 'content': msg}],
                    'llm_config': llm_config,
                    'mcp_config': mcp_servers
                },
                {'thread_id': client_id}
            )
            messages = res['messages']
            last_message = messages[-1]
            if isinstance(last_message, AIMessage):
                content = last_message.content
                ai_md.content = f'**AI:** {content}'
                await ui.run_javascript(f"""
                    var el = document.getElementById('{chat_column_id}');
                    if (el) el.scrollTop = el.scrollHeight;
                """)
        except Exception as e:
            ai_md.content = f'**AI:** 오류 발생: {e}'

    with ui.row().classes('w-full mt-2'):
        ui.button('전송', on_click=send_message, color='primary')
        user_input.on('keydown.enter', send_message) 