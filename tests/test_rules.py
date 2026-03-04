from sus_py.rules import STRICT_RULES, MODERATE_RULES, LOOSE_RULES, get_rules

def test_strict_rules_contain_os():
    assert 'os' in STRICT_RULES['dangerous_imports']
    assert 'eval' in STRICT_RULES['dangerous_calls']

def test_moderate_rules_subset():
    assert 'subprocess' in MODERATE_RULES['dangerous_imports']
    assert 'eval' in MODERATE_RULES['dangerous_calls']

def test_loose_rules_minimal():
    assert 'eval' in LOOSE_RULES['dangerous_calls']
    assert len(LOOSE_RULES.get('dangerous_imports', {})) == 0

def test_get_rules_strict():
    rules = get_rules('strict')
    assert rules == STRICT_RULES

def test_get_rules_default():
    rules = get_rules('moderate')
    assert rules == MODERATE_RULES
