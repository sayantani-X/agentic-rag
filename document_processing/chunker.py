def chunk_documents(documents, chunk_size=500, overlap=100):

    chunks = []

    for doc in documents:

        text = doc["text"]
        doc_id = doc["doc_id"]

        start = 0
        chunk_id = 0

        while start < len(text):

            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "chunk_id": f"{doc_id}_{chunk_id}",
                "doc_id": doc_id,
                "text": chunk_text,
                "start": start,
                "end": end
            })

            chunk_id += 1
            start += chunk_size - overlap
    print("Documents chunked into {} chunks".format(len(chunks)))
    return chunks