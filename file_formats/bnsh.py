import subprocess


def compile_shader(in_path, out_path):
    print(
        [
            "ShaderLibrary.CompileTool",
            "uam-nvn",
            in_path,
            out_path,
        ]
    )
    subprocess.run(
        [
            "ShaderLibrary.CompileTool",
            "uam-nvn",
            in_path,
            out_path,
        ],
        check=True,
    )


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
