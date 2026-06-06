from importlib.resources import files
from .util import flatbuffer_binary_to_json, json_to_flatbuffer_binary

SCHEMA = (files(__package__) / "gfbanm.fbs").read_text(encoding="utf-8")


def convert_gfbanm_raw(data: bytes, out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(flatbuffer_binary_to_json(data, SCHEMA))


def convert_gfbanm(in_path: str, out_path: str):
    with open(in_path, "rb") as in_f:
        convert_gfbanm_raw(in_f.read(), out_path)


def convert_to_gfbanm_raw(data: str) -> bytes:
    return json_to_flatbuffer_binary(data, SCHEMA)


def convert_to_gfbanm(in_path: str, out_path: str):
    with open(in_path, "r", encoding="utf-8") as in_f:
        with open(out_path, "wb") as out_f:
            out_f.write(convert_to_gfbanm_raw(in_f.read()))
