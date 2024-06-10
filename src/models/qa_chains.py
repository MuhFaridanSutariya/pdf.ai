from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain

class QAChains:
    def __init__(self, llm, retriever, chain_type_kwargs):
        self.chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs=chain_type_kwargs,
        )

    def get_chain(self):
        return self.chain