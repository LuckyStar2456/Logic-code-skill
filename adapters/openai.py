"""
OpenAI Plugin Adapter

Provides OpenAI-compatible plugin interface for the Logic-code skill.
"""

from typing import Dict, Any
from core import analyze, transcribe_code

class OpenAIAdapter:
    """
    Adapter for OpenAI Plugin API.
    
    Provides endpoints compatible with OpenAI's plugin system.
    """
    
    @staticmethod
    def get_plugin_manifest() -> Dict[str, Any]:
        """
        Get the OpenAI plugin manifest.
        
        Returns:
            Plugin manifest in OpenAI's required format
        """
        return {
            "schema_version": "v1",
            "name_for_human": "Logic Code Analyzer",
            "name_for_model": "logic_code_analyzer",
            "description_for_human": "Analyze code complexity and transcribe code to natural language",
            "description_for_model": "A tool for analyzing code complexity and transcribing code to natural language descriptions with intent analysis. Useful when you need to understand code logic, identify refactoring opportunities, or explain code to non-technical stakeholders.",
            "auth": {
                "type": "none"
            },
            "api": {
                "type": "openapi",
                "url": "/openapi.json"
            },
            "logo_url": "https://example.com/logo.png",
            "contact_email": "support@example.com",
            "legal_info_url": "https://example.com/legal"
        }
    
    @staticmethod
    def get_openapi_spec() -> Dict[str, Any]:
        """
        Get the OpenAPI specification for the plugin.
        
        Returns:
            OpenAPI 3.0 specification
        """
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Logic Code Analyzer API",
                "version": "1.0.0",
                "description": "API for code analysis and transcription"
            },
            "paths": {
                "/analyze": {
                    "post": {
                        "summary": "Analyze code complexity",
                        "operationId": "analyzeCode",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "code": {
                                                "type": "string",
                                                "description": "Source code to analyze"
                                            },
                                            "min_complexity_threshold": {
                                                "type": "integer",
                                                "default": 10,
                                                "description": "Minimum complexity threshold for warnings"
                                            }
                                        },
                                        "required": ["code"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Analysis results",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "summary": {"type": "object"},
                                                "functions": {"type": "array"},
                                                "complexity": {"type": "object"},
                                                "suggestions": {"type": "array"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/transcribe": {
                    "post": {
                        "summary": "Transcribe code to natural language",
                        "operationId": "transcribeCode",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "code": {
                                                "type": "string",
                                                "description": "Source code to transcribe"
                                            },
                                            "project_context": {
                                                "type": "string",
                                                "default": "",
                                                "description": "Project context for better intent analysis"
                                            }
                                        },
                                        "required": ["code"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Transcription results",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "natural_language": {"type": "string"},
                                                "detected_language": {"type": "string"},
                                                "functions": {"type": "array"},
                                                "intent_summary": {"type": "string"},
                                                "context_analysis": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    @staticmethod
    def analyze_endpoint(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle analyze endpoint request.
        
        Args:
            data: Request data containing 'code' and optional 'min_complexity_threshold'
        
        Returns:
            Analysis results
        """
        code = data.get('code', '')
        threshold = data.get('min_complexity_threshold', 10)
        
        context = {
            'config': {
                'min_complexity_threshold': threshold
            }
        }
        
        return analyze(code, context)
    
    @staticmethod
    def transcribe_endpoint(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle transcribe endpoint request.
        
        Args:
            data: Request data containing 'code' and optional 'project_context'
        
        Returns:
            Transcription results
        """
        code = data.get('code', '')
        project_context = data.get('project_context', '')
        
        context = {
            'config': {
                'project_context': project_context
            }
        }
        
        return transcribe_code(code, context)