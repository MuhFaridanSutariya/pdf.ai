from langchain.embeddings.openai import OpenAIEmbeddings

class Embeddings:
    def __init__(self):
        self.model = OpenAIEmbeddings(model="text-embedding-ada-002")

    def get_model(self):
        return self.model
