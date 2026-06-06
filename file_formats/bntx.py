import subprocess
from .util import raw_to_temp_file, IsolatedTempFile


def check_bntx_format(path) -> str:
    return subprocess.run(
        ["ultimate_tex_cli", "--print-format", path],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def check_bntx_format_raw(data) -> str:
    with raw_to_temp_file(data, suffix=".bntx") as f:
        return check_bntx_format(f.name)


def convert_bntx(path, out):
    subprocess.run(["ultimate_tex_cli", path, out], check=True)


def convert_bntx_raw(data, out_path):
    with raw_to_temp_file(data, suffix=".bntx") as f:
        convert_bntx(f.name, out_path)


def convert_to_bntx(path, out, format="BC7RgbaUnormSrgb"):
    subprocess.run(
        ["ultimate_tex_cli", path, out, "--format", format],
        check=True,
    )
    subprocess.run(
        ["BntxFixer", out, out],
        check=True,
    )


def convert_to_bntx_raw(in_path, name, format="BC7RgbaUnormSrgb") -> bytes:
    with IsolatedTempFile(name=name) as (d, f):
        convert_to_bntx(in_path, f.name, format)
        return f.read()
