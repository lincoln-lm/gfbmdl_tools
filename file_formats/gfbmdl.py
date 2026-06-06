from importlib.resources import files
import os
import json
import numpy as np

from .util import flatbuffer_binary_to_json, json_to_flatbuffer_binary

SCHEMA = (files(__package__) / "gfbmdl.fbs").read_text(encoding="utf-8")


def dump_materials(data, materials):
    return [
        {
            "name": material["name"],
            "shaderGroup": material["shaderGroup"],
            "renderLayer": material["renderLayer"],
            "unknown1": material["unknown1"],
            "unknown2": material["unknown2"],
            "unknown3": material["unknown3"],
            "unknown4": material["unknown4"],
            "unknown5": material["unknown5"],
            "unknown6": material["unknown6"],
            "unknown7": material["unknown7"],
            "parameter1": material["parameter1"],
            "parameter2": material["parameter2"],
            "parameter3": material["parameter3"],
            "shader": data["shaderNames"][material["shaderIndex"]],
            "parameter4": material["parameter4"],
            "parameter5": material["parameter5"],
            "textureMaps": [
                {
                    "sampler": map["sampler"],
                    "texture": data["textureNames"][map["index"]],
                    "params": map["params"],
                }
                for map in material["textureMaps"]
            ],
            "switches": {
                switch["name"]: switch["value"] for switch in material["switches"]
            },
            "values": {value["name"]: value["value"] for value in material["values"]},
            "colors": {
                color["name"]: [
                    color["color"]["r"],
                    color["color"]["g"],
                    color["color"]["b"],
                ]
                for color in material["colors"]
            },
            "common": {
                "values": {
                    value["name"]: value["value"]
                    for value in material["common"]["values"]
                },
                "switches": {
                    switch["name"]: switch["value"]
                    for switch in material["common"]["switches"]
                },
            },
        }
        for material in materials
    ]


def serialize_materials(data, materials):
    return [
        {
            "name": material["name"],
            "shaderGroup": material["shaderGroup"],
            "renderLayer": material["renderLayer"],
            "unknown1": material["unknown1"],
            "unknown2": material["unknown2"],
            "unknown3": material["unknown3"],
            "unknown4": material["unknown4"],
            "unknown5": material["unknown5"],
            "unknown6": material["unknown6"],
            "unknown7": material["unknown7"],
            "parameter1": material["parameter1"],
            "parameter2": material["parameter2"],
            "parameter3": material["parameter3"],
            "shaderIndex": data["shaderNames"].index(material["shader"]),
            "parameter4": material["parameter4"],
            "parameter5": material["parameter5"],
            "textureMaps": [
                {
                    "sampler": map["sampler"],
                    "index": data["textureNames"].index(map["texture"]),
                    "params": map["params"],
                }
                for map in material["textureMaps"]
            ],
            "switches": [
                {"name": name, "value": value}
                for name, value in material["switches"].items()
            ],
            "values": [
                {"name": name, "value": value}
                for name, value in material["values"].items()
            ],
            "colors": [
                {"name": name, "color": {"r": color[0], "g": color[1], "b": color[2]}}
                for name, color in material["colors"].items()
            ],
            "common": {
                "values": [
                    {"name": name, "value": value}
                    for name, value in material["common"]["values"].items()
                ],
                "switches": [
                    {"name": name, "value": value}
                    for name, value in material["common"]["switches"].items()
                ],
            },
        }
        for material in materials
    ]


MESH_ATTRIBUTES = [
    {"vertexType": "Position", "bufferFormat": "Float", "elementCount": 3},
    {"vertexType": "Normal", "bufferFormat": "HalfFloat", "elementCount": 4},
    {"vertexType": "Binormal", "bufferFormat": "HalfFloat", "elementCount": 4},
    {"vertexType": "UV1", "bufferFormat": "Float", "elementCount": 2},
    {"vertexType": "Color1", "bufferFormat": "Byte", "elementCount": 4},
    {"vertexType": "Color2", "bufferFormat": "Byte", "elementCount": 4},
    {"vertexType": "BoneID", "bufferFormat": "Byte", "elementCount": 4},
    {"vertexType": "BoneWeight", "bufferFormat": "BytesAsFloat", "elementCount": 4},
]
MESH_DT = np.dtype(
    [
        ("position", "f4", 3),
        ("normal", "f2", 4),
        ("binormal", "f2", 4),
        ("uv1", "f4", 2),
        ("color1", "u1", 4),
        ("color2", "u1", 4),
        ("bone_id", "u1", 4),
        ("bone_weight", "u1", 4),
    ]
)


def dump_meshes(data, meshes):
    assert len(meshes) == 1
    meshes = meshes[0]
    assert meshes["attributes"] == MESH_ATTRIBUTES
    vertices = np.frombuffer(bytes(meshes["data"]), dtype=MESH_DT)

    return {
        "materials": [
            {
                "material": data["materialNames"][material["materialIndex"]],
                "faces": material["faces"],
            }
            for material in meshes["polygons"]
        ],
        "vertices": [[d.tolist() for d in v] for v in vertices],
    }


