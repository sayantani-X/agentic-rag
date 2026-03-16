import json
from config import client, LLM_MODEL


SYSTEM_PROMPT = """
You are a routing agent for an AI assistant.

Your job is to decide which task should answer the user's request.

Available tasks:

WIKIPEDIA_SEARCH
Search Wikipedia for reliable factual information. 
Use for general factual knowledge questions.
use when the user explicitly mentions wikipedia.

CONTEXT_QA
Answer ONLY using provided context such as:
documents, typed text, YouTube transcripts, uploaded images,
image links, document links, or other user-provided material.
Use when the user refers to documents, uploaded files, videos, links, or provided context.

IMAGE_GENERATION
Generate an image from a prompt. Use when the user asks to create, generate, draw, design, render, or make an image.

IMAGE_QA
Answer questions about an uploaded image. Use when the user asks about the content of an image.

Rules:

1. Choose exactly ONE task.
2. Never combine tasks.
3. If the request is unclear, return AMBIGUOUS.
4. If the user asks to create/generate/paint/draw/make an image → IMAGE_GENERATION.
5. If the user asks about an uploaded image → IMAGE_QA.
6. If the user refers to provided/uploaded documents, video, or context → CONTEXT_QA.
7. If the question requires general factual knowledge or explicitly mentions wikipedia or web or internet search → WIKIPEDIA_SEARCH.

Return JSON:

{
 "task": "...",
 "reason": "..."
}
"""


def route_query(queries):

    if isinstance(queries, str):
        queries = [queries]

    query_block = "\n".join(queries)

    prompt = f"""
User query and possible interpretations:

{query_block}

Decide which tool should answer the request.
"""

    try:

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )

        text = response.choices[0].message.content

        try:
            return json.loads(text)
        except Exception:
            return {"task": "AMBIGUOUS", "reason": "Router parse failure"}

    except Exception as e:

        return {"task": "AMBIGUOUS", "reason": str(e)}