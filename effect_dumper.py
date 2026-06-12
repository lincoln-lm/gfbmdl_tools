import argparse
import pathlib
from file_formats import ptcl, bnsh

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dump a .ptcl file's shaders")
    parser.add_argument(
        "input",
    )
    parser.add_argument(
        "output",
    )
    parser.add_argument(
        "--remove-raw",
        action="store_true",
    )
    args = parser.parse_args()

    ptcl.dump_shaders(args.input, args.output)
    for bnsh_file in pathlib.Path(args.output).glob("*.bnsh*"):
        if bnsh_file.name.endswith(".bnsh_vsh"):
            bnsh_file_out = bnsh_file.with_suffix(".vert")
        elif bnsh_file.name.endswith(".bnsh_fsh"):
            bnsh_file_out = bnsh_file.with_suffix(".frag")
        else:
            continue
        bnsh.decompile_shader(bnsh_file, bnsh_file_out)
        if args.remove_raw:
            bnsh_file.unlink()
