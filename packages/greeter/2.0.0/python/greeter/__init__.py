__version__ = "2.0.0"


def greet(name: str, excited: bool = False) -> str:
    return f"Hello, {name}{'!!!' if excited else '!'}"
