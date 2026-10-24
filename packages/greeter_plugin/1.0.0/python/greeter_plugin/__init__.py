import greeter


def cheer(name: str) -> str:
    return greeter.greet(name, excited=True)
