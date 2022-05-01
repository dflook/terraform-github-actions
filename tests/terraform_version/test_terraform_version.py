from terraform.versions import Version, Constraint
from terraform.exec import init_args

def test_init_args():
    assert init_args({
        'INPUT_BACKEND_CONFIG_FILE': '',
        'INPUT_BACKEND_CONFIG': '',
        'INPUT_PATH': '.'
    }) == []

    assert init_args({
        'INPUT_BACKEND_CONFIG_FILE': 'tests/hello/terraform.backendconfig',
        'INPUT_BACKEND_CONFIG': '',
        'INPUT_PATH': '.'
    }) == ['-backend-config=tests/hello/terraform.backendconfig']

    assert init_args({
        'INPUT_BACKEND_CONFIG_FILE': 'tests/hello/terraform.backendconfig',
        'INPUT_BACKEND_CONFIG': '',
        'INPUT_PATH': 'tests'
    }) == ['-backend-config=hello/terraform.backendconfig']

    assert init_args({
        'INPUT_BACKEND_CONFIG_FILE': 'tests/terraform.backendconfig',
        'INPUT_BACKEND_CONFIG': '',
        'INPUT_PATH': 'tests/hello'
    }) == ['-backend-config=../terraform.backendconfig']

    assert init_args({
        'INPUT_BACKEND_CONFIG_FILE': '''
        tests/terraform.backendconfig
        env/prod/terraform.backendconfig,env/common.backendconfig
        ''',
        'INPUT_BACKEND_CONFIG': '',
        'INPUT_PATH': '.'
    }) == ['-backend-config=tests/terraform.backendconfig', '-backend-config=env/prod/terraform.backendconfig', '-backend-config=env/common.backendconfig']

    assert init_args({
        'INPUT_BACKEND_CONFIG_FILE': '',
        'INPUT_BACKEND_CONFIG': 'test=hello',
        'INPUT_PATH': '.'
    }) == ['-backend-config=test=hello']

    assert init_args({
        'INPUT_BACKEND_CONFIG_FILE': '',
        'INPUT_BACKEND_CONFIG': '''
        
        "test=hello"
        
        foo=bar,xyz=abc
        
        ''',
        'INPUT_PATH': '.'
    }) == ['-backend-config="test=hello"', '-backend-config=foo=bar', '-backend-config=xyz=abc']

def test_version():
    v0_1_1 = Version('0.1.1')
    assert v0_1_1.major == 0 and v0_1_1.minor == 1 and v0_1_1.patch == 1 and v0_1_1.pre_release == ''
    assert str(v0_1_1) == '0.1.1'

    v1_0_11 = Version('1.0.11')
    assert v1_0_11.major == 1 and v1_0_11.minor == 0 and v1_0_11.patch == 11 and v1_0_11.pre_release == ''
    assert str(v1_0_11) == '1.0.11'

    v0_15_0_rc2 = Version('0.15.0-rc2')
    assert v0_15_0_rc2.major == 0 and v0_15_0_rc2.minor == 15 and v0_15_0_rc2.patch == 0 and v0_15_0_rc2.pre_release == 'rc2'
    assert str(v0_15_0_rc2) == '0.15.0-rc2'

    v0_15_0 = Version('0.15.0')
    assert v0_15_0.major == 0 and v0_15_0.minor == 15 and v0_15_0.patch == 0 and v0_15_0.pre_release == ''
    assert str(v0_15_0) == '0.15.0'

    assert v0_1_1 == v0_1_1
    assert v1_0_11 != v0_1_1
    assert v0_15_0_rc2 < v0_15_0
    assert v1_0_11 > v0_15_0 > v0_1_1

