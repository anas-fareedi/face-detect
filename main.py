from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from routes import face_routes

# Database client
mongodb_client = None
database = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global mongodb_client, database
    mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = mongodb_client[settings.DATABASE_NAME]
    app.state.db = database
    print(f"Connected to MongoDB: {settings.DATABASE_NAME}")
    
    yield
    
    # Shutdown
    mongodb_client.close()
    print("Disconnected from MongoDB")

app = FastAPI(
    title="Face Recognition API",
    description="Backend API for face registration and recognition system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.CORS_ORIGINS,
    allow_origins=
    [
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(face_routes.router, prefix="/api/v1", tags=["Face Recognition"])

@app.get("/")
async def root():
    return {
        "message": "Face Recognition API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}
