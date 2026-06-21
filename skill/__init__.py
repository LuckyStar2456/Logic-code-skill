"""
Logic-code Skill

Provides code review and transcription capabilities.
- Analyzes code complexity and provides refactoring suggestions
- Transcribes code to logical natural language descriptions
- Supports project-level transcription with mirror directory mapping

Entry points:
- analyze(code: str, context: dict) -> dict - Code complexity analysis
- transcribe_code(code: str, context: dict) -> dict - Single file transcription
- transcribe_project(project_path: str, output_path: str, context: dict) -> dict - Project-level transcription
"""

import ast
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logic_code.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        logger.warning("Failed to parse code with AST, falling back to regex-based calculation")
        return calculate_cyclomatic_complexity_fallback(code)

def calculate_cyclomatic_complexity_fallback(code: str) -> int:
    """Fallback cyclomatic complexity calculation using regex."""
    complexity = 1
    keywords = ['if', 'elif', 'for', 'while', 'case', 'catch']
    
    for line in code.split('\n'):
        stripped = line.strip()
        if stripped.startswith('#') or '//' in stripped:
            continue
        
        for keyword in keywords:
            if re.match(r'\b' + re.escape(keyword) + r'\b', stripped):
                complexity += 1
        
        bool_ops = re.findall(r'\b(and|or)\b', stripped)
        complexity += len(bool_ops)
    
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
    """Count maximum nesting level."""
    max_level = 0
    current_level = 0
    
    for line in code.split('\n'):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        current_level = indent // 4
        
        if current_level > max_level:
            max_level = current_level
    
    return max_level

def calculate_average_complexity(functions: List[Dict[str, Any]]) -> float:
    """Calculate average complexity across functions."""
    if not functions:
        return 0.0
    
    total = sum(f['complexity'] for f in functions)
    return round(total / len(functions), 2)

def generate_suggestions(func_analysis: Dict[str, Any]) -> List[str]:
    """Generate refactoring suggestions based on analysis."""
    suggestions = []
    name = func_analysis['name']
    complexity = func_analysis['complexity']
    nesting = func_analysis['nesting_level']
    params = func_analysis['parameters']
    
    if complexity >= 20:
        suggestions.append(f"'{name}' has high complexity ({complexity}). Consider breaking it into smaller functions.")
    
    if nesting >= 4:
        suggestions.append(f"'{name}' has high nesting level ({nesting}). Consider simplifying control flow.")
    
    if params >= 5:
        suggestions.append(f"'{name}' has many parameters ({params}). Consider using a configuration object.")
    
    if complexity >= 15:
        suggestions.append(f"Consider applying the Single Responsibility Principle to '{name}'.")
    
    return suggestions

def check_code_style(code: str, context: dict = None) -> Dict[str, Any]:
    """Check code style and formatting."""
    results = {
        'issues': [],
        'warnings': [],
        'suggestions': []
    }
    
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        if len(line) > 120:
            results['warnings'].append(f"Line {i}: Line exceeds 120 characters")
        
        if 'TODO' in line or 'FIXME' in line:
            results['issues'].append(f"Line {i}: Contains TODO/FIXME comment")
        
        if 'print(' in line or 'console.log(' in line:
            results['suggestions'].append(f"Line {i}: Consider using proper logging instead of print")
    
    return results

