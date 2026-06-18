import subprocess
import tempfile
import pathlib
from .util import raw_to_temp_file, IsolatedTempFile


def compile_shader(in_path, out_path, constants=None):
    if constants is None:
        constants = {}
    with tempfile.NamedTemporaryFile(
        suffix=pathlib.Path(in_path).suffix, mode="w+"
    ) as f:
        shader_text = pathlib.Path(in_path).read_text("utf-8")
        for line in shader_text.split("\n"):
            for k, v in constants.items():
                if f"{k} = " in line:
                    line = line.split(f"{k} = ")[0] + f"{k} = {v};"
            f.write(line + "\n")
        f.flush()
        subprocess.run(
            [
                "ShaderLibrary.CompileTool",
                "uam-nvn",
                f.name,
                out_path,
            ],
            check=True,
        )


def compile_shader_raw(in_path, constants=None) -> bytes:
    with IsolatedTempFile() as (d, f):
        compile_shader(in_path, f.name, constants)
        return f.read()


def decompile_shader(in_path, out_path):
    subprocess.run(
        [
            "ShaderLibrary.CompileTool",
            "uam-nvn",
            in_path,
            out_path,
        ],
        check=True,
    )


def decompile_vertex_shader_raw(data, out_path):
    with raw_to_temp_file(data, suffix=".bnsh_vsh") as f:
        decompile_shader(f.name, out_path)


def decompile_fragment_shader_raw(data, out_path):
    with raw_to_temp_file(data, suffix=".bnsh_fsh") as f:
        decompile_shader(f.name, out_path)
