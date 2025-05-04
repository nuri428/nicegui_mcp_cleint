from nicegui import ui


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

    def send_message():
        msg = user_input.value.strip()
        if not msg:
            return
        add_message('나', msg)
        # 실제 LLM 연동 전 임시 응답
        response = f"{msg[::-1]}"  # 예시: 입력값 뒤집기
        add_message('AI', response)
        user_input.value = ''

    with ui.row().classes('w-full mt-2'):
        ui.button('전송', on_click=send_message, color='primary')
        user_input.on('keydown.enter', lambda e: send_message()) 