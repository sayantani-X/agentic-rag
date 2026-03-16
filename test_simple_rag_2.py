from pipeline.rag_pipeline import RAGPipeline
from tools.image_generation import generate_image
from tools.image_qa import ask_image_question
from tools.wikipedia_qa import ask_wikipedia
from agents.router_agent import route_query

import warnings
warnings.filterwarnings("ignore")


pipeline = RAGPipeline("data/documents")

image_path = None


while True:

    query = input("\nUser: ")

    if query.lower() in ["exit", "quit", "q"]:
        break

    routing = route_query(query)

    task = routing.get("task", "AMBIGUOUS")
    reason = routing.get("reason", "")

    print("\nRouting decision:", task)
    print("Reason:", reason)

    # ---------------------
    # AMBIGUOUS QUERY
    # ---------------------

    if task == "AMBIGUOUS":

        print("\nI cannot determine which tool to use.")

        print("""
Choose a mode (1/2/3/4):

1. Wikipedia search
2. Context QA
3. Image generation
4. Image question answering
""")

        choice = input("Enter choice: ")

        if choice == "1":
            task = "WIKIPEDIA_SEARCH"

        elif choice == "2":
            task = "CONTEXT_QA"

        elif choice == "3":
            task = "IMAGE_GENERATION"

        elif choice == "4":
            task = "IMAGE_QA"

        else:
            print("Invalid choice.")
            continue

    # ---------------------
    # WIKIPEDIA SEARCH
    # ---------------------

    if task == "WIKIPEDIA_SEARCH":

        print("\nMode: WIKIPEDIA SEARCH")

        answer = ask_wikipedia(query)

        print("\nAnswer:\n", answer)

    # ---------------------
    # CONTEXT QA
    # ---------------------

    elif task == "CONTEXT_QA":

        print("\nMode: CONTEXT QA (Strict Context Mode)")

        result = pipeline.ask(query)

        answer = result["answer"]

        if "not present in the context" in answer.lower():

            print("\nAnswer not found in provided context.")

            choice = input(
                "Would you like to search Wikipedia instead? (y/n): "
            )

            if choice.lower() == "y":

                print("\nSwitching to WIKIPEDIA SEARCH")

                answer = ask_wikipedia(query)

        print("\nAnswer:\n", answer)

    # ---------------------
    # IMAGE GENERATION
    # ---------------------

    elif task == "IMAGE_GENERATION":

        print("\nMode: IMAGE GENERATION")

        path = generate_image(query)

        if path:
            print("\nImage generated at:", path)
        else:
            print("Image generation failed.")

    # ---------------------
    # IMAGE QA
    # ---------------------

    elif task == "IMAGE_QA":

        print("\nMode: IMAGE QUESTION ANSWERING")

        if not image_path:

            image_path = input("Enter image path: ")

        answer = ask_image_question(image_path, query)

        print("\nAnswer:\n", answer)