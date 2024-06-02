import json
import os
import uuid
import settings
from typing import List
from langchain.schema import Document
from lighthouseweb3 import Lighthouse


def execute(documents: List[Document]) -> str:
    # Serialize the documents
    serialized_data = _serialize_documents(documents)
    
    # Generate a unique file name
    unique_id = uuid.uuid4().hex[:8]
    file_name = f"SmartoGent_{unique_id}.json"
    
    # Ensure the uploads directory exists
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Create the full file path
    file_path = os.path.join(uploads_dir, file_name)
    
    # Store the serialized data as a .json file
    with open(file_path, 'w') as json_file:
        json_file.write(serialized_data)
    
    # Initialize the Lighthouse instance
    lh = Lighthouse(token=settings.STORAGE_KEY)
    
    # Upload the .json file
    upload_response = lh.upload(source=file_path)
    
    # Extract the hash from the upload response
    file_hash = upload_response['data']['Hash']
    
    return file_hash


def _serialize_documents(documents: List[Document]) -> str:
    docs_dict = [
        {"page_content": doc.page_content, "metadata": doc.metadata}
        for doc in documents
    ]
    return json.dumps(docs_dict)
