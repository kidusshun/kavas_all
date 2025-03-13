from uuid import UUID
from pydantic import BaseModel

class VoiceRecognitionResponse(BaseModel):
    userid: UUID | None
    transcription: str
    score: float

class FaceRecognitionResponse(BaseModel):
    userid: str
    score: float

class TTSResponse(BaseModel):
    audio: bytes

class RAGResponse(BaseModel):
    generation: str

class CreateVoiceUserResponse(BaseModel):
    user_id: UUID

class CreateFaceUserResponse(BaseModel):
    user_id: str

class GenerateRequest(BaseModel):
    user_id: str
    question: str