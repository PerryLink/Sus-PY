# sus-py 完整项目设计方案

**日期**: 2026-02-27
**项目**: sus-py - Python 代码安全扫描工具
**状态**: 设计已批准,准备实施

## 📋 项目概述

**sus-py** 是一个基于 AST 的 Python 代码安全扫描 CLI 工具,专门用于检测 AI 生成代码中的危险操作。

**核心价值主张**: "Don't let AI brick your OS. Scan before you run."

**目标用户**: LLM 重度用户、Code Reviewer、安全意识较强的 Python 开发者

**CLI 命令**: `sus` (极致简洁,如: `sus script.py`)

## 🏗️ 整体架构

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
- `typer`: 构建 CLI 接口,处理命令行参数
- `rich`: 美化终端输出(彩色文本、表格、代码高亮)

**核心设计原则**:
1. 零执行: 绝不运行用户代码,仅静态分析
2. 快速失败: 遇到语法错误立即报告,不继续分析
3. 清晰输出: 明确指出危险代码的位置、类型和原因

## 📦 核心组件设计

### 1. rules.py - 规则定义模块 ✅

**状态**: 已完成并测试通过

**功能**: 定义三个严格级别的安全规则

**数据结构**:
```python
STRICT_RULES = {
    'dangerous_imports': {
        'os': {'severity': 'CRITICAL', 'reason': '...'},
        'subprocess': {'severity': 'CRITICAL', 'reason': '...'},
        ...
    },
    'dangerous_calls': {
        'eval': {'severity': 'CRITICAL', 'reason': '...'},
        'exec': {'severity': 'CRITICAL', 'reason': '...'},
        ...
    }
}
```

**三个严格级别**:
- **STRICT**: 检测 os, subprocess, shutil, sys, socket + eval/exec/compile/__import__/os.system/subprocess.*/shutil.rmtree
- **MODERATE** (默认): 检测 subprocess, shutil + eval/exec/os.system/subprocess.*
- **LOOSE**: 仅检测 eval/exec

### 2. analyzer.py - AST 分析器核心 ✅

**状态**: 已完成并测试通过

**功能**: 遍历 AST 节点,检测危险导入和函数调用

**核心类**: `SecurityVisitor(ast.NodeVisitor)`

**实现方法**:
- `visit_Import()`: 检测 `import os`
- `visit_ImportFrom()`: 检测 `from os import system`
- `visit_Call()`: 检测函数调用如 `eval()`, `os.system()`

**输出格式**:
```python
Issue = {
    'line': int,           # 行号
    'type': str,           # 'import' 或 'call'
    'name': str,           # 危险模块/函数名
    'severity': str,       # 'CRITICAL' / 'HIGH' / 'MEDIUM'
    'reason': str          # 危险原因说明
}
```

### 3. reporter.py - 结果渲染模块 ⏳

**状态**: 待实现

**功能**: 使用 rich 库美化输出

**接口设计**:
```python
def format_report(issues: List[Dict[str, Any]], filename: str) -> str:
    """格式化安全问题报告"""
```

**输出样式**:
- **安全时**: `✅ All clear - No security issues detected`
- **危险时**: 红色表格显示每个问题(行号、类型、名称、严重程度、原因)

**表格设计**:
```
🚨 Security Issues in malicious.py
┏━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Line ┃ Type   ┃ Name       ┃ Severity ┃ Reason                         ┃
┡━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ import │ os         │ CRITICAL │ Direct OS access can execute...│
│ 3    │ call   │ eval       │ CRITICAL │ Executes arbitrary Python code │
└──────┴────────┴────────────┴──────────┴────────────────────────────────┘
```

### 4. cli.py - CLI 接口 ⏳

**状态**: 待实现

**功能**: 使用 typer 构建命令行接口

**命令设计**:
```bash
sus <file_path> [--strict] [--loose]
```

**参数说明**:
- `file_path`: 要扫描的 Python 文件路径(必需)
- `--strict`: 使用严格模式
- `--loose`: 使用宽松模式
- 默认: 中等模式

