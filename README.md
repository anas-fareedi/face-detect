# Face Recognition System - FastAPI Backend

Complete FastAPI backend for face registration and recognition system with MongoDB Cloud integration.

## 🚀 Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure MongoDB Cloud

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your MongoDB Atlas connection string:

```env
MONGODB_URL=mongodb+srv://your-username:your-password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=face_recognition_db
```

### 4. Run the Backend Server

```bash
uvicorn main:app --reload 
```

The API will be available at `http://localhost:8000`

### 5. Run the Frontend

In a separate terminal, start a local server:

```bash
python -m http.server 8001
```

Open `http://localhost:8001/registerFace.html` in your browser

## 🐛 Troubleshooting

**Connection Error:**
- Check MongoDB connection string in `.env`
- Verify IP whitelist in MongoDB Atlas
- Ensure database user has correct permissions

**CORS Error:**
- Update `CORS_ORIGINS` in `config.py` or `.env`
- Check frontend is running on allowed origin

**Import Error:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`