import struct
from .ahtb import convert_ahtb_raw, convert_to_ahtb_raw


def convert_message_raw(dat: bytes, tbl: bytes):
    section_count, line_count, total_length, initial_key, section_data_offset = (
        struct.unpack_from("<HHIII", dat)
    )
    assert section_count == 1
    assert initial_key == 0
    assert section_data_offset == 0x10

    table = []
    hash_table = convert_ahtb_raw(tbl)

    (section_length,) = struct.unpack_from("<I", dat, section_data_offset)
    assert total_length == section_length
    section_data = dat[section_data_offset:]
    key = 0x7C89
    for line_num in range(line_count):
        offset, length, flags = struct.unpack_from(
            "<IHH", section_data, 4 + line_num * 8
        )
        line = bytearray(section_data[offset : offset + length * 2])
        temp_key = key

        for char_i in range(len(line) // 2):
            struct.pack_into(
                "<H",
                line,
                char_i * 2,
                struct.unpack_from("<H", line, char_i * 2)[0] ^ temp_key,
            )
            temp_key = (temp_key << 3 | temp_key >> 13) & 0xFFFF

        table.append(
            (
                hash_table[line_num],
                flags,
                line.decode("utf-16-le", "backslashreplace")[:-1],
            )
        )
        key += 0x2983
        key &= 0xFFFF
    if len(hash_table) > line_count:
        table.append((hash_table[line_count], None, None))
    return table


def convert_to_message_raw(data):
    header = bytearray(struct.pack("<HHIII", 1, 0, 0, 0, 0x10))
    hash_table = []
    section_data = bytearray(struct.pack("I", 0))
    line_count = 0
    for _, flags, line in data:
        if flags is None or line is None:
            continue
        section_data += struct.pack("<IHH", 0, len(line) + 1, flags)
        line_count += 1
    key = 0x7C89
    for line_num, (hashed_name, _, line) in enumerate(data):
        hash_table.append(hashed_name)
        if line is None:
            continue
        assert len(section_data) % 4 == 0
        struct.pack_into("I", section_data, 4 + line_num * 8, len(section_data))
        crypt = bytearray((line + "\x00").encode("utf-16-le", "backslashreplace"))
        temp_key = key
        for char_i in range(len(crypt) // 2):
            struct.pack_into(
                "<H",
                crypt,
                char_i * 2,
                struct.unpack_from("<H", crypt, char_i * 2)[0] ^ temp_key,
            )
            temp_key = (temp_key << 3 | temp_key >> 13) & 0xFFFF
        section_data += crypt
        section_data += b"\x00" * (-len(section_data) % 4)
        key += 0x2983
        key &= 0xFFFF

    struct.pack_into("<I", section_data, 0, len(section_data))
    struct.pack_into("<H", header, 2, line_count)
    struct.pack_into("<I", header, 4, len(section_data))
    return bytes(header + section_data), convert_to_ahtb_raw(hash_table)
