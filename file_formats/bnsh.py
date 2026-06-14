import subprocess
from .util import raw_to_temp_file, IsolatedTempFile


def compile_shader(in_path, out_path):
    subprocess.run(
        [
            "ShaderLibrary.CompileTool",
            "uam-nvn",
            in_path,
            out_path,
        ],
        check=True,
    )


def compile_shader_raw(in_path) -> bytes:
    with IsolatedTempFile() as (d, f):
        compile_shader(in_path, f.name)
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
