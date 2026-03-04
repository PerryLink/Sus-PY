# sus-py 项目状态总结

**更新时间**: 2026-02-27

## 📋 项目概述

**sus-py** 是一个基于 AST 的 Python 代码安全扫描 CLI 工具,用于检测 AI 生成代码中的危险操作。

**核心价值**: "Don't let AI brick your OS. Scan before you run." (别让 AI 变砖你的系统。运行前,先扫描。)

**项目进度**: 约 30% 完成

---

## ✅ 已完成的工作

### 1. 项目结构初始化
- ✅ `pyproject.toml` 配置完成
  - 构建系统: Poetry
  - Python 版本: ^3.8
  - 依赖: typer ^0.9.0, rich ^13.7.0
  - 开发依赖: pytest ^7.4.0
  - CLI 入口点: `sus` → `sus_py.cli:app`

### 2. 规则定义模块 (rules.py)
- ✅ 文件位置: `src/sus_py/rules.py`
- ✅ 实现了三个严格级别:
  - **STRICT_RULES**: 检测 os, subprocess, shutil, sys, socket 导入 + eval/exec/compile/__import__/os.system/subprocess.*/shutil.rmtree 调用
  - **MODERATE_RULES**: 检测 subprocess, shutil 导入 + eval/exec/os.system/subprocess.* 调用
  - **LOOSE_RULES**: 仅检测 eval/exec 调用
- ✅ 每条规则包含 severity (CRITICAL/HIGH/MEDIUM) 和 reason
- ✅ `get_rules(level)` 函数实现
- ✅ 单元测试通过 (5 个测试)

### 3. 设计文档
- ✅ `Creative-144.txt`: 产品设计理念
- ✅ `docs/plans/2026-02-27-sus-py-design.md`: 架构设计
- ✅ `docs/plans/2026-02-27-sus-py-implementation.md`: 详细实现计划
- ✅ `C:\Users\anqiao\.claude\plans\zazzy-discovering-cray.md`: 完整项目设计方案

---

## ❌ 待实现的工作

### Task 1: AST 分析器核心 (analyzer.py) ⭐ 最优先
**文件**: `src/sus_py/analyzer.py` (需创建)

**核心实现**:
```python
class SecurityVisitor(ast.NodeVisitor):
    def __init__(self, rules: dict):
        self.rules = rules
        self.issues: List[Dict] = []

    def visit_Import(self, node):
        # 检测: import os
        # 匹配 rules['dangerous_imports']

    def visit_ImportFrom(self, node):
        # 检测: from subprocess import call
        # 匹配 rules['dangerous_imports']

    def visit_Call(self, node):
        # 检测: eval('1+1'), os.system('cmd')
        # 匹配 rules['dangerous_calls']

def analyze_code(code: str, rules: dict) -> List[Dict[str, Any]]:
    """分析 Python 代码并返回安全问题列表"""
```

**测试文件**: `tests/test_analyzer.py` (需创建)

### Task 2: 结果渲染模块 (reporter.py)
**文件**: `src/sus_py/reporter.py` (需创建)

**核心实现**:
```python
def format_report(issues: List[Dict[str, Any]], filename: str) -> str:
    """格式化安全问题报告"""
    if not issues:
        return "✅ All clear - No security issues detected"

    # 使用 rich.table.Table 创建红色表格
    # 列: Line | Type | Name | Severity
```

**测试文件**: `tests/test_reporter.py` (需创建)

### Task 3: CLI 接口 (cli.py + __main__.py)
**文件**:
- `src/sus_py/cli.py` (需创建)
- `src/sus_py/__main__.py` (需创建)

**核心实现**:
```python
@app.command()
def main(
    file_path: Path,
    strict: bool = False,
    loose: bool = False
):
    # 1. 确定严格级别
    # 2. 验证文件存在
    # 3. 读取文件内容
    # 4. 调用 analyze_code()
    # 5. 调用 format_report()
    # 6. 返回退出码 (0=安全/1=危险/2=错误)
```

