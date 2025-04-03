from fastapi import FastAPI
from .api import router

app = FastAPI()
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8003, reload= True)