def serialize_meshes(data, meshes):
    vertices = [tuple(v) for v in meshes["vertices"]]
    vertices = np.array(vertices, dtype=MESH_DT)

    return [
        {
            "polygons": [
                {
                    "materialIndex": data["materialNames"].index(material["material"]),
                    "faces": material["faces"],
                }
                for material in meshes["materials"]
            ],
            "attributes": MESH_ATTRIBUTES,
            "data": list(vertices.tobytes()),
        }
    ]


def dump_bones(bones):
    new_bones = []
    for bone in bones:
        is_real = bone["boneType"] != "NoSkinning"
        assert bone["visible"] == is_real
        new_bones.append(
            {
                "name": bone["name"],
                "parent": bone["parent"],
                "position": [
                    bone["translation"]["x"],
                    bone["translation"]["y"],
                    bone["translation"]["z"],
                ],
                "rotation": [
                    bone["rotation"]["x"],
                    bone["rotation"]["y"],
                    bone["rotation"]["z"],
                ],
                "scale": [bone["scale"]["x"], bone["scale"]["y"], bone["scale"]["z"]],
                "isReal": is_real,
            }
        )
    return new_bones


def serialize_bones(bones):
    return [
        {
            k: v
            for k, v in {
                "name": bone["name"],
                "parent": bone["parent"],
                "zero": 0,
                "visible": bone["isReal"],
                "translation": {
                    "x": bone["position"][0],
                    "y": bone["position"][1],
                    "z": bone["position"][2],
                },
                "rotation": {
                    "x": bone["rotation"][0],
                    "y": bone["rotation"][1],
                    "z": bone["rotation"][2],
                },
                "scale": {
                    "x": bone["scale"][0],
                    "y": bone["scale"][1],
                    "z": bone["scale"][2],
                },
                "boneType": "NoSkinning" if not bone["isReal"] else "HasSkinning",
                "radiusStart": {"x": 0.0, "y": 0.0, "z": 0.0},
                "radiusEnd": {"x": 0.0, "y": 0.0, "z": 0.0},
                "rigidCheck": {"unknown1": 0},
            }.items()
            if not (k == "rigidCheck" and bone["isReal"]) or bone["parent"] == 1
        }
        for bone in bones
    ]


def dump_gfbmdl_raw(data: bytes, path: str):
    model = json.loads(flatbuffer_binary_to_json(data, SCHEMA))
    if not os.path.exists(path):
        os.mkdir(path)

    with open(os.path.join(path, "meshes.json"), "w", encoding="utf-8") as f:
        meshes = model.pop("meshes")
        assert meshes == serialize_meshes(model, dump_meshes(model, meshes))
        json.dump(dump_meshes(model, meshes), f, indent=2)
    with open(os.path.join(path, "materials.json"), "w", encoding="utf-8") as f:
        materials = model.pop("materials")
        assert materials == serialize_materials(model, dump_materials(model, materials))
        json.dump(dump_materials(model, materials), f, indent=2)
    with open(os.path.join(path, "bones.json"), "w", encoding="utf-8") as f:
        bones = model.pop("bones")
        assert bones == serialize_bones(dump_bones(bones))
        json.dump(dump_bones(bones), f, indent=2)
    with open(os.path.join(path, "model.json"), "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)


def dump_gfbmdl(in_path: str, out_path: str):
    with open(in_path, "rb") as f:
        dump_gfbmdl_raw(f.read(), out_path)


def serialize_gfbmdl_str_raw(data: str) -> bytes:
    model = json.loads(data)
    model["materials"] = serialize_materials(model, model["materials"])
    model["meshes"] = serialize_meshes(model, model["meshes"])
    model["bones"] = serialize_bones(model["bones"])
    model["unknown"] = []
    model["materialNames"] = model["shaderNames"]
    return json_to_flatbuffer_binary(json.dumps(model), SCHEMA)


def serialize_gfbmdl_path_raw(in_path: str) -> bytes:
    with open(os.path.join(in_path, "model.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(os.path.join(in_path, "materials.json"), "r", encoding="utf-8") as f:
        data["materials"] = json.load(f)
        data["materialNames"] = [mat["name"] for mat in data["materials"]]
    with open(os.path.join(in_path, "meshes.json"), "r", encoding="utf-8") as f:
        data["meshes"] = json.load(f)
    with open(os.path.join(in_path, "bones.json"), "r", encoding="utf-8") as f:
        data["bones"] = json.load(f)
    return serialize_gfbmdl_str_raw(json.dumps(data))


def serialize_gfbmdl(in_path: str, out_path: str):
    with open(out_path, "wb") as f:
        f.write(serialize_gfbmdl_path_raw(in_path))
