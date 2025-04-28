import time
import uuid
from .repository import identify_user, add_user_to_db
from .utils import (
    pyannote_embed_audio,
    whisper_transcribe,
    generate_speech,
    preprocess_audio_in_memory,
    process_audio,
    diarize_audio,
    diarization_pipeline,
)

from .types import TranscriptionResponse, CreateUserResponse
import httpx
from psycopg2.extensions import connection
import asyncio
from fastapi import HTTPException


async def process_voice(object, conn):
    start = time.time()
    
    try:
        user = identify_user(object[-1], conn=conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to identify user")
    
    print(f"Time taken for identifying user: {time.time() - start} seconds")

    start = time.time()
    try:
        response = await whisper_transcribe(audio_path=object[-2])
        transcription = response.get("text", None)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to transcribe audio")
    

    print(f"Time taken for transcribing: {time.time() - start} seconds")
    if not user:
        return TranscriptionResponse(userid=None, transcription=transcription, score=0)
    else:
        return TranscriptionResponse(userid=uuid.UUID(user[0]), transcription=transcription, score=user[1])


async def process_all_voices(embedded_voices, conn):
    tasks = [process_voice(obj, conn) for obj in embedded_voices]
    users = await asyncio.gather(*tasks)
    return users

async def find_user_service(*,audio_file_path: str,user_name:str | None, conn: connection,) -> list[TranscriptionResponse]:
    start = time.time()
    start_temp = time.time()
    preprocessed_audio_path = preprocess_audio_in_memory(audio_file_path)
    print(f"Time taken for preprocessing: {time.time() - start_temp} seconds")

    start_diarization = time.time()
    try:
        embedded_voices = process_audio(preprocessed_audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to diarize audio")

    print(f"Time taken for diarization: {time.time() - start_diarization} seconds")

    try:
        users = await process_all_voices(embedded_voices, conn=conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to process voices")
    
    print(f"Time taken for processing: {time.time() - start} seconds")
    return users


def generate_speech_service(text: str) -> bytes:
    text = text.replace('\n', '')

    return generate_speech(text)

async def add_user_service(*,audio_file_path: str,user_id: str, conn: connection) -> CreateUserResponse:
    preprocessed_audio_path = preprocess_audio_in_memory(audio_file_path)

    embedded_voice = pyannote_embed_audio(audio_path=preprocessed_audio_path)
    user_id = add_user_to_db(embedded_voice,user_id=uuid.UUID(user_id), conn=conn) #type: ignore
    return CreateUserResponse(user_id=user_id)