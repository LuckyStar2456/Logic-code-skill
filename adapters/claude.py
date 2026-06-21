"""
Claude Platform Adapter

Provides Claude Code compatible interface for the Logic-code skill.
"""

from typing import Dict, Any, List
from core import analyze, transcribe_code

class ClaudeAdapter:
    """
    Adapter for integrating with Claude/Claude Code.
    
    Provides methods compatible with Anthropic's Claude API.
    """
    
    @staticmethod
    def analyze_code(code: str, context: dict = None) -> Dict[str, Any]:
        """
        Analyze code complexity for Claude.
        
        Args:
            code: Source code to analyze
            context: Optional context dictionary
        
        Returns:
            Analysis results in Claude-compatible format
        """
        result = analyze(code, context)
        
        return {
            "type": "code_analysis",
            "version": "1.0",
            "content": {
                "success": result.get("success", False),
                "summary": result.get("summary", {}),
                "complexity": result.get("complexity", {}),
                "functions": result.get("functions", []),
                "suggestions": result.get("suggestions", [])
            }
        }
    
    @staticmethod
    def transcribe_code(code: str, project_context: str = "") -> Dict[str, Any]:
        """
        Transcribe code to natural language for Claude.
        
        Args:
            code: Source code to transcribe
            project_context: Optional project context
        
        Returns:
            Transcription results in Claude-compatible format
        """
        context = {"config": {"project_context": project_context}}
        result = transcribe_code(code, context)
        
        return {
            "type": "code_transcription",
            "version": "1.0",
            "content": {
                "success": result.get("success", False),
                "detected_language": result.get("detected_language", ""),
                "natural_language": result.get("natural_language", ""),
                "intent_summary": result.get("intent_summary", ""),
                "context_analysis": result.get("context_analysis", ""),
                "functions": result.get("functions", [])
            }
        }
    
    @staticmethod
    def format_for_claude(result: Dict[str, Any]) -> str:
        """
        Format results for Claude's response format.
        
        Args:
            result: Analysis or transcription result
        
        Returns:
            Formatted string for Claude
        """
        if result.get("type") == "code_analysis":
            content = result.get("content", {})
            lines = []
            
            if content.get("suggestions"):
                lines.append("代码分析发现以下问题：")
                lines.append("")
                for i, suggestion in enumerate(content["suggestions"], 1):
                    lines.append(f"{i}. {suggestion}")
                lines.append("")
            
            complexity = content.get("complexity", {})
            lines.append(f"复杂度分析：")
            lines.append(f"- 平均复杂度: {complexity.get('average', 0):.2f}")
            lines.append(f"- 最高复杂度: {complexity.get('highest', 0)}")
            
            return "\n".join(lines)
        
        elif result.get("type") == "code_transcription":
            content = result.get("content", {})
            return content.get("natural_language", "")
        
        return str(result)
    
    @staticmethod
    def get_tool_definitions() -> List[Dict[str, Any]]:
        """
        Get tool definitions for Claude.
        
        Returns:
            List of tool definitions in Claude's format
        """
        return [
            {
                "name": "analyze_code",
                "description": "分析代码复杂度，识别函数并提供重构建议",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "要分析的源代码"}
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "transcribe_code",
                "description": "将代码转写为自然语言描述，包含意图分析",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "要转写的源代码"},
                        "project_context": {"type": "string", "description": "项目上下文"}
                    },
                    "required": ["code"]
                }
            }
        ]