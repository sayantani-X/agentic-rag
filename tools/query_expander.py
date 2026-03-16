from config import client, LLM_MODEL


def expand_with_intent(query):

    prompt = f"""
The user's request is unclear.

Rewrite the question into 3 versions that clarify
the user's possible intent.

Keep the same topic but make the action clearer.

Question:
{query}

Return one query per line.
"""

    try:

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content

        variants = [
            q.strip() for q in text.split("\n")
            if q.strip()
        ]

        return [query] + variants[:3]

    except Exception:

        return [query]


def expand_query(query):

    prompt = f"""
Rewrite the query into 3 alternative versions that
preserve the same meaning but use different wording.

Query:
{query}

Return one per line.
"""

    try:

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content

        queries = [
            q.strip() for q in text.split("\n")
            if q.strip()
        ]

        return [query] + queries[:3]

    except Exception:

        return [query]