def generate_report(code: str, context: dict = None) -> str:
    """Generate a human-readable report."""
    analysis = analyze(code, context)
    
    if not analysis['success']:
        return f"Analysis failed: {analysis.get('error', 'Unknown error')}"
    
    report = []
    report.append("=" * 60)
    report.append("CODE COMPLEXITY ANALYSIS REPORT")
    report.append("=" * 60)
    report.append("")
    
    summary = analysis['summary']
    report.append(f"Total Lines: {summary['total_lines']}")
    report.append(f"Non-Empty Lines: {summary['non_empty_lines']}")
    report.append(f"Comment Lines: {summary['comment_lines']}")
    report.append(f"Blank Lines: {summary['blank_lines']}")
    report.append("")
    
    complexity = analysis['complexity']
    report.append(f"Average Complexity: {complexity['average']}")
    report.append(f"Highest Complexity: {complexity['highest']}")
    report.append(f"Total Complexity: {complexity['total']}")
    report.append("")
    
    report.append("FUNCTION ANALYSIS:")
    report.append("-" * 60)
    
    for func in analysis['functions']:
        status_color = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢',
            'unknown': '⚪'
        }[func['status']]
        
        report.append(f"{status_color} {func['name']}:")
        report.append(f"  Complexity: {func['complexity']}")
        report.append(f"  Lines: {func['lines']}")
        report.append(f"  Parameters: {func['parameters']}")
        report.append(f"  Nesting: {func['nesting_level']}")
        report.append("")
    
    if analysis['suggestions']:
        report.append("REFACTORING SUGGESTIONS:")
        report.append("-" * 60)
        for i, suggestion in enumerate(analysis['suggestions'], 1):
            report.append(f"{i}. {suggestion}")
        report.append("")
    
    report.append("=" * 60)
    report.append("END OF REPORT")
    report.append("=" * 60)
    
    return '\n'.join(report)

def transcribe_code(code: str, context: dict = None) -> Dict[str, Any]:
    """
    Transcribe code to logical natural language description with intent analysis.
    
    Args:
        code: The source code to transcribe
        context: Optional context dictionary with configuration
    
    Returns:
        Dictionary containing transcription results with intent analysis
    """
    config = context.get('config', {}) if context else {}
    language = config.get('language', 'auto')
    project_context = config.get('project_context', '')
    
    results = {
        'success': False,
        'natural_language': '',
        'detected_language': '',
        'functions': [],
        'intent_summary': '',
        'context_analysis': ''
    }
    
    try:
        detected_lang = detect_language(code)
        results['detected_language'] = detected_lang
        
        natural_lang_parts = []
        functions = extract_functions(code)
        
        all_intents = []
        
        for func in functions:
            func_code = extract_function_code(code, func)
            if func_code:
                func_transcription = transcribe_function(func_code, func, detected_lang)
                func_intent = analyze_function_intent(func_code, func, detected_lang)
                func_context = infer_context_purpose(func_code, func, project_context)
                
                full_transcription = f"{func_context}\n\n{func_intent}\n\n{func_transcription}"
                natural_lang_parts.append(full_transcription)
                results['functions'].append({
                    'name': func,
                    'transcription': func_transcription,
                    'intent': func_intent,
                    'context': func_context
                })
                all_intents.append(func_intent)
        
        if not functions:
            standalone_transcription = transcribe_standalone_code(code, detected_lang)
            standalone_intent = analyze_standalone_intent(code, detected_lang)
            standalone_context = infer_context_purpose(code, 'standalone', project_context)
            full_transcription = f"{standalone_context}\n\n{standalone_intent}\n\n{standalone_transcription}"
            natural_lang_parts.append(full_transcription)
            all_intents.append(standalone_intent)
        
        results['natural_language'] = '\n\n'.join(natural_lang_parts)
        
        results['intent_summary'] = synthesize_intent_summary(all_intents, project_context)
        
        if project_context:
            results['context_analysis'] = analyze_project_context(code, project_context)
        
        results['success'] = True
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}", exc_info=True)
        results['error'] = str(e)
    
    return results

def detect_language(code: str) -> str:
    """Detect the programming language of the code."""
    if re.search(r'\bdef\s+\w+\s*\(', code):
        return 'python'
    elif re.search(r'\bfunction\s+\w+\s*\(', code) or re.search(r'console\.log', code):
        return 'javascript'
    elif re.search(r'\bpublic\s+\w+\s+\w+\s*\(', code) or re.search(r'class\s+\w+\s*\{', code):
        return 'java'
    elif re.search(r'\bfunc\s+\w+\s*\(', code):
        return 'go'
    elif re.search(r'\bvar\s+\w+\s*=', code):
        return 'javascript'
    else:
        return 'python'

