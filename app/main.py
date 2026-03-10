"""FastAPI application for the Social Sentiment Agent."""

import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import ChatRequest, ChatResponse, ResetRequest, ResetResponse
from app.agent.agent import chat as agent_chat
from app.agent.memory import reset_memory

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Social Sentiment Agent starting up...")
    logger.info("   OpenAI model: %s", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    yield
    logger.info("👋 Social Sentiment Agent shutting down.")


app = FastAPI(
    title="Social Sentiment Agent",
    description="輿情分析 AI 助手 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the chat UI."""
    index_path = os.path.join(_static_dir, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Frontend not found")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """Send a message to the sentiment analysis agent."""
    try:
        logger.info("📩 [%s] User: %s", req.session_id[:8], req.message[:100])
        response = await agent_chat(req.session_id, req.message)
        logger.info("🤖 [%s] Agent: %s", req.session_id[:8], response[:100])
        return ChatResponse(response=response, session_id=req.session_id)
    except Exception as e:
        logger.error("❌ Agent error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.post("/api/reset", response_model=ResetResponse)
async def reset_endpoint(req: ResetRequest):
    """Reset conversation memory for a session."""
    reset_memory(req.session_id)
    logger.info("🔄 Session %s reset", req.session_id[:8])
    return ResetResponse(session_id=req.session_id)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "social-sentiment-agent"}
