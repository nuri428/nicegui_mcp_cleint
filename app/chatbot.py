from nicegui import ui


def chatbot_page() -> None:
    ui.label('챗봇 인터페이스')
    chat_output = ui.markdown('')
    user_input = ui.input('메시지를 입력하세요')

    def send_message():
        # 실제 LLM 연동 전 임시 응답
        response = f"응답: {user_input.value}"
        chat_output.content = response
        ui.notify('응답이 도착했습니다!')

    ui.button('전송', on_click=send_message) 