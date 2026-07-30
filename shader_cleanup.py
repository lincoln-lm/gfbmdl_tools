import argparse
import pathlib
from file_formats.bnsh import clean_shader

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dump a .ptcl file's shaders")
    parser.add_argument(
        "input",
    )
    parser.add_argument(
        "output",
    )
    args = parser.parse_args()
    pathlib.Path(args.output).write_text(
        clean_shader(pathlib.Path(args.input).read_text("utf-8")), "utf-8"
    )
