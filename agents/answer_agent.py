import json
import time
from config import client, LLM_MODEL


def generate_answer(query, contexts):

    context_text = "\n\n".join(
    [f"Source: {c['doc_id']}\n{c['text']}" for c in contexts]
    )

    prompt = f"""
You are a question-answering assistant working on a Retrieval-Augmented Generation (RAG) system.

The system retrieves text from documents and video transcripts. Your job is to answer the question using the retrieved context.

Guidelines:

1. Use the provided context as the primary source of information.
2. If the question refers to "this video", "the video", "this document", or "the material", assume it refers to the provided context.
3. If multiple context chunks mention related ideas, combine them to produce a clear answer.
4. If the context contains timestamps (e.g. [32.5s]), they refer to moments in a video transcript.
5. If the context does not contain enough information, say "The provided context does not contain enough information to answer this question" before answering with general knowledge.

Context:
{context_text}

Question:
{query}

Answer using the information from the context.

Return JSON in this format:

{{
 "answer": "...",
 "evidence": ["chunk_id_1","chunk_id_2"]
}}
"""

    max_retries = 5
    delay = 2

    for attempt in range(max_retries):

        try:

            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            text = response.choices[0].message.content

            try:
                return json.loads(text)
            except:
                return {
                    "answer": text,
                    "evidence": []
                }

        except Exception as e:

            print("API error:", e)

            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                raise e
    
    print("Answer generated for query: {}".format(query))