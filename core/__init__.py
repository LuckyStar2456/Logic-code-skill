"""
Logic-code Core Module

Provides code review and transcription capabilities.
- Analyzes code complexity and provides refactoring suggestions
- Transcribes code to logical natural language descriptions
- Supports project-level transcription with mirror directory mapping

This module is platform-agnostic and can be used with:
- Trae
- LangChain
- OpenAI Plugins
- Custom API services
- And more...
"""

from .analyzer import analyze
from .transcriber import transcribe_code
from .project import transcribe_project

__all__ = ['analyze', 'transcribe_code', 'transcribe_project']
__version__ = '1.0.0'