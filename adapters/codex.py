"""
Codex Platform Adapter

Provides GitHub Copilot/Codex compatible interface for the Logic-code skill.
"""

from typing import Dict, Any, List
from core import analyze, transcribe_code

class CodexAdapter:
    """
    Adapter for integrating with GitHub Copilot/Codex.
    
    Provides methods compatible with OpenAI Codex API format.
    """
    
    @staticmethod
    def analyze(code: str, context: dict = None) -> Dict[str, Any]:
        """
        Analyze code complexity for Codex.
        
        Args:
            code: Source code to analyze
            context: Optional context dictionary
        
        Returns:
            Analysis results in Codex-compatible format
        """
        result = analyze(code, context)
        
        return {
            "role": "system",
            "content": CodexAdapter._format_analysis(result)
        }
    
    @staticmethod
    def transcribe(code: str, project_context: str = "") -> Dict[str, Any]:
        """
        Transcribe code to natural language for Codex.
        
        Args:
            code: Source code to transcribe
            project_context: Optional project context
        
        Returns:
            Transcription results in Codex-compatible format
        """
        context = {"config": {"project_context": project_context}}
        result = transcribe_code(code, context)
        
        return {
            "role": "system",
            "content": CodexAdapter._format_transcription(result)
        }
    
    @staticmethod
    def _format_analysis(result: Dict[str, Any]) -> str:
        """
        Format analysis results for Codex.
        
        Args:
            result: Analysis result
        
        Returns:
            Formatted string
        """
        if not result.get("success", False):
            return f"Analysis failed: {result.get('error', 'Unknown error')}"
        
        parts = []
        parts.append("Code Analysis Results:")
        parts.append("")
        
        complexity = result.get("complexity", {})
        parts.append(f"Complexity: Average={complexity.get('average', 0.0):.2f}, Highest={complexity.get('highest', 0)}")
        
        suggestions = result.get("suggestions", [])
        if suggestions:
            parts.append("")
            parts.append("Refactoring Suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                parts.append(f"{i}. {suggestion}")
        
        return "\n".join(parts)
    
    @staticmethod
    def _format_transcription(result: Dict[str, Any]) -> str:
        """
        Format transcription results for Codex.
        
        Args:
            result: Transcription result
        
        Returns:
            Formatted string
        """
        if not result.get("success", False):
            return f"Transcription failed: {result.get('error', 'Unknown error')}"
        
        parts = []
        parts.append("Code Transcription:")
        parts.append("")
        
        if result.get("natural_language"):
            parts.append(result["natural_language"])
        
        if result.get("intent_summary"):
            parts.append("")
            parts.append(result["intent_summary"])
        
        return "\n".join(parts)
    
    @staticmethod
    def create_prompt(code: str, task: str = "analyze") -> List[Dict[str, Any]]:
        """
        Create a prompt for Codex.
        
        Args:
            code: Source code to process
            task: Task type ('analyze' or 'transcribe')
        
        Returns:
            Prompt messages in Codex format
        """
        system_prompt = {
            "role": "system",
            "content": "You are a code analysis assistant. Use the logic_code_analyzer tool to analyze code when needed."
        }
        
        user_prompt = {
            "role": "user",
            "content": f"Please {task} this code:\n\n{code}"
        }
        
        return [system_prompt, user_prompt]
    
    @staticmethod
    def get_function_definitions() -> List[Dict[str, Any]]:
        """
        Get function definitions for Codex function calling.
        
        Returns:
            List of function definitions
        """
        return [
            {
                "name": "logic_code_analyzer",
                "description": "Analyze code complexity and transcribe code to natural language",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The source code to analyze or transcribe"
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["analyze", "transcribe"],
                            "description": "Mode: 'analyze' for complexity analysis, 'transcribe' for natural language transcription",
                            "default": "analyze"
                        },
                        "project_context": {
                            "type": "string",
                            "description": "Optional project context for better intent analysis"
                        }
                    },
                    "required": ["code"]
                }
            }
        ]