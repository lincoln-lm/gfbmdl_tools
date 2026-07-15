import argparse
from io import BytesIO
import os
import struct
from dataclasses import dataclass
import json
import subprocess
import lz4.block

from file_formats import gfbmdl, gfbanm, gfbanmcfg, gfbpokecfg, bntx, bnsh


def fnv1a(s: str):
    """FNV1a hash"""
    h = 0xCBF29CE484222645
    for c in s:
        h ^= ord(c)
        h *= 0x00000100000001B3
        h &= 0xFFFFFFFFFFFFFFFF
    return h


hashes_path = os.path.join(os.path.dirname(__file__), "hashes.json")
if os.path.exists(hashes_path):
    with open(hashes_path, "r", encoding="utf-8") as f:
        HASHES = json.load(f)
else:
    HASHES = {}


class GFPak:
    """GFPAK file serializer"""

    @dataclass
    class Folder:
        folder_hash: int
        file_count: int
        padding: int
        files: list

    @dataclass
    class File:
        level: int
        compression_type: int
        decompressed_size: int
        compressed_size: int
        padding: int
        offset: int
        unused: int

    @dataclass
    class FileMeta:
        file_hash: int
        index: int
        padding: int

    def __init__(self) -> None:
        self.version = 0x1000
        self.file_count = 0
        self.folder_count = 0
        self.table_offset = None
        self.paths_offset = None
        self.folder_offsets = []
        self.absolute_hashes = []
        self.folders = []
        self.table = []
        self.decompressed_files = []

    def serialize_gfpak(self, gfpak_name: str) -> None:
        # TODO: find a better solution than dual streams
        if not gfpak_name.endswith(".gfpak"):
            gfpak_name += ".gfpak"
        buffer = BytesIO()
        buffer.write(b"GFLXPACK")
        buffer.write(
            struct.pack("IIII", self.version, 0, self.file_count, self.folder_count)
        )
        buffer.write(struct.pack("QQ", 0, 0))
        buffer.write(struct.pack("Q" * self.folder_count, *((0,) * self.folder_count)))
        paths_offset = buffer.tell()
        buffer.write(struct.pack("Q" * self.file_count, *self.absolute_hashes))
        folder_offsets = []
        for folder in self.folders:
            folder_offsets.append(buffer.tell())
            buffer.write(
                struct.pack("QII", folder.folder_hash, folder.file_count, 0xCC)
            )
            for file_meta in folder.files:
                buffer.write(
                    struct.pack("QII", file_meta.file_hash, file_meta.index, 0xCC)
                )
        table_offset = buffer.tell()
        buffer.write(b"\x00" * (self.file_count * 0x18))
        for i in range(self.file_count):
            decompressed_data = self.decompressed_files[i]
            compressed_data = lz4.block.compress(
                decompressed_data, "high_compression", store_size=False
            )
            self.table[i].decompressed_size = len(decompressed_data)
            self.table[i].compressed_size = len(compressed_data)
            self.table[i].offset = buffer.tell()
            buffer.write(compressed_data)
            while buffer.tell() & 0xF:
                buffer.write(b"\x00")
        buffer.seek(0x18)
        buffer.write(struct.pack("QQ", table_offset, paths_offset))
        buffer.write(struct.pack("Q" * self.folder_count, *folder_offsets))
        buffer.seek(table_offset)
        for file in self.table:
            buffer.write(
                struct.pack(
                    "HHIIIII",
                    file.level,
                    file.compression_type,
                    file.decompressed_size,
                    file.compressed_size,
                    0xCC,
                    file.offset,
                    file.unused,
                )
            )
        with open(gfpak_name, "wb+") as f:
            f.write(buffer.getbuffer())

    def dump_files(self, output_folder: str) -> None:
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        metadata = {"folders": []}
        for folder in self.folders:
            hash_ = folder.folder_hash
            folder_name = f"{hash_:016X}"
            if str(hash_) in HASHES:
                folder_name = HASHES[str(hash_)]
                hash_ = folder_name
            folder_meta = {
                "files": [],
                "name": folder_name,
                "hash": hash_,
            }
            folder_name = os.path.join(output_folder, folder_name.replace("/", "_"))
            if not os.path.exists(folder_name):
                os.mkdir(folder_name)

            for file_meta in folder.files:
                hash_ = file_meta.file_hash
                absolute_hash = self.absolute_hashes[file_meta.index]
                file_name = f"{hash_:016X}"
                if str(hash_) in HASHES:
                    file_name = HASHES[str(hash_)]
                    hash_ = file_name
                if str(absolute_hash) in HASHES:
                    absolute_hash = HASHES[str(absolute_hash)]
                file_type = "raw"
                if file_name.endswith(".gfbmdl"):
                    file_type = "model"
                    file_name = file_name.replace(".gfbmdl", "")
                if file_name.endswith(".gfbanm"):
                    file_type = "animation"
                    file_name = file_name.replace(".gfbanm", ".gfbanm.json")
                if file_name.endswith(".gfbanmcfg"):
                    file_type = "animation_config"
                    file_name = file_name.replace(".gfbanmcfg", ".gfbanmcfg.json")
                if file_name.endswith(".gfbpokecfg"):
                    file_type = "poke_config"
                    file_name = file_name.replace(".gfbpokecfg", ".gfbpokecfg.json")
                if file_name.endswith(".bntx"):
                    file_type = "texture"
                    file_name = file_name.replace(".bntx", ".png")
                if file_name.endswith(".bnsh_fsh"):
                    file_type = "fragment_shader"
                    file_name = file_name.replace(".bnsh_fsh", ".frag")
                if file_name.endswith(".bnsh_vsh"):
                    file_type = "vertex_shader"
                    file_name = file_name.replace(".bnsh_vsh", ".vert")
                folder_meta["files"].append(
                    {
                        "name": file_name,
                        "hash": hash_,
                        "type": file_type,
                        "absolute_hash": absolute_hash,
                    }
                )
                decompressed_data = self.decompressed_files[file_meta.index]
                if file_type == "raw":
                    with open(os.path.join(folder_name, file_name), "wb") as f:
                        f.write(decompressed_data)
                elif file_type == "model":
                    gfbmdl.dump_gfbmdl_raw(
                        decompressed_data, os.path.join(folder_name, file_name)
                    )
                elif file_type == "animation":
                    gfbanm.convert_gfbanm_raw(
                        decompressed_data, os.path.join(folder_name, file_name)
                    )
                elif file_type == "animation_config":
                    gfbanmcfg.convert_gfbanmcfg_raw(
                        decompressed_data, os.path.join(folder_name, file_name)
                    )
                elif file_type == "poke_config":
                    gfbpokecfg.convert_gfbpokecfg_raw(
                        decompressed_data, os.path.join(folder_name, file_name)
                    )
                elif file_type == "texture":
                    try:
                        bntx.convert_bntx_raw(
                            decompressed_data, os.path.join(folder_name, file_name)
                        )
                        folder_meta["files"][-1]["bntx_format"] = (
                            bntx.check_bntx_format_raw(decompressed_data)
                        )
                    except subprocess.CalledProcessError:
                        folder_meta["files"][-1]["file_type"] = "raw"
                        with open(os.path.join(folder_name, file_name), "wb") as f:
                            f.write(decompressed_data)
                elif file_type == "fragment_shader":
                    try:
                        bnsh.decompile_fragment_shader_raw(
                            decompressed_data, os.path.join(folder_name, file_name)
                        )
                    except subprocess.CalledProcessError:
                        folder_meta["files"][-1]["file_type"] = "raw"
                        with open(os.path.join(folder_name, file_name), "wb") as f:
                            f.write(decompressed_data)
                elif file_type == "vertex_shader":
                    try:
                        bnsh.decompile_vertex_shader_raw(
                            decompressed_data, os.path.join(folder_name, file_name)
                        )
                    except subprocess.CalledProcessError:
                        folder_meta["files"][-1]["file_type"] = "raw"
                        with open(os.path.join(folder_name, file_name), "wb") as f:
                            f.write(decompressed_data)

            metadata["folders"].append(folder_meta)

        with open(f"{output_folder}/metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def from_files(self, folder) -> None:
        with open(os.path.join(folder, "metadata.json"), "r", encoding="utf-8") as f:
            metadata = json.load(f)
        file_index = 0
        for folder_meta in metadata["folders"]:
            folder_hash = folder_meta["hash"]
            if isinstance(folder_hash, str):
                folder_hash = fnv1a(folder_hash)
            folder_name = folder_meta["name"].replace("/", "_")
            files = folder_meta["files"]
            file_metas = []
            for file_meta in files:
                file_hash = file_meta["hash"]
                if isinstance(file_hash, str):
                    file_hash = fnv1a(file_hash)
                absolute_hash = file_meta["absolute_hash"]
                if isinstance(absolute_hash, str):
                    absolute_hash = fnv1a(absolute_hash)
                self.absolute_hashes.append(absolute_hash)
                self.table.append(self.File(9, 2, -1, -1, 0xCC, -1, 0))
                file_name = file_meta["name"]
                file_metas.append(self.FileMeta(file_hash, file_index, 0xCC))
                # TODO: allow unordered
                assert len(self.decompressed_files) == file_index
                file_index += 1
                file_type = file_meta["type"]
                if file_type == "raw":
                    with open(os.path.join(folder, folder_name, file_name), "rb") as f:
                        self.decompressed_files.append(f.read())
                elif file_type == "model":
                    self.decompressed_files.append(
                        gfbmdl.serialize_gfbmdl_path_raw(
                            os.path.join(folder, folder_name, file_name)
                        )
                    )
                elif file_type == "animation":
                    with open(
                        os.path.join(folder, folder_name, file_name),
                        "r",
                        encoding="utf-8",
                    ) as f:
                        self.decompressed_files.append(
                            gfbanm.convert_to_gfbanm_raw(f.read())
                        )
                elif file_type == "animation_config":
                    with open(
                        os.path.join(folder, folder_name, file_name),
                        "r",
                        encoding="utf-8",
                    ) as f:
                        self.decompressed_files.append(
                            gfbanmcfg.convert_to_gfbanmcfg_raw(f.read())
                        )
                elif file_type == "poke_config":
                    with open(
                        os.path.join(folder, folder_name, file_name),
                        "r",
                        encoding="utf-8",
                    ) as f:
                        self.decompressed_files.append(
                            gfbpokecfg.convert_to_gfbpokecfg_raw(f.read())
                        )
                elif file_type == "texture":
                    tex_file_name, _ = os.path.splitext(file_name)
                    tex_file_name += ".bntx"
                    self.decompressed_files.append(
                        bntx.convert_to_bntx_raw(
                            os.path.join(folder, folder_name, file_name),
                            tex_file_name,
                            file_meta["bntx_format"],
                        )
                    )
                elif file_type in ("vertex_shader", "fragment_shader"):
                    self.decompressed_files.append(
                        bnsh.compile_shader_raw(
                            os.path.join(folder, folder_name, file_name),
                            file_meta.get("constants", None),
                        )
                    )

            self.folders.append(self.Folder(folder_hash, len(files), 0xCC, file_metas))

        self.file_count = sum(len(folder.files) for folder in self.folders)
        self.folder_count = len(self.folders)

    def parse_buffer(self, buffer: bytearray) -> None:
        """Parse a GFPAK buffer"""
        reader = BytesIO(buffer)
        assert reader.read(8) == b"GFLXPACK"
        self.version, self.is_relocated, self.file_count, self.folder_count = (
            struct.unpack("IIII", reader.read(0x10))
        )
        table_offset, paths_offset = struct.unpack("QQ", reader.read(0x10))
        folder_offsets = [
            *struct.unpack(
                "Q" * self.folder_count, reader.read(0x8 * self.folder_count)
            )
        ]
        assert paths_offset == reader.tell()
        self.absolute_hashes = [
            *struct.unpack("Q" * self.file_count, reader.read(0x8 * self.file_count))
        ]
        self.folders = []
        for folder_index in range(self.folder_count):
            assert folder_offsets[folder_index] == reader.tell()
            folder = self.Folder(*struct.unpack("QII", reader.read(0x10)), [])
            folder.files.extend(
                self.FileMeta(*struct.unpack("QII", reader.read(0x10)))
                for _ in range(folder.file_count)
            )
            self.folders.append(folder)
        assert table_offset == reader.tell()
        self.table = [
            self.File(*struct.unpack("HHIIIII", reader.read(0x18)))
            for _ in range(self.file_count)
        ]
        compressed_files = []
        self.decompressed_files = []
        for i in range(self.file_count):
            reader.seek(self.table[i].offset)
            compressed_files.append(reader.read(self.table[i].compressed_size))
            assert self.table[i].compression_type == 2  # lz4
            self.decompressed_files.append(
                lz4.block.decompress(
                    compressed_files[i], self.table[i].decompressed_size
                )
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pack or unpack a model GFPAK")
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--pack",
        action="store_true",
    )
    mode_group.add_argument(
        "--unpack",
        action="store_true",
    )
    parser.add_argument(
        "input",
    )
    parser.add_argument(
        "output",
    )
    args = parser.parse_args()

    gfpak = GFPak()
    if args.unpack:
        with open(args.input, "rb") as f:
            gfpak.parse_buffer(bytearray(f.read()))
        gfpak.dump_files(args.output)
    else:
        gfpak.from_files(args.input)
        gfpak.serialize_gfpak(args.output)
