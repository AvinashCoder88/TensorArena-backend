from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import arena, role_arena, chat, ml, classroom
from app.services.deepgram_service import DeepgramService

app = FastAPI(
    title="AI LeetCode Platform API",
    description="Backend for the AI-powered adaptive learning platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Vercel deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(arena.router)
app.include_router(role_arena.router)
app.include_router(chat.router)
app.include_router(ml.router)
app.include_router(classroom.router)

deepgram_service = DeepgramService()

@app.get("/")
async def root():
    return {"message": "Welcome to the AI LeetCode Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/deepgram/token")
async def get_deepgram_token():
    return await deepgram_service.get_token()


