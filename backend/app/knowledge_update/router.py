import shutil
from typing import Annotated
from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import shutil
import os
import pathlib
from app.knowledge_update.services import update_knowledge_base
from app.utils.security import get_current_user


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
router = APIRouter()

@router.post("/corpus/upload")
async def upload_pdf(
    file: UploadFile = File(...),  # Required PDF file
    _: str = Depends(get_current_user)  # JWT validation (email unused)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are accepted")
    
    try:
        chunk_count = await update_knowledge_base(file)
        return {
            "status": "success",
            "chunks_uploaded": chunk_count,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(500, f"PDF processing failed: {str(e)}")