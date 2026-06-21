"""
Logic-code Skill

A code analysis and transcription tool that supports multiple AI agent platforms.

Core Features:
- Code complexity analysis
- Code-to-natural-language transcription with intent analysis
- Project-level transcription with mirror directory mapping

Supported Platforms:
- Trae
- LangChain
- OpenAI Plugins
- Claude Code
- Cursor
- Codex/GitHub Copilot

Usage:
    from logic_code import analyze, transcribe_code, transcribe_project
    from logic_code.adapters import TraeAdapter, LangChainAdapter, OpenAIAdapter
    
    # Basic usage
    result = analyze(code)
    transcription = transcribe_code(code, {'config': {'project_context': 'game engine'}})
"""

from core import analyze, transcribe_code, transcribe_project

__all__ = ['analyze', 'transcribe_code', 'transcribe_project']
__version__ = '1.0.0'