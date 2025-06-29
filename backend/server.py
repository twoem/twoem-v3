from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timedelta
import jwt
import bcrypt
import base64
import random
import string
from typing import Union

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# JWT Configuration
SECRET_KEY = "your-super-secret-jwt-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Ensure uploads directory exists
UPLOAD_DIR = Path(ROOT_DIR) / "uploads" / "certificates"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

EULOGY_DIR = Path(ROOT_DIR) / "uploads" / "eulogies"
EULOGY_DIR.mkdir(parents=True, exist_ok=True)

# =============================
# MODELS
# =============================

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: Optional[EmailStr] = None
    role: str  # "admin" or "student"
    hashed_password: str
    is_first_login: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str
    role: str = "student"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    role: str
    is_first_login: bool

class PasswordChange(BaseModel):
    new_password: str

class ForgotPasswordRequest(BaseModel):
    username: str

class PasswordResetRequest(BaseModel):
    username: str
    reset_code: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ParentContact(BaseModel):
    father_name: Optional[str] = None
    father_phone: Optional[str] = None
    mother_name: Optional[str] = None
    mother_phone: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None

class AcademicRecord(BaseModel):
    ms_word: Optional[int] = Field(None, ge=0, le=100)
    ms_excel: Optional[int] = Field(None, ge=0, le=100)
    ms_powerpoint: Optional[int] = Field(None, ge=0, le=100)
    ms_access: Optional[int] = Field(None, ge=0, le=100)
    computer_intro: Optional[int] = Field(None, ge=0, le=100)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FinanceRecord(BaseModel):
    total_fees: float = 0.0
    paid_amount: float = 0.0
    balance: float = 0.0
    payment_reference: Optional[str] = None
    last_payment_date: Optional[datetime] = None
    is_cleared: bool = False
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Certificate(BaseModel):
    filename: str
    file_data: str  # base64 encoded
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: str  # admin user id

class Eulogy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    filename: str
    file_data: str  # base64 encoded
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))
    uploaded_by: str  # admin user id
    is_active: bool = True

class EulogyCreate(BaseModel):
    title: str
    description: Optional[str] = None

class EulogyResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    filename: str
    uploaded_at: datetime
    expires_at: datetime
    is_active: bool
    days_remaining: int

class DownloadFile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    filename: str
    file_data: str  # base64 encoded
    file_type: str  # "private" or "public"
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: str  # admin user id
    download_count: int = 0
    is_active: bool = True

class DownloadFileCreate(BaseModel):
    title: str
    description: Optional[str] = None
    file_type: str = "public"  # "private" or "public"

class DownloadFileResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    filename: str
    file_type: str
    uploaded_at: datetime
    download_count: int
    is_active: bool

class PasswordResetRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_username: str
    reset_code: str
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    status: str = "pending"  # "pending", "approved", "rejected", "used"
    admin_response: Optional[str] = None
    responded_at: Optional[datetime] = None

class PasswordResetResponse(BaseModel):
    id: str
    student_username: str
    requested_at: datetime
    status: str
    admin_response: Optional[str] = None

# =============================
# NEW MODELS FOR NOTIFICATIONS AND RESOURCES
# =============================

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str  # Rich text content
    attachment_filename: Optional[str] = None
    attachment_data: Optional[str] = None  # base64 encoded
    target_audience: str = "all"  # "all", "specific", "student_id"
    target_student_ids: List[str] = []  # if target_audience is "specific"
    created_by: str  # admin user id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    priority: str = "normal"  # "low", "normal", "high", "urgent"

class NotificationCreate(BaseModel):
    title: str
    content: str
    target_audience: str = "all"
    target_student_ids: List[str] = []
    priority: str = "normal"

class NotificationResponse(BaseModel):
    id: str
    title: str
    content: str
    attachment_filename: Optional[str] = None
    has_attachment: bool = False
    target_audience: str
    target_student_ids: List[str]
    created_by: str
    created_at: datetime
    is_active: bool
    priority: str

