"""
Platform Adapters

Provides adapters for various AI agent platforms:
- Trae
- LangChain
- OpenAI Plugins
- Claude Code
- Cursor
- Codex

All adapters use the core module for actual processing.
"""

from .trae import TraeAdapter
from .langchain import LangChainAdapter
from .openai import OpenAIAdapter
from .claude import ClaudeAdapter
from .cursor import CursorAdapter
from .codex import CodexAdapter

__all__ = [
    'TraeAdapter',
    'LangChainAdapter',
    'OpenAIAdapter',
    'ClaudeAdapter',
    'CursorAdapter',
    'CodexAdapter'
]