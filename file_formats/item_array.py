import struct
from dataclasses import dataclass, asdict, astuple, field


@dataclass(frozen=True)
class ItemData:
    table_index: int = field(compare=False)
    price: int
    price_watts: int
    price_other: int
    item_sprite: int
    field_5: int
    field_6: int
    field_7: int
    field_8: int
    field_9: int
    field_10: int
    field_11: int
    field_12: int
    field_13: int
    pouch: int
    effect_field: int
    field_16: int
    can_use_on_pokemon: int
    field_18: int
    field_19: int
    field_20: int
    field_21: int
    group_type: int
    group_index: int
    field_24: int
    field_25: int
    field_26: int
    field_27: int
    field_28: int
    field_29: int
    field_30: int
    field_31: int
    field_32: int
    field_33: int
    field_34: int
    field_35: int
    field_36: int
    field_37: int
    field_38: int
    field_39: int
    field_40: int
    field_41: int
    field_42: int
    field_43: int
    field_44: int
    field_45: int
    field_46: int
    field_47: int
    field_48: int
    field_49: int
    field_50: int
    field_51: int
    field_52: int
    field_53: int
    field_54: int
    field_55: int
    field_56: int
    field_57: int
    field_58: int
    field_59: int
    field_60: int
    field_61: int
    field_62: int
    field_63: int
    field_64: int
    field_65: int
    field_66: int
    field_67: int
    field_68: int
    field_69: int
    field_70: int

    @classmethod
    def from_dict(cls, data):
        if not hasattr(data, "table_index"):
            data["table_index"] = 0
        return cls(**data)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_bytes(cls, table_index, data):
        def get(size, offset, shift=0, bit_size=0):
            mask = (1 << bit_size) - 1
            if bit_size == 0:
                mask = 0xFFFFFFFFFFFFFFFF
            return (struct.unpack_from(size, data, offset)[0] >> shift) & mask

        return cls(
            table_index,
            get("I", 0),
            get("I", 4),
            get("I", 8),
            get("H", 0x1A),
            get("B", 0xC),
            get("B", 0xD),
            get("B", 0xE),
            get("H", 0x10, 0xC, 1),
            get("B", 0x12),
            get("B", 0xF),
            get("H", 0x10, 0, 5),
            get("H", 0x10, 5, 1),
            get("H", 0x10, 6, 1),
            get("B", 0x11, 0, 4),
            get("B", 0x13),
            get("B", 0x14),
            get("B", 0x15),
            get("B", 0x16),
            get("B", 0x17, 0, 4),
            get("B", 0x17, 4),
            get("B", 0x18),
            get("B", 0x1C),
            get("B", 0x1D),
            get("H", 0x10, 7, 1),
            get("H", 0x10, 0xD, 1),
            get("I", 0x1E, 0, 1),
            get("I", 0x1E, 1, 1),
            get("I", 0x1E, 2, 1),
            get("I", 0x1E, 3, 1),
            get("I", 0x1E, 4, 1),
            get("I", 0x1E, 5, 1),
            get("I", 0x1E, 6, 1),
            get("I", 0x1E, 7, 1),
            get("I", 0x1E, 8, 1),
            get("I", 0x1E, 9, 1),
            get("I", 0x1E, 10, 1),
            get("I", 0x1E, 0xB, 1),
            get("I", 0x1E, 0xC, 4),
            get("H", 0x20, 0, 4),
            get("I", 0x1E, 0x14, 4),
            get("B", 0x21, 0, 4),
            get("I", 0x1E, 0x1C),
            get("H", 0x22, 0, 4),
            get("H", 0x22, 4, 2),
            get("H", 0x22, 6, 1),
            get("H", 0x22, 7, 1),
            get("B", 0x23, 0, 1),
            get("H", 0x22, 9, 1),
            get("H", 0x22, 10, 1),
            get("H", 0x22, 0xB, 1),
            get("H", 0x22, 0xC, 1),
            get("H", 0x22, 0xD, 1),
            get("H", 0x22, 0xE, 1),
            get("H", 0x22, 0xF),
            get("B", 0x24, 0, 1),
            get("B", 0x24, 1, 1),
            get("B", 0x24, 2, 1),
            get("B", 0x24, 3, 1),
            get("B", 0x24, 4, 1),
            get("B", 0x25),
            get("B", 0x26),
            get("B", 0x27),
            get("B", 0x28),
            get("B", 0x29),
            get("B", 0x2A),
            get("B", 0x2B),
            get("B", 0x2C),
            get("B", 0x2D),
            get("B", 0x2E),
            get("B", 0x2F),
        )

    def to_bytes(self):
        data = bytearray(0x30)

        def write(value, size, offset, shift=0, bit_size=0):
            base = struct.unpack_from(size, data, offset)[0]
            mask = (1 << bit_size) - 1
            if bit_size == 0:
                mask = 0xFFFFFFFFFFFFFFFF
            base &= ~(mask << shift)
            base |= (value & mask) << shift
            struct.pack_into(size, data, offset, base)

        fields = astuple(self)[1:]

        # TODO: use named fields
        write(fields[0], "I", 0)
        write(fields[1], "I", 4)
        write(fields[2], "I", 8)
        write(fields[3], "H", 0x1A)
        write(fields[4], "B", 0xC)
        write(fields[5], "B", 0xD)
        write(fields[6], "B", 0xE)
        write(fields[7], "H", 0x10, 0xC, 1)
        write(fields[8], "B", 0x12)
        write(fields[9], "B", 0xF)
        write(fields[10], "H", 0x10, 0, 5)
        write(fields[11], "H", 0x10, 5, 1)
        write(fields[12], "H", 0x10, 6, 1)
        write(fields[13], "B", 0x11, 0, 4)
        write(fields[14], "B", 0x13)
        write(fields[15], "B", 0x14)
        write(fields[16], "B", 0x15)
        write(fields[17], "B", 0x16)
        write(fields[18], "B", 0x17, 0, 4)
        write(fields[19], "B", 0x17, 4)
        write(fields[20], "B", 0x18)
        write(fields[21], "B", 0x1C)
        write(fields[22], "B", 0x1D)
        write(fields[23], "H", 0x10, 7, 1)
        write(fields[24], "H", 0x10, 0xD, 1)
        write(fields[25], "I", 0x1E, 0, 1)
        write(fields[26], "I", 0x1E, 1, 1)
        write(fields[27], "I", 0x1E, 2, 1)
        write(fields[28], "I", 0x1E, 3, 1)
        write(fields[29], "I", 0x1E, 4, 1)
        write(fields[30], "I", 0x1E, 5, 1)
        write(fields[31], "I", 0x1E, 6, 1)
        write(fields[32], "I", 0x1E, 7, 1)
        write(fields[33], "I", 0x1E, 8, 1)
        write(fields[34], "I", 0x1E, 9, 1)
        write(fields[35], "I", 0x1E, 10, 1)
        write(fields[36], "I", 0x1E, 0xB, 1)
        write(fields[37], "I", 0x1E, 0xC, 4)
        write(fields[38], "H", 0x20, 0, 4)
        write(fields[39], "I", 0x1E, 0x14, 4)
        write(fields[40], "B", 0x21, 0, 4)
        write(fields[41], "I", 0x1E, 0x1C)
        write(fields[42], "H", 0x22, 0, 4)
        write(fields[43], "H", 0x22, 4, 2)
        write(fields[44], "H", 0x22, 6, 1)
        write(fields[45], "H", 0x22, 7, 1)
        write(fields[46], "B", 0x23, 0, 1)
        write(fields[47], "H", 0x22, 9, 1)
        write(fields[48], "H", 0x22, 10, 1)
        write(fields[49], "H", 0x22, 0xB, 1)
        write(fields[50], "H", 0x22, 0xC, 1)
        write(fields[51], "H", 0x22, 0xD, 1)
        write(fields[52], "H", 0x22, 0xE, 1)
        write(fields[53], "H", 0x22, 0xF)
        write(fields[54], "B", 0x24, 0, 1)
        write(fields[55], "B", 0x24, 1, 1)
        write(fields[56], "B", 0x24, 2, 1)
        write(fields[57], "B", 0x24, 3, 1)
        write(fields[58], "B", 0x24, 4, 1)
        write(fields[59], "B", 0x25)
        write(fields[60], "B", 0x26)
        write(fields[61], "B", 0x27)
        write(fields[62], "B", 0x28)
        write(fields[63], "B", 0x29)
        write(fields[64], "B", 0x2A)
        write(fields[65], "B", 0x2B)
        write(fields[66], "B", 0x2C)
        write(fields[67], "B", 0x2D)
        write(fields[68], "B", 0x2E)
        write(fields[69], "B", 0x2F)

        return data


