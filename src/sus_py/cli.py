"""CLI interface using typer."""
import sys
from pathlib import Path
import typer

from sus_py.analyzer import analyze_code
from sus_py.rules import get_rules
from sus_py.reporter import format_report

app = typer.Typer(help="Static analyzer for detecting suspicious Python code")


@app.command()
def main(
    file_path: Path,
    strict: bool = typer.Option(False, "--strict", help="Use strict mode (blocks all dangerous libraries)"),
    loose: bool = typer.Option(False, "--loose", help="Use loose mode (only warns about eval/exec)"),
):
    """Scan Python file for suspicious code patterns.

    Exit codes:
        0: No security issues detected
        1: Security issues found
        2: Parse error or file not found
    """
    # Debug: print parameters (will be removed after fixing)
    import os
    if os.environ.get('DEBUG_SUS_PY'):
        print(f"DEBUG: strict={strict}, loose={loose}", file=sys.stderr)

    if strict:
        level = 'strict'
    elif loose:
        level = 'loose'
    else:
        level = 'moderate'

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(2)

    try:
        code = file_path.read_text(encoding='utf-8')

        if not code.strip():
            print("All clear (empty file)")
            sys.exit(0)

        rules = get_rules(level)
        issues = analyze_code(code, rules)

        report = format_report(issues, file_path.name)
        print(report)

        sys.exit(1 if issues else 0)

    except SyntaxError as e:
        print(f"Parse Error: Invalid Python syntax at line {e.lineno}")
        sys.exit(2)
    except UnicodeDecodeError:
        print(f"Error: Unable to read file (encoding issue)")
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    app()
