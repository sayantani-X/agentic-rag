import wikipedia
from config import client, LLM_MODEL

# avoid language issues
wikipedia.set_lang("en")


def search_wikipedia(query, top_k=5):

    try:
        results = wikipedia.search(query, results=top_k)
        return results
    except Exception:
        return []


def choose_best_article(query, titles):

    if len(titles) == 1:
        return titles[0]

    options = "\n".join([f"{i+1}. {t}" for i, t in enumerate(titles)])

    prompt = f"""
User question:
{query}

Which Wikipedia article best answers the question?

Options:
{options}

Return ONLY the number.
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.choices[0].message.content.strip()

    try:
        idx = int(answer) - 1
        if 0 <= idx < len(titles):
            return titles[idx]
    except:
        pass

    return titles[0]


def fetch_article(title):

    try:
        # IMPORTANT: disable autosuggest
        page = wikipedia.page(title, auto_suggest=False)
        return page.content[:4000]

    except wikipedia.DisambiguationError as e:
        try:
            page = wikipedia.page(e.options[0], auto_suggest=False)
            return page.content[:4000]
        except:
            return None

    except Exception:
        return None


def ask_wikipedia(question):

    titles = search_wikipedia(question)

    if not titles:
        return "No Wikipedia results found."

    best_title = choose_best_article(question, titles)

    article_text = fetch_article(best_title)

    # fallback if something went wrong
    if not article_text:
        try:
            page = wikipedia.page(question, auto_suggest=True)
            article_text = page.content[:4000]
            best_title = page.title
        except:
            return "Could not retrieve article."

    prompt = f"""
Answer the question using the Wikipedia article below.

Article title: {best_title}

Article content:
{article_text}

Question:
{question}

Provide a clear answer based only on the article.
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content