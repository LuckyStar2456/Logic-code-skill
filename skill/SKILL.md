---
name: "Logic-code"
description: "具备代码审查能力，同时为开发人员提供将代码转写成逻辑化自然语言的功能。当用户请求代码审查或代码转写时调用。"
---

# Logic-code 技能

## 功能概述

本技能为开发人员提供三大核心功能：

### 1. 代码审查
- 分析代码复杂度（圈复杂度）
- 检查代码风格和潜在问题
- 提供重构建议
- 支持多种编程语言

### 2. 代码转写
- 将复杂代码转换为逻辑化的自然语言描述
- 保持代码逻辑结构清晰易懂
- 支持多种编程语言（Python、JavaScript、Java、Go等）
- 默认参考上下文语言

### 3. 项目级转写（镜像映射）
- 自动扫描项目目录结构
- 创建与项目目录结构镜面对称的镜像路径
- 批量转写项目中所有可转写的代码文件
- 自动生成 Markdown 格式的自然语言文档

## 触发条件

当用户提出以下请求时自动触发：
- "帮我审查这段代码"
- "分析代码复杂度"
- "解释这段代码的逻辑"
- "将代码转写成文字"
- "代码转写"
- "转写整个项目"
- "转写项目"
- "project transcribe"
- "code review"
- "explain code"

## 核心功能详解

### 项目级转写（镜像映射）

**工作流程：**

1. **目录扫描**：自动扫描项目目录，过滤忽略的目录（node_modules、.git等）
2. **镜像创建**：在项目根目录创建 `logic_code/` 镜像目录，保持原有目录结构
3. **文件转写**：将每个代码文件转写为自然语言 Markdown 文档
4. **自动保存**：所有转写文档保存到镜像路径中

**支持的文件类型：**

```
.py, .js, .jsx, .ts, .tsx, .java, .go, .rs,
.cpp, .c, .h, .hpp, .cs, .rb, .php, .swift,
.kt, .scala, .r, .lua, .pl, .sh, .bash
```

**忽略的目录：**

```
node_modules, .git, __pycache__, venv, .venv,
env, build, dist, .idea, .vscode, bin, obj,
target, .cache, .pytest_cache
```

**输出结构示例：**

```
项目根目录/
├── src/
│   ├── main.py          → logic_code/src/main.py.md
│   └── utils/
│       └── helpers.py   → logic_code/src/utils/helpers.py.md
├── tests/
│   └── test_main.py     → logic_code/tests/test_main.py.md
└── config.py            → logic_code/config.py.md
```

## 使用示例

### 示例 1: 代码审查
```python
def complex_function(x, y, z):
    if x > y:
        if z < 10:
            return x + y
        else:
            return x - y
    else:
        return z * 2
```

审查结果会包含：复杂度分析、潜在问题、重构建议。

### 示例 2: 代码转写
将上述代码转写为自然语言：
"定义一个名为 complex_function 的函数，接受三个参数 x、y、z。
如果 x 大于 y：
    如果 z 小于 10：返回 x 加 y 的结果
    否则：返回 x 减 y 的结果
否则：返回 z 乘以 2 的结果"

### 示例 3: 项目级转写
```
调用 transcribe_project('c:/my-project')
```

自动创建：
```
c:/my-project/logic_code/
├── src/
│   └── main.py.md
├── utils/
│   └── helpers.py.md
└── config.py.md
```

## API 接口

### process_code(code, context)
主入口函数，支持审查和转写两种模式

### transcribe_project(project_path, output_base_path=None, context=None)
项目级转写主函数

**参数：**
- `project_path`: 项目目录路径
- `output_base_path`: 输出基础路径（默认：project_path/logic_code/）
- `context`: 配置字典

**返回：**
```json
{
  "success": true,
  "project_path": "项目路径",
  "output_path": "logic_code/",
  "total_files": 10,
  "transcribed_files": 9,
  "failed_files": 1,
  "files": [
    {
      "source": "src/main.py",
      "output": "logic_code/src/main.py.md",
      "status": "success",
      "language": "python"
    }
  ]
}
```

## 配置选项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| min_complexity_threshold | integer | 10 | 复杂度警告阈值 |
| enable_suggestions | boolean | true | 是否启用重构建议 |
| language | string | auto | 目标编程语言（auto/python/javascript/java/go） |
| mode | string | review | 操作模式（review/transcribe） |

## 安全保障

- 不执行任何用户提供的代码
- 不存储用户代码
- 所有分析在内存中完成
- 支持敏感信息过滤
- 只读扫描，不修改原始代码
- 自动过滤 node_modules、.git 等敏感目录

## 输出格式

返回结构化的 JSON 结果，包含：

**代码审查模式：**
- summary: 代码摘要信息
- complexity: 复杂度分析数据
- functions: 函数级分析详情
- suggestions: 重构建议列表

**代码转写模式：**
- natural_language: 代码的自然语言描述
- detected_language: 检测到的编程语言
- functions: 函数级转写详情

**项目转写模式：**
- project_path: 项目路径
- output_path: 输出目录路径
- total_files: 总文件数
- transcribed_files: 成功转写数
- failed_files: 失败文件数
- files: 文件转写详情列表
