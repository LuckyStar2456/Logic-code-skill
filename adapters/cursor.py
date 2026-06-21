"""
Cursor Platform Adapter

Provides Cursor IDE compatible interface for the Logic-code skill.
"""

from typing import Dict, Any, List
from core import analyze, transcribe_code

class CursorAdapter:
    """
    Adapter for integrating with Cursor IDE.
    
    Provides methods compatible with Cursor's AI assistant API.
    """
    
    @staticmethod
    def analyze(code: str, context: dict = None) -> Dict[str, Any]:
        """
        Analyze code complexity for Cursor.
        
        Args:
            code: Source code to analyze
            context: Optional context dictionary
        
        Returns:
            Analysis results in Cursor-compatible format
        """
        result = analyze(code, context)
        
        cursor_result = {
            "kind": "analysis",
            "version": "1.0",
            "title": "Code Complexity Analysis",
            "sections": []
        }
        
        summary = result.get("summary", {})
        if summary:
            cursor_result["sections"].append({
                "title": "Summary",
                "content": [
                    f"Total Lines: {summary.get('total_lines', 0)}",
                    f"Non-empty Lines: {summary.get('non_empty_lines', 0)}",
                    f"Comment Lines: {summary.get('comment_lines', 0)}",
                    f"Blank Lines: {summary.get('blank_lines', 0)}"
                ]
            })
        
        complexity = result.get("complexity", {})
        if complexity:
            cursor_result["sections"].append({
                "title": "Complexity Metrics",
                "content": [
                    f"Average: {complexity.get('average', 0.0):.2f}",
                    f"Highest: {complexity.get('highest', 0)}",
                    f"Total: {complexity.get('total', 0)}"
                ]
            })
        
        suggestions = result.get("suggestions", [])
        if suggestions:
            cursor_result["sections"].append({
                "title": "Refactoring Suggestions",
                "content": suggestions
            })
        
        return cursor_result
    
    @staticmethod
    def transcribe(code: str, project_context: str = "") -> Dict[str, Any]:
        """
        Transcribe code to natural language for Cursor.
        
        Args:
            code: Source code to transcribe
            project_context: Optional project context
        
        Returns:
            Transcription results in Cursor-compatible format
        """
        context = {"config": {"project_context": project_context}}
        result = transcribe_code(code, context)
        
        cursor_result = {
            "kind": "transcription",
            "version": "1.0",
            "title": "Code Transcription",
            "detected_language": result.get("detected_language", ""),
            "sections": []
        }
        
        if result.get("natural_language"):
            cursor_result["sections"].append({
                "title": "Natural Language Description",
                "content": [result["natural_language"]]
            })
        
        if result.get("intent_summary"):
            cursor_result["sections"].append({
                "title": "Intent Summary",
                "content": [result["intent_summary"]]
            })
        
        if result.get("context_analysis"):
            cursor_result["sections"].append({
                "title": "Context Analysis",
                "content": [result["context_analysis"]]
            })
        
        return cursor_result
    
    @staticmethod
    def to_markdown(result: Dict[str, Any]) -> str:
        """
        Convert result to markdown format for Cursor.
        
        Args:
            result: Analysis or transcription result
        
        Returns:
            Markdown string
        """
        lines = []
        
        if result.get("title"):
            lines.append(f"## {result['title']}")
            lines.append("")
        
        for section in result.get("sections", []):
            lines.append(f"### {section['title']}")
            lines.append("")
            
            for item in section.get("content", []):
                if isinstance(item, str):
                    lines.append(f"- {item}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def get_actions() -> List[Dict[str, Any]]:
        """
        Get available actions for Cursor.
        
        Returns:
            List of action definitions
        """
        return [
            {
                "id": "logic-code.analyze",
                "title": "Analyze Code Complexity",
                "description": "Analyze code complexity and get refactoring suggestions",
                "icon": "code",
                "inputs": [
                    {
                        "type": "code",
                        "label": "Code to analyze",
                        "required": True
                    }
                ]
            },
            {
                "id": "logic-code.transcribe",
                "title": "Transcribe Code to Natural Language",
                "description": "Convert code to natural language with intent analysis",
                "icon": "file-text",
                "inputs": [
                    {
                        "type": "code",
                        "label": "Code to transcribe",
                        "required": True
                    },
                    {
                        "type": "text",
                        "label": "Project context (optional)",
                        "required": False
                    }
                ]
            }
        ]