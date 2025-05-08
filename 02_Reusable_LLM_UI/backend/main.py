import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import LANGCHAIN_PROJECT
from routes.chat_routes import router as chat_router

app = FastAPI()

# Set LangChain project name
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT

# Get allowed origins from environment variable
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Allow CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Only allow specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only allow necessary methods
    # Only allow necessary headers
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(chat_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
