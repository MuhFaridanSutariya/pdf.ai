import chainlit as cl
import asyncio
from typing import Dict, Optional
from literalai import LiteralClient
from chainlit.types import AskFileResponse


from src.pdf_processor import PDFProcessor
from src.search_engine_builder import SearchEngineBuilder
from src.models.chat_models import ChatModels
from src.models.embeddings import Embeddings
from src.models.qa_chains import QAChains
from src.prompts import EXAMPLE_PROMPT, COMBINE_PROMPT

class PDFChatApplication:
    def __init__(self, client: LiteralClient):
        self.client = client

    async def on_chat_start(self):
        files = None
        while files is None:
            files = await cl.AskFileMessage(
                content="Please Upload the PDF only contain text file you want to chat with...",
                accept=["application/pdf"],
                max_size_mb=50,
            ).send()
        file = files[0]

        msg = cl.Message(content=f"Processing `{file.name}`...")
        await msg.send()

        processor = PDFProcessor(file=file)
        docs = processor.process_file()
        cl.user_session.set("docs", docs)
        msg.content = f"`{file.name}` processed. Loading ..."
        await msg.update()

        embeddings_model = Embeddings().get_model()
        chat_model = ChatModels().get_model()

        try:
            search_engine = await cl.make_async(SearchEngineBuilder(docs, embeddings_model).create_search_engine)()
        except Exception as e:
            await cl.Message(content=f"Error: {e}").send()
            raise SystemError

        msg.content = f"`{file.name}` loaded. You can now ask questions!"
        await msg.update()

        chain_type_kwargs = {"prompt": COMBINE_PROMPT, "document_prompt": EXAMPLE_PROMPT}
        qa_chains = QAChains(llm=chat_model, retriever=search_engine.as_retriever(max_token_limit=4097), chain_type_kwargs=chain_type_kwargs).get_chain()

        cl.user_session.set("qa_chains", qa_chains)

    async def main(self, message: cl.Message):
        qa_chains = cl.user_session.get("qa_chains")
        response = await qa_chains.acall(
            message.content,
            callbacks=[cl.AsyncLangchainCallbackHandler(stream_final_answer=True)]
        )
        answer = response["answer"]
        sources = response["sources"].strip()

        docs = cl.user_session.get("docs")
        metadatas = [doc.metadata for doc in docs]
        all_sources = [m["source"] for m in metadatas]

        source_elements = []
        if sources:
            found_sources = []
            for source in sources.split(","):
                source_name = source.strip().replace(".", "")
                try:
                    index = all_sources.index(source_name)
                except ValueError:
                    continue
                text = docs[index].page_content
                found_sources.append(source_name)
                source_elements.append(cl.Text(content=text, name=source_name))

            if found_sources:
                answer += f"\nSources: {', '.join(found_sources)}"
            else:
                answer += "\nNo sources found"

        await cl.Message(content=answer, elements=source_elements).send()

    def oauth_callback(self, provider_id: str, token: str, raw_user_data: Dict[str, str], default_user: cl.User) -> Optional[cl.User]:
        return default_user


async def run_app():
    client = LiteralClient(api_key=os.getenv("LITERAL_API_KEY"))
    app = PDFChatApplication(client=client)

    # Register the callbacks
    cl.on_chat_start(app.on_chat_start)
    cl.on_message(app.main)
    cl.oauth_callback(app.oauth_callback)

    cl.run()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    asyncio.run(run_app())
