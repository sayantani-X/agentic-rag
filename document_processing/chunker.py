import re


def split_sentences(text):
    return re.split(r'(?<=[.!?]) +', text)


def chunk_documents(documents, chunk_size=500):

    chunks = []

    for doc in documents:

        doc_id = doc["doc_id"]
        paragraphs = doc["text"].split("\n")

        chunk_text = ""
        chunk_id = 0

        for para in paragraphs:

            sentences = split_sentences(para)

            for sent in sentences:

                if len(chunk_text) + len(sent) < chunk_size:
                    chunk_text += sent + " "
                else:

                    chunks.append({
                        "chunk_id": f"{doc_id}_{chunk_id}",
                        "doc_id": doc_id,
                        "text": chunk_text.strip()
                    })

                    chunk_id += 1
                    chunk_text = sent + " "

        if chunk_text:

            chunks.append({
                "chunk_id": f"{doc_id}_{chunk_id}",
                "doc_id": doc_id,
                "text": chunk_text.strip()
            })

    return chunks