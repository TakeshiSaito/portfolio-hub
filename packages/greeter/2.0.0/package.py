name = 'greeter'
version = '2.0.0'


def commands():
    env.PYTHONPATH.prepend('{root}/python')
    env.PATH.prepend('{root}/bin')
