import struct


def fnv1a(s: str):
    """FNV1a hash"""
    h = 0xCBF29CE484222645
    for c in s:
        h ^= ord(c)
        h *= 0x00000100000001B3
        h &= 0xFFFFFFFFFFFFFFFF
    return h


def convert_ahtb_raw(data: bytes):
    assert struct.unpack_from("I", data) == (0x42544841,)
    (count,) = struct.unpack_from("I", data, 4)
    offset = 8
    table = []
    for _ in range(count):
        (hash_,) = struct.unpack_from("Q", data, offset)
        (length,) = struct.unpack_from("H", data, offset + 8)
        (name,) = struct.unpack_from(f"{length}s", data, offset + 10)
        offset += 10 + length
        table.append(name.decode("utf-8")[:-1])
        assert hash_ == fnv1a(table[-1])

    return table


def convert_to_ahtb_raw(data: list):
    table = b""
    table += struct.pack("I", 0x42544841)
    table += struct.pack("I", len(data))
    for name in data:
        table += struct.pack("Q", fnv1a(name))
        table += struct.pack("H", len(name) + 1)
        table += name.encode("utf-8")
        table += b"\x00"
    return table
