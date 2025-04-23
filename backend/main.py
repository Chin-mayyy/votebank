from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from query_processor import process_user_query, stream_response
import uvicorn
import os
from dotenv import load_dotenv
import logging
import json
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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

@app.post("/api/query", response_model=dict)
async def process_query(request: QueryRequest):
    """
    Process user query and stream the response
    """
    try:
        logger.info(f"Received query request: {request.question}")
        
        # Process the query and get the GPT-4 response
        try:
            response = process_user_query(request.question)
            logger.info("Successfully processed user query")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing query: {error_msg}")
            
            # Get detailed error information
            error_info = {
                "message": error_msg,
                "traceback": traceback.format_exc(),
                "environment": {
                    "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
                    "vanna_api_key_set": bool(os.getenv("VANNA_API_KEY")),
                    "database_connection": {
                        "host": os.getenv("DB_HOST", "localhost"),
                        "port": os.getenv("DB_PORT", "5432"),
                        "database": os.getenv("DB_NAME", "votebank")
                    }
                }
            }
            
            # Determine error type
            if "API key" in error_msg:
                error_type = "configuration_error"
            elif "connection" in error_msg.lower():
                error_type = "connection_error"
            elif "database" in error_msg.lower():
                error_type = "database_error"
            else:
                error_type = "processing_error"
            
            raise HTTPException(
                status_code=500,
                detail=json.dumps({
                    "error": error_msg,
                    "type": error_type,
                    "debug_info": error_info
                })
            )
        
        # Stream the response back to the client
        async def generate():
            try:
                async for chunk in stream_response(response):
                    yield f"data: {json.dumps({'response': chunk})}\n\n"
                logger.info("Successfully streamed response")
            except Exception as e:
                error_msg = f"Error streaming response: {str(e)}"
                logger.error(error_msg)
                error_info = {
                    "message": error_msg,
                    "traceback": traceback.format_exc()
                }
                yield f"data: {json.dumps({'error': error_msg, 'type': 'streaming_error', 'debug_info': error_info})}\n\n"
        
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
        error_info = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(
            status_code=500,
            detail=json.dumps({
                "error": str(e),
                "type": "unexpected_error",
                "debug_info": error_info
            })
        )

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 