from fastapi import APIRouter
from dtos.rag import RAGRequest
from workflows.master.graphs import master_workflow
from langgraph.checkpoint.memory import MemorySaver 
from langchain_core.messages import HumanMessage, AIMessage
from scripts.chat_persistence_service import get_chat_history, save_chat_message

# instantiate a short term memory checkpointer
# memory = MemorySaver()
app = master_workflow.compile()


rag_router = APIRouter(prefix='/rag', tags=['RAG'])

@rag_router.post("/query")
async def get_response(request: RAGRequest):

    print(request)
    history = ["My name is Tinsae"]# get_chat_history(request.user_id)

    result = app.invoke(
        {
            "prompt": request.question,
            "user_id": request.user_id,
            "conversation_history": history
        }
    )

    # save_chat_message(request.user_id, request.question, result)

    return result