def convert_item_array_raw(data: bytes):
    count, last, highest_entry, tm_section_size = struct.unpack_from("HHHH", data)
    assert count == last
    # some code uses a hardcoded offset which requires this section to be 200 entries long
    assert tm_section_size == 200
    sublist_sizes = struct.unpack_from("12B", data, 8)
    sublist_last_entries = struct.unpack_from("12B", data, 0x14)
    category_sizes = struct.unpack_from("16H", data, 0x20)
    # enforced for whatever reason shield@710141fd10
    for category_size, limit in zip(
        category_sizes, (61, 31, 21, 81, 551, 211, 101, 101, 65)
    ):
        assert category_size < limit
    (data_offset,) = struct.unpack_from("I", data, 0x40)
    assert data_offset + highest_entry * 0x30 == len(data)
    item_indexes = struct.unpack_from(f"{count}H", data, 0x44)
    assert all(0 <= index < highest_entry for index in item_indexes)
    item_data = [
        ItemData.from_bytes(
            index, data[data_offset + index * 0x30 : data_offset + index * 0x30 + 0x30]
        )
        for index in item_indexes
    ]
    tm_info = list(
        struct.iter_unpack(
            "HH", data[0x44 + count * 2 : 0x44 + count * 2 + tm_section_size * 4]
        )
    )
    offset = 0x44 + count * 2 + tm_section_size * 4
    sublists = []
    for sublist_size in sublist_sizes:
        sublists.append(struct.unpack_from(f"{sublist_size}H", data, offset))
        offset += sublist_size * 2
    assert offset == data_offset

    return {
        "item_data": [i.to_dict() for i in item_data],
        "tm_info": tm_info,
        "sublists": sublists,
        "category_sizes": category_sizes,
    }


