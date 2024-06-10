from typing import List
import chromadb
from chromadb.config import Settings
from langchain.schema import Document
from langchain.schema.embeddings import Embeddings
from langchain.vectorstores.chroma import Chroma
from langchain.vectorstores.base import VectorStore

class SearchEngineBuilder:
    def __init__(self, docs: List[Document], embeddings: Embeddings):
        self.docs = docs
        self.embeddings = embeddings

    def create_search_engine(self) -> VectorStore:
        client = chromadb.EphemeralClient()
        client_settings = Settings(
            allow_reset=True,
            anonymized_telemetry=False
        )

        search_engine = Chroma(
            client=client,
            client_settings=client_settings
        )
        search_engine._client.reset()

        search_engine = Chroma.from_documents(
            client=client,
            documents=self.docs,
            embedding=self.embeddings,
            client_settings=client_settings
        )

        return search_engine
