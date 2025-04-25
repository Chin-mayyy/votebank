from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
# Import from the query processor
from query_processor import process_query, stream_response
import uvicorn
import os
from dotenv import load_dotenv
import logging
import json
import traceback
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Debug environment variables
logger.info("Checking environment variables...")
logger.info(f"VANNA_API_KEY is set: {bool(os.getenv('VANNA_API_KEY'))}")

# Application configuration
# Add any app-wide configuration here


app = FastAPI()

# Configure CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Flutter app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class ErrorResponse(BaseModel):
    detail: str
    error_type: str
    debug_info: dict

@app.post("/api/query")
async def handle_query(request: QueryRequest):
    """
    Process user query and stream the response
    """
    try:
        logger.info(f"Received query request: {request.question}")
        
        # Process the query and get the response
        try:
            response = process_query(request.question)
            logger.info("Successfully processed user query")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing query: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Stream the response back to the client
        async def generate():
            try:
                async for word in stream_response(response):
                    yield f"data: {word}\n\n"
                logger.info("Successfully streamed response")
            except Exception as e:
                error_msg = f"Error streaming response: {str(e)}"
                logger.error(error_msg)
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in process_query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 