def transcribe_line(stripped_line: str, indent: str) -> str:
    """Transcribe a single line of code to natural language."""
    if stripped_line.startswith('#') or stripped_line.startswith('//'):
        return None
    
    if 'if ' in stripped_line or 'elif ' in stripped_line:
        condition = stripped_line.split('if')[1].split(':')[0].strip() if ':' in stripped_line else stripped_line.split('if')[1].strip()
        return f"{indent}如果 {condition}："
    
    elif 'else:' in stripped_line:
        return f"{indent}else："
    
    elif 'for ' in stripped_line:
        loop_content = stripped_line.split('for')[1].split(':')[0].strip() if ':' in stripped_line else stripped_line.split('for')[1].strip()
        return f"{indent}循环 {loop_content}："
    
    elif 'while ' in stripped_line:
        condition = stripped_line.split('while')[1].split(':')[0].strip() if ':' in stripped_line else stripped_line.split('while')[1].strip()
        return f"{indent}当 {condition} 时循环："
    
    elif 'return ' in stripped_line:
        return_val = stripped_line.split('return')[1].strip()
        return f"{indent}返回 {return_val}"
    
    elif '=' in stripped_line and not stripped_line.startswith('def ') and not stripped_line.startswith('var ') and not stripped_line.startswith('let ') and not stripped_line.startswith('const '):
        parts = stripped_line.split('=', 1)
        left = parts[0].strip()
        right = parts[1].strip()
        return f"{indent}将 {right} 赋值给 {left}"
    
    elif stripped_line.startswith('print(') or stripped_line.startswith('console.log('):
        content = stripped_line.replace('print(', '').replace('console.log(', '').replace(')', '').strip()
        return f"{indent}输出 {content}"
    
    else:
        return f"{indent}{stripped_line}"

