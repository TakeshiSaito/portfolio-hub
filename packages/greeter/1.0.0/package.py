name = 'greeter'
version = '1.0.0'


def commands():
    env.PYTHONPATH.prepend('{root}/python')
    env.PATH.prepend('{root}/bin')
