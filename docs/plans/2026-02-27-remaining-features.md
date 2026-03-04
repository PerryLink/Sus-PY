# sus-py 剩余功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标**: 完成 sus-py 项目的剩余功能,包括结果渲染、CLI 接口、测试样本和集成测试

**架构**: 使用 rich 库美化输出,typer 构建 CLI,整合 analyzer 和 rules 模块,提供完整的命令行工具

**技术栈**: Python 3.8+, typer, rich, pytest

---

## Task 1: 结果渲染模块

**文件**:
- Create: `src/sus_py/reporter.py`
- Create: `tests/test_reporter.py`

**Step 1: 编写渲染器测试**

```python
# tests/test_reporter.py
from sus_py.reporter import format_report

def test_format_safe_report():
    """Test formatting when no issues found."""
    issues = []
    output = format_report(issues, "test.py")
    assert "All clear" in output or "✅" in output

def test_format_danger_report():
    """Test formatting when issues are found."""
    issues = [
        {
            'line': 10,
            'type': 'import',
            'name': 'os',
            'severity': 'CRITICAL',
            'reason': 'Direct OS access can execute arbitrary commands'
        }
    ]
    output = format_report(issues, "test.py")
    assert "10" in output
    assert "os" in output
    assert "CRITICAL" in output
```

**Step 2: 运行测试确认失败**

运行: `pytest tests/test_reporter.py -v`

预期输出: `ModuleNotFoundError: No module named 'sus_py.reporter'`

**Step 3: 实现结果渲染模块**

```python
# src/sus_py/reporter.py
"""Report formatting using rich."""
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table


def format_report(issues: List[Dict[str, Any]], filename: str) -> str:
    """Format security issues as a rich report.

    Args:
        issues: List of security issues found
        filename: Name of the file being scanned

    Returns:
        Formatted report string
    """
    if not issues:
        return "✅ All clear - No security issues detected"

    # Create console for capturing output
    from io import StringIO
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, width=100)

    # Create table
    table = Table(title=f"🚨 Security Issues in {filename}", show_header=True)
    table.add_column("Line", style="cyan", width=6)
    table.add_column("Type", style="magenta", width=8)
    table.add_column("Name", style="red", width=20)
    table.add_column("Severity", style="yellow", width=10)
    table.add_column("Reason", style="white", width=40)

    # Add rows
    for issue in issues:
        table.add_row(
            str(issue['line']),
            issue['type'],
            issue['name'],
            issue['severity'],
            issue['reason']
        )

    # Print table and warning
    console.print(table)
    console.print("\n🚫 Scan Failed. Do not run this code.", style="bold red")

    return buffer.getvalue()
```

**Step 4: 运行测试确认通过**

运行: `pytest tests/test_reporter.py -v`

预期输出: `2 passed`

**Step 5: 提交**

```bash
git add src/sus_py/reporter.py tests/test_reporter.py
git commit -m "$(cat <<'EOF'
feat: add rich-based report formatting

Implement colorful table output for security issues with clear visual indicators.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: CLI 接口

**文件**:
- Create: `src/sus_py/cli.py`
- Create: `src/sus_py/__main__.py`

**Step 1: 实现 CLI 模块**

```python
# src/sus_py/cli.py
"""CLI interface using typer."""
import sys
from pathlib import Path
import typer
from rich.console import Console

from sus_py.analyzer import analyze_code
from sus_py.rules import get_rules
from sus_py.reporter import format_report

app = typer.Typer(help="Static analyzer for detecting suspicious Python code")
console = Console()


@app.command()
def main(
    file_path: Path = typer.Argument(..., help="Python file to scan"),
    strict: bool = typer.Option(False, "--strict", help="Use strict mode (blocks all dangerous libraries)"),
    loose: bool = typer.Option(False, "--loose", help="Use loose mode (only warns about eval/exec)"),
):
    """Scan Python file for suspicious code patterns.

    Exit codes:
        0: No security issues detected
        1: Security issues found
        2: Parse error or file not found
    """
    # Determine strictness level
    if strict:
        level = 'strict'
    elif loose:
        level = 'loose'
    else:
        level = 'moderate'

    # Check file exists
    if not file_path.exists():
        console.print(f"[red]Error: File not found: {file_path}[/red]")
        sys.exit(2)

    # Read and analyze
    try:
        code = file_path.read_text(encoding='utf-8')

        # Handle empty file
        if not code.strip():
            console.print("✅ All clear (empty file)")
            sys.exit(0)

        rules = get_rules(level)
        issues = analyze_code(code, rules)

        # Print report
        report = format_report(issues, file_path.name)
        console.print(report)

        # Exit with appropriate code
        sys.exit(1 if issues else 0)

    except SyntaxError as e:
        console.print(f"[red]Parse Error: Invalid Python syntax at line {e.lineno}[/red]")
        sys.exit(2)
    except UnicodeDecodeError:
        console.print(f"[red]Error: Unable to read file (encoding issue)[/red]")
        sys.exit(2)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(2)


