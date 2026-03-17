from pipeline.rag_pipeline import RAGPipeline
from tools.image_generation import generate_image
from tools.image_qa import ask_image_question
from tools.wikipedia_qa import ask_wikipedia
from tools.deterministic_qa import ask_deterministic
from tools.general_qa import ask_general
from agents.router_agent import route_query
from tools.query_expander import expand_with_intent, expand_query

from document_processing.retrieval.retriever import retrieve
from agents.answer_agent import generate_answer
from config import client, LLM_MODEL

from utils.memory_manager import MemoryManager


pipeline = RAGPipeline("data/documents")
memory = MemoryManager()

image_path = None

# -------------------------
# QUERY REWRITE USING MEMORY
# -------------------------

def rewrite_with_memory(query, memory):

    history = memory.get_history_text()

    if not history:
        return query

    prompt = f"""
Rewrite the query ONLY if it depends on previous context.

If the query is independent, return it unchanged.

Conversation:
{history}

Query:
{query}

Rewritten query:
"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()

    except:
        return query


# -------------------------
# MAIN LOOP
# -------------------------

while True:

    query = input("\nUser: ")

    if query.lower() in ["exit", "quit", "q"]:
        print("\nSession ended. Memory cleared.\n")
        break

    # -------------------------
    # RESET MEMORY
    # -------------------------

    if query.lower() in ["reset", "clear memory"]:
        memory.reset()
        continue

    # -------------------------
    # FIXED QUERY HANDLING
    # -------------------------

    original_query = query

    # avoid rewriting long independent queries
    if len(query.split()) < 10:
        rewritten_query = rewrite_with_memory(query, memory)
    else:
        rewritten_query = query

    # 🔥 router uses rewritten query ONLY
    routing = route_query(rewritten_query)

    task = routing.get("task", "AMBIGUOUS")
    reason = routing.get("reason", "")

    print("\nRouter decision:", task)
    print("Reason:", reason)


    # -------------------------
    # INTENT EXPANSION
    # -------------------------

    if task == "AMBIGUOUS":

        print("\nRouter uncertain → expanding intent")

        intent_queries = expand_with_intent(rewritten_query)

        routing = route_query(intent_queries)
        task = routing.get("task", "AMBIGUOUS")

        print("Router after intent expansion:", task)

        if task == "AMBIGUOUS":

            print("""
1. Wikipedia search
2. Context QA
3. Image generation
4. Image QA
5. Deterministic
""")

            choice = input("Choose mode: ")

            mapping = {
                "1": "WIKIPEDIA_SEARCH",
                "2": "CONTEXT_QA",
                "3": "IMAGE_GENERATION",
                "4": "IMAGE_QA",
                "5": "DETERMINISTIC"
            }

            task = mapping.get(choice, "AMBIGUOUS")

    # -------------------------
    # QUERY EXPANSION
    # -------------------------

    if task == "CONTEXT_QA" or task == "WIKIPEDIA_SEARCH":
        queries = expand_query(rewritten_query)
    else:
        queries = [rewritten_query]

    # -------------------------
    # EXECUTION
    # -------------------------

    if task == "DETERMINISTIC":

        print("\nMode: DETERMINISTIC")

        answer = ask_deterministic(original_query)

    elif task == "WIKIPEDIA_SEARCH":

        print("\nMode: WIKIPEDIA SEARCH")

        answer = ask_wikipedia(original_query)

        memory.set_resource("wikipedia")

    elif task == "CONTEXT_QA":

        print("\nMode: CONTEXT QA")

        if not pipeline.initialized:

            choice = input(
                "Do you want to load and use the provided documents? (y/n): "
            )

            if choice.lower() != "y":
                print("Context usage skipped.")
                continue

            pipeline.initialize()

            if pipeline.vector_store is None:
                print("Failed to initialize vector store.")
                continue

        all_contexts = []

        for q in queries:
            contexts = retrieve(q, pipeline.vector_store)
            all_contexts.extend(contexts)

        unique_contexts = {
            c["chunk_id"]: c for c in all_contexts
        }.values()

        result = generate_answer(original_query, list(unique_contexts))
        answer = result["answer"]

        memory.set_resource("documents")

    elif task == "IMAGE_GENERATION":

        print("\nMode: IMAGE GENERATION")

        path = generate_image(original_query)

        if path:
            print("\nImage saved at:", path)
        else:
            print("Image generation failed.")

        continue

    elif task == "IMAGE_QA":

        print("\nMode: IMAGE QUESTION ANSWERING")

        if not image_path:
            image_path = input("Enter image path: ")

        answer = ask_image_question(image_path, original_query)

        memory.set_resource(image_path)

    elif task == "GENERAL":

        print("\nMode: GENERAL")

        answer = ask_general(original_query, memory)

    else:
        print("Could not determine task.")
        continue

    # -------------------------
    # STORE MEMORY
    # -------------------------

    memory.set_mode(task)
    memory.add(original_query, answer)

    # -------------------------
    # OUTPUT
    # -------------------------

    print("\nAnswer:\n", answer)

    