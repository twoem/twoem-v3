from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
import os
import logging
import base64
import uuid

# Import our models and utilities
from .models import (
    User, UserCreate, UserLogin, UserResponse, Token,
    File, FileCreate, FileResponse, FileUpdate,
    Eulogy, EulogyCreate, EulogyResponse,
    ContactSubmission, ContactCreate, ContactResponse,
    Credentials, CredentialsCreate, CredentialsResponse,
    Service, ServiceResponse
)
from .auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_user, get_current_admin_user, create_user_response,
    security
)
from .utils import (
    save_file_to_disk, read_file_as_base64, calculate_expiry_date,
    is_expired, encrypt_string, decrypt_string, is_valid_file_type,
    format_file_size
)

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="TWOEM API", description="TWOEM Online Productions API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Dependency to get database
async def get_database() -> AsyncIOMotorDatabase:
    return db

# Initialize admin user
async def create_admin_user():
    """Create default admin user if not exists."""
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@twoem.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "TwoemAdmin2025!")
    
    existing_admin = await db.users.find_one({"email": admin_email})
    if not existing_admin:
        admin_user = User(
            email=admin_email,
            full_name="TWOEM Administrator",
            hashed_password=get_password_hash(admin_password),
            is_admin=True
        )
        await db.users.insert_one(admin_user.dict())
        logging.info(f"Created admin user: {admin_email}")

# Initialize default services
async def initialize_services():
    """Initialize default services if not exist."""
    services_count = await db.services.count_documents({})
    if services_count == 0:
        default_services = [
            {
                "name": "eCitizen Services",
                "category": "government",
                "description": "Logbook Transfer, Vehicle Inspection, Smart DL Application, Handbook DL Renewal, PSV Badge Applications",
                "image_url": "images/ecitizen.jpg"
            },
            {
                "name": "iTax Services", 
                "category": "tax",
                "description": "Tax Compliance Certificate, Individual Tax Return, Advanced Tax, Company Returns, Group KRA PIN Application",
                "image_url": "images/itax.jpg"
            },
            {
                "name": "Digital Printing",
                "category": "printing",
                "description": "Business Cards, Award Certificates, Brochures, Funeral Programs, Handouts, Flyers, Maps, Posters",
                "image_url": "images/digital_printing.jpg"
            },
            {
                "name": "Cyber Services",
                "category": "cyber",
                "description": "Printing, Lamination, Photocopy, Internet Browsing, Typesetting, Instant Passport Photos",
                "image_url": "images/cyber_services.jpg"
            },
            {
                "name": "Other Services",
                "category": "other",
                "description": "High-Speed Internet, Online Services, Scanning & Photocopy, Design & Layout",
                "image_url": "images/other_services.jpg"
            }
        ]
        
        for service_data in default_services:
            service = Service(**service_data)
            await db.services.insert_one(service.dict())
        
        logging.info("Initialized default services")

# Authentication Routes
@api_router.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, database: AsyncIOMotorDatabase = Depends(get_database)):
    # Check if user already exists
    existing_user = await database.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_admin=user_data.is_admin
    )
    
    await database.users.insert_one(user.dict())
    return create_user_response(user)

