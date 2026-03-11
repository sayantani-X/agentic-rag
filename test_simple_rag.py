from pipeline.rag_pipeline import RAGPipeline
from tools.image_qa import ask_image_question


print("Choose mode:")
print("1. Ask questions from documents (RAG)")
print("2. Ask questions about an image (VQA)")

mode = input("Enter choice (1/2): ")


# -------------------------
# IMAGE QUESTION ANSWERING
# -------------------------

if mode == "2":

    image_path = input("Enter image path: ")

    question = input("Ask a question about the image: ")

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