def convert_to_item_array_raw(data: dict, preserve_table_indexes=False):
    item_data = [ItemData.from_dict(i) for i in data["item_data"]]
    deduplicated_item_data = list(set(item_data))
    if preserve_table_indexes:
        table_len = max(item_data, key=lambda i: i.table_index).table_index + 1
    else:
        table_len = len(deduplicated_item_data)
    array = bytearray(
        struct.pack(
            "HHHH",
            len(item_data),
            len(item_data),
            table_len,
            200,
        )
    )
    array += struct.pack("12B", *(len(sublist) for sublist in data["sublists"]))
    array += struct.pack(
        "12B", *(len(sublist) - sublist.count(0) for sublist in data["sublists"])
    )
    array += struct.pack("16H", *data["category_sizes"])
    array += struct.pack("I", 0)

    preserved_table = [None] * table_len
    for item in item_data:
        if preserve_table_indexes:
            array += struct.pack("H", item.table_index)
            assert (
                preserved_table[item.table_index] is None
                or preserved_table[item.table_index] == item
            ), f"Duplicate table index {item.table_index}"
            preserved_table[item.table_index] = item
        else:
            array += struct.pack("H", deduplicated_item_data.index(item))

    for info in data["tm_info"]:
        array += struct.pack("HH", *info)

    for sublist in data["sublists"]:
        array += struct.pack(f"{len(sublist)}H", *sublist)

    data_offset = len(array)
    struct.pack_into("I", array, 0x40, data_offset)

    if preserve_table_indexes:
        for i, item in enumerate(preserved_table):
            assert item is not None, f"No item assigned to table index {i}"
            array += item.to_bytes()
    else:
        for item in deduplicated_item_data:
            array += item.to_bytes()

    return array
