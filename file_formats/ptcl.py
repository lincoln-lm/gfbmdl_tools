import subprocess
import pathlib
import tempfile
import shutil
from .util import IsolatedTempFile
from .bnsh import compile_shader


def dump_shaders(in_path, out_path):
    in_path = pathlib.Path(in_path)
    out_path = pathlib.Path(out_path)
    out_path.mkdir(exist_ok=True)

    subprocess.run(
        ["EffectShaderReplacer", "dump", str(in_path), str(out_path)],
        check=True,
    )
    shutil.copy(in_path, out_path / "base.ptcl")


def replace_shaders(in_path, out_path, decompiled_shaders=None):
    in_path = pathlib.Path(in_path)
    out_path = pathlib.Path(out_path)
    with tempfile.TemporaryDirectory() as d:
        directory = pathlib.Path(shutil.copytree(in_path, d, dirs_exist_ok=True))
        if decompiled_shaders is None:
            decompiled_shaders = [x.name for x in directory.glob("*.vert")] + [
                x.name for x in directory.glob("*.frag")
            ]
        for shader in decompiled_shaders:
            shader_out = None
            if shader.endswith(".vert"):
                shader_out = shader.replace(".vert", ".bnsh_vsh")
            elif shader.endswith(".frag"):
                shader_out = shader.replace(".frag", ".bnsh_fsh")
            assert shader_out is not None
            compile_shader(directory / shader, directory / shader_out)
        subprocess.run(
            [
                "EffectShaderReplacer",
                "replace",
                str(directory / "base.ptcl"),
                str(out_path),
            ],
            check=True,
        )


def replace_shaders_raw(in_path, decompiled_shaders=None) -> bytes:
    with IsolatedTempFile() as (d, f):
        replace_shaders(in_path, f.name, decompiled_shaders)
        return f.read()
