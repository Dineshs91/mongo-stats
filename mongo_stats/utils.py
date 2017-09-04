import json


def json_format(indent=2):
    def inner(f):
        def func_wrapper(*args, **kwargs):
            result = f(*args, **kwargs)

            return json.dumps(result, indent=indent)
        return func_wrapper
    return inner
