from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import time
import uvicorn
import json
import os
from main import AshaAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("asha_api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AshaAI-API")

# Initialize AshaAI instance
asha_ai = AshaAI()

# Create FastAPI app
app = FastAPI(
    title="AshaAI API",
    description="API for the AshaAI chatbot for JobsForHer Foundation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request and response models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    chat_history: Optional[List[Dict[str, str]]] = None

class QueryResponse(BaseModel):
    response: str
    session_id: str
    has_bias: bool = False
    bias_info: Optional[Dict[str, Any]] = None
    job_recommendations: Optional[List[Dict[str, Any]]] = None
    processing_time: float

class SessionsResponse(BaseModel):
    sessions: List[Dict[str, Any]]

# Simple in-memory session store
sessions = {}

def get_api_key(api_key: str = Header(None)):
    """
    Validate API key
    """
    expected_key = os.getenv("ASHA_API_KEY", "test-api-key")
    if not api_key or api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, api_key: str = Depends(get_api_key)):
    """
    Process a user query and return a response
    """
    start_time = time.time()
    logger.info(f"Processing query: {request.query}")
    
    try:
        # Get or create session
        session_id = request.session_id or f"session_{int(time.time())}"
        if session_id not in sessions:
            sessions[session_id] = []
        
        # Convert chat history to the format expected by AshaAI
        chat_history = []
        if request.chat_history:
            for i in range(0, len(request.chat_history) - 1, 2):
                if i + 1 < len(request.chat_history):
                    user_msg = request.chat_history[i]["content"]
                    ai_msg = request.chat_history[i + 1]["content"]
                    chat_history.append([user_msg, ai_msg])
        
        # Process the query
        result = asha_ai.process_query(request.query, chat_history)
        
        # Update session
        if session_id not in sessions:
            sessions[session_id] = []
        sessions[session_id].append({"role": "user", "content": request.query})
        sessions[session_id].append({"role": "assistant", "content": result["response"]})
        
        # Calculate processing time
        processing_time = time.time() - start_time
        logger.info(f"Query processed in {processing_time:.2f} seconds")
        
        return QueryResponse(
            response=result["response"],
            session_id=session_id,
            has_bias=result.get("has_bias", False),
            bias_info=result.get("bias_info") if result.get("has_bias", False) else None,
            job_recommendations=result.get("job_recommendations", []),
            processing_time=processing_time
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your request: {str(e)}"
        )

@app.get("/api/jobs", response_model=List[Dict[str, Any]])
async def search_jobs(query: str, limit: int = 5, api_key: str = Depends(get_api_key)):
    """
    Search for job listings based on query
    """
    logger.info(f"Searching jobs with query: {query}")
    
    try:
        results = asha_ai.job_processor.search_jobs(query, top_k=limit)
        return results
    except Exception as e:
        logger.error(f"Error searching jobs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error searching jobs: {str(e)}"
        )

@app.get("/api/sessions", response_model=SessionsResponse)
async def get_upcoming_sessions(limit: int = 5, api_key: str = Depends(get_api_key)):
    """
    Get upcoming sessions/events
    """
    logger.info(f"Getting upcoming sessions (limit: {limit})")
    
    try:
        sessions = asha_ai.get_upcoming_events(limit)
        return SessionsResponse(sessions=sessions)
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting upcoming sessions: {str(e)}"
        )

@app.post("/api/detect-bias")
async def detect_bias(request: QueryRequest, api_key: str = Depends(get_api_key)):
    """
    Detect bias in a query
    """
    logger.info(f"Detecting bias in query: {request.query}")
    
    try:
        _, bias_info = asha_ai.bias_system.handle_biased_query(request.query)
        return bias_info
    except Exception as e:
        logger.error(f"Error detecting bias: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error detecting bias: {str(e)}"
        )

@app.get("/api/healthcheck")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok", "version": "1.0.0"}

@app.get("/")
async def root():
    """
    API root endpoint
    """
    return {
        "message": "Welcome to AshaAI API",
        "docs": "/docs",
        "healthcheck": "/api/healthcheck"
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
