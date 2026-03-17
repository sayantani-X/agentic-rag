import json
import re
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

DETERMINISTIC
Use when the query requires exact computation such as, arithmetic, unit conversions, dates, logic
If the answer must be exact and computable, ALWAYS choose DETERMINISTIC.

Rules:

1. Choose exactly ONE task.
2. Never combine tasks.
3. If the request is unclear, return AMBIGUOUS.
4. If the user asks to create/generate/paint/draw/make an image → IMAGE_GENERATION.
5. If the user asks about an uploaded image → IMAGE_QA.
6. If the user refers to provided/uploaded documents, video, or context → CONTEXT_QA.
7. If the question requires general factual knowledge or explicitly mentions wikipedia or web or internet search → WIKIPEDIA_SEARCH.
8. If the question requires exact computation or logic → DETERMINISTIC.

Return JSON:

{
 "task": "...",
 "reason": "..."
}

Return ONLY valid JSON. Do not include any explanation or text outside JSON.
"""

def parse_json_safe(text):

    try:
        return json.loads(text)

    except Exception:

        # try extracting JSON block
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            try:
                return json.loads(match.group())
            except:
                pass

    return {
        "task": "AMBIGUOUS",
        "reason": "Router parse failure"
    }

def route_query(queries):

    # ensure list
    if isinstance(queries, str):
        queries = [queries]


    # -------------------------
    # BUILD ROUTER INPUT
    # -------------------------
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

        result = parse_json_safe(text)

        return result

    except Exception as e:

        return {
            "task": "AMBIGUOUS",
            "reason": f"Router failed: {str(e)}"
        }