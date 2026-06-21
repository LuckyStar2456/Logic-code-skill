"""
Trae Platform Adapter

Provides Trae-specific interface for the Logic-code skill.
"""

from typing import Dict, Any
from core import analyze, transcribe_code, transcribe_project

class TraeAdapter:
    """
    Adapter for integrating with Trae platform.
    
    Provides methods that match Trae's skill interface requirements.
    """
    
    @staticmethod
    def analyze(code: str, context: dict = None) -> Dict[str, Any]:
        """
        Analyze code complexity.
        
        Args:
            code: Source code to analyze
            context: Trae context dictionary
        
        Returns:
            Analysis results in Trae-compatible format
        """
        return analyze(code, context)
    
    @staticmethod
    def transcribe(code: str, context: dict = None) -> Dict[str, Any]:
        """
        Transcribe code to natural language.
        
        Args:
            code: Source code to transcribe
            context: Trae context dictionary
        
        Returns:
            Transcription results in Trae-compatible format
        """
        return transcribe_code(code, context)
    
    @staticmethod
    def process_project(project_path: str, output_path: str = None, context: dict = None) -> Dict[str, Any]:
        """
        Transcribe an entire project.
        
        Args:
            project_path: Path to project directory
            output_path: Output directory for transcribed files
            context: Trae context dictionary
        
        Returns:
            Project transcription results
        """
        return transcribe_project(project_path, output_path, context)
    
    @staticmethod
    def generate_report(code: str, context: dict = None) -> str:
        """
        Generate a human-readable report.
        
        Args:
            code: Source code to analyze
            context: Trae context dictionary
        
        Returns:
            Formatted report string
        """
        analysis = analyze(code, context)
        
        if not analysis.get('success', False):
            return f"分析失败: {analysis.get('error', '未知错误')}"
        
        report = []
        report.append("=" * 60)
        report.append("CODE ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")
        
        summary = analysis.get('summary', {})
        report.append("SUMMARY:")
        report.append("-" * 60)
        report.append(f"  Total Lines: {summary.get('total_lines', 0)}")
        report.append(f"  Non-empty Lines: {summary.get('non_empty_lines', 0)}")
        report.append(f"  Comment Lines: {summary.get('comment_lines', 0)}")
        report.append(f"  Blank Lines: {summary.get('blank_lines', 0)}")
        report.append("")
        
        complexity = analysis.get('complexity', {})
        report.append("COMPLEXITY:")
        report.append("-" * 60)
        report.append(f"  Average: {complexity.get('average', 0.0):.2f}")
        report.append(f"  Highest: {complexity.get('highest', 0)}")
        report.append(f"  Total: {complexity.get('total', 0)}")
        report.append("")
        
        functions = analysis.get('functions', [])
        if functions:
            report.append("FUNCTIONS:")
            report.append("-" * 60)
            for func in functions:
                report.append(f"  Name: {func['name']}")
                report.append(f"    Complexity: {func['complexity']} ({func['status']})")
                report.append(f"    Lines: {func['lines']}")
                report.append(f"    Parameters: {func['parameters']}")
                report.append(f"    Nesting: {func['nesting_level']}")
                report.append("")
        
        suggestions = analysis.get('suggestions', [])
        if suggestions:
            report.append("REFACTORING SUGGESTIONS:")
            report.append("-" * 60)
            for i, suggestion in enumerate(suggestions, 1):
                report.append(f"{i}. {suggestion}")
            report.append("")
        
        report.append("=" * 60)
        report.append("END OF REPORT")
        report.append("=" * 60)
        
        return '\n'.join(report)