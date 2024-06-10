from tempfile import NamedTemporaryFile
from typing import List
from chainlit.types import AskFileResponse
from langchain.document_loaders import PDFPlumberLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
    def __init__(self, file: AskFileResponse):
        self.file = file

    def process_file(self) -> List[Document]:
        if self.file.type != "application/pdf":
            raise TypeError("Only PDF files are supported")

        with NamedTemporaryFile(dir='/', delete=True) as tempfile:
            with open(self.file.path, 'rb') as source_file:
                tempfile.write(source_file.read())
            tempfile.seek(0)

            loader = PDFPlumberLoader(file_path=tempfile.name)
            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=5000,
                chunk_overlap=800
            )
            docs = text_splitter.split_documents(documents)

            for i, doc in enumerate(docs):
                doc.metadata["source"] = f"source_{i}"

            if not docs:
                raise ValueError("PDF file parsing failed.")

            return docs