class StudentResource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    subject: str  # Subject category
    filename: str
    file_data: str  # base64 encoded PDF
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: str  # admin user id
    is_active: bool = True

class StudentResourceCreate(BaseModel):
    title: str
    description: Optional[str] = None
    subject: str

class StudentResourceResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    subject: str
    filename: str
    uploaded_at: datetime
    is_active: bool

class WiFiCredentials(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    network_name: str
    password: str
    connection_guide: str  # Rich text with connection instructions
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str  # admin user id

class WiFiCredentialsUpdate(BaseModel):
    network_name: str
    password: str
    connection_guide: str

class WiFiCredentialsResponse(BaseModel):
    network_name: str
    password: str
    connection_guide: str
    updated_at: datetime

class Student(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Reference to User
    full_name: str
    id_number: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    parent_contacts: Optional[ParentContact] = None
    academic_record: Optional[AcademicRecord] = None
    finance_record: Optional[FinanceRecord] = Field(default_factory=FinanceRecord)
    certificate: Optional[Certificate] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StudentCreate(BaseModel):
    username: str
    password: str
    full_name: str
    id_number: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    parent_contacts: Optional[ParentContact] = None

class AcademicUpdate(BaseModel):
    ms_word: Optional[int] = Field(None, ge=0, le=100)
    ms_excel: Optional[int] = Field(None, ge=0, le=100)
    ms_powerpoint: Optional[int] = Field(None, ge=0, le=100)
    ms_access: Optional[int] = Field(None, ge=0, le=100)
    computer_intro: Optional[int] = Field(None, ge=0, le=100)

class FinanceUpdate(BaseModel):
    total_fees: Optional[float] = None
    paid_amount: Optional[float] = None
    payment_reference: Optional[str] = None

class StudentResponse(BaseModel):
    id: str
    username: str
    full_name: str
    id_number: str
    email: Optional[str] = None
    phone: Optional[str] = None
    parent_contacts: Optional[ParentContact] = None
    academic_record: Optional[AcademicRecord] = None
    finance_record: Optional[FinanceRecord] = None
    certificate: Optional[Certificate] = None
    has_certificate: bool = False
    can_download_certificate: bool = False
    average_score: Optional[float] = None

# =============================
# UTILITY FUNCTIONS
# =============================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_reset_code() -> str:
    return ''.join(random.choices(string.digits, k=6))

def calculate_average_score(academic_record: Optional[AcademicRecord]) -> Optional[float]:
    if not academic_record:
        return None
    
    scores = [
        academic_record.ms_word,
        academic_record.ms_excel,
        academic_record.ms_powerpoint,
        academic_record.ms_access,
        academic_record.computer_intro
    ]
    
    valid_scores = [score for score in scores if score is not None]
    if not valid_scores:
        return None
    
    return sum(valid_scores) / len(valid_scores)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# =============================
# AUTHENTICATION ROUTES
# =============================

@api_router.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"username": user_credentials.username})
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    # Check if user exists and is a student
    user = await db.users.find_one({"username": request.username, "role": "student"})
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Create password reset record without OTP (OTP will be generated when admin approves)
    reset_record = PasswordResetRecord(
        student_username=request.username,
        reset_code=""  # Empty until admin approves
    )
    
    await db.password_resets.insert_one(reset_record.dict())
    
    return {"message": "Password reset request submitted. Please contact admin for approval."}