def transcribe_function(func_code: str, func_name: str, language: str) -> str:
    """Transcribe a single function to natural language."""
    params = extract_parameters(func_code)
    param_str = ', '.join(params) if params else ''
    
    lines = func_code.split('\n')
    body_lines = lines[1:] if len(lines) > 1 else []
    
    result = []
    
    if language == 'python':
        result.append(f"定义一个名为 {func_name} 的函数，接受参数：{param_str}")
    elif language == 'javascript':
        result.append(f"定义一个函数 {func_name}，参数为：{param_str}")
    elif language == 'java':
        result.append(f"定义一个方法 {func_name}，参数为：{param_str}")
    elif language == 'go':
        result.append(f"定义一个函数 {func_name}，参数为：{param_str}")
    else:
        result.append(f"定义函数 {func_name}，参数：{param_str}")
    
    for line in body_lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        current_indent = len(line) - len(stripped)
        indent = '    ' * (current_indent // 4)
        
        transcribed = transcribe_line(stripped, indent)
        if transcribed:
            result.append(transcribed)
    
    return '\n'.join(result)

def extract_parameters(func_code: str) -> List[str]:
    """Extract parameter names from function definition, handling type annotations and defaults."""
    match = re.search(r'\((.*?)\)', func_code)
    if match:
        params = match.group(1).strip()
        if params:
            result = []
            for p in params.split(','):
                p = p.strip()
                if p:
                    p = p.split(':')[0].split('=')[0].strip()
                    p = p.lstrip('*')
                    result.append(p)
            return result
    return []

def transcribe_standalone_code(code: str, language: str) -> str:
    """Transcribe standalone code (not in functions) to natural language."""
    lines = code.split('\n')
    result = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        indent = '    ' * ((len(line) - len(stripped)) // 4)
        
        transcribed = transcribe_line(stripped, indent)
        if transcribed:
            result.append(transcribed)
    
    return '\n'.join(result)

def analyze_function_intent(func_code: str, func_name: str, language: str) -> str:
    """Analyze and describe the intent/purpose of a function."""
    params = extract_parameters(func_code)
    
    comparisons = []
    operations = []
    returns = []
    conditions = []
    
    for line in func_code.split('\n'):
        stripped = line.strip()
        
        if not stripped or stripped.startswith('#') or stripped.startswith('//'):
            continue
        
        if 'if ' in stripped or 'elif ' in stripped:
            cond = stripped.split('if')[-1].split(':')[0].strip() if ':' in stripped else stripped.split('if')[-1].strip()
            if '>' in cond or '<' in cond or '==' in cond or '!=' in cond:
                comparisons.append(cond)
            else:
                conditions.append(cond)
        
        if '+' in stripped and '=' in stripped and not stripped.startswith('def'):
            operations.append("加法运算")
        elif '-' in stripped and '=' in stripped and not stripped.startswith('def'):
            operations.append("减法运算")
        elif '*' in stripped and '=' in stripped and not stripped.startswith('def'):
            operations.append("乘法运算")
        elif '/' in stripped and '=' in stripped and not stripped.startswith('def'):
            operations.append("除法运算")
        
        if 'return' in stripped:
            return_val = stripped.split('return')[-1].strip()
            if return_val:
                returns.append(return_val)
    
    comparisons = list(set(comparisons))
    operations = list(set(operations))
    conditions = list(set(conditions))
    
    intent_parts = []
    
    intent_parts.append(f"在方法 {func_name} 中")
    
    if comparisons:
        comparison_desc = "、".join(comparisons)
        intent_parts.append(f"比较 {comparison_desc}")
    
    if conditions and not comparisons:
        condition_desc = "、".join(conditions)
        intent_parts.append(f"判断条件 {condition_desc}")
    
    if operations:
        op_desc = "、".join(operations)
        if comparisons or conditions:
            intent_parts.append(f"，根据判断结果进行{op_desc}")
        else:
            intent_parts.append(f"进行{op_desc}")
    
    if returns:
        return_desc = "、".join(returns)
        intent_parts.append(f"，返回结果 {return_desc}")
    
    if len(intent_parts) == 1:
        return f"在方法 {func_name} 中执行特定操作并返回结果。"
    
    return "".join(intent_parts) + "。"

def analyze_standalone_intent(code: str, language: str) -> str:
    """Analyze and describe the intent/purpose of standalone code."""
    comparisons = []
    operations = []
    outputs = []
    
    for line in code.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('//'):
            continue
        
        if '>' in stripped or '<' in stripped or '==' in stripped or '!=' in stripped:
            if 'if' in stripped:
                cond = stripped.split('if')[-1].split(':')[0].strip() if ':' in stripped else stripped.split('if')[-1].strip()
                comparisons.append(cond)
        
        if '+' in stripped and '=' in stripped:
            operations.append("加法")
        elif '-' in stripped and '=' in stripped:
            operations.append("减法")
        elif '*' in stripped and '=' in stripped:
            operations.append("乘法")
        elif '/' in stripped and '=' in stripped:
            operations.append("除法")
        
        if 'print' in stripped or 'console.log' in stripped:
            outputs.append("输出信息")
    
    comparisons = list(set(comparisons))
    operations = list(set(operations))
    
    intent_parts = ["此代码段的意图是："]
    
    if comparisons:
        comparison_desc = "、".join(comparisons)
        intent_parts.append(f"比较 {comparison_desc}")
    
    if operations:
        op_desc = "、".join(operations)
        if comparisons:
            intent_parts.append(f"，根据条件执行{op_desc}运算")
        else:
            intent_parts.append(f"执行{op_desc}运算")
    
    if outputs:
        intent_parts.append("，并输出结果")
    
    return "".join(intent_parts) + "。"

def infer_context_purpose(code: str, func_name: str, project_context: str) -> str:
    """Infer the contextual purpose of code based on naming and project context."""
    purpose_clues = []
    
    if 'collision' in func_name.lower() or 'hit' in func_name.lower():
        purpose_clues.append("坐标碰撞检测")
    elif 'distance' in func_name.lower():
        purpose_clues.append("距离计算")
    elif 'intersect' in func_name.lower():
        purpose_clues.append("图形相交判断")
    elif 'overlap' in func_name.lower():
        purpose_clues.append("重叠检测")
    elif 'bounding' in func_name.lower():
        purpose_clues.append("边界框计算")
    elif 'move' in func_name.lower() or 'step' in func_name.lower():
        purpose_clues.append("移动逻辑")
    elif 'calc' in func_name.lower() or 'compute' in func_name.lower():
        purpose_clues.append("数值计算")
    elif 'validate' in func_name.lower() or 'check' in func_name.lower():
        purpose_clues.append("参数验证")
    elif 'convert' in func_name.lower() or 'transform' in func_name.lower():
        purpose_clues.append("数据转换")
    elif 'format' in func_name.lower():
        purpose_clues.append("格式化处理")
    elif 'parse' in func_name.lower():
        purpose_clues.append("解析处理")
    elif 'build' in func_name.lower():
        purpose_clues.append("构建操作")
    elif 'update' in func_name.lower():
        purpose_clues.append("更新操作")
    elif 'process' in func_name.lower():
        purpose_clues.append("处理流程")
    elif 'get' in func_name.lower():
        purpose_clues.append("获取数据")
    elif 'set' in func_name.lower():
        purpose_clues.append("设置数据")
    elif 'create' in func_name.lower():
        purpose_clues.append("创建对象")
    elif 'delete' in func_name.lower():
        purpose_clues.append("删除操作")
    elif 'search' in func_name.lower() or 'find' in func_name.lower():
        purpose_clues.append("搜索查询")
    elif 'sort' in func_name.lower():
        purpose_clues.append("排序处理")
    elif 'filter' in func_name.lower():
        purpose_clues.append("数据过滤")
    elif 'save' in func_name.lower() or 'store' in func_name.lower():
        purpose_clues.append("数据持久化")
    elif 'load' in func_name.lower() or 'fetch' in func_name.lower():
        purpose_clues.append("数据加载")
    elif 'init' in func_name.lower():
        purpose_clues.append("初始化操作")
    elif 'cleanup' in func_name.lower() or 'destroy' in func_name.lower():
        purpose_clues.append("资源清理")
    elif 'error' in func_name.lower() or 'exception' in func_name.lower():
        purpose_clues.append("异常处理")
    elif 'log' in func_name.lower():
        purpose_clues.append("日志记录")
    
    if project_context:
        project_lower = project_context.lower()
        if 'game' in project_lower or 'gaming' in project_lower:
            if not purpose_clues:
                purpose_clues.append("游戏逻辑")
            else:
                purpose_clues = [f"游戏{clue}" for clue in purpose_clues]
        elif 'api' in project_lower or 'server' in project_lower or 'backend' in project_lower:
            if not purpose_clues:
                purpose_clues.append("服务端逻辑")
            else:
                purpose_clues = [f"后端{clue}" for clue in purpose_clues]
        elif 'frontend' in project_lower or 'ui' in project_lower or 'web' in project_lower:
            if not purpose_clues:
                purpose_clues.append("前端逻辑")
            else:
                purpose_clues = [f"前端{clue}" for clue in purpose_clues]
        elif 'database' in project_lower or 'db' in project_lower or 'sql' in project_lower:
            if not purpose_clues:
                purpose_clues.append("数据库操作")
            else:
                purpose_clues = [f"数据库{clue}" for clue in purpose_clues]
        elif 'ml' in project_lower or 'machine' in project_lower or 'learn' in project_lower:
            if not purpose_clues:
                purpose_clues.append("机器学习")
            else:
                purpose_clues = [f"ML{clue}" for clue in purpose_clues]
    
    if purpose_clues:
        return f"【用途推断】此代码可能用于：{'、'.join(purpose_clues)}"
    else:
        return "【用途推断】根据函数命名和上下文，此代码用于执行特定业务逻辑，可能涉及数据处理、条件判断或数值计算等功能"

def synthesize_intent_summary(intents: List[str], project_context: str) -> str:
    """Synthesize a summary of all intents."""
    if not intents:
        return ""
    
    summary_parts = ["## 意图汇总\n\n"]
    
    for i, intent in enumerate(intents, 1):
        summary_parts.append(f"{i}. {intent}")
    
    if project_context:
        summary_parts.append(f"\n根据项目上下文「{project_context}」，这些代码共同构成了该项目的核心业务逻辑。")
    
    return '\n'.join(summary_parts)

def analyze_project_context(code: str, project_context: str) -> str:
    """Analyze how the code fits into the project context."""
    context_analysis = []
    project_lower = project_context.lower()
    code_lower = code.lower()
    
    context_analysis.append(f"项目上下文：{project_context}")
    context_analysis.append("")
    
    if 'game' in project_lower or 'gaming' in project_lower:
        context_analysis.append("结合游戏项目上下文分析：")
        if 'collision' in code_lower or 'hit' in code_lower:
            context_analysis.append("- 此代码可能用于碰撞检测系统")
        if 'move' in code_lower or 'step' in code_lower:
            context_analysis.append("- 此代码可能用于角色移动控制")
        if 'score' in code_lower or 'point' in code_lower:
            context_analysis.append("- 此代码可能用于计分系统")
        if 'level' in code_lower:
            context_analysis.append("- 此代码可能用于关卡系统")
        if 'enemy' in code_lower or 'monster' in code_lower:
            context_analysis.append("- 此代码可能用于敌人AI系统")
    
    elif 'api' in project_lower or 'server' in project_lower or 'backend' in project_lower:
        context_analysis.append("结合API服务上下文分析：")
        if 'validate' in code_lower:
            context_analysis.append("- 此代码可能用于请求参数验证")
        if 'response' in code_lower or 'return' in code_lower:
            context_analysis.append("- 此代码可能用于响应处理")
        if 'auth' in code_lower or 'login' in code_lower or 'token' in code_lower:
            context_analysis.append("- 此代码可能用于用户认证系统")
        if 'db' in code_lower or 'database' in code_lower:
            context_analysis.append("- 此代码可能用于数据库操作")
    
    elif 'frontend' in project_lower or 'ui' in project_lower or 'web' in project_lower:
        context_analysis.append("结合前端项目上下文分析：")
        if 'render' in code_lower or 'display' in code_lower:
            context_analysis.append("- 此代码可能用于UI渲染")
        if 'click' in code_lower or 'event' in code_lower:
            context_analysis.append("- 此代码可能用于事件处理")
        if 'state' in code_lower:
            context_analysis.append("- 此代码可能用于状态管理")
    
    elif 'database' in project_lower or 'db' in project_lower or 'sql' in project_lower:
        context_analysis.append("结合数据库项目上下文分析：")
        if 'query' in code_lower or 'select' in code_lower:
            context_analysis.append("- 此代码可能用于数据查询")
        if 'insert' in code_lower or 'update' in code_lower:
            context_analysis.append("- 此代码可能用于数据更新")
        if 'index' in code_lower:
            context_analysis.append("- 此代码可能用于索引优化")
    
    elif 'ml' in project_lower or 'machine' in project_lower or 'learn' in project_lower:
        context_analysis.append("结合机器学习项目上下文分析：")
        if 'train' in code_lower:
            context_analysis.append("- 此代码可能用于模型训练")
        if 'predict' in code_lower or 'infer' in code_lower:
            context_analysis.append("- 此代码可能用于预测推理")
        if 'loss' in code_lower or 'accuracy' in code_lower:
            context_analysis.append("- 此代码可能用于指标计算")
    
    else:
        context_analysis.append("结合通用项目上下文分析：")
        if 'function' in code_lower or 'method' in code_lower:
            context_analysis.append("- 此代码包含函数/方法定义")
        if 'if ' in code_lower or 'else' in code_lower:
            context_analysis.append("- 此代码包含条件判断逻辑")
        if 'for ' in code_lower or 'while' in code_lower:
            context_analysis.append("- 此代码包含循环逻辑")
    
    return '\n'.join(context_analysis)

def process_code(code: str, context: dict = None) -> Dict[str, Any]:
    """
    Main entry point that handles both review and transcription modes.
    
    Args:
        code: The source code to process
        context: Optional context dictionary with configuration
    
    Returns:
        Dictionary containing processing results
    """
    config = context.get('config', {}) if context else {}
    mode = config.get('mode', 'review')
    
    if mode == 'transcribe':
        return transcribe_code(code, context)
    else:
        return analyze(code, context)

CODE_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs',
    '.cpp', '.c', '.h', '.hpp', '.cs', '.rb', '.php', '.swift',
    '.kt', '.scala', '.r', '.lua', '.pl', '.sh', '.bash'
}

IGNORED_DIRS = {
    'node_modules', '.git', '__pycache__', 'venv', '.venv',
    'env', '.env', 'build', 'dist', '.idea', '.vscode',
    'bin', 'obj', 'target', '.cache', '.pytest_cache'
}

def transcribe_project(project_path: str, output_base_path: str = None, context: dict = None) -> Dict[str, Any]:
    """
    Transcribe entire project to logical natural language.
    
    Args:
        project_path: Path to the project directory
        output_base_path: Base path for output (default: project_path/logic_code/)
        context: Optional context dictionary with configuration
    
    Returns:
        Dictionary containing transcription results
    """
    logger.info(f"Starting project transcription for: {project_path}")
    
    results = {
        'success': False,
        'project_path': project_path,
        'output_path': '',
        'total_files': 0,
        'transcribed_files': 0,
        'failed_files': 0,
        'files': [],
        'error_details': []
    }
    
    try:
        project_path = Path(project_path)
        
        if not project_path.exists():
            error_msg = f"项目路径不存在: {project_path}"
            logger.error(error_msg)
            results['error'] = error_msg
            results['error_details'].append({'stage': 'validation', 'message': error_msg})
            return results
        
        if not project_path.is_dir():
            error_msg = f"项目路径不是目录: {project_path}"
            logger.error(error_msg)
            results['error'] = error_msg
            results['error_details'].append({'stage': 'validation', 'message': error_msg})
            return results
        
        if output_base_path is None:
            output_base_path = project_path / 'logic_code'
        else:
            output_base_path = Path(output_base_path)
        
        logger.info(f"Output directory: {output_base_path}")
        
        try:
            project_structure = scan_project_structure(project_path)
            results['total_files'] = project_structure['total_code_files']
            logger.info(f"Found {project_structure['total_code_files']} code files in {project_structure['total_directories']} directories")
        except Exception as e:
            error_msg = f"扫描项目结构失败: {str(e)}"
            logger.error(error_msg)
            results['error'] = error_msg
            results['error_details'].append({'stage': 'scan', 'message': error_msg})
            return results
        
        try:
            mirror_structure = create_mirror_directory(project_structure, output_base_path)
            logger.info(f"Created {mirror_structure['total_created']} mirror directories")
        except Exception as e:
            error_msg = f"创建镜像目录失败: {str(e)}"
            logger.error(error_msg)
            results['error'] = error_msg
            results['error_details'].append({'stage': 'directory_create', 'message': error_msg})
            return results
        
        for rel_path in project_structure['code_files']:
            source_file = project_path / rel_path
            mirror_file = output_base_path / rel_path.with_suffix('.md')
            
            try:
                logger.debug(f"Processing file: {rel_path}")
                
                try:
                    with open(source_file, 'r', encoding='utf-8') as f:
                        code_content = f.read()
                except UnicodeDecodeError:
                    with open(source_file, 'r', encoding='latin-1') as f:
                        code_content = f.read()
                
                transcribe_result = transcribe_code(code_content, context)
                
                if transcribe_result['success']:
                    doc_content = generate_transcription_document(source_file, transcribe_result)
                    
                    with open(mirror_file, 'w', encoding='utf-8') as f:
                        f.write(doc_content)
                    
                    results['transcribed_files'] += 1
                    results['files'].append({
                        'source': str(rel_path),
                        'output': str(mirror_file),
                        'status': 'success',
                        'language': transcribe_result['detected_language']
                    })
                    logger.debug(f"Successfully transcribed: {rel_path}")
                else:
                    error_msg = transcribe_result.get('error', '未知错误')
                    logger.warning(f"Transcription failed for {rel_path}: {error_msg}")
                    results['failed_files'] += 1
                    results['files'].append({
                        'source': str(rel_path),
                        'output': str(mirror_file),
                        'status': 'failed',
                        'error': error_msg
                    })
            
            except FileNotFoundError:
                error_msg = f"文件不存在: {source_file}"
                logger.warning(error_msg)
                results['failed_files'] += 1
                results['files'].append({
                    'source': str(rel_path),
                    'output': str(mirror_file),
                    'status': 'error',
                    'error': error_msg,
                    'error_type': 'FileNotFound'
                })
            except PermissionError:
                error_msg = f"权限不足，无法访问文件: {source_file}"
                logger.warning(error_msg)
                results['failed_files'] += 1
                results['files'].append({
                    'source': str(rel_path),
                    'output': str(mirror_file),
                    'status': 'error',
                    'error': error_msg,
                    'error_type': 'PermissionError'
                })
            except Exception as e:
                error_msg = f"处理文件时发生错误: {str(e)}"
                logger.warning(f"Error processing {rel_path}: {error_msg}")
                results['failed_files'] += 1
                results['files'].append({
                    'source': str(rel_path),
                    'output': str(mirror_file),
                    'status': 'error',
                    'error': error_msg,
                    'error_type': 'Unknown'
                })
        
        results['output_path'] = str(output_base_path)
        results['success'] = True
        logger.info(f"Project transcription completed: {results['transcribed_files']}/{results['total_files']} files succeeded")
    
    except Exception as e:
        error_msg = f"项目转写过程中发生严重错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        results['error'] = error_msg
        results['error_details'].append({'stage': 'main', 'message': error_msg, 'exception': str(type(e).__name__)})
    
    return results

def scan_project_structure(project_path: Path) -> Dict[str, Any]:
    """
    Scan project directory structure and collect code files.
    
    Args:
        project_path: Path to the project directory
    
    Returns:
        Dictionary containing project structure information
    """
    structure = {
        'directories': [],
        'code_files': [],
        'total_code_files': 0,
        'total_directories': 0
    }
    
    for root, dirs, files in os.walk(project_path):
        root_path = Path(root)
        
        # 过滤忽略的目录
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith('.')]
        
        # 记录目录
        rel_dir = root_path.relative_to(project_path)
        if str(rel_dir) != '.':
            structure['directories'].append(rel_dir)
            structure['total_directories'] += 1
        
        # 收集代码文件
        for file in files:
            file_path = root_path / file
            
            # 检查文件扩展名
            if file_path.suffix.lower() in CODE_EXTENSIONS:
                rel_path = file_path.relative_to(project_path)
                structure['code_files'].append(rel_path)
                structure['total_code_files'] += 1
    
    return structure

