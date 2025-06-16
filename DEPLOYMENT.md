# TWOEM Deployment Guide for Render

## 🚀 Render Deployment Overview

Your TWOEM application can be deployed on Render with the following architecture:
- **Backend**: Web Service (FastAPI)
- **Frontend**: Static Site (React)
- **Database**: MongoDB Atlas (external)

## 📋 Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **MongoDB Atlas**: Set up free cluster at [mongodb.com](https://cloud.mongodb.com)

## 🗄️ Database Setup (MongoDB Atlas)

### Step 1: Create MongoDB Atlas Cluster
1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a free account
3. Create a new cluster (choose free tier)
4. Wait for cluster to be created (2-3 minutes)

### Step 2: Configure Database Access
1. Go to "Database Access" → "Add New Database User"
2. Create a user with read/write permissions
3. Go to "Network Access" → "Add IP Address"
4. Add `0.0.0.0/0` (allow access from anywhere)

### Step 3: Get Connection String
1. Click "Connect" on your cluster
2. Choose "Connect your application"
3. Copy the connection string
4. Replace `<password>` with your database user password

Example connection string:
```
mongodb+srv://username:password@cluster0.xyz.mongodb.net/twoem_production?retryWrites=true&w=majority
```

## 🔧 Render Deployment Steps

### Option 1: Using render.yaml (Recommended)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/twoem.git
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file

3. **Configure Environment Variables**
   - Set `MONGO_URL` to your MongoDB Atlas connection string
   - Other variables will be auto-generated or use defaults

### Option 2: Manual Setup

#### Backend Deployment
1. **Create Web Service**
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `twoem-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `cd backend && pip install -r requirements.txt`
     - **Start Command**: `cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT`

2. **Set Environment Variables**
   ```
   MONGO_URL=mongodb+srv://username:password@cluster0.xyz.mongodb.net/twoem_production?retryWrites=true&w=majority
   DB_NAME=twoem_production
   JWT_SECRET_KEY=your-super-secret-jwt-key-generate-random
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=24
   ADMIN_EMAIL=admin@twoem.com
   ADMIN_PASSWORD=YourSecureAdminPassword2025!
   UPLOAD_DIR=uploads
   MAX_FILE_SIZE=50000000
   ENCRYPTION_KEY=generate-32-byte-key
   ```

#### Frontend Deployment
1. **Create Static Site**
   - Click "New" → "Static Site"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `twoem-frontend`
     - **Build Command**: `cd frontend && yarn install && yarn build`
     - **Publish Directory**: `frontend/build`

2. **Set Environment Variables**
   ```
   REACT_APP_BACKEND_URL=https://twoem-backend.onrender.com
   ```

## 🔧 Required Code Modifications

### Backend Modifications

1. **Update CORS for Production** (already configured in server.py):
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_credentials=True,
       allow_origins=["*"],  # In production, specify your frontend URL
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Environment Variables** (already configured in .env):
   - All required environment variables are already set up
   - Just need to update them for production values

### Frontend Modifications

1. **Build Configuration** (already configured):
   - `package.json` already has build scripts
   - Environment variables properly configured

2. **API Calls** (already configured):
   - All API calls use `process.env.REACT_APP_BACKEND_URL`
   - No hardcoded URLs

## 🌐 Production URLs

After deployment, your application will be available at:
- **Frontend**: `https://twoem-frontend.onrender.com`
- **Backend API**: `https://twoem-backend.onrender.com`

## 🔐 Security Considerations

### Environment Variables to Generate:
1. **JWT_SECRET_KEY**: Generate a strong random key
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **ADMIN_PASSWORD**: Create a strong admin password

3. **ENCRYPTION_KEY**: Generate for credential encryption
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

### Production Settings:
- Use strong passwords
- Restrict CORS origins to your domain
- Enable HTTPS (Render provides this automatically)
- Secure your MongoDB Atlas cluster

## 📊 Monitoring & Maintenance

### Render Features:
- **Automatic Deployments**: Updates when you push to GitHub
- **Logs**: View application logs in Render dashboard
- **Metrics**: Monitor performance and usage
- **Custom Domains**: Add your own domain name

### MongoDB Atlas Features:
- **Monitoring**: Database performance metrics
- **Backups**: Automatic backups
- **Alerts**: Set up alerts for issues

## 💰 Cost Considerations

### Free Tier Limits:
- **Render**: 750 hours/month for web services
- **MongoDB Atlas**: 512MB storage free tier
- **Static Sites**: Unlimited on Render

### Scaling:
- Upgrade to paid plans for production use
- Render Pro plans start at $7/month
- MongoDB Atlas paid tiers for larger storage

## 🐛 Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check build logs in Render dashboard
   - Ensure all dependencies are in requirements.txt/package.json

2. **Database Connection**:
   - Verify MongoDB Atlas connection string
   - Check network access settings

3. **CORS Errors**:
   - Verify frontend URL in backend CORS settings
   - Check environment variables

4. **Environment Variables**:
   - Ensure all required variables are set
   - Check for typos in variable names

### Debug Commands:
```bash
# Test backend locally
cd backend && python -m uvicorn server:app --reload

# Test frontend locally
cd frontend && yarn start

# Test database connection
python -c "from motor.motor_asyncio import AsyncIOMotorClient; print('DB connection test')"
```

## 🚀 Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] MongoDB Atlas cluster created
- [ ] Database user and network access configured
- [ ] Render services created (backend + frontend)
- [ ] Environment variables configured
- [ ] Services deployed successfully
- [ ] Admin account accessible
- [ ] File upload/download working
- [ ] Authentication flow tested
- [ ] All features verified in production

## 📞 Support

If you encounter issues:
1. Check Render documentation: [docs.render.com](https://docs.render.com)
2. MongoDB Atlas docs: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
3. Review application logs in Render dashboard

Your TWOEM application is production-ready and can be deployed on Render with these configurations!