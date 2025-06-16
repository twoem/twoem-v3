# TWOEM Online Productions - Full Stack Application

## 🌟 Overview

TWOEM Online Productions is a modern, full-stack web application that provides comprehensive cyber services in Kenya, specifically in Nyanduma Ward, Lari, Kiambu County. The application has been transformed from a static website into a dynamic, secure platform with advanced authentication and file management capabilities.

## 🚀 Features

### 🔐 Authentication & Security
- **JWT-based Authentication**: Secure user registration and login
- **Role-based Access Control**: Admin and regular user roles
- **Protected Routes**: Secure access to sensitive areas
- **Encrypted Storage**: Gmail/iTax credentials stored with encryption

### 📁 File Management
- **Secure File Upload/Download**: Base64 storage with access control
- **Public & Private Files**: Flexible file sharing options
- **File Type Validation**: Support for PDF, DOC, DOCX, images, and text files
- **Download Tracking**: Monitor file access statistics

### ⏰ Eulogy System
- **Auto-Expiring Eulogies**: PDF eulogies that expire after 3 days
- **Upload Management**: Easy upload and management interface
- **Download Tracking**: Monitor eulogy access
- **Automatic Cleanup**: Background task to remove expired content

### 📞 Contact Management
- **Contact Form**: Integrated contact form with database storage
- **Admin Dashboard**: View and manage all contact submissions
- **Email Integration**: Professional contact handling

### 💼 Services Showcase
- **eCitizen Services**: Government document processing
- **iTax Services**: Tax-related documentation and filing
- **Digital Printing**: Business cards, certificates, brochures
- **Cyber Services**: Internet, printing, lamination services
- **Internet Installation**: Network setup and maintenance

### 📱 Modern UI/UX
- **Responsive Design**: Works perfectly on all devices
- **Light Mode**: Clean, professional appearance
- **Tailwind CSS**: Modern styling framework
- **Interactive Elements**: Smooth animations and transitions
- **Toast Notifications**: Real-time user feedback

## 🏗️ Technical Architecture

### Backend (FastAPI + MongoDB)
```
/app/backend/
├── server.py              # Main FastAPI application
├── models.py              # Pydantic data models
├── auth.py                # JWT authentication logic
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

### Frontend (React + Tailwind CSS)
```
/app/frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Navbar.js
│   │   ├── Footer.js
│   │   ├── LoadingSpinner.js
│   │   └── ProtectedRoute.js
│   ├── contexts/          # React contexts
│   │   └── AuthContext.js
│   ├── pages/             # Page components
│   │   ├── Home.js
│   │   ├── Login.js
│   │   ├── Register.js
│   │   ├── Services.js
│   │   ├── Eulogies.js
│   │   ├── Downloads.js
│   │   ├── Admin.js
│   │   └── GmailItax.js
│   ├── App.js             # Main application component
│   └── index.js           # Entry point
├── public/                # Static assets
│   ├── images/            # Service and gallery images
│   └── eulogies/          # Sample eulogy files
├── package.json           # Node.js dependencies
└── .env                   # Environment variables
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### File Management
- `POST /api/files` - Upload file
- `GET /api/files` - List files
- `GET /api/files/{file_id}` - Download file
- `DELETE /api/admin/files/{file_id}` - Delete file (admin)

### Eulogy Management
- `POST /api/eulogies` - Upload eulogy
- `GET /api/eulogies` - List active eulogies
- `GET /api/eulogies/{eulogy_id}` - Download eulogy
- `DELETE /api/admin/eulogies/{eulogy_id}` - Delete eulogy (admin)
- `POST /api/admin/cleanup-expired` - Cleanup expired eulogies

### Contact & Services
- `POST /api/contact` - Submit contact form
- `GET /api/contact` - List contacts (admin)
- `GET /api/services` - List all services

### Credentials (Gmail/iTax)
- `POST /api/credentials` - Save encrypted credentials

### Health & Admin
- `GET /api/health` - Health check
- Various admin endpoints for management

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database with Motor async driver
- **JWT**: JSON Web Tokens for authentication
- **Pydantic**: Data validation and serialization
- **Passlib**: Password hashing with bcrypt
- **Cryptography**: Encryption for sensitive data

### Frontend
- **React 19**: Latest React framework
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **React Hot Toast**: Toast notifications
- **Heroicons**: Beautiful SVG icons
- **jsPDF**: PDF generation in browser

### Development Tools
- **ESLint**: JavaScript linting
- **PostCSS**: CSS processing
- **Yarn**: Package management
- **Hot Reload**: Development server with live updates

## 🔐 Security Features

### Authentication Security
- JWT tokens with configurable expiration
- Password hashing with bcrypt
- Protected API endpoints
- Role-based access control

### Data Security
- Encrypted storage for sensitive credentials
- Input validation and sanitization
- File type validation
- SQL injection prevention
- XSS protection

### File Security
- Base64 encoded file storage
- Access control for downloads
- File size limitations (50MB)
- Type validation for uploads

## 🚀 Deployment

### Environment Variables
```bash
# Backend (.env)
MONGO_URL="mongodb://localhost:27017"
DB_NAME="twoem_database"
JWT_SECRET_KEY="your-super-secret-jwt-key"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS=24
ADMIN_EMAIL="admin@twoem.com"
ADMIN_PASSWORD="TwoemAdmin2025!"

# Frontend (.env)
REACT_APP_BACKEND_URL="https://your-domain.com"
```

### Installation & Setup
```bash
# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup
cd frontend
yarn install

# Start services
sudo supervisorctl restart all
```

### Default Admin Account
- **Email**: admin@twoem.com
- **Password**: TwoemAdmin2025!

## 📱 User Experience

### Public Features
- Browse services information
- View gallery
- Submit contact forms
- Access public eulogies
- Learn about the company

### Authenticated Features
- Upload and manage files
- Access private downloads
- Upload eulogies with auto-expiry
- Generate Gmail/iTax credential PDFs
- Secure credential storage

### Admin Features
- Complete dashboard with statistics
- Manage all files and eulogies
- View and manage contact submissions
- User management capabilities
- System cleanup and maintenance

## 🌐 Business Services

### Government Services
- **eCitizen Processing**: Logbook transfers, vehicle inspections, driving license applications
- **iTax Services**: Tax compliance certificates, returns filing, PIN applications

### Digital Solutions
- **Digital Printing**: Business materials, certificates, marketing collateral
- **Cyber Services**: Internet access, document services, passport photos
- **Network Installation**: Internet setup in Nyanduma Ward area

### Document Management
- **Eulogy Hosting**: Secure, time-limited access to memorial documents
- **File Storage**: Private and public file sharing capabilities
- **Credential Management**: Secure storage of sensitive login information

## 📞 Contact Information

**Location**: Plaza Building, Kagwe Town (opposite Total Petrol Station)  
**Phone**: 0707 330 204 / 0769 720 002  
**Email**: twoemcyber@gmail.com  
**WhatsApp**: [0707330204](https://wa.me/0707330204)

## 📄 License

© 2025 TWOEM Online Productions. All rights reserved.

## 🔄 Version History

- **v1.0.0**: Complete transformation from static website to full-stack application
- Modern React frontend with Tailwind CSS
- Comprehensive FastAPI backend with MongoDB
- Advanced authentication and security features
- Professional file and eulogy management system
- Admin dashboard with full management capabilities

---

*Built with ❤️ for the Kagwe community and beyond.*