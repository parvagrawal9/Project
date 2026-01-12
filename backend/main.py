"""
Main FastAPI application for Zero Hunger Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from database import engine, Base
from routers import auth, food, referral, ai, analytics, subscription, ngo
from schemas import ChatRequest, ChatResponse

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Zero Hunger Platform API",
    description="AI-powered food distribution platform ensuring no one sleeps hungry",
    version="1.0.0"
)

# CORS middleware
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(food.router)
app.include_router(referral.router)
app.include_router(ai.router)
app.include_router(analytics.router)
app.include_router(subscription.router)
app.include_router(ngo.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Zero Hunger Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "zero-hunger-platform"}


@app.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    try:
        return await ai.chat_with_ai(chat_request)
    except Exception as e:
        # Log the error for debugging
        print(f"Error in /chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        # Catch the error and return a friendly message
        return ChatResponse(reply="Sorry, something went wrong. Please try again.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


