from __future__ import annotations
import subprocess
import tempfile
import pathlib
from dataclasses import dataclass
import re
from .util import raw_to_temp_file, IsolatedTempFile

BASE_TYPE_SIZES = {
    "float": 4,
    "int": 4,
}


@dataclass
class Struct:
    name: str
    fields: list[tuple[str | Struct, str]]

    def pretty_members(self):
        for type_, name in self.fields:
            type_ = type_.name if isinstance(type_, Struct) else type_
            yield f"    {type_} {name};"

    def size(self):
        return sum(
            BASE_TYPE_SIZES[type_] if isinstance(type_, str) else type_.size()
            for type_, _ in self.fields
        )

    def at(self, offset: int):
        for type_, name in self.fields:
            size = BASE_TYPE_SIZES[type_] if isinstance(type_, str) else type_.size()
            if offset < size:
                if isinstance(type_, Struct):
                    sub_name = type_.at(offset)
                    if sub_name.startswith("["):
                        return f"{name}{sub_name}"
                    return f"{name}.{sub_name}"
                assert offset == 0
                return name
            offset -= size
        assert False


def array(name, type_, count):
    return Struct(
        name,
        [(type_, f"[{i}]") for i in range(count)],
    )


vec4 = Struct(
    "vec4",
    [
        ("float", "x"),
        ("float", "y"),
        ("float", "z"),
        ("float", "w"),
    ],
)
mat4 = array("mat4", vec4, 4)
vec2 = Struct(
    "vec2",
    [
        ("float", "x"),
        ("float", "y"),
    ],
)

ivec4 = Struct(
    "ivec4",
    [
        ("int", "x"),
        ("int", "y"),
        ("int", "z"),
        ("int", "w"),
    ],
)

TexPatAnim = Struct(
    "TexPatAnim",
    [
        ("float", "num"),
        ("float", "frequency"),
        ("float", "numRandom"),
        ("float", "pad0"),
        (ivec4, "table0"),
        (ivec4, "table1"),
        (ivec4, "table2"),
        (ivec4, "table3"),
        (ivec4, "table4"),
        (ivec4, "table5"),
        (ivec4, "table6"),
        (ivec4, "table7"),
    ],
)

TexScrollAnim = Struct(
    "TexScrollAnim",
    [
        (vec2, "scrollAdd"),
        (vec2, "scroll"),
        (vec2, "scrollRandom"),
        (vec2, "scaleAdd"),
        (vec2, "scale"),
        (vec2, "scaleRandom"),
        ("float", "rotationAdd"),
        ("float", "rotation"),
        ("float", "rotationRandom"),
        ("float", "rotationType"),
        (vec2, "uvScale"),
        (vec2, "uvDiv"),
    ],
)

AnimationKeyTable = Struct(
    "AnimationKeyTable",
    [
        (vec4, "key0"),
        (vec4, "key1"),
        (vec4, "key2"),
        (vec4, "key3"),
        (vec4, "key4"),
        (vec4, "key5"),
        (vec4, "key6"),
        (vec4, "key7"),
    ],
)

sysViewUniformBlock = Struct(
    "sysViewUniformBlock",
    [
        (mat4, "viewMatrix"),
        (mat4, "projectionMatrix"),
        (mat4, "viewProjectionMatrix"),
        (mat4, "unk0"),
        (vec4, "cameraDirection"),
        (vec4, "cameraPosition"),
        (vec4, "depthParam"),
        (vec4, "unk2"),
    ],
)

sysEmitterDynamicUniformBlock = Struct(
    "sysEmitterDynamicUniformBlock",
    [
        (vec4, "color0"),
        (vec4, "color1"),
        ("float", "time"),
        ("float", "d"),
        ("float", "e"),
        ("float", "f"),
        ("float", "alphaParam"),
        ("float", "scaleX"),
        ("float", "scaleY"),
        ("float", "scaleZ"),
        (mat4, "transform0"),
        (mat4, "transform1"),
    ],
)