@api_router.post("/auth/reset-password")
async def reset_password(request: PasswordResetRequest):
    # Find the reset record
    reset_record = await db.password_resets.find_one({
        "student_username": request.username,
        "reset_code": request.reset_code,
        "status": "approved"
    })
    
    if not reset_record:
        raise HTTPException(status_code=400, detail="Invalid or unapproved reset code")
    
    # Check if code has expired
    if datetime.utcnow() > reset_record["expires_at"]:
        raise HTTPException(status_code=400, detail="Reset code has expired")
    
    # Update user password
    hashed_password = hash_password(request.new_password)
    await db.users.update_one(
        {"username": request.username},
        {"$set": {"hashed_password": hashed_password, "is_first_login": False}}
    )
    
    # Mark reset record as used
    await db.password_resets.update_one(
        {"id": reset_record["id"]},
        {"$set": {"status": "used", "responded_at": datetime.utcnow()}}
    )
    
    return {"message": "Password reset successfully"}

@api_router.post("/auth/change-password")
async def change_password(password_change: PasswordChange, current_user: User = Depends(get_current_user)):
    hashed_password = hash_password(password_change.new_password)
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"hashed_password": hashed_password, "is_first_login": False}}
    )
    return {"message": "Password changed successfully"}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_first_login=current_user.is_first_login
    )

# =============================
# ADMIN ROUTES
# =============================

