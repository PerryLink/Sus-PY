"""Report formatting using rich."""
from typing import List, Dict, Any


def format_report(issues: List[Dict[str, Any]], filename: str) -> str:
    """Format security issues as a rich report.

    Args:
        issues: List of security issues found
        filename: Name of the file being scanned

    Returns:
        Formatted report string
    """
    if not issues:
        return "All clear - No security issues detected"

    # Build simple text report without emoji to avoid encoding issues
    lines = [f"\nSecurity Issues in {filename}"]
    lines.append("=" * 80)

    for issue in issues:
        lines.append(f"Line {issue['line']}: {issue['name']} ({issue['severity']})")
        lines.append(f"  Type: {issue['type']}")
        lines.append(f"  Reason: {issue['reason']}")
        lines.append("")

    lines.append("Scan Failed. Do not run this code.")

    return "\n".join(lines)
