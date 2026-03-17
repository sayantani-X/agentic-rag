from pipeline.rag_pipeline import RAGPipeline
from tools.image_generation import generate_image
from tools.image_qa import ask_image_question
from tools.wikipedia_qa import ask_wikipedia
from agents.router_agent import route_query
from tools.query_expander import expand_with_intent, expand_query
from tools.deterministic_qa import ask_deterministic

from document_processing.retrieval.retriever import retrieve
from agents.answer_agent import generate_answer


pipeline = RAGPipeline("data/documents")

image_path = None


while True:

    query = input("\nUser: ")

    if query.lower() in ["exit", "quit", "q"]:
        break

    # -----------------------
    # FIRST ROUTER PASS
    # -----------------------

    routing = route_query(query)

    task = routing.get("task", "AMBIGUOUS")
    # reason = routing.get("reason", "")

    print("\nRouter decision:", task)
    # print("Reason:", reason)

    # -----------------------
    # INTENT EXPANSION (ONLY IF AMBIGUOUS)
    # -----------------------

    if task == "AMBIGUOUS":

        print("\nRouter uncertain → expanding intent")

        intent_queries = expand_with_intent(query)

        routing = route_query(intent_queries)

        task = routing.get("task", "AMBIGUOUS")

        print("Router after intent expansion:", task)

        if task == "AMBIGUOUS":

            print("\nI still cannot determine the correct mode.")

            print("""
1. Wikipedia search
2. Context QA
3. Image generation
4. Image QA
""")

            choice = input("Choose mode: ")

            if choice == "1":
                task = "WIKIPEDIA_SEARCH"
            elif choice == "2":
                task = "CONTEXT_QA"
            elif choice == "3":
                task = "IMAGE_GENERATION"
            elif choice == "4":
                task = "IMAGE_QA"
            else:
                print("Invalid choice")
                continue

    # -----------------------
    # NORMAL QUERY EXPANSION
    # -----------------------

    if task != "IMAGE_GENERATION":
        queries = expand_query(query)
    else:
        queries = [query]

    # -----------------------
    # EXECUTE TASK
    # -----------------------

    # ✅ WIKIPEDIA
    if task == "WIKIPEDIA_SEARCH":

        print("\nMode: WIKIPEDIA SEARCH")

        answer = ask_wikipedia(queries[0])

        print("\nAnswer:\n", answer)

    # ✅ CONTEXT QA (FIXED VERSION)
    elif task == "CONTEXT_QA":

        print("\nMode: CONTEXT QA")

        # 🔥 ENSURE INITIALIZATION BEFORE RETRIEVAL
        if not pipeline.initialized:

            choice = input(
                "Use the provided documents? (y/n): "
            )

            if choice.lower() != "y":
                print("Context usage skipped.")
                continue

            pipeline.initialize()

            # safety check
            if pipeline.vector_store is None:
                print("Failed to initialize vector store.")
                continue

        all_contexts = []

        for q in queries:
            contexts = retrieve(q, pipeline.vector_store)
            all_contexts.extend(contexts)

        # remove duplicates
        unique_contexts = {
            c["chunk_id"]: c for c in all_contexts
        }.values()

        result = generate_answer(query, list(unique_contexts))

        answer = result["answer"]

        print("\nAnswer:\n", answer)

    # ✅ IMAGE GENERATION
    elif task == "IMAGE_GENERATION":

        print("\nMode: IMAGE GENERATION")

        path = generate_image(query)

        if path:
            print("\nImage saved at:", path)
        else:
            print("Image generation failed.")

    # ✅ IMAGE QA
    elif task == "IMAGE_QA":

        print("\nMode: IMAGE QUESTION ANSWERING")

        if not image_path:
            image_path = input("Enter image path: ")

        answer = ask_image_question(image_path, query)

        print("\nAnswer:\n", answer)

    # -----------------------
    # DETERMINISTIC
    # -----------------------

    elif task == "DETERMINISTIC":

        print("\nMode: DETERMINISTIC")

        answer = ask_deterministic(query)

        print("\nAnswer:\n", answer)