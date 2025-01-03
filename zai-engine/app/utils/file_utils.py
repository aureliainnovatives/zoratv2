import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
import magic

def get_file_mime_type(file_path: str) -> str:
    """Get MIME type of a file."""
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)

def generate_unique_filename(original_filename: str) -> Tuple[str, str]:
    """Generate a unique filename while preserving extension."""
    ext = Path(original_filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return unique_name, ext.lower()[1:]  # Return filename and extension without dot

async def save_upload_file(upload_file: UploadFile, destination: str) -> Tuple[str, str]:
    """Save an uploaded file and return its path and MIME type."""
    unique_filename, file_type = generate_unique_filename(upload_file.filename)
    file_path = os.path.join(destination, unique_filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save file
    content = await upload_file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Get MIME type
    mime_type = get_file_mime_type(file_path)
    
    return file_path, mime_type

def get_storage_path(folder: str = "uploads") -> str:
    """Get absolute path to storage folder."""
    base_path = Path(__file__).parent.parent.parent / "storage"
    return str(base_path / folder) 