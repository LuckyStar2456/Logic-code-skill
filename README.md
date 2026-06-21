# Logic-code Skill

一个强大的代码审查和转写技能，帮助开发人员理解复杂代码逻辑。

## 功能特性

### 1. 代码审查
- 📊 **圈复杂度分析**：使用AST精确计算代码复杂度
- 🔍 **函数分析**：详细的函数/方法级别分析
- 📝 **代码风格检查**：识别风格问题和改进建议
- 💡 **重构建议**：自动生成代码改进建议
- 📋 **报告生成**：生成易读的分析报告

### 2. 代码转写
- 🔄 **代码转自然语言**：将代码转换为逻辑化的自然语言描述
- 🌐 **多语言支持**：支持 Python、JavaScript、Java、Go 等多种语言
- 📖 **意图理解**：理解代码意图并生成清晰的描述

### 3. 项目级转写（镜像映射）
- 🗂️ **目录扫描**：自动扫描项目目录结构
- 🪞 **镜像创建**：创建与项目结构对称的镜像目录
- 📦 **批量转写**：批量转写所有代码文件
- 📄 **Markdown输出**：生成格式化的 Markdown 文档

## 项目结构

```
my-skill-project/
├── .trae/
│   └── skills/
│       └── Logic-code/
│           └── SKILL.md          # 技能定义文件
├── skill/
│   ├── __init__.py               # 核心技能代码
│   └── skill.json                # 技能配置
├── scripts/
│   ├── install_skill.py          # 安装脚本
│   └── package_skill.py          # 打包脚本
├── examples/
│   └── example_usage.py          # 使用示例
├── README.md                     # 项目文档
└── package.json                  # 项目元数据
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

# 代码转写
transcription = transcribe_code(code)
print(transcription['natural_language'])
# 输出：
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
        'mode': 'review'                  # 操作模式（review/transcribe）
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

将代码转写为自然语言描述。

**返回值：**
```python
{
    'success': bool,
    'natural_language': str,
    'detected_language': str,
    'functions': [{
        'name': str,
        'transcription': str
    }]
}
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