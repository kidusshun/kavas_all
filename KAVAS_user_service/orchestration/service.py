import requests
from fastapi import File, UploadFile
from .types import VoiceRecognitionResponse, RAGResponse, FaceRecognitionResponse, TTSResponse, CreateVoiceUserResponse, CreateFaceUserResponse, GenerateRequest
import httpx

import uuid

async def identify_voice(
    voice_file: UploadFile = File(...),
):
    try:
        url = "http://localhost:8000/voice/process"
        files = {"file": ("voice.wav", voice_file.file, voice_file.content_type)}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, timeout=60.0)
        res = response.json()
        return VoiceRecognitionResponse(**res)
    except Exception as e:
        print(e)
        raise Exception("can't identify voice")

async def answer_user_query(
    request: GenerateRequest,
):
    try:
        url = "http://localhost:8002/rag/query"
        response = requests.post(url, json={
            "user_id":request.user_id,
            "question":request.question,
        })
        res = response.json()
        return RAGResponse(**res)
    except Exception as e:
        raise e

async def generate_tts(
    text: str,
):
    try:
        url = "http://localhost:8000/voice/tts"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"text":text}, timeout=60.0)
        
        return response
    except:
        raise Exception("Can't generate speech")
    

async def identify_face(
    image: UploadFile = File(...),
):
    try:
        url = "http://localhost:8003/api/v1/identify-face"
        files = {"image": ("image.jpg", image.file, image.content_type)}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, timeout=60.0)

        res = response.json()
        print(res)
        return FaceRecognitionResponse(userid=res[0], score=res[1])
    except:
        raise Exception("can't identify face")
    
async def add_voice_user(id: uuid.UUID, audio: UploadFile):
    try:
        url = "http://localhost:8000/voice/add_user"
        # Reset file pointer before sending
        await audio.seek(0)
        
        files = {"file": ("voice.wav", audio.file, audio.content_type)}
        data = {"user_id": str(id)}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, data=data, timeout=60.0)

        return CreateVoiceUserResponse(**response.json())
    except:
        raise Exception("can't add voice user")


async def add_face_user(id: uuid.UUID, image: UploadFile):
    try:
        url = "http://localhost:8003/api/v1/embed"
        # Reset file pointer before sending
        await image.seek(0)
        files = {"image": ("image.jpg", image.file, image.content_type)}
        data = {"person_id": str(id)}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, data=data, timeout=60.0)

        return CreateFaceUserResponse(user_id = response.json())
    except:
        raise Exception("can't add face user")