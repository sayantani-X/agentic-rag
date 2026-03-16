Below is a **clean, complete snapshot of your current Phase-1 RAG system** with:

✔ multi-format documents
✔ YouTube video transcripts
✔ FAISS vector retrieval
✔ improved answer prompt
✔ timestamp-aware transcript chunks

❌ **query expander removed** (as requested)
❌ no verification / reflexion agents

This is a **stable baseline RAG**.

---

# Project Structure

```
project/
│
├── config.py
│
├── agents/
│   └── answer_agent.py
│
├── document_processing/
│   ├── loader.py
│   ├── chunker.py
│   └── youtube_loader.py
│
├── retrieval/
│   ├── vector_retriever.py
│   ├── vector_store.py
│   └── retriever.py
│
├── pipeline/
│   └── rag_pipeline.py
│
└── test_simple_rag.py
```

---

# 1️⃣ `config.py`

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBED_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
TOP_K = 8
```

---

# 2️⃣ `agents/answer_agent.py`

```python
import json
from config import client, LLM_MODEL


def generate_answer(query, contexts):

    context_text = "\n\n".join(
        [
            f"Source: {c['doc_id']}\nContent: {c['text']}"
            for c in contexts
        ]
    )

    prompt = f"""
You are a question-answering assistant working on a Retrieval-Augmented Generation (RAG) system.

The system retrieves text from documents and video transcripts.

Guidelines:

1. Use the provided context as the primary source of information.
2. If the question refers to "this video" or "this document", assume it refers to the retrieved context.
3. Combine information from multiple chunks when necessary.
4. If timestamps like [32.5s] appear, they refer to moments in a video.

Context:
{context_text}

Question:
{query}

Return JSON:

{{
 "answer": "...",
 "evidence": []
}}
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content

    try:
        return json.loads(text)
    except:
        return {
            "answer": text,
            "evidence": []
        }
```

---

# 3️⃣ `document_processing/loader.py`

```python
import os
from pypdf import PdfReader
from docx import Document
from document_processing.youtube_loader import load_youtube_video


def load_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_pdf(path):

    reader = PdfReader(path)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def load_docx(path):

    doc = Document(path)

    text = []

    for para in doc.paragraphs:
        text.append(para.text)

    return "\n".join(text)


def load_documents(folder_path):

    documents = []

    for filename in os.listdir(folder_path):

        path = os.path.join(folder_path, filename)

        try:

            if filename.endswith(".txt"):
                text = load_txt(path)

            elif filename.endswith(".pdf"):
                text = load_pdf(path)

            elif filename.endswith(".docx"):
                text = load_docx(path)

            else:
                continue

            documents.append({
                "doc_id": filename,
                "text": text.strip()
            })

        except Exception as e:
            print(f"Skipping {filename}: {e}")

    return documents


def load_youtube(url):
    return load_youtube_video(url)
```

---

# 4️⃣ `document_processing/chunker.py`

```python
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

    return chunks
```

---

# 5️⃣ `document_processing/youtube_loader.py`

```python
import re
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url):

    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)

    if match:
        return match.group(1)

    return None


def load_youtube_video(url):

    video_id = extract_video_id(url)

    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)

    chunks = []

    current_text = ""
    start_time = transcript[0].start

    window = 30

    for segment in transcript:

        if segment.start - start_time < window:

            current_text += segment.text + " "

        else:

            chunks.append({
                "doc_id": f"youtube:{video_id}",
                "text": f"[{start_time:.1f}s] {current_text.strip()}"
            })

            start_time = segment.start
            current_text = segment.text + " "

    if current_text:
        chunks.append({
            "doc_id": f"youtube:{video_id}",
            "text": f"[{start_time:.1f}s] {current_text.strip()}"
        })

    return chunks
```

---

# 6️⃣ `retrieval/vector_retriever.py`

```python
from config import client, EMBED_MODEL


def embed_query(query):

    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=query
    )

    return response.data[0].embedding
```

---

# 7️⃣ `retrieval/vector_store.py`

```python
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

        return response.data[0].embedding

    def build_index(self, chunks):

        embeddings = []

        for chunk in chunks:

            emb = self.embed(chunk["text"])

            embeddings.append(emb)
            self.texts.append(chunk)

        embeddings = np.array(embeddings).astype("float32")

        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

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
```

---

# 8️⃣ `retrieval/retriever.py`

```python
from retrieval.vector_retriever import embed_query
from config import TOP_K


def retrieve(query, vector_store, k=TOP_K):

    q_embedding = embed_query(query)

    results = vector_store.search(q_embedding, k)

    return results
```

---

# 9️⃣ `pipeline/rag_pipeline.py`

```python
from document_processing.loader import load_documents, load_youtube
from document_processing.chunker import chunk_documents

from retrieval.vector_store import VectorStore
from retrieval.retriever import retrieve

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

        chunks = chunk_documents(documents)

        print(f"Documents chunked into {len(chunks)} chunks")

        self.vector_store = VectorStore()
        self.vector_store.build_index(chunks)

        print(f"Index built with {len(chunks)} chunks")

    def ask(self, query):

        contexts = retrieve(query, self.vector_store)

        answer = generate_answer(query, contexts)

        return answer
```

---

# 🔟 `test_simple_rag.py`

```python
from pipeline.rag_pipeline import RAGPipeline


youtube_url = input("Enter YouTube URL (or press enter to skip): ")

if youtube_url.strip() == "":
    pipeline = RAGPipeline("data/documents")
else:
    pipeline = RAGPipeline("data/documents", youtube_url=youtube_url)


while True:

    query = input("\nQuestion: ")

    if query.lower() in ["exit", "quit", "q"]:
        break

    result = pipeline.ask(query)

    print("\nAnswer:\n", result["answer"])
```

---

# Your Current System Capabilities

✔ PDF documents
✔ DOCX documents
✔ TXT files
✔ YouTube videos
✔ timestamp-aware transcript chunks
✔ FAISS vector retrieval
✔ simple RAG answer generation

---

# Architecture

```
Documents / YouTube
        ↓
Loader
        ↓
Chunking
        ↓
Embedding
        ↓
FAISS
        ↓
Retriever
        ↓
Answer Agent
```

---

If you'd like, the **next upgrade I recommend before moving to agents** is one small change that makes retrieval from long documents **significantly more accurate without adding any extra API calls**.
