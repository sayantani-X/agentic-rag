from pipeline.rag_pipeline import RAGPipeline
from tools.image_generation import generate_image
from tools.image_qa import ask_image_question
from tools.wikipedia_qa import ask_wikipedia
from agents.router_agent import route_query
from tools.query_expander import expand_with_intent, expand_query


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

    print("\nRouter decision:", task)

    # -----------------------
    # INTENT EXPANSION
    # -----------------------

    if task == "AMBIGUOUS":

        print("Router uncertain → expanding intent")

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

            choice = input("Choose mode (1/2/3/4): ")

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

    if task == "WIKIPEDIA_SEARCH":

        print("\nMode: WIKIPEDIA SEARCH")

        answer = ask_wikipedia(queries[0])

        print("\nAnswer:\n", answer)

    elif task == "CONTEXT_QA":

        print("\nMode: CONTEXT QA")

        contexts = []

        for q in queries:

            result = pipeline.ask(q)

            contexts.append(result["answer"])

        print("\nAnswer:\n", contexts[0])

    elif task == "IMAGE_GENERATION":

        print("\nMode: IMAGE GENERATION")

        path = generate_image(query)

        print("Image saved at:", path)

    elif task == "IMAGE_QA":

        print("\nMode: IMAGE QUESTION ANSWERING")

        if not image_path:
            image_path = input("Enter image path: ")

        answer = ask_image_question(image_path, query)

        print("\nAnswer:\n", answer)