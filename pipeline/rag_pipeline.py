from document_processing.loader import load_documents
from document_processing.chunker import chunk_documents

from document_processing.retrieval.vector_store import VectorStore
from document_processing.retrieval.retriever import retrieve

from agents.answer_agent import generate_answer


class RAGPipeline:

    def __init__(self, data_path):

        documents = load_documents(data_path)

        chunks = chunk_documents(documents)

        self.vector_store = VectorStore()
        self.vector_store.build_index(chunks)

    def ask(self, query):

        results = retrieve(
            query,
            self.vector_store
        )

        answer = generate_answer(query, results)

        return answer