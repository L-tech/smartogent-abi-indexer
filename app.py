import settings
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
import os
import shutil
import uuid
from knowledgebase import load_documents_use_case, upload_documents_use_case, request_indexing_use_case
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload/")
async def upload_documents(file: UploadFile = File(...), chunk_size: int = 8000, chunk_overlap: int = 100):
    if not settings.STORAGE_KEY:
        raise HTTPException(status_code=500, detail="NFT_STORAGE_API_KEY missing from .env")
    
    # Check if the uploaded file is a .json file
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only .json files are accepted.")
    
    # Create a unique directory for the uploaded file
    upload_dir = f"uploads/{file.filename}_{uuid.uuid4().hex[:8]}"
    os.makedirs(upload_dir, exist_ok=True)

    # Save the uploaded file to the directory
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Execute the document processing logic
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    documents = load_documents_use_case.execute(upload_dir, text_splitter)
    cid: str = upload_documents_use_case.execute(documents)
    response = request_indexing_use_case.execute(cid)
    
    # Clean up the uploaded file (optional)
    # shutil.rmtree(upload_dir)

    if response.is_processed and response.index_cid:
        return {
            "message": "Knowledge base indexed successfully",
            "index_cid": response.index_cid,
            "cid": cid
        }
    else:
        raise HTTPException(status_code=500, detail=response.error or "Failed to index knowledge base.")

if __name__ == "__main__":
    port = os.getenv("PORT") or 8080
    uvicorn.run(app, host="0.0.0.0", port=int(port))
