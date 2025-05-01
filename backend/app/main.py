from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.router import router as auth_router
from app.knowledge_update.router import router as update_router

app = FastAPI()

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (or keep ["POST", "GET", "OPTIONS"])
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(update_router, prefix="/knowledge-base", tags=["Knowledge Base"])

@app.get("/")
def home():
    return {"message": "OTP Auth Service is running!"}