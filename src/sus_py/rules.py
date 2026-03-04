"""Security rules for different strictness levels."""

STRICT_RULES = {
    'dangerous_imports': {
        'os': {'severity': 'CRITICAL', 'reason': 'Direct OS access can execute arbitrary commands'},
        'subprocess': {'severity': 'CRITICAL', 'reason': 'Can spawn processes and execute shell commands'},
        'shutil': {'severity': 'HIGH', 'reason': 'Can delete files and directories'},
        'sys': {'severity': 'MEDIUM', 'reason': 'Can modify system state and exit program'},
        'socket': {'severity': 'HIGH', 'reason': 'Can create network connections'}
    },
    'dangerous_calls': {
        'eval': {'severity': 'CRITICAL', 'reason': 'Executes arbitrary Python code'},
        'exec': {'severity': 'CRITICAL', 'reason': 'Executes arbitrary Python statements'},
        'compile': {'severity': 'HIGH', 'reason': 'Compiles code that can be executed later'},
        '__import__': {'severity': 'MEDIUM', 'reason': 'Dynamic import can bypass static analysis'},
        'os.system': {'severity': 'CRITICAL', 'reason': 'Executes shell commands directly'},
        'subprocess.call': {'severity': 'CRITICAL', 'reason': 'Spawns subprocess with shell access'},
        'subprocess.run': {'severity': 'CRITICAL', 'reason': 'Spawns subprocess with shell access'},
        'subprocess.Popen': {'severity': 'CRITICAL', 'reason': 'Spawns subprocess with full control'},
        'shutil.rmtree': {'severity': 'CRITICAL', 'reason': 'Recursively deletes directory trees'}
    }
}

MODERATE_RULES = {
    'dangerous_imports': {
        'subprocess': STRICT_RULES['dangerous_imports']['subprocess'],
        'shutil': STRICT_RULES['dangerous_imports']['shutil']
    },
    'dangerous_calls': {
        'eval': STRICT_RULES['dangerous_calls']['eval'],
        'exec': STRICT_RULES['dangerous_calls']['exec'],
        'os.system': STRICT_RULES['dangerous_calls']['os.system'],
        'subprocess.call': STRICT_RULES['dangerous_calls']['subprocess.call'],
        'subprocess.run': STRICT_RULES['dangerous_calls']['subprocess.run'],
        'subprocess.Popen': STRICT_RULES['dangerous_calls']['subprocess.Popen']
    }
}

LOOSE_RULES = {
    'dangerous_imports': {},
    'dangerous_calls': {
        'eval': STRICT_RULES['dangerous_calls']['eval'],
        'exec': STRICT_RULES['dangerous_calls']['exec']
    }
}

def get_rules(level: str) -> dict:
    """Get rules for the specified strictness level."""
    rules_map = {
        'strict': STRICT_RULES,
        'moderate': MODERATE_RULES,
        'loose': LOOSE_RULES
    }
    return rules_map.get(level, MODERATE_RULES)
