from document_processing.retrieval.vector_retriever import embed_query


def retrieve(query, vector_store, k=5):

    q_embedding = embed_query(query)

    results = vector_store.search(q_embedding, k)

    print("Retrieval completed")
    return results