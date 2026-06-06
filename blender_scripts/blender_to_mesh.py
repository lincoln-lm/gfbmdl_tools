import bpy
import mathutils
import json

meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
armatures = [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]

mesh_json = {"materials": [], "vertices": []}

material_names = list(
    set(slot.material.name for mesh in meshes for slot in mesh.material_slots)
)

bone_id_lookup = {}
bones_json = []
bone_i = 0
bpy.ops.object.mode_set(mode="EDIT")
for armature in armatures:
    for bone in armature.data.bones:
        world_matrix = bone.matrix_local
        if bone.parent:
            local_matrix = bone.parent.matrix_local.inverted() @ world_matrix
        else:
            local_matrix = world_matrix
        position, rotation, scale = local_matrix.decompose()
        parent_id = -1
        if bone.parent:
            # TODO: support arbitrary order and not enforce parent before child?
            assert bone.parent.name in bone_id_lookup
            parent_id = bone_id_lookup[bone.parent.name]
            rotation = rotation.to_euler(
                "XYZ", mathutils.Euler(bones_json[parent_id]["rotation"])
            )
        else:
            rotation = rotation.to_euler("XYZ")

        bones_json.append(
            {
                "name": bone.name,
                "parent": parent_id,
                "position": list(position),
                "rotation": list(rotation),
                "scale": list(scale),
                "isReal": bone.use_deform,
            }
        )
        bone_id_lookup[bone.name] = bone_i
        bone_i += 1

