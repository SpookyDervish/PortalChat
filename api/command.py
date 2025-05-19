import inspect, argparse
from enum import Enum
from dataclasses import dataclass

from api import command, Message, Channel


command_registry = {}


class Permission(Enum):
    SEND_MESSAGES = 1
    VIEW_MESSAGE_HISTORY = 2
    MUTE_MEMBERS = 3
    KICK_MEMBERS = 4
    BAN_MEMBERS = 5
    MANAGE_CHANNELS = 6
    MANAGE_SERVER = 7
    SUPER_ADMIN = 8

@dataclass
class CommandContext:
    channel: Channel
    message: Message


def command(name: str, required_permissions: list[Permission] = []):
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
        print(command_registry)
        return wrapper
    return decorator