**执行流程**:
1. 确定严格级别
2. 验证文件存在
3. 读取文件内容
4. 调用 `analyze_code()`
5. 调用 `format_report()`
6. 打印报告
7. 返回退出码

**退出码**:
- `0`: 安全,未发现问题
- `1`: 发现危险代码
- `2`: 解析错误或文件不存在

**错误处理**:
- 文件不存在: `Error: File not found: <path>`
- 语法错误: `Parse Error: Invalid Python syntax at line X`
- 权限问题: `Error: Permission denied`
- 空文件: `All clear (empty file)`

### 5. __main__.py - 入口点 ⏳

**状态**: 待实现

**功能**: 简单的入口文件

**实现**:
```python
from sus_py.cli import app

if __name__ == "__main__":
    app()
```

## 🔄 数据流设计

**完整执行流程**:

```
1. 用户执行: sus script.py --strict
   ↓
2. CLI 解析参数
   - file_path = "script.py"
   - level = "strict"
   ↓
3. 验证文件存在
   - 不存在 → 错误退出(2)
   - 存在 → 继续
   ↓
4. 读取文件内容
   ↓
5. AST 解析
   - 语法错误 → 错误退出(2)
   - 成功 → 继续
   ↓
6. 加载规则: get_rules("strict")
   ↓
7. SecurityVisitor 遍历 AST
   - visit_Import: 检查导入
   - visit_ImportFrom: 检查 from 导入
   - visit_Call: 检查函数调用
   ↓
8. 收集违规项到 issues 列表
   ↓
9. 格式化报告: format_report(issues, filename)
   ↓
10. 打印报告到终端
   ↓
11. 返回退出码
   - issues 为空 → 退出(0)
   - issues 不为空 → 退出(1)
```

## 🧪 测试策略

### 单元测试

**test_rules.py** ✅
- 测试三个严格级别的规则定义
- 测试 `get_rules()` 函数
- 状态: 5个测试已通过

**test_analyzer.py** ✅
- 测试危险导入检测
- 测试危险函数调用检测
- 测试安全代码不误报
- 状态: 已实现并通过

**test_reporter.py** ⏳
- 测试安全报告格式化
- 测试危险报告格式化
- 测试表格输出正确性

### 集成测试

**test_integration.py** ⏳
- 测试安全代码 → 退出码 0
- 测试危险代码 → 退出码 1
- 测试语法错误 → 退出码 2
- 测试文件不存在 → 退出码 2

**测试样本文件** ⏳
- `tests/samples/safe.py`: 安全代码
- `tests/samples/dangerous.py`: 危险代码
- `tests/samples/syntax_error.py`: 语法错误代码

### 手动测试场景

```bash
# 测试安全代码
python -m sus_py tests/samples/safe.py
# 预期: ✅ All clear, 退出码 0

# 测试危险代码
python -m sus_py tests/samples/dangerous.py
# 预期: 🚨 红色表格, 退出码 1

# 测试严格模式
python -m sus_py --strict tests/samples/dangerous.py
# 预期: 检测到更多问题

# 测试语法错误
python -m sus_py tests/samples/syntax_error.py
# 预期: Parse Error, 退出码 2
```

## 📂 项目结构

```
sus-py/
├── src/sus_py/
│   ├── __init__.py          ✅ 已完成
│   ├── rules.py             ✅ 已完成
│   ├── analyzer.py          ✅ 已完成
│   ├── reporter.py          ⏳ 待实现
│   ├── cli.py               ⏳ 待实现
│   └── __main__.py          ⏳ 待实现
├── tests/
│   ├── test_rules.py        ✅ 已完成
│   ├── test_analyzer.py     ✅ 已完成
│   ├── test_reporter.py     ⏳ 待实现
│   ├── test_integration.py  ⏳ 待实现
│   └── samples/             ⏳ 待创建
│       ├── safe.py
│       ├── dangerous.py
│       └── syntax_error.py
├── docs/plans/              ✅ 已完成
│   ├── 2026-02-27-sus-py-design.md
│   ├── 2026-02-27-sus-py-implementation.md
│   └── 2026-02-27-sus-py-complete-design.md
├── pyproject.toml           ✅ 已完成
├── README.md                ⏳ 待更新
└── LICENSE                  ✅ 已完成
```

