#!/usr/bin/env python3
"""Answer Tidal's /dirt/handshake so a headless tick can run without SuperDirt."""
import socket


def osc_string(s: str) -> bytes:
    b = s.encode("utf-8") + b"\x00"
    return b + b"\x00" * (-len(b) % 4)


def osc_message(address: str, args: list) -> bytes:
    tags = ","
    body = b""
    for a in args:
        if isinstance(a, str):
            tags += "s"
            body += osc_string(a)
        else:
            tags += "i"
            body += a.to_bytes(4, "big", signed=True)
    return osc_string(address) + osc_string(tags) + body


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 57199))
reply = osc_message("/dirt/handshake/reply", ["&controlBusIndices"] + [0] * 12)
while True:
    data, addr = sock.recvfrom(65535)
    if b"/dirt/handshake" in data:
        sock.sendto(reply, addr)
