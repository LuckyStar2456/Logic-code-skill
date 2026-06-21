"""
Code Analyzer Module

Provides code complexity analysis and refactoring suggestions.
"""

import ast
import re
from typing import Dict, Any, List

def analyze(code: str, context: dict = None) -> Dict[str, Any]:
    """
    Main entry point for the code complexity analyzer.
    
    Args:
        code: The source code to analyze
        context: Optional context dictionary with configuration
    
    Returns:
        Dictionary containing analysis results
    """
    config = context.get('config', {}) if context else {}
    min_threshold = config.get('min_complexity_threshold', 10)
    enable_suggestions = config.get('enable_suggestions', True)
    
    results = {
        'summary': {},
        'functions': [],
        'complexity': {},
        'suggestions': []
    }
    
    try:
        lines = code.split('\n')
        results['summary']['total_lines'] = len(lines)
        results['summary']['non_empty_lines'] = len([l for l in lines if l.strip()])
        results['summary']['comment_lines'] = count_comments(code)
        results['summary']['blank_lines'] = len([l for l in lines if l.strip() == ''])
        
        functions = extract_functions(code)
        results['functions'] = []
        
        for func in functions:
            func_analysis = analyze_function(code, func)
            results['functions'].append(func_analysis)
            
            if func_analysis['complexity'] >= min_threshold:
                results['suggestions'].extend(generate_suggestions(func_analysis))
        
        results['complexity']['average'] = calculate_average_complexity(results['functions'])
        results['complexity']['highest'] = max(
            [f['complexity'] for f in results['functions']],
            default=0
        )
        results['complexity']['total'] = sum(f['complexity'] for f in results['functions'])
        
        results['success'] = True
        
    except Exception as e:
        results['success'] = False
        results['error'] = str(e)
    
    return results

def count_comments(code: str) -> int:
    """Count comment lines in the code."""
    lines = code.split('\n')
    comment_count = 0
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            comment_count += 1
        elif '//' in stripped:
            comment_count += 1
    
    return comment_count

def extract_functions(code: str) -> List[str]:
    """Extract function/method names from code."""
    function_patterns = [
        r'\bdef\s+(\w+)\s*\(',
        r'\bfunction\s+(\w+)\s*\(',
        r'\bclass\s+(\w+)',
        r'\bpublic\s+\w+\s+(\w+)\s*\(',
        r'\bprivate\s+\w+\s+(\w+)\s*\(',
        r'\bprotected\s+\w+\s+(\w+)\s*\('
    ]
    
    functions = set()
    
    for pattern in function_patterns:
        matches = re.findall(pattern, code)
        functions.update(matches)
    
    return list(functions)

def analyze_function(code: str, func_name: str) -> Dict[str, Any]:
    """Analyze a specific function's complexity."""
    try:
        func_code = extract_function_code(code, func_name)
        
        if func_code:
            complexity = calculate_cyclomatic_complexity(func_code)
            line_count = len(func_code.split('\n'))
            params = count_parameters(func_code)
            nesting = count_nesting(func_code)
            
            return {
                'name': func_name,
                'complexity': complexity,
                'lines': line_count,
                'parameters': params,
                'nesting_level': nesting,
                'status': 'high' if complexity >= 15 else 'medium' if complexity >= 10 else 'low'
            }
        else:
            return {
                'name': func_name,
                'complexity': 0,
                'lines': 0,
                'parameters': 0,
                'nesting_level': 0,
                'status': 'unknown'
            }
    except Exception:
        return {
            'name': func_name,
            'complexity': 0,
            'lines': 0,
            'parameters': 0,
            'nesting_level': 0,
            'status': 'error'
        }

def extract_function_code(code: str, func_name: str) -> str:
    """Extract the code of a specific function."""
    lines = code.split('\n')
    in_function = False
    indent_level = 0
    func_lines = []
    
    for line in lines:
        if re.match(r'\bdef\s+' + re.escape(func_name) + r'\s*\(', line):
            in_function = True
            indent_level = len(line) - len(line.lstrip())
            func_lines.append(line)
        elif in_function:
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and line.strip() != '':
                break
            func_lines.append(line)
    
    return '\n'.join(func_lines)

def calculate_cyclomatic_complexity(code: str) -> int:
    """Calculate cyclomatic complexity using AST for Python code."""
    try:
        tree = ast.parse(code)
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
    except SyntaxError:
        return calculate_cyclomatic_complexity_fallback(code)

def calculate_cyclomatic_complexity_fallback(code: str) -> int:
    """Fallback cyclomatic complexity calculation using regex."""
    complexity = 1
    keywords = ['if', 'elif', 'for', 'while', 'case', 'catch']
    
    for line in code.split('\n'):
        stripped = line.strip()
        for keyword in keywords:
            if stripped.startswith(keyword + ' ') or stripped.startswith(keyword + '('):
                complexity += 1
                break
        
        if '&&' in stripped or '||' in stripped:
            complexity += stripped.count('&&') + stripped.count('||')
    
    return complexity

def count_parameters(func_code: str) -> int:
    """Count the number of parameters in a function."""
    match = re.search(r'\((.*?)\)', func_code)
    if match:
        params = match.group(1).strip()
        if params:
            return len([p.strip() for p in params.split(',') if p.strip()])
    return 0

def count_nesting(code: str) -> int:
    """Count the maximum nesting level in code."""
    lines = code.split('\n')
    max_nesting = 0
    current_nesting = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        indent = len(line) - len(stripped)
        current_nesting = indent // 4
        
        if current_nesting > max_nesting:
            max_nesting = current_nesting
    
    return max_nesting

def calculate_average_complexity(functions: List[Dict[str, Any]]) -> float:
    """Calculate average cyclomatic complexity."""
    if not functions:
        return 0.0
    return sum(f['complexity'] for f in functions) / len(functions)

def generate_suggestions(func_analysis: Dict[str, Any]) -> List[str]:
    """Generate refactoring suggestions based on function analysis."""
    suggestions = []
    complexity = func_analysis['complexity']
    params = func_analysis['parameters']
    nesting = func_analysis['nesting_level']
    
    if complexity >= 15:
        suggestions.append(f"函数 '{func_analysis['name']}' 复杂度较高({complexity})，建议拆分为多个小函数")
    
    if params > 5:
        suggestions.append(f"函数 '{func_analysis['name']}' 参数较多({params})，建议使用对象封装")
    
    if nesting > 3:
        suggestions.append(f"函数 '{func_analysis['name']}' 嵌套深度较大({nesting})，建议简化控制流")
    
    return suggestions