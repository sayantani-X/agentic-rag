import json
from config import client, LLM_MODEL


SYSTEM_PROMPT = """
You are a routing agent for an AI assistant.

Your job is to decide which task should answer the user's request.

Available tasks:

WIKIPEDIA_SEARCH
Search Wikipedia for reliable factual information.

CONTEXT_QA
Answer ONLY using provided context such as:
documents, typed text, YouTube transcripts, uploaded images,
image links, document links, or other user-provided material.

IMAGE_GENERATION
Generate an image from a prompt.

IMAGE_QA
Answer questions about an uploaded image.

Rules:

1. Choose exactly ONE task.
2. Never combine tasks.
3. If the request is unclear, return AMBIGUOUS.
4. If the user asks to create an image → IMAGE_GENERATION.
5. If the user asks about an uploaded image → IMAGE_QA.
6. If the user refers to provided documents, video, or context → CONTEXT_QA.
7. If the question requires general factual knowledge or explicitly mentions wikipedia or web or internet search → WIKIPEDIA_SEARCH.

Return JSON:

{
 "task": "...",
 "reason": "..."
}
"""


def route_query(query):

    try:

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ]
        )

        text = response.choices[0].message.content

        try:
            result = json.loads(text)
            return result
        except Exception:
            return {"task": "AMBIGUOUS", "reason": "Router output parsing failed"}

    except Exception as e:

        return {
            "task": "AMBIGUOUS",
            "reason": f"Router failed: {str(e)}"
        }