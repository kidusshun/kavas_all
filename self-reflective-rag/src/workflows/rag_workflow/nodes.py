from scripts.embedding_service import PineconeEmbeddingManager
from workflows.rag_workflow.states import RAGState
from workflows.rag_workflow.agents import query_extractor
from langchain_openai import ChatOpenAI
from dtos.rag import RAGRequest


def query_extractor(talks: list[RAGRequest], prompt_extractor=query_extractor) -> str:
    """
    Extract the query from the input state.
    """
    print('---EXTRACTING QUERY---')
    prompt = prompt_extractor.invoke({
        "questions": [talk.question for talk in talks]
    })

    return prompt

def retrieve_documents(state: RAGState, retriever: PineconeEmbeddingManager) -> RAGState:
    print('---RETRIEVING---')
    prompt = state['prompt']
    documents = retriever.search_matching(query=prompt)

    return {"prompt": prompt, "documents": documents}

def grade_documents(state: RAGState, document_grader: ChatOpenAI) -> RAGState:
    print("---CHECK DOCUMENT RELEVANCE TO prompt---")
    prompt = state['prompt']
    documents = [f"{doc}" for doc in state['documents']]

    filtered_docs = []
    score = document_grader.invoke({
            "prompt": str(prompt),
            "document": str(''.join(documents))
        })

    result = score.binary_score
    print(result)
    if ("'yes'" in result) or ("'Yes'" in result) or ("'YES'" in result) or ("yes" in result) or ("Yes" in result):
        print("---GRADE: DOCUMENT RELEVANT---")
        filtered_docs.append(documents)
    else:
        print("---GRADE: DOCUMENT NOT RELEVANT---")
    
    return {"documents": filtered_docs, "prompt": prompt}

def generate_response(state: RAGState, answer_generator: ChatOpenAI) -> RAGState:
    print('---GENERATING RESPONSE---')
    documents = state["documents"]
    try:
        _  = state['rewrite_count']
        prompt = state['rewritten_prompt']

    except Exception as e:
        prompt = state['prompt']

    result = answer_generator.invoke({
        "question": prompt,
        "context": documents
    })

    return {
        "generation": result
    }

def transform_query(state: RAGState, prompt_rewriter: ChatOpenAI) -> RAGState:
    print('---REWRITTING---')
   
    try:
        count  = state['rewrite_count']
        prompt = state['rewritten_prompt']
        result = prompt_rewriter.invoke({
        "prompt": prompt
        })
        count += 1
    except Exception as e:
        prompt = state['prompt']
        result = prompt_rewriter.invoke({
        "prompt": prompt
        })
        count = 1

    return {"rewritten_prompt": result, "rewrite_count": count}
