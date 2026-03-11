import faiss
import numpy as np
from config import client, EMBED_MODEL


class VectorStore:

    def __init__(self):

        self.index = None
        self.texts = []
        self.doc_count = 0

    def embed_batch(self, texts, batch_size=128):

        embeddings = []

        for i in range(0, len(texts), batch_size):

            batch = texts[i:i + batch_size]

            response = client.embeddings.create(
                model=EMBED_MODEL,
                input=batch
            )

            for item in response.data:
                embeddings.append(item.embedding)

        return embeddings

    def build_index(self, chunks):

        texts = [c["text"] for c in chunks]

        embeddings = self.embed_batch(texts)

        embeddings = np.array(embeddings).astype("float32")

        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        self.texts = chunks
        self.doc_count = len(chunks)

    def search(self, query_embedding, k=8):

        D, I = self.index.search(
            np.array([query_embedding]).astype("float32"),
            k
        )

        results = []

        for idx in I[0]:
            results.append(self.texts[idx])

        return results