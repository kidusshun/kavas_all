import httpx
import requests
from .types import RAGResponse, GenerateRequest, CreateVoiceUserResponse, CreateFaceUserResponse
import uuid
import os
from fastapi import UploadFile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_tts(
    text: str,
):
    host = os.getenv("VOICE_RECOGNITION_HOST")
    port = os.getenv("VOICE_RECOGNITION_PORT")
    try:
        url = f"http://{host}:{port}/voice/tts"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"text":text}, timeout=60.0)
        
        return response
    except:
        raise Exception("Can't generate speech")
    

async def answer_user_query(
    queries: list[GenerateRequest],
):
    try:
        url = "http://localhost:8002/rag/multi_query"
        response = requests.post(url, json={
            "queries":queries,
        })
        res = response.json()
        print("JSON OUTPUT")
        return RAGResponse(**res)
    except Exception as e:
        raise e

async def greet_user(user_id: str):
    try:
        url = f"http://127.0.0.1:8000/users/{user_id}/greet"
        response = requests.post(url)
        return response.json()
    except Exception as e:
        raise e


async def add_voice_user(id: uuid.UUID, audio: UploadFile):
    host = os.getenv("VOICE_RECOGNITION_HOST")
    port = os.getenv("VOICE_RECOGNITION_PORT")
    try:
        url = f"http://{host}:{port}/voice/add_user"
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
    """Minimal face embedding consumer that returns response object or None"""
    try:
        host = os.getenv("FACE_RECOGNITION_HOST")
        port = os.getenv("FACE_RECOGNITION_PORT")
        url = f"http://{host}:{port}/api/v2/embed"
        # Reset file pointer before sending
        await image.seek(0)
        files = {"image": ("image.jpg", image.file, image.content_type)}
        data = {"person_id": str(id)}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, data=data, timeout=60.0)
            data = response.json()  
            if response.status_code in (200, 201) and data.get("status") == "success":
                return CreateFaceUserResponse(user_id=data["person_id"])
            
            logger.error(f"Embed failed for {id}: {data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        logger.info(f"Error adding face user {id}")
        return None
    
    

async def mark_greeted_users(person_ids: list[str]):
    """Consumer for marking multiple users as greeted"""
    try:
        host = os.getenv("FACE_RECOGNITION_HOST")
        port = os.getenv("FACE_RECOGNITION_PORT")
        url = f"http://{host}:{port}/api/v2/mark-greeted"
        
        form_data = [("person_ids", pid) for pid in person_ids]

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=form_data, timeout=30.0)
            data = response.json()

            if response.status_code == 200 and data.get("status") == "success":
                return data
            
            logger.error(f"Mark greeted failed: {data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        logger.error(f"Error in mark_greeted_users: {str(e)}")
        return None


async def update_face_user(id: uuid.UUID, image: UploadFile):
    try:
        host = os.getenv("FACE_RECOGNITION_HOST")
        port = os.getenv("FACE_RECOGNITION_PORT")
        url = f"http://{host}:{port}/api/v2/update"
        # Reset file pointer before sending
        await image.seek(0)
        files = {"image": ("image.jpg", image.file, image.content_type)}
        data = {"person_id": str(id)}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, data=data, timeout=60.0)
            data = response.json()  
            if response.status_code in (200, 201) and data.get("status") == "success":
                return CreateFaceUserResponse(user_id=data["person_id"])
            
            logger.error(f"Embed failed for {id}: {data.get('message', 'Unknown error')}")
            return None
    except:
        print("Error updating face user {id}")
        return None