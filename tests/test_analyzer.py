"""Tests for the AST analyzer."""
from sus_py.analyzer import analyze_code
from sus_py.rules import STRICT_RULES, MODERATE_RULES


def test_detect_dangerous_import():
    """Test detection of dangerous import statement."""
    code = "import os"
    issues = analyze_code(code, STRICT_RULES)
    assert len(issues) == 1
    assert issues[0]['type'] == 'import'
    assert issues[0]['name'] == 'os'
    assert issues[0]['severity'] == 'CRITICAL'


def test_detect_dangerous_from_import():
    """Test detection of dangerous from-import statement."""
    code = "from subprocess import call"
    issues = analyze_code(code, STRICT_RULES)
    assert len(issues) == 1
    assert issues[0]['type'] == 'import'
    assert issues[0]['name'] == 'subprocess'


def test_detect_dangerous_call():
    """Test detection of dangerous function call."""
    code = "eval('1+1')"
    issues = analyze_code(code, STRICT_RULES)
    assert len(issues) == 1
    assert issues[0]['type'] == 'call'
    assert issues[0]['name'] == 'eval'


def test_detect_attribute_call():
    """Test detection of dangerous attribute call like os.system()."""
    code = "import os\nos.system('ls')"
    issues = analyze_code(code, STRICT_RULES)
    assert len(issues) == 2
    assert any(issue['name'] == 'os.system' for issue in issues)


def test_safe_code():
    """Test that safe code returns no issues."""
    code = "import json\nprint('hello')"
    issues = analyze_code(code, STRICT_RULES)
    assert len(issues) == 0


def test_moderate_rules():
    """Test that moderate rules detect fewer issues."""
    code = "import os"
    issues = analyze_code(code, MODERATE_RULES)
    assert len(issues) == 0  # os not in MODERATE_RULES
