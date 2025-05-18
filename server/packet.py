from dataclasses import dataclass, asdict
from typing import Any
from enum import Enum
from datetime import datetime

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
    if isinstance(packet.packet_type, PacketType):
        packet.packet_type = packet.packet_type.value

    # ensure timestamps are converted to strings to avoid issues
    if packet.data and packet.data.get("timestamp"):
        packet.data["timestamp"] = datetime.strftime(packet.data["timestamp"], "%Y-%m-%d %H:%M:%S")

    # return the bytes of the packet
    return msgpack.packb(asdict(packet))

def to_packet(data):
    unpacked = msgpack.unpackb(data, raw=False) # convert the bytes to a dict
    packet = Packet(**unpacked) # load that dict into the Packet dataclass

    # convert the packet_type from an int to an Enum
    packet.packet_type = PacketType(packet.packet_type)

    # return the packet
    return packet