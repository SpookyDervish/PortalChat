from dataclasses import dataclass, asdict
from typing import Any
from enum import Enum

import msgpack


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


def to_bytes(packet: Packet):
        # convert the packet to a dict, and then convert it to be bytes
        # so it can be sent over the socket
        packet_type = packet.packet_type.value
        packet.packet_type = packet_type

        return msgpack.packb(asdict(packet))

def to_packet(data):
    unpacked = msgpack.unpackb(data, raw=False) # convert the bytes to a dict
    return Packet(**unpacked) # load that dict into the Packet dataclass