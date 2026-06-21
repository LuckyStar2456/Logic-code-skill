# Logic-code Skill

一个强大的代码审查和转写技能，支持多个 AI 智能体平台。

## 功能特性

### 1. 代码审查
- 📊 **圈复杂度分析**：使用 AST 精确计算代码复杂度
- 🔍 **函数分析**：详细的函数/方法级别分析
- 📝 **代码风格检查**：识别风格问题和改进建议
- 💡 **重构建议**：自动生成代码改进建议
- 📋 **报告生成**：生成易读的分析报告

### 2. 代码转写（带意图分析）
- 🔄 **代码转自然语言**：将代码转换为逻辑化的自然语言描述
- 🎯 **意图识别**：分析代码的业务意图和目的
- 🌐 **多语言支持**：支持 Python、JavaScript、Java、Go 等多种语言
- 📖 **上下文理解**：结合项目上下文推断代码用途

### 3. 项目级转写（镜像映射）
- 🗂️ **目录扫描**：自动扫描项目目录结构
- 🪞 **镜像创建**：创建与项目结构对称的镜像目录
- 📦 **批量转写**：批量转写所有代码文件
- 📄 **Markdown输出**：生成格式化的 Markdown 文档

## 支持的平台

| 平台 | 状态 | 说明 |
|------|------|------|
| ✅ **Trae** | 原生支持 | 通过 `.trae/skills/` 目录集成 |
| ✅ **LangChain** | 原生支持 | 提供 LangChain Tools |
| ✅ **OpenAI 插件** | 原生支持 | 提供插件 manifest 和 API |
| ✅ **Claude Code** | 原生支持 | 提供 Claude 兼容接口 |
| ✅ **Cursor** | 原生支持 | 提供 Cursor IDE 兼容接口 |
| ✅ **Codex/Copilot** | 原生支持 | 提供函数调用格式 |
| ✅ **REST API** | 原生支持 | 提供 FastAPI 服务 |

## 项目结构

```
logic-code-skill/
├── core/                    # 核心模块（纯 Python）
│   ├── __init__.py          # 核心入口
│   ├── analyzer.py          # 代码分析器
│   ├── transcriber.py       # 代码转写器
│   └── project.py           # 项目级转写
├── adapters/                # 平台适配器
│   ├── __init__.py          # 适配器入口
│   ├── trae.py              # Trae 适配器
│   ├── langchain.py         # LangChain 适配器
│   ├── openai.py            # OpenAI 插件适配器
│   ├── claude.py            # Claude 适配器
│   ├── cursor.py            # Cursor 适配器
│   └── codex.py             # Codex 适配器
├── api/                     # REST API 服务
│   ├── __init__.py          # API 入口
│   └── main.py              # FastAPI 应用
├── .trae/                   # Trae 技能配置
│   └── skills/
│       └── Logic-code/
│           └── SKILL.md
├── skill/                   # 兼容旧版的技能代码
│   ├── __init__.py
│   └── skill.json
├── scripts/                 # 辅助脚本
│   ├── install_skill.py
│   └── package_skill.py
├── examples/                # 使用示例
│   └── example_usage.py
├── README.md
└── package.json
```

## 安装

### 方法 1：手动安装

1. 复制 `skill/` 文件夹到项目的 `.trae/skills/` 目录
2. 重命名为 `Logic-code`
3. 重启或重新加载技能

### 方法 2：使用安装脚本

```bash
python scripts/install_skill.py /path/to/your/project
```

### 方法 3：打包分发

```bash
python scripts/package_skill.py
```

将在 `dist/` 目录创建 ZIP 包。

## 使用方法

### Python API

```python
from skill import analyze, transcribe_code, transcribe_project, generate_report

# 代码审查
code = """
def complex_function(x, y, z):
    if x > y:
        if z < 10:
            return x + y
        else:
            return x - y
    else:
        return z * 2
"""

result = analyze(code)
print(f"平均复杂度: {result['complexity']['average']}")
print(f"最高复杂度: {result['complexity']['highest']}")

# 代码转写（带意图分析）
context = {
    'config': {
        'language': 'auto',
        'project_context': '2D游戏引擎碰撞检测系统'
    }
}
transcription = transcribe_code(code, context)
print(transcription['natural_language'])
# 输出：
# 【用途推断】此代码可能用于：坐标碰撞检测
# 
# 在方法 complex_function 中比较 x > y、z < 10，返回结果 x + y、x - y、z * 2。
# 
# 定义一个名为 complex_function 的函数，接受参数：x, y, z
#     如果 x > y：
#         如果 z < 10：
#             返回 x + y
#         else：
#             返回 x - y
#     else：
#         返回 z * 2

# 项目级转写
project_result = transcribe_project('/path/to/project')
print(f"成功转写: {project_result['transcribed_files']}/{project_result['total_files']} 文件")
```

