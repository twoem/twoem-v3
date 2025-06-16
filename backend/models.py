from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_admin: Optional[bool] = None

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class UserResponse(UserBase):
    id: str
    created_at: datetime
    is_active: bool

# Authentication Models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# File Models
class FileBase(BaseModel):
    filename: str
    file_type: str
    file_size: int
    description: Optional[str] = None

class FileCreate(FileBase):
    content: str  # base64 encoded content
    is_public: bool = False

class FileUpdate(BaseModel):
    description: Optional[str] = None
    is_public: Optional[bool] = None

class File(FileBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str  # base64 encoded content
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = False
    download_count: int = 0

class FileResponse(FileBase):
    id: str
    uploaded_by: str
    uploaded_at: datetime
    is_public: bool
    download_count: int

# Eulogy Models
class EulogyBase(BaseModel):
    title: str
    deceased_name: str
    description: Optional[str] = None

class EulogyCreate(EulogyBase):
    content: str  # base64 encoded PDF content

class Eulogy(EulogyBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    content: str  # base64 encoded PDF content
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    download_count: int = 0

class EulogyResponse(EulogyBase):
    id: str
    filename: str
    uploaded_by: str
    uploaded_at: datetime
    expires_at: datetime
    download_count: int

# Contact Models
class ContactSubmission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    message: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = False

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    message: str

class ContactResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    message: str
    submitted_at: datetime
    is_read: bool

# Credentials Models (for Gmail/iTax)
class CredentialsBase(BaseModel):
    first_name: str
    email: EmailStr

class CredentialsCreate(CredentialsBase):
    email_password: str
    itax_pin: str
    itax_password: str

class Credentials(CredentialsBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    encrypted_email_password: str
    encrypted_itax_pin: str
    encrypted_itax_password: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CredentialsResponse(CredentialsBase):
    id: str
    created_by: str
    created_at: datetime

# Service Models
class ServiceBase(BaseModel):
    name: str
    category: str
    description: str
    image_url: Optional[str] = None

class Service(ServiceBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ServiceResponse(ServiceBase):
    id: str
    is_active: bool
    created_at: datetime