## 🚀 实现顺序

按照依赖关系,建议按以下顺序实现:

1. **reporter.py** (输出模块,CLI 需要它)
2. **cli.py + __main__.py** (用户接口,整合所有模块)
3. **测试样本文件** (用于手动测试)
4. **test_reporter.py** (渲染器单元测试)
5. **test_integration.py** (验证整体功能)
6. **README.md** (完善文档)

## ✅ MVP 范围

### 包含功能

- ✅ 基于 AST 的静态分析
- ✅ 三个严格级别 (strict/moderate/loose)
- ✅ 黑名单机制
- ⏳ Rich 美化输出
- ⏳ 明确的退出码 (0/1/2)
- ⏳ 基本错误处理

### 不包含功能

- ❌ 变量污点追踪 (如 `cmd = 'rm -rf /'; os.system(cmd)`)
- ❌ 动态导入检测 (如 `__import__('os')`)
- ❌ 配置文件支持 (.sus-py.yaml)
- ❌ 白名单机制
- ❌ 自动修复功能
- ❌ 递归目录扫描

## 🎨 用户体验设计

### 成功场景

```bash
$ sus safe.py
✅ All clear - No security issues detected
```

### 危险场景

```bash
$ sus malicious.py

🚨 Security Issues in malicious.py
┏━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Line ┃ Type   ┃ Name           ┃ Severity ┃ Reason                                 ┃
┡━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ import │ os             │ CRITICAL │ Direct OS access can execute commands  │
│ 3    │ call   │ os.system      │ CRITICAL │ Executes shell commands directly       │
│ 5    │ call   │ eval           │ CRITICAL │ Executes arbitrary Python code         │
└──────┴────────┴────────────────┴──────────┴────────────────────────────────────────┘

🚫 Scan Failed. Do not run this code.
```

### 错误场景

```bash
$ sus nonexistent.py
Error: File not found: nonexistent.py

$ sus broken.py
Parse Error: Invalid Python syntax at line 5
```

## 🔑 关键设计决策

### 1. 为什么选择 AST 而不是正则表达式?

- AST 无法被混淆代码绕过
- 能准确识别代码结构
- Python 标准库自带,无额外依赖

### 2. 为什么不追踪变量?

- 保持 MVP 简单
- 变量追踪复杂度高
- 大多数 AI 生成的危险代码是直接调用

### 3. 为什么三个严格级别?

- **strict**: 适合完全不信任的代码
- **moderate**: 平衡安全和实用性(默认)
- **loose**: 仅拦截最危险的操作

### 4. 为什么不自动修复?

- 自动修复可能破坏代码逻辑
- 用户应该理解代码在做什么
- MVP 阶段保持简单

## 📊 项目进度

**当前进度**: 约 60% 完成

**已完成**:
- ✅ 项目结构初始化
- ✅ 规则定义模块
- ✅ AST 分析器核心
- ✅ 设计文档完整

**待完成**:
- ⏳ 结果渲染模块
- ⏳ CLI 接口
- ⏳ 集成测试
- ⏳ 文档完善

## 🎯 验收标准

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] CLI 可以正确扫描文件
- [ ] 三个严格级别工作正常
- [ ] 退出码正确 (0/1/2)
- [ ] 输出使用 rich 美化
- [ ] 文档完整
- [ ] 可以通过 `pip install sus-py` 安装
- [ ] 可以通过 `sus script.py` 命令使用

## 📚 参考文档

1. **产品设计理念**: `Creative-144.txt`
2. **架构设计**: `docs/plans/2026-02-27-sus-py-design.md`
3. **详细实现计划**: `docs/plans/2026-02-27-sus-py-implementation.md`
4. **项目状态**: `PROJECT_STATUS.md`
5. **已实现的规则模块**: `src/sus_py/rules.py`
6. **已实现的分析器**: `src/sus_py/analyzer.py`

## 🚀 下一步

设计已批准,现在转入实现计划阶段。使用 writing-plans skill 创建详细的实现步骤。
