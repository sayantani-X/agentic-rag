import json
import time
from config import client, LLM_MODEL


def generate_answer(query, contexts):

    context_text = "\n\n".join(
        [c["text"] for c in contexts]
    )

    prompt = f"""
Answer the question using ONLY the context below.
If the answer cannot be found in the context, reply:
"The provided documents do not contain enough information to answer this question."

Return JSON.

Context:
{context_text}

Question:
{query}

Format:

{{
 "answer": "...",
 "evidence": ["chunk1","chunk2"]
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