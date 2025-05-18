from dataclasses import dataclass
from typing import Any
from enum import Enum


class PacketType(Enum):
    CONNECTION_STARTED = 1
    MESSAGE_RECV = 2
    MESSAGE_SEND = 3
    SYSTEM_MESSAGE = 4
    PING = 5
    GET = 6
    DATA = 7
    ERROR = 8
    DISCONNECT = 9
    WAIT = 10
    NOTIFICATION = 11
    STOP = 12

@dataclass
class Packet:
    packet_type: PacketType
    data: Any = None
    tag: str = None