def create_mirror_directory(project_structure: Dict, output_base_path: Path) -> Dict[str, Any]:
    """
    Create mirror directory structure for the project.
    
    Args:
        project_structure: Project structure information
        output_base_path: Base path for output directory
    
    Returns:
        Dictionary containing created directories information
    """
    created_dirs = []
    
    for dir_path in project_structure['directories']:
        full_dir_path = output_base_path / dir_path
        full_dir_path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(full_dir_path))
    
    return {
        'success': True,
        'created_directories': created_dirs,
        'total_created': len(created_dirs)
    }

def generate_transcription_document(source_file: Path, transcribe_result: Dict[str, Any]) -> str:
    """
    Generate formatted transcription document.
    
    Args:
        source_file: Original source file path
        transcribe_result: Transcription result dictionary
    
    Returns:
        Formatted transcription document
    """
    doc = []
    
    # 文档标题
    doc.append(f"# {source_file.name} - 自然语言逻辑转写\n")
    
    # 元信息
    doc.append(f"**原始文件**: `{source_file}`\n")
    doc.append(f"**检测语言**: {transcribe_result.get('detected_language', 'unknown')}\n")
    doc.append(f"**转写时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    doc.append("\n---\n\n")
    
    # 自然语言转写内容
    doc.append("## 代码逻辑转写\n\n")
    doc.append(transcribe_result.get('natural_language', ''))
    doc.append("\n\n")
    
    # 函数列表（如果有）
    if transcribe_result.get('functions'):
        doc.append("## 函数列表\n\n")
        for func in transcribe_result['functions']:
            doc.append(f"### {func['name']}\n")
            doc.append(f"{func['transcription']}\n\n")
    
    return ''.join(doc)