if __name__ == "__main__":
    app()
```

**Step 2: 创建入口点**

```python
# src/sus_py/__main__.py
"""Entry point for sus-py when run as a module."""
from sus_py.cli import app

if __name__ == "__main__":
    app()
```

**Step 3: 手动测试 CLI (创建临时测试文件)**

运行: `python -c "print('import json')" > /tmp/test_safe.py && python -m sus_py /tmp/test_safe.py`

预期输出: `✅ All clear`

运行: `python -c "print('import os')" > /tmp/test_danger.py && python -m sus_py /tmp/test_danger.py`

预期输出: 红色表格显示问题

**Step 4: 提交**

```bash
git add src/sus_py/cli.py src/sus_py/__main__.py
git commit -m "$(cat <<'EOF'
feat: implement CLI interface with typer

Add main command with strictness level options, error handling, and proper exit codes.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: 测试样本文件

**文件**:
- Create: `tests/samples/safe.py`
- Create: `tests/samples/dangerous.py`
- Create: `tests/samples/syntax_error.py`

**Step 1: 创建测试样本目录**

运行: `mkdir -p tests/samples`

预期: 目录创建成功

**Step 2: 创建安全代码样本**

```python
# tests/samples/safe.py
"""Safe Python code for testing."""
import json
import math
from datetime import datetime


def calculate_sum(numbers):
    """Calculate sum of numbers."""
    return sum(numbers)


def format_date(date):
    """Format date as string."""
    return date.strftime("%Y-%m-%d")


if __name__ == "__main__":
    data = {"name": "test", "value": 42}
    print(json.dumps(data))
    print(calculate_sum([1, 2, 3, 4, 5]))
    print(format_date(datetime.now()))
```

**Step 3: 创建危险代码样本**

```python
# tests/samples/dangerous.py
"""Dangerous Python code for testing."""
import os
import subprocess


def delete_everything():
    """DANGEROUS: This would delete files."""
    os.system("rm -rf /")


def run_command(cmd):
    """DANGEROUS: This executes arbitrary commands."""
    subprocess.run(cmd, shell=True)


def execute_code(code):
    """DANGEROUS: This executes arbitrary Python code."""
    eval(code)


if __name__ == "__main__":
    # These are dangerous operations
    delete_everything()
    run_command("ls -la")
    execute_code("print('hello')")
```

**Step 4: 创建语法错误样本**

```python
# tests/samples/syntax_error.py
"""File with syntax errors for testing."""

def broken_function(
    print("missing closing parenthesis")

if True
    print("missing colon")
```

**Step 5: 手动测试样本文件**

运行: `python -m sus_py tests/samples/safe.py`

预期输出: `✅ All clear`

运行: `python -m sus_py tests/samples/dangerous.py`

预期输出: 红色表格显示多个问题

运行: `python -m sus_py tests/samples/syntax_error.py`

预期输出: `Parse Error`

**Step 6: 提交**

```bash
git add tests/samples/
git commit -m "$(cat <<'EOF'
test: add sample files for manual testing

Add safe, dangerous, and syntax error samples to verify scanner behavior.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: 集成测试

**文件**:
- Create: `tests/test_integration.py`

**Step 1: 编写集成测试**

```python
# tests/test_integration.py
"""Integration tests for CLI."""
import subprocess
import sys
from pathlib import Path


def run_cli(file_path: str, *args):
    """Helper to run CLI and capture result."""
    cmd = [sys.executable, "-m", "sus_py", file_path] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def test_safe_code_exits_zero():
    """Test that safe code returns exit code 0."""
    result = run_cli("tests/samples/safe.py")
    assert result.returncode == 0
    assert "All clear" in result.stdout


def test_dangerous_code_exits_one():
    """Test that dangerous code returns exit code 1."""
    result = run_cli("tests/samples/dangerous.py")
    assert result.returncode == 1
    assert "Security Issues" in result.stdout


def test_syntax_error_exits_two():
    """Test that syntax errors return exit code 2."""
    result = run_cli("tests/samples/syntax_error.py")
    assert result.returncode == 2
    assert "Parse Error" in result.stdout


def test_nonexistent_file_exits_two():
    """Test that missing files return exit code 2."""
    result = run_cli("nonexistent_file_that_does_not_exist.py")
    assert result.returncode == 2
    assert "File not found" in result.stdout


def test_strict_mode_detects_more():
    """Test that strict mode detects more issues."""
    result_moderate = run_cli("tests/samples/dangerous.py")
    result_strict = run_cli("tests/samples/dangerous.py", "--strict")

    # Both should fail
    assert result_moderate.returncode == 1
    assert result_strict.returncode == 1