### 配置选项

```python
context = {
    'config': {
        'min_complexity_threshold': 10,  # 复杂度警告阈值
        'enable_suggestions': True,       # 启用重构建议
        'language': 'auto',               # 目标语言（auto/python/javascript/java/go）
        'mode': 'review',                 # 操作模式（review/transcribe）
        'project_context': '游戏引擎'      # 项目上下文，用于意图分析
    }
}

result = analyze(code, context)
```

## API 参考

### analyze(code, context)

代码复杂度分析主入口。

**返回值：**
```python
{
    'summary': {
        'total_lines': int,
        'non_empty_lines': int,
        'comment_lines': int,
        'blank_lines': int
    },
    'functions': [{
        'name': str,
        'complexity': int,
        'lines': int,
        'parameters': int,
        'nesting_level': int,
        'status': 'high' | 'medium' | 'low' | 'unknown'
    }],
    'complexity': {
        'average': float,
        'highest': int,
        'total': int
    },
    'suggestions': [str],
    'success': bool
}
```

### transcribe_code(code, context)

将代码转写为自然语言描述，包含意图分析和上下文推断。

**参数：**
- `code` (str): 要转写的源代码
- `context` (dict, optional): 配置选项，包括：
  - `language`: 目标语言（auto/python/javascript/java/go）
  - `project_context`: 项目上下文描述，用于意图分析

**返回值：**
```python
{
    'success': bool,
    'natural_language': str,      # 完整的自然语言描述（包含意图、用途、转写）
    'detected_language': str,     # 检测到的编程语言
    'functions': [{
        'name': str,
        'transcription': str,     # 函数代码转写
        'intent': str,            # 函数意图描述
        'context': str            # 函数用途推断
    }],
    'intent_summary': str,        # 意图汇总
    'context_analysis': str       # 项目上下文分析
}
```

**示例输出：**
```
【用途推断】此代码可能用于：坐标碰撞检测

在方法 check_collision 中比较 x > y、z < 10，返回结果 x + y、x - y、z * 2。

定义一个名为 check_collision 的函数，接受参数：x, y, z
    如果 x > y：
        如果 z < 10：
            返回 x + y
        else：
            返回 x - y
    else：
        返回 z * 2
```

### transcribe_project(project_path, output_base_path, context)

项目级转写，创建镜像目录结构。

**返回值：**
```python
{
    'success': bool,
    'project_path': str,
    'output_path': str,
    'total_files': int,
    'transcribed_files': int,
    'failed_files': int,
    'files': [{
        'source': str,
        'output': str,
        'status': str,
        'language': str
    }],
    'error_details': [dict]
}
```

### generate_report(code, context)

生成人类可读的分析报告。

## 支持的文件类型

| 语言 | 扩展名 |
|------|--------|
| Python | `.py` |
| JavaScript | `.js`, `.jsx` |
| TypeScript | `.ts`, `.tsx` |
| Java | `.java` |
| Go | `.go` |
| Rust | `.rs` |
| C/C++ | `.c`, `.cpp`, `.h`, `.hpp` |
| C# | `.cs` |
| Ruby | `.rb` |
| PHP | `.php` |
| Swift | `.swift` |
| Kotlin | `.kt` |
| Scala | `.scala` |
| R | `.r` |
| Lua | `.lua` |
| Perl | `.pl` |
| Shell | `.sh`, `.bash` |

## 忽略的目录

自动过滤以下目录：
- `node_modules`, `.git`, `__pycache__`
- `venv`, `.venv`, `env`, `.env`
- `build`, `dist`, `target`
- `.idea`, `.vscode`
- `bin`, `obj`, `.cache`, `.pytest_cache`

## 安全保障

- ✅ 不执行任何用户代码
- ✅ 不存储用户代码
- ✅ 所有分析在内存中完成
- ✅ 只读扫描，不修改原始文件
- ✅ 完善的错误处理和日志记录

## 版本历史

### v1.0.0
- ✨ 代码复杂度分析（AST精确计算）
- ✨ 代码转自然语言功能
- ✨ 项目级转写（镜像映射）
- ✨ 多语言支持（20+编程语言）
- ✨ 完善的日志系统
- ✨ 增强的错误处理

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！