**测试样本文件** (需创建):
- `tests/samples/safe.py`: 安全代码
- `tests/samples/dangerous.py`: 危险代码
- `tests/samples/syntax_error.py`: 语法错误代码

### Task 4: 集成测试
**文件**: `tests/test_integration.py` (需创建)

**测试场景**:
- 安全代码 → 退出码 0
- 危险代码 → 退出码 1
- 语法错误 → 退出码 2
- 文件不存在 → 退出码 2

### Task 5: 文档完善
**文件**: `README.md` (需更新)

**内容**:
- 项目简介
- 安装方法
- 使用示例 (三种严格级别)
- 退出码说明
- 检测规则说明
- 输出示例

---

## 📂 关键文件路径

### 已存在的文件
- `src/sus_py/__init__.py`
- `src/sus_py/rules.py` ✅
- `tests/test_rules.py` ✅
- `pyproject.toml` ✅
- `Creative-144.txt` ✅

### 需要创建的文件
- `src/sus_py/analyzer.py`
- `src/sus_py/reporter.py`
- `src/sus_py/cli.py`
- `src/sus_py/__main__.py`
- `tests/test_analyzer.py`
- `tests/test_reporter.py`
- `tests/test_integration.py`
- `tests/samples/safe.py`
- `tests/samples/dangerous.py`
- `tests/samples/syntax_error.py`

---

## 🧪 验证方案

### 单元测试
```bash
pytest -v
```

预期结果:
- test_rules.py: 5 passed ✅
- test_analyzer.py: 4 passed (待实现)
- test_reporter.py: 2 passed (待实现)
- test_integration.py: 4 passed (待实现)

### 手动测试
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

---

## 🔄 实现顺序建议

按照依赖关系,建议按以下顺序实现:

1. **analyzer.py** (核心引擎,其他模块依赖它)
2. **reporter.py** (输出模块,CLI 需要它)
3. **cli.py + __main__.py** (用户接口,整合所有模块)
4. **测试样本文件** (用于手动测试)
5. **集成测试** (验证整体功能)
6. **文档完善** (最后完善 README)

---

## 📚 参考文档

1. **完整设计方案**: `C:\Users\anqiao\.claude\plans\zazzy-discovering-cray.md`
2. **产品设计理念**: `Creative-144.txt`
3. **架构设计**: `docs/plans/2026-02-27-sus-py-design.md`
4. **详细实现计划**: `docs/plans/2026-02-27-sus-py-implementation.md`
5. **已实现的规则模块**: `src/sus_py/rules.py`

---

## 🛠️ 技术栈

- **Python**: 3.8+
- **AST**: Python 标准库 (静态分析)
- **typer**: CLI 框架
- **rich**: 终端美化输出
- **pytest**: 测试框架
- **Poetry**: 包管理和构建

---

## 🎯 MVP 范围

### ✅ 包含
- 基于 AST 的静态分析
- 三个严格级别
- 黑名单机制
- Rich 美化输出
- 明确的退出码

### ❌ 不包含
- 变量污点追踪
- 动态导入检测
- 配置文件支持
- 白名单机制
- 自动修复功能

---

## 🚀 下一步行动

在新的 Claude 会话中,你可以直接说:

**"请根据 PROJECT_STATUS.md 和设计方案,按照实现顺序开始实现 sus-py 项目。首先实现 analyzer.py。"**

或者更简洁:

**"请实现 sus-py 项目,从 analyzer.py 开始。"**

---

## 📊 Git 状态

**当前分支**: master
**主分支**: main

**最近提交**:
- ee924b0 feat: add security rules with enhanced structure
- 2272874 chore: initialize project structure
- d0c55e1 docs: add detailed implementation plan
- 001bac4 docs: add initial design document and product spec

**未跟踪文件**:
- .claude/
- nul
- tests/__pycache__/