def test_constraint():
    constraint = Constraint('0.12.4-hello')
    assert constraint.major == 0 and constraint.minor == 12 and constraint.patch == 4 and constraint.pre_release == 'hello' and constraint.operator == '='
    assert str(constraint) == '=0.12.4-hello'
    assert constraint.is_allowed(Version('0.12.4-hello'))
    assert not constraint.is_allowed(Version('0.12.4'))

    constraint = Constraint('0.12.4')
    assert constraint.major == 0 and constraint.minor == 12 and constraint.patch == 4 and constraint.pre_release == '' and constraint.operator == '='
    assert str(constraint) == '=0.12.4'

    constraint = Constraint(' =  0  .1 2. 4-hello')
    assert constraint.major == 0 and constraint.minor == 12 and constraint.patch == 4 and constraint.pre_release == 'hello' and constraint.operator == '='
    assert str(constraint) == '=0.12.4-hello'

    constraint = Constraint('  =   0  .1 2. 4')
    assert constraint.major == 0 and constraint.minor == 12 and constraint.patch == 4 and constraint.pre_release == '' and constraint.operator == '='
    assert str(constraint) == '=0.12.4'

    constraint = Constraint('  >=  0  .1 2. 4')
    assert constraint.major == 0 and constraint.minor == 12 and constraint.patch == 4 and constraint.pre_release == '' and constraint.operator == '>='
    assert str(constraint) == '>=0.12.4'
    assert constraint.is_allowed(Version('0.12.4'))
    assert constraint.is_allowed(Version('0.12.8'))
    assert constraint.is_allowed(Version('0.13.0'))
    assert constraint.is_allowed(Version('1.1.1'))
    assert not constraint.is_allowed(Version('0.12.3'))
    assert not constraint.is_allowed(Version('0.10.0'))

    constraint = Constraint('  >  0  .1 2. 4')
    assert constraint.major == 0 and constraint.minor == 12 and constraint.patch == 4 and constraint.pre_release == '' and constraint.operator == '>'
    assert str(constraint) == '>0.12.4'
    assert not constraint.is_allowed(Version('0.12.4'))
    assert constraint.is_allowed(Version('0.12.8'))
    assert constraint.is_allowed(Version('0.13.0'))
    assert constraint.is_allowed(Version('1.1.1'))
    assert not constraint.is_allowed(Version('0.12.3'))
    assert not constraint.is_allowed(Version('0.10.0'))

    constraint = Constraint('  <  0  .1 2. 4')
    assert constraint.major == 0 and constraint.minor == 12 and constraint.patch == 4 and constraint.pre_release == '' and constraint.operator == '<'
    assert str(constraint) == '<0.12.4'
    assert not constraint.is_allowed(Version('0.12.4'))
    assert not constraint.is_allowed(Version('0.12.8'))
    assert not constraint.is_allowed(Version('0.13.0'))
    assert not constraint.is_allowed(Version('1.1.1'))
    assert constraint.is_allowed(Version('0.12.3'))
    assert constraint.is_allowed(Version('0.10.0'))

    constraint = Constraint(' <= 0  .1 2. 4')
    assert constraint.major == 0 and constraint.minor == 12 and constraint.patch == 4 and constraint.pre_release == '' and constraint.operator == '<='
    assert str(constraint) == '<=0.12.4'
    assert constraint.is_allowed(Version('0.12.4'))
    assert not constraint.is_allowed(Version('0.12.8'))
    assert not constraint.is_allowed(Version('0.13.0'))
    assert not constraint.is_allowed(Version('1.1.1'))
    assert constraint.is_allowed(Version('0.12.3'))
    assert constraint.is_allowed(Version('0.10.0'))

    constraint = Constraint('  !=  0  .1 2. 4')
    assert constraint.major == 0 and constraint.minor == 12 and constraint.patch == 4 and constraint.pre_release == '' and constraint.operator == '!='
    assert str(constraint) == '!=0.12.4'
    assert not constraint.is_allowed(Version('0.12.4'))
    assert constraint.is_allowed(Version('0.12.8'))
    assert constraint.is_allowed(Version('0.13.0'))
    assert constraint.is_allowed(Version('1.1.1'))
    assert constraint.is_allowed(Version('0.12.3'))
    assert constraint.is_allowed(Version('0.10.0'))

    constraint = Constraint('1')
    assert (
        constraint.major == 1
        and constraint.minor is None
        and constraint.patch is None
        and constraint.pre_release == ''
        and constraint.operator == '='
    )

    assert str(constraint) == '=1'
    assert constraint.is_allowed(Version('1.0.0'))
    assert not constraint.is_allowed(Version('1.0.1'))
    assert not constraint.is_allowed(Version('0.0.9'))
    assert not constraint.is_allowed(Version('1.0.0-wooo'))

    constraint = Constraint('1.2')
    assert (
        constraint.major == 1
        and constraint.minor == 2
        and constraint.patch is None
        and constraint.pre_release == ''
        and constraint.operator == '='
    )

    assert str(constraint) == '=1.2'

    constraint = Constraint('~>1.2.3')
    assert constraint.major == 1 and constraint.minor == 2 and constraint.patch == 3 and constraint.pre_release == '' and constraint.operator == '~>'
    assert str(constraint) == '~>1.2.3'

    constraint = Constraint('~>1.2')
    assert (
        constraint.major == 1
        and constraint.minor == 2
        and constraint.patch is None
        and constraint.pre_release == ''
        and constraint.operator == '~>'
    )

    assert str(constraint) == '~>1.2'

    assert Constraint('0.12.0') < Constraint('0.12.1')
    assert Constraint('0.12.0') == Constraint('0.12.0')
    assert Constraint('0.12.0') != Constraint('0.15.0')

    test_ordering = [
        Constraint('0.11.0'),
        Constraint('<0.12.0'),
        Constraint('<=0.12.0'),
        Constraint('0.12.0'),
        Constraint('~>0.12.0'),
        Constraint('>=0.12.0'),
        Constraint('>0.12.0'),
        Constraint('0.12.5'),
        Constraint('0.13.0'),
    ]
    assert test_ordering == sorted(test_ordering)
