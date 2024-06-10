from langchain.chat_models import ChatOpenAI

class ChatModels:
    def __init__(self):
        self.model = ChatOpenAI(
            model="gpt-3.5-turbo-16k-0613",
            temperature=0,
            streaming=True
        )

    def get_model(self):
        return self.model