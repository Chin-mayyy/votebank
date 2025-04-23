from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from query_processor import process_user_query, stream_response
import uvicorn
from typing import Generator
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class QueryRequest(BaseModel):
    question: str

@app.get("/")
async def read_root():
    return FileResponse('templates/index.html')

@app.post("/api/query")
async def process_query(request: QueryRequest) -> Generator[str, None, None]:
    """
    Process user query and stream the response
    """
    try:
        # Process the query and get the GPT-4 response
        response = process_user_query(request.question)
        
        # Stream the response back to the client
        async def generate():
            for chunk in stream_response(response):
                yield f"data: {chunk}\n\n"
        
        return generate()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    # Create necessary directories if they don't exist
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 