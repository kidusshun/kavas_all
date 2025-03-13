from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from orchestration.router import user_router

app = FastAPI(title="KAVAS Orchestrator", version="0.1.0")

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update this with your frontend origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(user_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload= True)