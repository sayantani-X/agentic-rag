from pipeline.rag_pipeline import RAGPipeline

pipeline = RAGPipeline("data/documents")

while True:

    query = input("\nQuestion (type 'exit' to quit): ")

    if query.lower() in ["exit", "quit", "q"]:
        print("Stopping RAG system.")
        break

    result = pipeline.ask(query)

    print("\nAnswer:\n", result["answer"])