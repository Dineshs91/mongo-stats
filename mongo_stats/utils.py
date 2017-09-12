import json
from contextlib import ContextDecorator


def json_format(indent=2):
    def inner(f):
        def func_wrapper(*args, **kwargs):
            result = f(*args, **kwargs)

            return json.dumps(result, indent=indent)
        return func_wrapper
    return inner


class screen_col(ContextDecorator):
    def __init__(self, screen, col):
        self.screen = screen
        self.col = col
        self.actual_col = self.screen.init_col
        self.screen.init_col = col

        self.actual_col = self.screen.col

    def __enter__(self):
        self.screen.col = self.col

    def __exit__(self, *exc):
        self.screen.init_col = self.actual_col
        self.screen.col = self.actual_col
