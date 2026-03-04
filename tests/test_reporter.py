"""Tests for the reporter module."""
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