@api_router.post("/auth/login", response_model=Token)
async def login_user(login_data: UserLogin, database: AsyncIOMotorDatabase = Depends(get_database)):
    user = await authenticate_user(database, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=create_user_response(user)
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    user = await get_current_user(credentials, database)
    return create_user_response(user)

# File Management Routes
@api_router.post("/files", response_model=FileResponse)
async def upload_file(
    file_data: FileCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    current_user = await get_current_user(credentials, database)
    
    # Validate file type
    allowed_types = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt']
    if not is_valid_file_type(file_data.filename, allowed_types):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Create file record
    file_record = File(
        filename=file_data.filename,
        file_type=file_data.file_type,
        file_size=file_data.file_size,
        content=file_data.content,
        description=file_data.description,
        uploaded_by=current_user.id,
        is_public=file_data.is_public
    )
    
    await database.files.insert_one(file_record.dict())
    
    return FileResponse(
        id=file_record.id,
        filename=file_record.filename,
        file_type=file_record.file_type,
        file_size=file_record.file_size,
        description=file_record.description,
        uploaded_by=file_record.uploaded_by,
        uploaded_at=file_record.uploaded_at,
        is_public=file_record.is_public,
        download_count=file_record.download_count
    )

@api_router.get("/files", response_model=List[FileResponse])
async def list_files(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: AsyncIOMotorDatabase = Depends(get_database),
    public_only: bool = False
):
    current_user = await get_current_user(credentials, database)
    
    if public_only:
        query = {"is_public": True}
    elif current_user.is_admin:
        query = {}  # Admin can see all files
    else:
        query = {"$or": [{"is_public": True}, {"uploaded_by": current_user.id}]}
    
    files = await database.files.find(query).to_list(1000)
    return [FileResponse(**file_data) for file_data in files]

@api_router.get("/files/{file_id}")
async def download_file(
    file_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    current_user = await get_current_user(credentials, database)
    
    file_record = await database.files.find_one({"id": file_id})
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check permissions
    if not file_record["is_public"] and file_record["uploaded_by"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Increment download count
    await database.files.update_one({"id": file_id}, {"$inc": {"download_count": 1}})
    
    # Return file content as base64
    content = base64.b64decode(file_record["content"])
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_record['filename']}"}
    )

# Eulogy Routes
@api_router.post("/eulogies", response_model=EulogyResponse)
async def upload_eulogy(
    eulogy_data: EulogyCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    current_user = await get_current_user(credentials, database)
    
    # Generate filename
    filename = f"{eulogy_data.deceased_name.replace(' ', '_')}_eulogy.pdf"
    
    # Create eulogy record with 3-day expiry
    eulogy = Eulogy(
        title=eulogy_data.title,
        deceased_name=eulogy_data.deceased_name,
        description=eulogy_data.description,
        filename=filename,
        content=eulogy_data.content,
        uploaded_by=current_user.id,
        expires_at=calculate_expiry_date(3)
    )
    
    await database.eulogies.insert_one(eulogy.dict())
    
    return EulogyResponse(
        id=eulogy.id,
        title=eulogy.title,
        deceased_name=eulogy.deceased_name,
        description=eulogy.description,
        filename=eulogy.filename,
        uploaded_by=eulogy.uploaded_by,
        uploaded_at=eulogy.uploaded_at,
        expires_at=eulogy.expires_at,
        download_count=eulogy.download_count
    )

@api_router.get("/eulogies", response_model=List[EulogyResponse])
async def list_eulogies(database: AsyncIOMotorDatabase = Depends(get_database)):
    # Only return non-expired eulogies
    current_time = datetime.utcnow()
    eulogies = await database.eulogies.find({"expires_at": {"$gt": current_time}}).to_list(1000)
    return [EulogyResponse(**eulogy) for eulogy in eulogies]

@api_router.get("/eulogies/{eulogy_id}")
async def download_eulogy(
    eulogy_id: str,
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    eulogy = await database.eulogies.find_one({"id": eulogy_id})
    if not eulogy:
        raise HTTPException(status_code=404, detail="Eulogy not found")
    
    # Check if expired
    if is_expired(eulogy["expires_at"]):
        raise HTTPException(status_code=410, detail="Eulogy has expired")
    
    # Increment download count
    await database.eulogies.update_one({"id": eulogy_id}, {"$inc": {"download_count": 1}})
    
    # Return PDF content
    content = base64.b64decode(eulogy["content"])
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={eulogy['filename']}"}
    )

# Contact Routes
@api_router.post("/contact", response_model=ContactResponse)
async def submit_contact(contact_data: ContactCreate, database: AsyncIOMotorDatabase = Depends(get_database)):
    contact = ContactSubmission(
        name=contact_data.name,
        email=contact_data.email,
        message=contact_data.message
    )
    
    await database.contacts.insert_one(contact.dict())
    
    return ContactResponse(
        id=contact.id,
        name=contact.name,
        email=contact.email,
        message=contact.message,
        submitted_at=contact.submitted_at,
        is_read=contact.is_read
    )

@api_router.get("/contact", response_model=List[ContactResponse])
async def list_contacts(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    current_user = await get_current_admin_user(await get_current_user(credentials, database))
    
    contacts = await database.contacts.find().sort("submitted_at", -1).to_list(1000)
    return [ContactResponse(**contact) for contact in contacts]

# Services Routes
@api_router.get("/services", response_model=List[ServiceResponse])
async def list_services(database: AsyncIOMotorDatabase = Depends(get_database)):
    services = await database.services.find({"is_active": True}).to_list(1000)
    return [ServiceResponse(**service) for service in services]

# Credentials Routes (Gmail/iTax)
@api_router.post("/credentials", response_model=CredentialsResponse)
async def save_credentials(
    cred_data: CredentialsCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    current_user = await get_current_user(credentials, database)
    
    # Encrypt sensitive data
    encrypted_creds = Credentials(
        first_name=cred_data.first_name,
        email=cred_data.email,
        encrypted_email_password=encrypt_string(cred_data.email_password),
        encrypted_itax_pin=encrypt_string(cred_data.itax_pin),
        encrypted_itax_password=encrypt_string(cred_data.itax_password),
        created_by=current_user.id
    )
    
    await database.credentials.insert_one(encrypted_creds.dict())
    
    return CredentialsResponse(
        id=encrypted_creds.id,
        first_name=encrypted_creds.first_name,
        email=encrypted_creds.email,
        created_by=encrypted_creds.created_by,
        created_at=encrypted_creds.created_at
    )

# Admin Routes
@api_router.delete("/admin/files/{file_id}")
async def delete_file(
    file_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    current_user = await get_current_admin_user(await get_current_user(credentials, database))
    
    result = await database.files.delete_one({"id": file_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {"message": "File deleted successfully"}

@api_router.delete("/admin/eulogies/{eulogy_id}")
async def delete_eulogy(
    eulogy_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    current_user = await get_current_admin_user(await get_current_user(credentials, database))
    
    result = await database.eulogies.delete_one({"id": eulogy_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Eulogy not found")
    
    return {"message": "Eulogy deleted successfully"}

# Cleanup expired eulogies (admin only)
@api_router.post("/admin/cleanup-expired")
async def cleanup_expired_eulogies(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    current_user = await get_current_admin_user(await get_current_user(credentials, database))
    
    current_time = datetime.utcnow()
    result = await database.eulogies.delete_many({"expires_at": {"$lt": current_time}})
    
    return {"message": f"Deleted {result.deleted_count} expired eulogies"}

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize the application."""
    await create_admin_user()
    await initialize_services()
    logger.info("TWOEM API started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Cleanup on shutdown."""
    client.close()
    logger.info("TWOEM API shutdown complete")