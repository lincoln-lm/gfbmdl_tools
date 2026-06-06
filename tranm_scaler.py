import argparse
import json

from file_formats import gfbanm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scale a .tranm file and convert to JSON"
    )
    parser.add_argument(
        "input",
    )
    parser.add_argument(
        "output",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=100.0,
    )
    args = parser.parse_args()

    gfbanm.convert_gfbanm(args.input, args.output)
    with open(args.output, "r", encoding="utf-8") as f:
        data = json.load(f)

    for track in data["skeleton"]["tracks"]:
        translate_data = track["translate"]["co"]
        if isinstance(translate_data, list):
            track["translate"]["co"] = [
                {
                    "x": v["x"] * args.scale,
                    "y": v["y"] * args.scale,
                    "z": v["z"] * args.scale,
                }
                for v in translate_data
            ]
        else:
            track["translate"]["co"] = {
                "x": translate_data["x"] * args.scale,
                "y": translate_data["y"] * args.scale,
                "z": translate_data["z"] * args.scale,
            }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