sysEmitterStaticUniformBlock = Struct(
    "sysEmitterStaticUniformBlock",
    [
        (vec4, "pad0"),
        (vec4, "pad1"),
        (vec4, "pad2"),
        (vec4, "pad3"),
        (vec4, "pad4"),
        (ivec4, "flags"),
        ("int", "numColor0Keys"),
        ("int", "numAlpha0Keys"),
        ("int", "numColor1Keys"),
        ("int", "numAlpha1Keys"),
        ("int", "numScaleKeys"),
        ("int", "numParamKeys"),
        ("int", "pad5"),
        ("int", "pad6"),
        ("float", "color0LoopRate"),
        ("float", "alpha0LoopRate"),
        ("float", "color1LoopRate"),
        ("float", "alpha1LoopRate"),
        ("float", "scaleLoopRate"),
        ("float", "color0LoopRandom"),
        ("float", "alpha0LoopRandom"),
        ("float", "color1LoopRandom"),
        ("float", "alpha1LoopRandom"),
        ("float", "scaleLoopRandom"),
        ("float", "pad7"),
        ("float", "pad8"),
        (vec4, "gravity"),
        ("float", "airResistance"),
        ("float", "pad9"),
        ("float", "pad10"),
        ("float", "pad11"),
        (vec2, "center"),
        ("float", "offset"),
        ("float", "pad12"),
        (vec2, "amplitude"),
        (vec2, "cycle"),
        (vec2, "phaseRandom"),
        (vec2, "phaseInitial"),
        ("float", "coefficient0"),
        ("float", "coefficient1"),
        ("float", "pad13"),
        ("float", "pad14"),
        (TexPatAnim, "texPatAnim0"),
        (TexPatAnim, "texPatAnim1"),
        (TexPatAnim, "texPatAnim2"),
        (TexScrollAnim, "texScrollAnim0"),
        (TexScrollAnim, "texScrollAnim1"),
        (TexScrollAnim, "texScrollAnim2"),
        ("float", "colorScale"),
        ("float", "pad15"),
        ("float", "pad16"),
        ("float", "pad17"),
        (AnimationKeyTable, "color0"),
        (AnimationKeyTable, "alpha0"),
        (AnimationKeyTable, "color1"),
        (AnimationKeyTable, "alpha1"),
        ("float", "softEdgeParam1"),
        ("float", "softEdgeParam2"),
        ("float", "fresnelAlphaParam1"),
        ("float", "fresnelAlphaParam2"),
        ("float", "nearDistAlphaParam1"),
        ("float", "nearDistAlphaParam2"),
        ("float", "farDistAlphaParam1"),
        ("float", "farDistAlphaParam2"),
        ("float", "decalParam1"),
        ("float", "decalParam2"),
        ("float", "alphaThreshold"),
        ("float", "pad18"),
        ("float", "addVelToScale"),
        ("float", "softParticleDist"),
        ("float", "softParticleVolume"),
        ("float", "pad19"),
        (AnimationKeyTable, "scaleAnim"),
        (AnimationKeyTable, "paramAnim"),
        (vec4, "rotateInitial"),
        (vec4, "rotateInitialRandom"),
        (vec4, "rotateAdd"),
        (vec4, "rotateAddRandom"),
        ("float", "scaleLimitDistNear"),
        ("float", "scaleLimitDistFar"),
        ("float", "pad20"),
        ("float", "pad21"),
    ],
)


def clean_shader(shader):
    shader = shader.replace(
        "layout (binding = 0, std140) uniform _support_buffer\n{\n    uint alpha_test;\n    uint is_bgra[8];\n    precise vec4 viewport_inverse;\n    precise vec4 viewport_size;\n    int frag_scale_count;\n    precise float render_scale[73];\n    ivec4 tfe_offset;\n    int tfe_vertex_count;\n} support_buffer;",
        "",
    )

    lines = shader.split("\n")
    for line in lines:
        if " uniform " in line:
            break

    first_uniform_line = lines.index(line)
    lines_before = lines[:first_uniform_line]
    lines_after = lines[first_uniform_line:]
    for struct in [TexPatAnim, TexScrollAnim, AnimationKeyTable]:
        lines_before.append(f"struct {struct.name}\n{{")
        for member in struct.pretty_members():
            lines_before.append(f"{member}")
        lines_before.append("};\n")

    shader = "\n".join(lines_before + lines_after)

    for ubo in (
        sysViewUniformBlock,
        sysEmitterDynamicUniformBlock,
        sysEmitterStaticUniformBlock,
    ):

        shader = shader.replace(
            f"{ubo.name}\n{{\n    precise vec4 data[4096];\n}}",
            f"{ubo.name}\n{{\n{'\n'.join(ubo.pretty_members())}\n}}",
        )

        pattern = rf"_{re.escape(ubo.name)}(?P<var>)\.data\[(?P<index>\d+)\]\.(?P<member>[a-zA-Z_]\w*)"

        def replace_callback(match):
            index = int(match.group("index"))
            member = match.group("member")
            offset = index * 16 + "xyzw".index(member) * 4

            return f"_{ubo.name}.{ubo.at(offset)}"

        shader = re.sub(pattern, replace_callback, shader)
    return shader


def compile_shader(in_path, out_path, constants=None):
    if constants is None:
        constants = {}
    with tempfile.NamedTemporaryFile(
        suffix=pathlib.Path(in_path).suffix, mode="w+"
    ) as f:
        shader_text = pathlib.Path(in_path).read_text("utf-8")
        for line in shader_text.split("\n"):
            for k, v in constants.items():
                if f"{k} = " in line:
                    line = line.split(f"{k} = ")[0] + f"{k} = {v};"
            f.write(line + "\n")
        f.flush()
        subprocess.run(
            [
                "ShaderLibrary.CompileTool",
                "uam-nvn",
                f.name,
                out_path,
            ],
            check=True,
        )


def compile_shader_raw(in_path, constants=None) -> bytes:
    with IsolatedTempFile() as (d, f):
        compile_shader(in_path, f.name, constants)
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

    with open(out_path, "r") as f:
        shader = f.read()
    with open(out_path, "w") as f:
        f.write(clean_shader(shader))


def decompile_vertex_shader_raw(data, out_path):
    with raw_to_temp_file(data, suffix=".bnsh_vsh") as f:
        decompile_shader(f.name, out_path)


def decompile_fragment_shader_raw(data, out_path):
    with raw_to_temp_file(data, suffix=".bnsh_fsh") as f:
        decompile_shader(f.name, out_path)
