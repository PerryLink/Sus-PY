"""AST-based security analyzer."""
import ast
from typing import List, Dict, Any


class SecurityVisitor(ast.NodeVisitor):
    """AST visitor that detects dangerous imports and calls."""

    def __init__(self, rules: dict):
        self.rules = rules
        self.issues: List[Dict[str, Any]] = []

    def visit_Import(self, node: ast.Import):
        """Check for dangerous imports like 'import os'."""
        for alias in node.names:
            if alias.name in self.rules.get('dangerous_imports', {}):
                rule = self.rules['dangerous_imports'][alias.name]
                self.issues.append({
                    'line': node.lineno,
                    'type': 'import',
                    'name': alias.name,
                    'severity': rule['severity'],
                    'reason': rule['reason']
                })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Check for dangerous from imports like 'from os import system'."""
        if node.module and node.module in self.rules.get('dangerous_imports', {}):
            rule = self.rules['dangerous_imports'][node.module]
            self.issues.append({
                'line': node.lineno,
                'type': 'import',
                'name': node.module,
                'severity': rule['severity'],
                'reason': rule['reason']
            })
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Check for dangerous function calls like 'eval()' or 'os.system()'."""
        # Simple function call: eval()
        if isinstance(node.func, ast.Name):
            if node.func.id in self.rules.get('dangerous_calls', {}):
                rule = self.rules['dangerous_calls'][node.func.id]
                self.issues.append({
                    'line': node.lineno,
                    'type': 'call',
                    'name': node.func.id,
                    'severity': rule['severity'],
                    'reason': rule['reason']
                })
        # Attribute call: os.system()
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                call_name = f"{node.func.value.id}.{node.func.attr}"
                if call_name in self.rules.get('dangerous_calls', {}):
                    rule = self.rules['dangerous_calls'][call_name]
                    self.issues.append({
                        'line': node.lineno,
                        'type': 'call',
                        'name': call_name,
                        'severity': rule['severity'],
                        'reason': rule['reason']
                    })
        self.generic_visit(node)


def analyze_code(code: str, rules: dict) -> List[Dict[str, Any]]:
    """Analyze Python code and return list of security issues."""
    tree = ast.parse(code)
    visitor = SecurityVisitor(rules)
    visitor.visit(tree)
    return visitor.issues
