"""
Logic-code API Service

RESTful API for code analysis and transcription.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from core import analyze, transcribe_code, transcribe_project

app = FastAPI(
    title="Logic-code API",
    description="API for code analysis and transcription",
    version="1.0.0"
)

class AnalyzeRequest(BaseModel):
    code: str
    min_complexity_threshold: Optional[int] = 10
    enable_suggestions: Optional[bool] = True

class TranscribeRequest(BaseModel):
    code: str
    language: Optional[str] = "auto"
    project_context: Optional[str] = ""

class ProjectRequest(BaseModel):
    project_path: str
    output_path: Optional[str] = None
    project_context: Optional[str] = ""

@app.post("/api/analyze", tags=["Analysis"])
async def analyze_code(request: AnalyzeRequest):
    """
    Analyze code complexity.
    
    Args:
        code: Source code to analyze
        min_complexity_threshold: Minimum complexity threshold for warnings
        enable_suggestions: Enable refactoring suggestions
    
    Returns:
        Analysis results
    """
    try:
        context = {
            'config': {
                'min_complexity_threshold': request.min_complexity_threshold,
                'enable_suggestions': request.enable_suggestions
            }
        }
        result = analyze(request.code, context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transcribe", tags=["Transcription"])
async def transcribe_code_endpoint(request: TranscribeRequest):
    """
    Transcribe code to natural language.
    
    Args:
        code: Source code to transcribe
        language: Target language (auto/python/javascript/java/go)
        project_context: Project context for better intent analysis
    
    Returns:
        Transcription results with intent analysis
    """
    try:
        context = {
            'config': {
                'language': request.language,
                'project_context': request.project_context
            }
        }
        result = transcribe_code(request.code, context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/project", tags=["Project"])
async def transcribe_project_endpoint(request: ProjectRequest):
    """
    Transcribe an entire project.
    
    Args:
        project_path: Path to project directory
        output_path: Output directory for transcribed files
        project_context: Project context for better intent analysis
    
    Returns:
        Project transcription results
    """
    try:
        context = {
            'config': {
                'project_context': request.project_context
            }
        }
        result = transcribe_project(request.project_path, request.output_path, context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy", "service": "logic-code-api"}

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.
    
    Returns:
        API information
    """
    return {
        "name": "Logic-code API",
        "version": "1.0.0",
        "description": "API for code analysis and transcription",
        "endpoints": [
            "/api/analyze - POST: Analyze code complexity",
            "/api/transcribe - POST: Transcribe code to natural language",
            "/api/project - POST: Transcribe entire project",
            "/health - GET: Health check",
            "/docs - GET: API documentation"
        ]
    }