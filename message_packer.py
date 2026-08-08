import argparse
import pathlib
import json
from file_formats.message import convert_message_raw, convert_to_message_raw

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dump a .dat&.tbl message archive")
    parser.add_argument(
        "input",
    )
    parser.add_argument(
        "output",
    )
    args = parser.parse_args()
    base_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)
    if base_path.suffix == ".json":
        cvt = json.loads(base_path.read_text("utf-8"))
        dat, tbl = convert_to_message_raw(cvt)
        output_path.with_suffix(".dat").write_bytes(dat)
        output_path.with_suffix(".tbl").write_bytes(tbl)
    else:
        dat = base_path.with_suffix(".dat").read_bytes()
        tbl = base_path.with_suffix(".tbl").read_bytes()
        cvt = convert_message_raw(dat, tbl)
        output_path.write_text(json.dumps(cvt, indent=4), "utf-8")
