"""
LangChain Platform Adapter

Provides LangChain Tool interface for the Logic-code skill.
"""

from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from core import analyze, transcribe_code

class CodeAnalysisInput(BaseModel):
    """Input schema for code analysis tool."""
    code: str = Field(description="The source code to analyze")

class CodeTranscriptionInput(BaseModel):
    """Input schema for code transcription tool."""
    code: str = Field(description="The source code to transcribe")
    project_context: Optional[str] = Field(
        description="Project context for better intent analysis",
        default=""
    )

class CodeAnalyzerTool(BaseTool):
    """
    LangChain tool for code complexity analysis.
    
    Args:
        code: Source code to analyze
        
    Returns:
        Dictionary containing complexity analysis results
    """
    name = "code_analyzer"
    description = "Analyze code complexity, identify functions, and get refactoring suggestions"
    args_schema: Type[BaseModel] = CodeAnalysisInput
    
    def _run(
        self,
        code: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> dict:
        return analyze(code)
    
    async def _arun(
        self,
        code: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> dict:
        return analyze(code)

class CodeTranscriberTool(BaseTool):
    """
    LangChain tool for code-to-natural-language transcription.
    
    Args:
        code: Source code to transcribe
        project_context: Optional project context for better intent analysis
        
    Returns:
        Dictionary containing transcription results with intent analysis
    """
    name = "code_transcriber"
    description = "Transcribe code to natural language with intent analysis and context understanding"
    args_schema: Type[BaseModel] = CodeTranscriptionInput
    
    def _run(
        self,
        code: str,
        project_context: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> dict:
        context = {'config': {'project_context': project_context}}
        return transcribe_code(code, context)
    
    async def _arun(
        self,
        code: str,
        project_context: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> dict:
        context = {'config': {'project_context': project_context}}
        return transcribe_code(code, context)

class LangChainAdapter:
    """
    Adapter for integrating with LangChain.
    
    Provides LangChain Tools for code analysis and transcription.
    """
    
    @staticmethod
    def get_tools():
        """Get all LangChain tools provided by this adapter."""
        return [CodeAnalyzerTool(), CodeTranscriberTool()]
    
    @staticmethod
    def get_analyzer_tool():
        """Get the code analyzer tool."""
        return CodeAnalyzerTool()
    
    @staticmethod
    def get_transcriber_tool():
        """Get the code transcriber tool."""
        return CodeTranscriberTool()