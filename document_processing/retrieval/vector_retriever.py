from config import client, EMBED_MODEL, TOP_K


def embed_query(query):

    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=query
    )
    print("Query embedded")
    return response.data[0].embedding


def retrieve(query, vector_store, k=TOP_K):

    q_embedding = embed_query(query)

    results = vector_store.search(q_embedding, k)

    chunks = []

    for r in results:
        chunks.append(r["chunk"])

    print("Retrieval completed with {} chunks".format(len(chunks)))
    return chunks