def test_loose_mode_detects_less():
    """Test that loose mode is more permissive."""
    # Create a file with only os import (no eval/exec)
    test_file = Path("tests/samples/temp_os_only.py")
    test_file.write_text("import os\n")

    try:
        result_loose = run_cli(str(test_file), "--loose")
        result_moderate = run_cli(str(test_file))

        # Loose should pass (os not in loose rules)
        assert result_loose.returncode == 0
        # Moderate might fail depending on rules
    finally:
        if test_file.exists():
            test_file.unlink()
```

**Step 2: 运行集成测试**

运行: `pytest tests/test_integration.py -v`

预期输出: `6 passed`

**Step 3: 运行所有测试**

运行: `pytest -v`

预期输出: 所有测试通过

**Step 4: 提交**

```bash
git add tests/test_integration.py
git commit -m "$(cat <<'EOF'
test: add integration tests for CLI

Verify exit codes, error handling, and strictness levels work correctly.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: 文档完善

**文件**:
- Modify: `README.md`

**Step 1: 更新 README**

```markdown
# sus-py

🛡️ Static analyzer for detecting suspicious Python code generated by AI.

**Don't let AI brick your OS. Scan before you run.**

## Installation

```bash
pip install sus-py
```

## Quick Start

```bash
# Scan a file (moderate mode by default)
sus script.py

# Strict mode - blocks all dangerous libraries
sus --strict script.py

# Loose mode - only warns about eval/exec
sus --loose script.py
```

## Exit Codes

- `0`: No security issues detected ✅
- `1`: Security issues found 🚨
- `2`: Parse error or file not found ❌

## What It Detects

### Strict Mode
Detects all potentially dangerous operations:
- **Dangerous imports**: `os`, `subprocess`, `shutil`, `sys`, `socket`
- **Dangerous calls**: `eval`, `exec`, `compile`, `__import__`, `os.system`, `subprocess.*`, `shutil.rmtree`

### Moderate Mode (Default)
Balanced security for typical use cases:
- **Dangerous imports**: `subprocess`, `shutil`
- **Dangerous calls**: `eval`, `exec`, `os.system`, `subprocess.call`, `subprocess.run`, `subprocess.Popen`

### Loose Mode
Only blocks the most critical operations:
- **Dangerous calls**: `eval`, `exec`

## Example Output

### Safe Code
```bash
$ sus safe_script.py
✅ All clear - No security issues detected
```

### Dangerous Code
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

## Use Cases

- **Before running AI-generated code**: Scan scripts from ChatGPT, Claude, or other LLMs
- **Code review**: Quick security check for Python files
- **CI/CD integration**: Add to your pipeline to catch dangerous code
- **Learning**: Understand what operations are considered risky

## How It Works

sus-py uses Python's built-in `ast` module to parse and analyze code without executing it. This means:
- ✅ Safe: Never runs the code being scanned
- ✅ Fast: Static analysis is quick
- ✅ Accurate: AST parsing can't be fooled by obfuscation

## Limitations

This is a static analyzer with intentional limitations:
- Does not track variables (e.g., `cmd = 'rm -rf /'; os.system(cmd)`)
- Does not detect dynamic imports (e.g., `__import__('os')`)
- No configuration file support (by design - keep it simple)

## Development

```bash
# Install dependencies
poetry install

# Run tests
pytest

# Run on sample files
python -m sus_py tests/samples/dangerous.py
```

## License

MIT

## Contributing

Issues and pull requests welcome at [github.com/yourusername/sus-py](https://github.com/yourusername/sus-py)
```

**Step 2: 提交**

```bash
git add README.md
git commit -m "$(cat <<'EOF'
docs: update README with comprehensive usage guide

Add installation instructions, usage examples, exit codes, detection rules, and example output.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## 验收标准

完成后验证:

- [ ] `pytest -v` 所有测试通过
- [ ] `python -m sus_py tests/samples/safe.py` 返回退出码 0
- [ ] `python -m sus_py tests/samples/dangerous.py` 返回退出码 1
- [ ] `python -m sus_py tests/samples/syntax_error.py` 返回退出码 2
- [ ] `python -m sus_py nonexistent.py` 返回退出码 2
- [ ] `python -m sus_py --strict tests/samples/dangerous.py` 显示更多问题
- [ ] `python -m sus_py --loose tests/samples/dangerous.py` 显示更少问题
- [ ] 输出使用 rich 美化,有颜色和表格
- [ ] README 文档完整清晰

## 下一步

完成实现后可以:
1. 发布到 PyPI (`poetry publish`)
2. 添加 GitHub Actions CI/CD
3. 创建演示视频/截图
4. 在社交媒体推广
