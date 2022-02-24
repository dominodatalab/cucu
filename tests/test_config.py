from cucu.config import CONFIG


def test_config_lookup_for_inexistent_is_none():
    assert CONFIG['INEXISTENT'] is None


def test_config_lookup_env_works():
    assert CONFIG['HOME'] is not None


def test_config_lookup_env_precedes_internal_value():
    env_value = CONFIG['HOME']
    CONFIG['HOME'] = 'foo'
    assert CONFIG['HOME'] == env_value


def test_config_true_method():
    CONFIG['VAR1'] = 'true'
    assert CONFIG.true('VAR1')
    assert CONFIG.true('INEXISTENT') is False


def test_config_false_method():
    CONFIG['VAR1'] = 'false'
    assert CONFIG.false('VAR1')
    CONFIG['VAR1'] = 'true'
    assert CONFIG.false('VAR1') is False
    assert CONFIG.false('INEXISTENT')


def test_config_resolves_variables():
    CONFIG['VAR1'] = 'foo'
    CONFIG['VAR2'] = 'bar'
    assert CONFIG.resolve('{VAR1} and {VAR2}') == 'foo and bar'
