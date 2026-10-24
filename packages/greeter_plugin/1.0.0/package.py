name = 'greeter_plugin'
version = '1.0.0'
requires = ['greeter-2']


def commands():
    env.PYTHONPATH.prepend('{root}/python')
    env.PATH.prepend('{root}/bin')
