import faiss
import numpy as np
from config import client, EMBED_MODEL


class VectorStore:

    def __init__(self):

        self.index = None
        self.texts = []
        self.doc_count = 0

    def embed(self, text):

        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=text
        )
        # print("Text embedded")
        return response.data[0].embedding

    def build_index(self, chunks, batch_size=50):

        embeddings = []

        for i in range(0, len(chunks), batch_size):

            batch = chunks[i:i+batch_size]

            texts = [c["text"] for c in batch]

            response = client.embeddings.create(
                model=EMBED_MODEL,
                input=texts
            )

            for emb, chunk in zip(response.data, batch):

                embeddings.append(emb.embedding)
                self.texts.append(chunk)

        embeddings = np.array(embeddings).astype("float32")

        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        self.doc_count = len(chunks)
        print("Index built with {} documents".format(self.doc_count))

    def search(self, query_embedding, k=5):

        D, I = self.index.search(
            np.array([query_embedding]).astype("float32"),
            k
        )

        results = []

        for idx in I[0]:
            results.append(self.texts[idx])
        print("Vector Search completed")
        return results