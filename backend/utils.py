import base64
import os
import aiofiles
from typing import Optional
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import uuid

# Encryption setup
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_string(text: str) -> str:
    """Encrypt a string."""
    return cipher_suite.encrypt(text.encode()).decode()

def decrypt_string(encrypted_text: str) -> str:
    """Decrypt a string."""
    return cipher_suite.decrypt(encrypted_text.encode()).decode()

async def save_file_to_disk(content: str, filename: str, directory: str = "uploads") -> str:
    """Save base64 content to disk and return file path."""
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Decode base64 content
    file_content = base64.b64decode(content)
    
    # Generate unique filename
    file_extension = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(directory, unique_filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)
    
    return file_path

async def read_file_as_base64(file_path: str) -> Optional[str]:
    """Read file from disk and return as base64."""
    try:
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
            return base64.b64encode(content).decode()
    except FileNotFoundError:
        return None

def calculate_expiry_date(days: int = 3) -> datetime:
    """Calculate expiry date for eulogies (default 3 days)."""
    return datetime.utcnow() + timedelta(days=days)

def is_expired(expires_at: datetime) -> bool:
    """Check if a timestamp has expired."""
    return datetime.utcnow() > expires_at

def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return os.path.splitext(filename)[1].lower()

def is_valid_file_type(filename: str, allowed_types: list) -> bool:
    """Check if file type is allowed."""
    extension = get_file_extension(filename)
    return extension in allowed_types

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"