from app.pinecone.pinecone import PDFToPinecone
from app.config import settings

pdf_processor = PDFToPinecone(
    pinecone_api_key=settings.pinecone_api_key,
    pinecone_env=settings.pinecone_environment
)

async def update_knowledge_base(file, index_name = "kifiya"):
    chunk_count = await pdf_processor.process_uploaded_pdf(file, index_name)      
    return chunk_count 