from pipeline.rag_pipeline import RAGPipeline


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