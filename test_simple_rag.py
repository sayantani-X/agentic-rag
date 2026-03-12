from pipeline.rag_pipeline import RAGPipeline
from tools.image_qa import ask_image_question
from tools.image_generation import generate_image
from tools.wikipedia_qa import ask_wikipedia


print("Choose mode:")
print("1. Ask questions from context (RAG)")
print("2. Ask questions about an image (VQA)")
print("3. Generate an image")
print("4. Ask questions using Wikipedia")

mode = input("Enter choice (1/2/3/4): ")

# -------------------------
# WIKIPEDIA QUESTION ANSWERING
# -------------------------

if mode == "4":

    while True:

        question = input("\nAsk a Wikipedia question (or type 'exit'): ")

        if question.lower() in ["exit", "quit", "q"]:
            break

        answer = ask_wikipedia(question)

        print("\nAnswer:\n", answer)

    exit()


# -------------------------
# IMAGE GENERATION
# -------------------------

if mode == "3":

    prompt = input("Enter image prompt: ")

    path = generate_image(prompt)

    print("\nImage generated and saved at:")
    print(path)

    exit()


# -------------------------
# IMAGE QUESTION ANSWERING
# -------------------------

if mode == "2":

    image_path = input("Enter image path: ")

    while True:

        question = input("\nAsk a question about the image (or type 'exit'): ")

        if question.lower() in ["exit", "quit", "q"]:
            break

        answer = ask_image_question(image_path, question)

        print("\nAnswer:\n", answer)

    exit()


# -------------------------
# RAG PIPELINE
# -------------------------

youtube_url = input("Enter YouTube URL (or press enter to skip): ")

if youtube_url.strip() == "":
    pipeline = RAGPipeline("data/documents")
else:
    pipeline = RAGPipeline("data/documents", youtube_url=youtube_url)


while True:

    query = input("\nQuestion: ")

    if query.lower() in ["exit", "quit", "q"]:
        break

    result = pipeline.ask(query)

    print("\nAnswer:\n", result["answer"])

