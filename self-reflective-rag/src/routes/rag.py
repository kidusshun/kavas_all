import json, os
from dotenv import find_dotenv, load_dotenv
from fastapi import APIRouter
from dtos.rag import RAGRequest
from workflows.master.graphs import master_workflow 
from langchain_core.messages import HumanMessage, AIMessage
from scripts.chat_persistence_service import ChatHistory

# find and load the .env
load_dotenv(find_dotenv())

# instantiate a short term memory checkpointer
app = master_workflow.compile()

# instantiate the chat history class
chat_history = ChatHistory(
    mongo_host=os.environ.get('MONGO_HOST'),
    mongo_port=os.environ.get('MONGO_PORT'),
    mongo_user=os.environ.get('MONGO_USER'),
    mongo_pass=os.environ.get('MONGO_PASSWORD'),
    openai_key=os.environ.get('API_KEY'),
    openai_model=os.environ.get('MODEL_NAME'),
    auth_mechanism="SCRAM-SHA-256"
)

rag_router = APIRouter(prefix='/rag', tags=['RAG'])

@rag_router.post("/query")
async def get_response(request: RAGRequest):
    history = chat_history.get_chat_history(request.user_id) 

    print(history)

    if history == None:
        history_as_strings = [
            "None"
        ]
    else:
        history_as_strings = [json.dumps(item) for item in history["full_history"]]
        print("History: ", history["full_history"])

    result = app.invoke(
        {
            "prompt": request.question,
            "user_id": request.user_id,
            "conversation_history": history_as_strings,
        }
    )

    chat_history.save_chat_message(request.user_id, request.question, result)

    return result
