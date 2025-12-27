"""
Sub-Zero Backend API
FastAPI application with Supabase integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import subscriptions, cancellations

# Initialize FastAPI app
app = FastAPI(
    title="Sub-Zero API",
    description="AI-Powered Subscription Assassin Backend",
    version="1.0.0"
)

# CORS configuration for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://*.supabase.co",
        # Add production mobile app domains here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(subscriptions.router, prefix="/api", tags=["subscriptions"])
app.include_router(cancellations.router, prefix="/api", tags=["cancellations"])


@app.get("/")
async def root():
    """Root endpoint - API status check"""
    return {
        "status": "online",
        "service": "Sub-Zero API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"  # TODO: Add real timestamp
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
