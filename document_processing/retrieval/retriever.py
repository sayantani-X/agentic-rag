from document_processing.retrieval.vector_retriever import embed_query


def retrieve(query, vector_store, k=10):

    if "video" in query.lower():
        query = "youtube video transcript " + query

    q_embedding = embed_query(query)

    results = vector_store.search(q_embedding, k)

    print("Retrieval completed")
    return results