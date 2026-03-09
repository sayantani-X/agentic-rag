from document_processing.loader import load_documents, load_youtube
from document_processing.chunker import chunk_documents

from document_processing.retrieval.vector_store import VectorStore
from document_processing.retrieval.retriever import retrieve

from agents.answer_agent import generate_answer


class RAGPipeline:

    def __init__(self, data_path=None, youtube_url=None):

        documents = []

        if data_path:
            docs = load_documents(data_path)
            print(f"Loaded {len(docs)} documents")
            documents.extend(docs)

        if youtube_url:
            yt_docs = load_youtube(youtube_url)
            print("Loaded YouTube transcript")
            documents.extend(yt_docs)

        if documents and documents[0]["doc_id"].startswith("youtube:"):
            chunks = documents
        else:
            chunks = chunk_documents(documents)
        print(f"Documents chunked into {len(chunks)} chunks")

        self.vector_store = VectorStore()
        self.vector_store.build_index(chunks)

        print(f"Index built with {len(chunks)} chunks")

    def ask(self, query):

        contexts = retrieve(query, self.vector_store)

        answer = generate_answer(query, contexts)

        print("\nRetrieved sources:\n")

        for c in contexts:
            print(c["doc_id"])

        return answer