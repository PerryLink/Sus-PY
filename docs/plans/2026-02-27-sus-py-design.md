# sus-py 设计文档

**日期**: 2026-02-27
**项目**: sus-py - Python 代码安全扫描工具
**方案**: 简单 AST Walker

## 概述

sus-py 是一个用于扫描 AI 生成的 Python 代码中潜在危险操作的静态分析工具。通过 AST（抽象语法树）分析，在不执行代码的情况下识别危险的库导入和函数调用。

**目标用户**: 个人开发者本地使用
**核心价值**: 在运行 AI 生成的代码前，快速识别潜在的危险操作

## 整体架构

```
用户输入 (CLI)
    ↓
参数解析 (typer)
    ↓
文件读取 & AST 解析
    ↓
安全规则检查 (SecurityVisitor)
    ↓
结果渲染 (rich)
    ↓
输出 & 退出码
```

**技术栈**:
- Python 标准库 `ast`: 解析 Python 代码为抽象语法树
- `typer`: 构建 CLI 接口，处理命令行参数
- `rich`: 美化终端输出（彩色文本、表格、代码高亮）

**核心设计原则**:
1. 零执行：绝不运行用户代码，仅静态分析
2. 快速失败：遇到语法错误立即报告，不继续分析
3. 清晰输出：明确指出危险代码的位置、类型和原因

## 核心组件

### 1. cli.py - CLI 入口
- 使用 `typer` 定义命令行接口
- 主命令：`sus <file_path>`
- 参数：
  - `--strict`: 严格模式（阻止所有危险库）
  - `--moderate`: 中等模式（默认，阻止明显危险操作）
  - `--loose`: 宽松模式（仅警告 eval/exec 等）
- 返回退出码：0=安全，1=发现危险代码，2=解析错误

### 2. rules.py - 规则定义
定义三个严格级别的黑名单字典：

```python
STRICT_RULES = {
    'dangerous_imports': ['os', 'subprocess', 'shutil', 'sys', 'socket'],
    'dangerous_calls': ['eval', 'exec', 'compile', '__import__']
}

MODERATE_RULES = {
    'dangerous_imports': ['subprocess', 'shutil'],
    'dangerous_calls': ['eval', 'exec', 'os.system']
}

LOOSE_RULES = {
    'dangerous_calls': ['eval', 'exec']
}
```

### 3. analyzer.py - AST 分析器
- `SecurityVisitor(ast.NodeVisitor)` 类
- 实现方法：
  - `visit_Import()`: 检测 `import os`
  - `visit_ImportFrom()`: 检测 `from os import system`
  - `visit_Call()`: 检测函数调用如 `eval()`
- 收集违规信息：行号、代码片段、危险类型、严重程度

### 4. reporter.py - 结果渲染
- 使用 `rich.console.Console` 输出
- 安全时：绿色 ✅ + "All clear"
- 危险时：红色表格显示每个问题（行号、代码、原因、严重程度）

## 数据流与执行流程

**执行流程**:
1. CLI 接收参数（文件路径 + 严格级别）
2. 读取文件内容
3. 尝试 ast.parse() 解析
   - 成功 → 继续
   - 失败 → 输出语法错误，退出码 2
4. 根据严格级别加载对应规则
5. SecurityVisitor 遍历 AST
6. 收集所有违规项到列表
7. Reporter 渲染结果
8. 返回退出码（0/1）

**数据结构**:
```python
Issue = {
    'line': int,           # 行号
    'code': str,           # 代码片段
    'type': str,           # 'import' 或 'call'
    'name': str,           # 危险模块/函数名
    'severity': str        # 'CRITICAL' / 'HIGH' / 'MEDIUM'
}
```

**关键决策**:
- 不追踪变量（如 `cmd = 'rm -rf /'; os.system(cmd)`），保持简单
- 不检测动态导入（如 `__import__('os')`），MVP 阶段可接受
- 只报告问题，不提供修复建议

## 错误处理

**错误场景与处理策略**:

1. **文件不存在**
   - 输出：`Error: File not found: <path>`
   - 退出码：2

2. **语法错误（无法解析）**
   - 输出：`Parse Error: Invalid Python syntax at line X`
   - 退出码：2

3. **文件读取权限问题**
   - 输出：`Error: Permission denied`
   - 退出码：2

4. **空文件**
   - 视为安全，输出：`All clear (empty file)`
   - 退出码：0

**设计原则**:
- 所有错误都使用 `rich` 的红色输出
- 错误信息简洁明了，不暴露内部堆栈
- 区分"解析错误"（退出码 2）和"发现危险代码"（退出码 1）

## 测试策略

**测试范围**:

1. **单元测试（tests/）**
   - `test_analyzer.py`: 测试 AST 分析器
     - 正常导入检测
     - 危险函数调用检测
     - 不同严格级别的规则应用
   - `test_rules.py`: 验证规则定义正确性

2. **集成测试（tests/samples/）**
   - `safe.py`: 无害代码（应通过）
   - `dangerous_import.py`: 包含 `import os`
   - `dangerous_call.py`: 包含 `eval()`
   - `syntax_error.py`: 语法错误文件

**测试工具**: 使用 `pytest`

**验收标准**:
- 所有单元测试通过
- 三个严格级别都能正确识别对应的危险代码
- 语法错误能被正确捕获并报告

## 项目结构

```
sus-py/
├── src/sus_py/
│   ├── __init__.py
│   ├── __main__.py      # 入口点
│   ├── cli.py           # CLI 接口
│   ├── analyzer.py      # AST 分析器
│   ├── rules.py         # 规则定义
│   └── reporter.py      # 结果渲染
├── tests/
│   ├── test_analyzer.py
│   ├── test_rules.py
│   └── samples/         # 测试用例文件
├── docs/
│   └── plans/           # 设计文档
├── pyproject.toml       # Poetry 配置
├── README.md
└── LICENSE
```

## MVP 范围

**包含**:
- 基于 AST 的静态分析
- 三个严格级别（strict/moderate/loose）
- 终端友好的彩色输出
- 基本的错误处理

**不包含**:
- 配置文件支持
- 变量污点追踪
- 动态导入检测
- 自动修复功能
- 白名单机制

## 下一步

转入实现计划阶段，使用 writing-plans skill 创建详细的实现步骤。
