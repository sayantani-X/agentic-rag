from config import client, LLM_MODEL

def ask_general(query, memory):

    history = memory.get_history_text()

    prompt = f"""
Continue the conversation naturally.

Conversation so far:
{history}

User:
{query}

Assistant:
"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"