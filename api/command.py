import inspect, argparse


command_registry = {}


def command(name: str):
    def decorator(func):
        sig = inspect.signature(func)
        parser = argparse.ArgumentParser(prog=f"/{name}")
        
        for param in sig.parameters.values():
            param_name = param.name
            param_type = param.annotation if param.annotation != inspect._empty else str
            default = param.default

            # Positional argument
            if default == inspect._empty:
                parser.add_argument(param_name, type=param_type)
            # Optional argument
            elif isinstance(default, bool):
                parser.add_argument(f"--{param_name}", action='store_true')
            else:
                parser.add_argument(f"--{param_name}", type=param_type, default=default)

        def wrapper(args):
            try:
                parsed = parser.parse_args(args)
                kwargs = vars(parsed)
                func(**kwargs)
            except SystemExit:
                pass # TODO: help message

        command_registry[name] = wrapper
        return wrapper
    return decorator