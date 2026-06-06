from importlib.resources import files
from .util import flatbuffer_binary_to_json, json_to_flatbuffer_binary

SCHEMA = (files(__package__) / "gfbanmcfg.fbs").read_text(encoding="utf-8")


def convert_gfbanmcfg_raw(data: bytes, out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(flatbuffer_binary_to_json(data, SCHEMA))


def convert_gfbanmcfg(in_path: str, out_path: str):
    with open(in_path, "rb") as in_f:
        convert_gfbanmcfg_raw(in_f.read(), out_path)


def convert_to_gfbanmcfg_raw(data: str) -> bytes:
    return json_to_flatbuffer_binary(data, SCHEMA)


def convert_to_gfbanmcfg(in_path: str, out_path: str):
    with open(in_path, "r", encoding="utf-8") as in_f:
        with open(out_path, "wb") as out_f:
            out_f.write(convert_to_gfbanmcfg_raw(in_f.read()))