@api_router.post("/admin/students", response_model=StudentResponse)
async def create_student(student_data: StudentCreate, admin_user: User = Depends(get_admin_user)):
    # Check if username already exists
    existing_user = await db.users.find_one({"username": student_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user account
    hashed_password = hash_password(student_data.password)
    user = User(
        username=student_data.username,
        email=student_data.email,
        role="student",
        hashed_password=hashed_password,
        is_first_login=True
    )
    await db.users.insert_one(user.dict())
    
    # Create student profile
    student = Student(
        user_id=user.id,
        full_name=student_data.full_name,
        id_number=student_data.id_number,
        email=student_data.email,
        phone=student_data.phone
    )
    await db.students.insert_one(student.dict())
    
    return await get_student_response(student)

@api_router.get("/admin/students", response_model=List[StudentResponse])
async def get_all_students(admin_user: User = Depends(get_admin_user)):
    students = await db.students.find().to_list(1000)
    return [await get_student_response(Student(**student)) for student in students]

@api_router.get("/admin/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str, admin_user: User = Depends(get_admin_user)):
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return await get_student_response(Student(**student))

@api_router.delete("/admin/students/{student_id}")
async def delete_student(student_id: str, admin_user: User = Depends(get_admin_user)):
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Delete the student's user account
    user_id = student["user_id"]
    await db.users.delete_one({"id": user_id})
    
    # Delete the student profile
    await db.students.delete_one({"id": student_id})
    
    return {"message": "Student deleted successfully"}

@api_router.put("/admin/students/{student_id}/profile")
async def update_student_profile(
    student_id: str,
    profile_data: StudentUpdate,
    admin_user: User = Depends(get_admin_user)
):
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = profile_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await db.students.update_one(
        {"id": student_id},
        {"$set": {**update_data, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Student profile updated successfully"}

@api_router.put("/admin/students/{student_id}/academic")
async def update_student_academic(
    student_id: str,
    academic_data: AcademicUpdate,
    admin_user: User = Depends(get_admin_user)
):
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = academic_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await db.students.update_one(
        {"id": student_id},
        {"$set": {"academic_record": update_data, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Academic record updated successfully"}

@api_router.put("/admin/students/{student_id}/finance")
async def update_student_finance(
    student_id: str,
    finance_data: FinanceUpdate,
    admin_user: User = Depends(get_admin_user)
):
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    current_finance = student.get("finance_record", {})
    
    update_dict = {}
    if finance_data.total_fees is not None:
        update_dict["total_fees"] = finance_data.total_fees
    if finance_data.paid_amount is not None:
        update_dict["paid_amount"] = finance_data.paid_amount
        update_dict["last_payment_date"] = datetime.utcnow()
    if finance_data.payment_reference is not None:
        update_dict["payment_reference"] = finance_data.payment_reference
    
    # Calculate balance and clearance status
    total_fees = update_dict.get("total_fees", current_finance.get("total_fees", 0))
    paid_amount = update_dict.get("paid_amount", current_finance.get("paid_amount", 0))
    
    update_dict["balance"] = total_fees - paid_amount
    update_dict["is_cleared"] = update_dict["balance"] <= 0
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.students.update_one(
        {"id": student_id},
        {"$set": {"finance_record": update_dict, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Finance record updated successfully"}

@api_router.post("/admin/students/{student_id}/certificate")
async def upload_certificate(
    student_id: str,
    file: UploadFile = File(...),
    admin_user: User = Depends(get_admin_user)
):
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Read file content and encode to base64
    file_content = await file.read()
    file_data = base64.b64encode(file_content).decode('utf-8')
    
    certificate = Certificate(
        filename=file.filename,
        file_data=file_data,
        uploaded_by=admin_user.id
    )
    
    await db.students.update_one(
        {"id": student_id},
        {"$set": {"certificate": certificate.dict(), "updated_at": datetime.utcnow()}}
    )
    return {"message": "Certificate uploaded successfully"}

@api_router.get("/admin/password-resets", response_model=List[PasswordResetResponse])
async def get_password_reset_requests(admin_user: User = Depends(get_admin_user)):
    resets = await db.password_resets.find({"status": "pending"}).to_list(1000)
    return [PasswordResetResponse(**reset) for reset in resets]

@api_router.put("/admin/password-resets/{reset_id}/approve")
async def approve_password_reset(reset_id: str, admin_user: User = Depends(get_admin_user)):
    # Generate 6-digit OTP when admin approves
    otp_code = generate_reset_code()
    
    await db.password_resets.update_one(
        {"id": reset_id},
        {"$set": {
            "status": "approved", 
            "responded_at": datetime.utcnow(), 
            "admin_response": "Approved by admin",
            "reset_code": otp_code
        }}
    )
    return {"message": "Password reset request approved", "otp_code": otp_code}

@api_router.put("/admin/password-resets/{reset_id}/reject")
async def reject_password_reset(reset_id: str, admin_user: User = Depends(get_admin_user)):
    await db.password_resets.update_one(
        {"id": reset_id},
        {"$set": {"status": "rejected", "responded_at": datetime.utcnow(), "admin_response": "Rejected by admin"}}
    )
    return {"message": "Password reset request rejected"}

@api_router.post("/admin/eulogies")
async def upload_eulogy(
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    admin_user: User = Depends(get_admin_user)
):
    # Read file content and encode to base64
    file_content = await file.read()
    file_data = base64.b64encode(file_content).decode('utf-8')
    
    eulogy = Eulogy(
        title=title,
        description=description,
        filename=file.filename,
        file_data=file_data,
        uploaded_by=admin_user.id
    )
    
    await db.eulogies.insert_one(eulogy.dict())
    return {"message": "Eulogy uploaded successfully", "id": eulogy.id}

@api_router.get("/admin/eulogies", response_model=List[EulogyResponse])
async def get_all_eulogies_admin(admin_user: User = Depends(get_admin_user)):
    eulogies = await db.eulogies.find().to_list(1000)
    result = []
    for eulogy in eulogies:
        days_remaining = max(0, (eulogy["expires_at"] - datetime.utcnow()).days)
        result.append(EulogyResponse(
            **eulogy,
            days_remaining=days_remaining
        ))
    return result

@api_router.delete("/admin/eulogies/{eulogy_id}")
async def delete_eulogy(eulogy_id: str, admin_user: User = Depends(get_admin_user)):
    await db.eulogies.delete_one({"id": eulogy_id})
    return {"message": "Eulogy deleted successfully"}

# =============================
# DOWNLOADS MANAGEMENT ROUTES
# =============================

DOWNLOADS_DIR = Path(ROOT_DIR) / "uploads" / "downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

@api_router.post("/admin/downloads")
async def upload_download_file(
    title: str = Form(...),
    description: str = Form(None),
    file_type: str = Form("public"),
    file: UploadFile = File(...),
    admin_user: User = Depends(get_admin_user)
):
    if file_type not in ["public", "private"]:
        raise HTTPException(status_code=400, detail="File type must be 'public' or 'private'")
    
    # Read file content and encode to base64
    file_content = await file.read()
    file_data = base64.b64encode(file_content).decode('utf-8')
    
    download_file = DownloadFile(
        title=title,
        description=description,
        filename=file.filename,
        file_data=file_data,
        file_type=file_type,
        uploaded_by=admin_user.id
    )
    
    await db.downloads.insert_one(download_file.dict())
    return {"message": "File uploaded successfully", "id": download_file.id}

@api_router.get("/admin/downloads", response_model=List[DownloadFileResponse])
async def get_all_downloads_admin(admin_user: User = Depends(get_admin_user)):
    downloads = await db.downloads.find({"is_active": True}).to_list(1000)
    return [DownloadFileResponse(**download) for download in downloads]

@api_router.delete("/admin/downloads/{download_id}")
async def delete_download_file(download_id: str, admin_user: User = Depends(get_admin_user)):
    await db.downloads.update_one(
        {"id": download_id},
        {"$set": {"is_active": False}}
    )
    return {"message": "Download file deleted successfully"}

# =============================
# NEW ADMIN ROUTES FOR NOTIFICATIONS AND RESOURCES
# =============================

# Notifications Management
@api_router.post("/admin/notifications")
async def create_notification(
    title: str = Form(...),
    content: str = Form(...),
    target_audience: str = Form("all"),
    target_student_ids: str = Form(""),
    priority: str = Form("normal"),
    file: UploadFile = File(None),
    admin_user: User = Depends(get_admin_user)
):
    # Parse target_student_ids
    target_ids = [id.strip() for id in target_student_ids.split(",") if id.strip()] if target_student_ids else []
    
    # Handle file attachment
    attachment_filename = None
    attachment_data = None
    if file:
        file_content = await file.read()
        attachment_data = base64.b64encode(file_content).decode('utf-8')
        attachment_filename = file.filename
    
    notification = Notification(
        title=title,
        content=content,
        attachment_filename=attachment_filename,
        attachment_data=attachment_data,
        target_audience=target_audience,
        target_student_ids=target_ids,
        priority=priority,
        created_by=admin_user.id
    )
    
    await db.notifications.insert_one(notification.dict())
    return {"message": "Notification created successfully", "id": notification.id}

@api_router.get("/admin/notifications", response_model=List[NotificationResponse])
async def get_all_notifications_admin(admin_user: User = Depends(get_admin_user)):
    notifications = await db.notifications.find({"is_active": True}).to_list(1000)
    return [
        NotificationResponse(
            **notif,
            has_attachment=notif["attachment_filename"] is not None
        ) for notif in notifications
    ]

@api_router.delete("/admin/notifications/{notification_id}")
async def delete_notification(notification_id: str, admin_user: User = Depends(get_admin_user)):
    await db.notifications.update_one(
        {"id": notification_id},
        {"$set": {"is_active": False}}
    )
    return {"message": "Notification deleted successfully"}

# Student Resources Management
@api_router.post("/admin/resources")
async def upload_student_resource(
    title: str = Form(...),
    description: str = Form(None),
    subject: str = Form(...),
    file: UploadFile = File(...),
    admin_user: User = Depends(get_admin_user)
):
    # Validate file is PDF
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed for resources")
    
    # Read file content and encode to base64
    file_content = await file.read()
    file_data = base64.b64encode(file_content).decode('utf-8')
    
    resource = StudentResource(
        title=title,
        description=description,
        subject=subject,
        filename=file.filename,
        file_data=file_data,
        uploaded_by=admin_user.id
    )
    
    await db.student_resources.insert_one(resource.dict())
    return {"message": "Resource uploaded successfully", "id": resource.id}

@api_router.get("/admin/resources", response_model=List[StudentResourceResponse])
async def get_all_resources_admin(admin_user: User = Depends(get_admin_user)):
    resources = await db.student_resources.find({"is_active": True}).to_list(1000)
    return [StudentResourceResponse(**resource) for resource in resources]

@api_router.delete("/admin/resources/{resource_id}")
async def delete_student_resource(resource_id: str, admin_user: User = Depends(get_admin_user)):
    await db.student_resources.update_one(
        {"id": resource_id},
        {"$set": {"is_active": False}}
    )
    return {"message": "Resource deleted successfully"}

# WiFi Credentials Management
@api_router.post("/admin/wifi")
async def update_wifi_credentials(
    wifi_data: WiFiCredentialsUpdate,
    admin_user: User = Depends(get_admin_user)
):
    # Check if WiFi credentials exist
    existing = await db.wifi_credentials.find_one({})
    
    wifi_creds = WiFiCredentials(
        network_name=wifi_data.network_name,
        password=wifi_data.password,
        connection_guide=wifi_data.connection_guide,
        updated_by=admin_user.id
    )
    
    if existing:
        await db.wifi_credentials.update_one(
            {"id": existing["id"]},
            {"$set": wifi_creds.dict()}
        )
    else:
        await db.wifi_credentials.insert_one(wifi_creds.dict())
    
    return {"message": "WiFi credentials updated successfully"}

@api_router.get("/admin/wifi", response_model=WiFiCredentialsResponse)
async def get_wifi_credentials_admin(admin_user: User = Depends(get_admin_user)):
    wifi = await db.wifi_credentials.find_one({})
    if not wifi:
        raise HTTPException(status_code=404, detail="WiFi credentials not found")
    return WiFiCredentialsResponse(**wifi)

# =============================
# PUBLIC DOWNLOADS ROUTES  
# =============================

@api_router.get("/downloads", response_model=List[DownloadFileResponse])
async def get_public_downloads():
    # Get only active public downloads
    downloads = await db.downloads.find({
        "is_active": True,
        "file_type": "public"
    }).to_list(1000)
    
    return [DownloadFileResponse(**download) for download in downloads]

@api_router.get("/downloads/{download_id}")
async def download_file(download_id: str):
    download = await db.downloads.find_one({"id": download_id, "is_active": True})
    if not download:
        raise HTTPException(status_code=404, detail="Download not found")
    
    # Check if file is public (no authentication needed)
    if download["file_type"] != "public":
        raise HTTPException(status_code=403, detail="Access denied. File is private.")
    
    # Increment download count
    await db.downloads.update_one(
        {"id": download_id},
        {"$inc": {"download_count": 1}}
    )
    
    # Decode base64 file data
    file_data = base64.b64decode(download["file_data"])
    
    # Create a temporary file
    temp_file = DOWNLOADS_DIR / f"temp_{download_id}_{download['filename']}"
    with open(temp_file, "wb") as f:
        f.write(file_data)
    
    return FileResponse(
        path=temp_file,
        filename=download["filename"],
        media_type="application/octet-stream"
    )

@api_router.get("/downloads/private/{download_id}")
async def download_private_file(download_id: str, current_user: User = Depends(get_current_user)):
    download = await db.downloads.find_one({"id": download_id, "is_active": True})
    if not download:
        raise HTTPException(status_code=404, detail="Download not found")
    
    # Only admins can download private files
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required for private files")
    
    # Increment download count
    await db.downloads.update_one(
        {"id": download_id},
        {"$inc": {"download_count": 1}}
    )
    
    # Decode base64 file data
    file_data = base64.b64decode(download["file_data"])
    
    # Create a temporary file
    temp_file = DOWNLOADS_DIR / f"temp_{download_id}_{download['filename']}"
    with open(temp_file, "wb") as f:
        f.write(file_data)
    
    return FileResponse(
        path=temp_file,
        filename=download["filename"],
        media_type="application/octet-stream"
    )

# =============================
# STUDENT ROUTES
# =============================

@api_router.get("/student/profile", response_model=StudentResponse)
async def get_student_profile(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    student = await db.students.find_one({"user_id": current_user.id})
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    return await get_student_response(Student(**student))

@api_router.put("/student/parent-contacts")
async def update_parent_contacts(
    parent_contacts: ParentContact,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    await db.students.update_one(
        {"user_id": current_user.id},
        {"$set": {"parent_contacts": parent_contacts.dict(), "updated_at": datetime.utcnow()}}
    )
    return {"message": "Parent contacts updated successfully"}

@api_router.get("/student/certificate")
async def download_certificate(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    student = await db.students.find_one({"user_id": current_user.id})
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    student_obj = Student(**student)
    
    # Check eligibility
    if not student_obj.certificate:
        raise HTTPException(status_code=404, detail="No certificate available")
    
    average_score = calculate_average_score(student_obj.academic_record)
    if not average_score or average_score < 60:
        raise HTTPException(status_code=403, detail="Average score must be 60% or above")
    
    if not student_obj.finance_record or not student_obj.finance_record.is_cleared:
        raise HTTPException(status_code=403, detail="Fees must be cleared")
    
    # Decode base64 file data
    file_data = base64.b64decode(student_obj.certificate.file_data)
    
    # Create a temporary file
    temp_file = UPLOAD_DIR / f"temp_{student_obj.id}_{student_obj.certificate.filename}"
    with open(temp_file, "wb") as f:
        f.write(file_data)
    
    return FileResponse(
        path=temp_file,
        filename=student_obj.certificate.filename,
        media_type="application/pdf"
    )

# =============================
# NEW STUDENT ROUTES FOR RESOURCES
# =============================

@api_router.get("/student/notifications", response_model=List[NotificationResponse])
async def get_student_notifications(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    # Get student profile to get student ID
    student = await db.students.find_one({"user_id": current_user.id})
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Get notifications for this student
    notifications = await db.notifications.find({
        "is_active": True,
        "$or": [
            {"target_audience": "all"},
            {"target_audience": "specific", "target_student_ids": {"$in": [student["id"]]}}
        ]
    }).to_list(1000)
    
    return [
        NotificationResponse(
            **notif,
            has_attachment=notif["attachment_filename"] is not None
        ) for notif in notifications
    ]

@api_router.get("/student/notifications/{notification_id}/attachment")
async def download_notification_attachment(notification_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    notification = await db.notifications.find_one({"id": notification_id, "is_active": True})
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if not notification["attachment_data"]:
        raise HTTPException(status_code=404, detail="No attachment found")
    
    # Get student profile to check access
    student = await db.students.find_one({"user_id": current_user.id})
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Check if student has access to this notification
    if notification["target_audience"] == "specific" and student["id"] not in notification["target_student_ids"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Decode base64 file data
    file_data = base64.b64decode(notification["attachment_data"])
    
    # Create a temporary file
    temp_file = DOWNLOADS_DIR / f"notification_attachment_{notification_id}_{notification['attachment_filename']}"
    with open(temp_file, "wb") as f:
        f.write(file_data)
    
    return FileResponse(
        path=temp_file,
        filename=notification["attachment_filename"],
        media_type="application/octet-stream"
    )

@api_router.get("/student/resources", response_model=List[StudentResourceResponse])
async def get_student_resources(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    resources = await db.student_resources.find({"is_active": True}).to_list(1000)
    return [StudentResourceResponse(**resource) for resource in resources]

@api_router.get("/student/resources/{resource_id}/download")
async def download_student_resource(resource_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    resource = await db.student_resources.find_one({"id": resource_id, "is_active": True})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Decode base64 file data
    file_data = base64.b64decode(resource["file_data"])
    
    # Create a temporary file
    temp_file = DOWNLOADS_DIR / f"resource_{resource_id}_{resource['filename']}"
    with open(temp_file, "wb") as f:
        f.write(file_data)
    
    return FileResponse(
        path=temp_file,
        filename=resource["filename"],
        media_type="application/pdf"
    )

@api_router.get("/student/wifi", response_model=WiFiCredentialsResponse)
async def get_wifi_credentials_student(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    wifi = await db.wifi_credentials.find_one({})
    if not wifi:
        raise HTTPException(status_code=404, detail="WiFi credentials not found")
    return WiFiCredentialsResponse(**wifi)

@api_router.get("/student/downloads", response_model=List[DownloadFileResponse])
async def get_student_downloads(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    # Get all downloads (both public and private, but students can only download public ones)
    downloads = await db.downloads.find({"is_active": True}).to_list(1000)
    return [DownloadFileResponse(**download) for download in downloads]

# =============================
# PUBLIC ROUTES
# =============================

@api_router.get("/")
async def root():
    return {"message": "TWOEM Online Productions API"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@api_router.get("/eulogies", response_model=List[EulogyResponse])
async def get_public_eulogies():
    # Get only active eulogies that haven't expired
    current_time = datetime.utcnow()
    eulogies = await db.eulogies.find({
        "is_active": True,
        "expires_at": {"$gt": current_time}
    }).to_list(1000)
    
    result = []
    for eulogy in eulogies:
        days_remaining = max(0, (eulogy["expires_at"] - current_time).days)
        result.append(EulogyResponse(
            **eulogy,
            days_remaining=days_remaining
        ))
    return result

@api_router.get("/eulogies/{eulogy_id}/download")
async def download_eulogy(eulogy_id: str):
    eulogy = await db.eulogies.find_one({"id": eulogy_id})
    if not eulogy:
        raise HTTPException(status_code=404, detail="Eulogy not found")
    
    # Check if eulogy is active and not expired
    if not eulogy["is_active"] or datetime.utcnow() > eulogy["expires_at"]:
        raise HTTPException(status_code=410, detail="Eulogy has expired or is no longer available")
    
    # Decode base64 file data
    file_data = base64.b64decode(eulogy["file_data"])
    
    # Create a temporary file
    temp_file = EULOGY_DIR / f"temp_{eulogy_id}_{eulogy['filename']}"
    with open(temp_file, "wb") as f:
        f.write(file_data)
    
    return FileResponse(
        path=temp_file,
        filename=eulogy["filename"],
        media_type="application/pdf"
    )

# =============================
# HELPER FUNCTIONS
# =============================

async def get_student_response(student: Student) -> StudentResponse:
    user = await db.users.find_one({"id": student.user_id})
    username = user["username"] if user else "unknown"
    
    average_score = calculate_average_score(student.academic_record)
    has_certificate = student.certificate is not None
    can_download = (
        has_certificate and
        average_score is not None and
        average_score >= 60 and
        student.finance_record is not None and
        student.finance_record.is_cleared
    )
    
    return StudentResponse(
        id=student.id,
        username=username,
        full_name=student.full_name,
        id_number=student.id_number,
        email=student.email,
        phone=student.phone,
        parent_contacts=student.parent_contacts,
        academic_record=student.academic_record,
        finance_record=student.finance_record,
        certificate=student.certificate,
        has_certificate=has_certificate,
        can_download_certificate=can_download,
        average_score=average_score
    )

# Include the router in the main app
app.include_router(api_router)

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

# Create default admin user on startup
@app.on_event("startup")
async def create_default_admin():
    admin_exists = await db.users.find_one({"role": "admin"})
    if not admin_exists:
        admin_user = User(
            username="admin",
            email="admin@twoem.com",
            role="admin",
            hashed_password=hash_password("Twoemweb@2020"),
            is_first_login=False
        )
        await db.users.insert_one(admin_user.dict())
        logger.info("Default admin user created: username=admin, password=Twoemweb@2020")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()