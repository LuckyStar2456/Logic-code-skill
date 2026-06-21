"""
Code Transcriber Module

Provides code-to-natural-language transcription with intent analysis.
"""

import re
from typing import Dict, Any, List

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

def extract_functions(code: str) -> List[str]:
    """Extract function/method names from code."""
    function_patterns = [
        r'\bdef\s+(\w+)\s*\(',
        r'\bfunction\s+(\w+)\s*\(',
        r'\bpublic\s+\w+\s+(\w+)\s*\(',
        r'\bprivate\s+\w+\s+(\w+)\s*\(',
        r'\bprotected\s+\w+\s+(\w+)\s*\('
    ]
    
    functions = set()
    
    for pattern in function_patterns:
        matches = re.findall(pattern, code)
        functions.update(matches)
    
    return list(functions)

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
    """Extract parameter names from function definition."""
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
    """Transcribe standalone code to natural language."""
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