vertex_offset = 0
material_polygons = {}
for mesh in meshes:
    mesh.data.calc_loop_triangles()
    mesh.data.calc_tangents()

    uv_data = {}
    bitangent_data = {}
    group_lookup = {g.index: g.name for g in mesh.vertex_groups}

    for i, triangle in enumerate(mesh.data.loop_triangles):
        for loop_i in triangle.loops:
            vertex = mesh.data.loops[loop_i].vertex_index
            uv = mesh.data.uv_layers.active.data[loop_i].uv
            bitangent = mesh.data.loops[loop_i].bitangent
            uv_data[vertex] = list(uv)
            bitangent_data[vertex] = list(bitangent)
        global_material_index = material_names.index(
            mesh.material_slots[triangle.material_index].name
        )
        if global_material_index not in material_polygons:
            material_polygons[global_material_index] = []
        material_polygons[global_material_index].extend(
            (x + vertex_offset for x in triangle.vertices)
        )

    for v_i, v in enumerate(mesh.data.vertices):
        bones = []
        weights = []
        for g in v.groups:
            bone_name = group_lookup[g.group]
            bone_id = bone_id_lookup[bone_name]
            assert bone_id >= 1
            bones.append(bone_id - 1)
            weights.append(int(g.weight * 255 // 1))
        bones = bones + [0, 0, 0, 0][len(bones) :]
        weights = weights + [0, 0, 0, 0][len(weights) :]
        b = sorted(list(map(tuple, zip(bones, weights))))
        bones = [x[0] for x in b]
        weights = [x[1] for x in b]
        assert len(bones) == len(weights)
        assert len(weights) == 4
        mesh_json["vertices"].append(
            [
                list(v.co),
                list(v.normal) + [1],
                bitangent_data[v_i] + [1],
                uv_data[v_i],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                bones,
                weights,
            ]
        )
        vertex_offset += 1


for material_index, tris in material_polygons.items():
    mesh_json["materials"].append(
        {"material": material_names[material_index], "faces": tris}
    )


def material_template(name, texture, shader, index):
    return {
        "name": name,
        "shaderGroup": "PokeDefaultShader",
        "renderLayer": 0,
        "unknown1": 1,
        "unknown2": 1,
        "unknown3": 0,
        "unknown4": 1,
        "unknown5": 0,
        "unknown6": 0,
        "unknown7": 0,
        "parameter1": 0,
        "parameter2": 0,
        "parameter3": 1,
        "shader": shader,
        "parameter4": -1,
        "parameter5": index,
        "textureMaps": [
            {
                "sampler": "Col0Tex",
                "texture": texture,
                "params": {
                    "unknown1": 0,
                    "wrapModeX": "Mirror",
                    "wrapModeY": "Repeat",
                    "wrapModeZ": "Repeat",
                    "unknown5": 0,
                    "unknown6": 0,
                    "unknown7": 0,
                    "unknown8": 0,
                    "lodBias": 0.0,
                },
            }
        ],
        "switches": {
            "useColorTex": True,
            "SwitchEmissionMaskTexUV": False,
            "EmissionMaskUse": True,
            "SwitchPriority": False,
            "Layer1Enable": True,
            "SwitchAmbientTexUV": False,
            "AmbientMapEnable": True,
            "SwitchNormalMapUV": False,
            "NormalMapEnable": True,
            "LightTableEnable": True,
            "SpecularMaskEnable": False,
            "BaseColorAddEnable": True,
            "SphereMapEnable": True,
            "SphereMaskEnable": True,
            "RimMaskEnable": False,
            "alphaShell": False,
            "EffectVal": True,
            "NormalEdgeEnable": True,
            "OutLineIDEnable": False,
            "OutLineColFixed": False,
        },
        "values": {
            "ColorUVScaleU": 1.0,
            "ColorUVScaleV": 1.0,
            "ColorUVTranslateU": 0.0,
            "ColorBaseU": 0.0,
            "ColorUVTranslateV": 0.0,
            "ColorBaseV": 0.0,
            "ConstantColor0Val": 1.0,
            "Layer1UVScaleU": 1.0,
            "Layer1UVScaleV": 1.0,
            "Layer1UVTranslateU": 0.0,
            "Layer1BaseU": 0.0,
            "Layer1UVTranslateV": 0.0,
            "Layer1BaseV": 0.0,
            "EmissionMaskVal": 0.0,
            "ConstantColorSd0Val": 1.0,
            "ConstantColor1Val": 1.0,
            "ConstantColorSd1Val": 1.0,
            "ColorLerpValue": 0.0,
            "L1ConstantColor0Val": 1.0,
            "L1AddColor0Val": 0.0,
            "L1ConstantColor1Val": 1.0,
            "L1AddColor1Val": 0.0,
            "L1ConstantColorSd0Val": 1.0,
            "L1ConstantColorSd1Val": 1.0,
            "Layer1OverLerpValue": 0.0,
            "NormalMapUVScaleU": 2.0,
            "NormalMapUVScaleV": 4.0,
            "LightTblIndex": 4.0,
            "LightMul": 1.0,
            "SpecularPower": 1.0,
            "SpecularScale": 0.35,
            "SphereMapColorVal": 0.35,
            "RimColorVal": 0.5,
            "RimPower": 8.0,
            "RimStrength": 8.0,
            "OnGameEmissionVal": 1.0,
            "ConstantColorVal": 1.0,
            "ConstantAlpha": 1.0,
            "OnGameColorVal": 1.0,
            "OnGameAlpha": 1.0,
            "OutLineID": 0.0,
            "ProgID": 0.0,
            "Def0_OneMin1_FreCol": 1.0,
            "DistortionIntensity": 1.0,
            "Sin01": 4.0,
            "ScaleUV": 1.0,
            "EffectTexTranslateU": 0.0,
            "EffectTexTranslateV": 0.0,
            "EffectTexRotate": 0.0,
            "EffectTexScaleU": 8.0,
            "EffectTexScaleV": 5.0,
            "EffectColPower": 1.0,
        },
        "colors": {
            "ConstantColor0": [1.0, 1.0, 1.0],
            "ConstantColorSd0": [0.598, 0.612733, 0.65],
            "ConstantColor1": [1.0, 1.0, 1.0],
            "ConstantColorSd1": [0.643067, 0.598, 0.65],
            "L1ConstantColor0": [1.0, 1.0, 1.0],
            "L1AddColor0": [1.0, 1.0, 1.0],
            "L1ConstantColor1": [1.0, 1.0, 1.0],
            "L1AddColor1": [1.0, 1.0, 1.0],
            "L1ConstantColorSd0": [1.0, 1.0, 1.0],
            "L1ConstantColorSd1": [1.0, 1.0, 1.0],
            "DeepShadowColor": [1.0, 1.0, 1.0],
            "SpecularColor": [0.2, 0.2, 0.2],
            "SphereMapColor": [0.245, 0.639333, 0.7],
            "RimColor": [0.224, 0.239867, 0.28],
            "RimColorShadow": [0.144, 0.1542, 0.18],
            "ConstantColor": [1.0, 1.0, 1.0],
            "OnGameColor": [1.0, 1.0, 1.0],
            "OutLineCol": [0.4959, 0.516895, 0.57],
            "EffectColor01": [1.0, 0.0, 1.0],
        },
        "common": {
            "values": {
                "CullMode": 0,
                "LightSetNo": 0,
                "ShaderType": 0,
                "Priority": 0,
                "MipMapBias": 0,
                "PreMultiplieMode": 0,
                "BlendMode": 0,
                "ColorMapUvIndex": 0,
                "Layer1UvIdx": 0,
                "EmissionMaskTexSS": 7,
                "AmbientTexSS": 7,
                "NormalMapTexSS": 7,
                "Col0TexSS": 7,
                "LyCol0TexSS": 7,
                "PolygonOffset": 0,
            },
            "switches": {
                "FogEnable": True,
                "DiscardEnable": False,
                "CastShadow": True,
                "ReceiveShadow": False,
                "TextureAlphaTestEnable": False,
                "ShadowMapPrevEnable": True,
                "LayerCalcMulti": False,
                "FireMaskPathEnable": False,
                "GPUInstancingEnable": False,
                "Wireframe": False,
                "DepthWrite": True,
                "DepthTest": True,
                "IsErase": False,
                "MayaPreviewEnable": False,
            },
        },
    }


materials = [
    material_template(material_name, material_name, "BodyATattu", i)
    for i, material_name in enumerate(material_names)
]


print(json.dumps(bones_json))

print(json.dumps(mesh_json))

print(json.dumps(material_names))

print(json.dumps(materials))
