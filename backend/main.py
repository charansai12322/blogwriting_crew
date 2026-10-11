"""
FastAPI Backend Server for Blog Writing Crew.
Provides health monitoring and blog generation API endpoints.
"""

import sys
import os
import asyncio
import logging

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Ensure both repository root and backend directory are in sys.path
_current_dir = Path(__file__).resolve().parent
_repo_root = _current_dir.parent
for _p in [str(_repo_root), str(_current_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Load local environment variables from backend/.env or repo root .env
_backend_env = _current_dir / ".env"
_root_env = _repo_root / ".env"
if _backend_env.exists():
    load_dotenv(dotenv_path=_backend_env)
if _root_env.exists():
    load_dotenv(dotenv_path=_root_env)
load_dotenv()

try:
    from backend.agent import run_blog_crew, get_model_name
except (ImportError, ModuleNotFoundError):
    from agent import run_blog_crew, get_model_name

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("blogwriting_crew_backend")

app = FastAPI(
    title="Blog Writing Crew API",
    description="Backend API powering the multi-agent Blog Writing Crew",
    version="1.0.0"
)

# CORS configuration
raw_cors = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
origins = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Concurrency lock to prevent multiple simultaneous crew executions from colliding
crew_execution_lock = asyncio.Lock()


class BlogGenerateRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The topic or query for the blog post",
        examples=["How AI agents are transforming software development"]
    )


class BlogStats(BaseModel):
    word_count: int
    char_count: int


class BlogMetadata(BaseModel):
    model: str
    stats: BlogStats


class BlogGenerateResponse(BaseModel):
    success: bool
    topic: str
    blog: str
    metadata: BlogMetadata


class HealthResponse(BaseModel):
    status: str
    message: str
    model: str
    agents: list[str]


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify backend status and configuration."""
    return HealthResponse(
        status="ok",
        message="Blog Writing Crew backend is running and ready.",
        model=get_model_name(),
        agents=["content_strategist", "blog_writer", "editor"]
    )


@app.post("/api/generate", response_model=BlogGenerateResponse)
async def generate_blog(request: BlogGenerateRequest):
    """
    Generate a full blog post using the three-agent CrewAI pipeline.
    Agents:
    1. content_strategist - Creates outline & content plan
    2. blog_writer - Writes full markdown blog post
    3. editor - Proofreads and polishes final markdown
    """
    cleaned_topic = request.topic.strip()
    if not cleaned_topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The blog topic cannot be empty or whitespace only."
        )

    logger.info(f"Received blog generation request for topic: '{cleaned_topic}'")

    # Guard with concurrency lock
    async with crew_execution_lock:
        try:
            result = await run_blog_crew(cleaned_topic)

            return BlogGenerateResponse(
                success=True,
                topic=cleaned_topic,
                blog=result["blog_markdown"],
                metadata=BlogMetadata(
                    model=result["model"],
                    stats=BlogStats(
                        word_count=result["stats"]["word_count"],
                        char_count=result["stats"]["char_count"]
                    )
                )
            )
        except ValueError as ve:
            # Typically missing API key or configuration error
            logger.error(f"Configuration or validation error: {str(ve)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(ve)
            )
        except Exception as exc:
            # Log full error internally for debugging, return sanitized message to user
            logger.exception("Error occurred during CrewAI execution")
            err_msg = str(exc)
            # Sanitize in case an API key was accidentally included in raw vendor message
            sanitized_msg = err_msg if len(err_msg) < 300 else err_msg[:300] + "..."
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI generation failed: {sanitized_msg}"
            )


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
