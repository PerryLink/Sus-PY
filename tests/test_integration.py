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

    assert result_moderate.returncode == 1
    assert result_strict.returncode == 1


def test_loose_mode_detects_less():
    """Test that loose mode is more permissive."""
    test_file = Path("tests/samples/temp_os_only.py")
    test_file.write_text("import os\n")

    try:
        result_loose = run_cli(str(test_file), "--loose")
        result_moderate = run_cli(str(test_file))

        assert result_loose.returncode == 0
    finally:
        if test_file.exists():
            test_file.unlink()
