from sentence_transformers import SentenceTransformer
import os
from typing import List, Dict
from PyPDF2 import PdfReader
import tempfile
from fastapi import UploadFile
from pinecone import Pinecone, ServerlessSpec

class PDFToPinecone:
    def __init__(self, pinecone_api_key: str, pinecone_env: str = "us-west1-gcp"):
        """
        Initialize with Pinecone credentials and embedding model
        """
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.pc = Pinecone(api_key=pinecone_api_key)

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file
        """
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text.strip()

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into chunks with overlap for context preservation
        """
        words = text.split()
        if not words:
            return []
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def create_vectors(self, document_id: str, text: str) -> List[Dict]:
        """
        Convert text chunks to vectors with metadata
        """
        chunks = self.chunk_text(text)
        embeddings = self.embedding_model.encode(chunks, show_progress_bar=True, normalize_embeddings=True)
        
        return [{
            "id": f"{document_id}_chunk_{i}",
            "values": embedding.tolist(),
            "metadata": {
                "text": chunk,
                "document_id": document_id,
                "chunk_num": i,
                "type": "pdf",
                "char_length": len(chunk)
            }
        } for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))]

    def process_pdf(self, file_path: str, index_name: str, document_id: str = None) -> int:
        """
        Full pipeline: PDF → Text → Chunks → Vectors → Pinecone
        """

        if not document_id:
            document_id = os.path.splitext(os.path.basename(file_path))[0]
        
        text = self.extract_text_from_pdf(file_path)
        vectors = self.create_vectors(document_id, text)
        
        # print(vectors)
        index = self.pc.Index("quickstart")
        
        # Upsert in batches
        for i in range(0, len(vectors), 100):  # Pinecone's recommended batch size
            batch = vectors[i:i + 100]
            index.upsert(vectors=batch, namespace="ns1")
        
        print(f"Uploaded {len(vectors)} chunks from PDF to Pinecone")
        return len(vectors)

    async def process_uploaded_pdf(self, uploaded_file: UploadFile, index_name: str) -> int:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Define the path for the temporary file within the directory
            tmp_path = os.path.join(tmpdirname, uploaded_file.filename)
            
            # Read the uploaded file's content
            content = await uploaded_file.read()
            
            # Write the content to the temporary file
            with open(tmp_path, 'wb') as tmp_file:
                tmp_file.write(content)
            
            # Process the PDF file
            chunk_count = self.process_pdf(
                file_path=tmp_path,
                index_name=index_name,
                document_id=uploaded_file.filename
            )
            
        # The temporary directory and its contents are automatically cleaned up
        return chunk_count