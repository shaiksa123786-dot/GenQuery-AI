from studentapp.rag.embeddings import embed_text
from studentapp.rag.generator import generate_answer
from studentapp.rag.vector_store import search_chunks
from studentapp.rag.structured_retriever import(
    get_student_data,
    student_data_to_context
)

#main RAG_pipeline
#connect student data , document retrieval,
#asn gemini to generaet the final answer.
def ask_rag(question , user):
    #get the loggedin students structured data (db)
    student_data = get_student_data(user)
    structured_context = student_data_to_context(
        student_data
    )
    #convert the user query into vectors so that it can be compared with document vector 
    query_vector = embed_text(question)
    #searxh chromadb for the most relavant  document chunk belongimg to this student 
    results = search_chunks(
        query_vector, student_id = student_data["student_id"],
        n_results=3

    )
    documents= results["documents"][0]
    metadatas = results["metadatas"][0]
    #combine the retireved documents chunks into ome piece of context for gemini 
    document_context = "\n\n".join(
        documents
    )
    #combine the  structured student data and unstrutured docment data
    context = f"""
STRUCTURED STUDENT DATA :
{structured_context}
UNSTRUCTURES DOCUMENT DATA :
{document_context}"""
    #send the question and combine context to gemini model to generate final answer 
    result = generate_answer(question,context)
    sources =[]
    for metadata in metadatas:
        source = metadata.get("source")
        if source:
            sources.append({
                "document_id":metadata.get("document_id"),
                "source":source,
                "chunk_index":metadata.get("chunk_index")
            })
    response = result.model_dump()
    response["sources"] = sources
    return response 