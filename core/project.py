"""
Project Transcription Module

Provides project-level code transcription with mirror directory mapping.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from .transcriber import transcribe_code

SUPPORTED_EXTENSIONS = (
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs',
    '.c', '.cpp', '.h', '.hpp', '.cs', '.rb', '.php', '.swift',
    '.kt', '.scala', '.r', '.lua', '.pl', '.sh', '.bash'
)

IGNORED_DIRS = (
    'node_modules', '.git', '__pycache__', 'venv', '.venv', 'env', '.env',
    'build', 'dist', 'target', '.idea', '.vscode', 'bin', 'obj', '.cache',
    '.pytest_cache'
)

def transcribe_project(project_path: str, output_base_path: str = None, context: dict = None) -> Dict[str, Any]:
    """
    Transcribe all code files in a project to natural language.
    
    Creates a mirror directory structure with transcribed files.
    
    Args:
        project_path: Path to the project directory
        output_base_path: Base path for output (default: project_path/logic_code)
        context: Optional context dictionary with configuration
    
    Returns:
        Dictionary containing transcription results
    """
    if output_base_path is None:
        output_base_path = os.path.join(project_path, 'logic_code')
    
    results = {
        'success': False,
        'project_path': project_path,
        'output_path': output_base_path,
        'total_files': 0,
        'transcribed_files': 0,
        'failed_files': 0,
        'files': [],
        'error_details': []
    }
    
    try:
        os.makedirs(output_base_path, exist_ok=True)
        
        all_files = []
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            
            for file in files:
                if file.endswith(SUPPORTED_EXTENSIONS):
                    all_files.append(os.path.join(root, file))
        
        results['total_files'] = len(all_files)
        
        for src_path in all_files:
            rel_path = os.path.relpath(src_path, project_path)
            dest_path = os.path.join(output_base_path, rel_path)
            dest_path = os.path.splitext(dest_path)[0] + '.md'
            
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            try:
                with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                
                if code.strip():
                    result = transcribe_code(code, context)
                    
                    if result['success']:
                        content = generate_markdown(src_path, result)
                        with open(dest_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        results['transcribed_files'] += 1
                        results['files'].append({
                            'source': src_path,
                            'output': dest_path,
                            'status': 'success',
                            'language': result.get('detected_language', 'unknown')
                        })
                    else:
                        results['failed_files'] += 1
                        results['files'].append({
                            'source': src_path,
                            'output': dest_path,
                            'status': 'failed',
                            'language': 'unknown',
                            'error': result.get('error', 'Unknown error')
                        })
                        results['error_details'].append({
                            'file': src_path,
                            'error': result.get('error', 'Unknown error')
                        })
            
            except Exception as e:
                results['failed_files'] += 1
                results['files'].append({
                    'source': src_path,
                    'output': dest_path,
                    'status': 'failed',
                    'language': 'unknown',
                    'error': str(e)
                })
                results['error_details'].append({
                    'file': src_path,
                    'error': str(e)
                })
        
        results['success'] = True
        
    except Exception as e:
        results['error'] = str(e)
    
    return results

def generate_markdown(source_path: str, result: Dict[str, Any]) -> str:
    """Generate markdown content for transcribed code."""
    parts = []
    
    parts.append(f"# {os.path.basename(source_path)}")
    parts.append("")
    parts.append(f"**原始文件:** `{source_path}`")
    parts.append(f"**检测语言:** {result.get('detected_language', 'unknown')}")
    parts.append(f"**转写时间:** {result.get('transcribe_time', 'N/A')}")
    parts.append("")
    parts.append("---")
    parts.append("")
    
    if result.get('natural_language'):
        parts.append("## 自然语言描述")
        parts.append("")
        parts.append(result['natural_language'])
        parts.append("")
    
    if result.get('intent_summary'):
        parts.append(result['intent_summary'])
        parts.append("")
    
    if result.get('context_analysis'):
        parts.append("## 上下文分析")
        parts.append("")
        parts.append(result['context_analysis'])
        parts.append("")
    
    if result.get('functions'):
        parts.append("## 函数详情")
        parts.append("")
        
        for func in result['functions']:
            parts.append(f"### {func['name']}")
            parts.append("")
            if 'context' in func:
                parts.append(f"- **用途:** {func['context']}")
            if 'intent' in func:
                parts.append(f"- **意图:** {func['intent']}")
            parts.append("")
    
    parts.append("---")
    parts.append("*Generated by Logic-code Skill*")
    
    return '\n'.join(parts)