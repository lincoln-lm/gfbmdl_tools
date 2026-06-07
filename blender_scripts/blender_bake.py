import bpy
import os

meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
materials = list(set(slot.material for mesh in meshes for slot in mesh.material_slots))

blend_dir = bpy.path.abspath("//")

bpy.ops.object.select_all(action="DESELECT")
bpy.ops.object.mode_set(mode="OBJECT")

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.bake_type = "DIFFUSE"
scene.render.bake.use_pass_direct = False
scene.render.bake.use_pass_indirect = False
scene.render.bake.use_pass_color = True

img_settings = scene.render.image_settings
img_settings.file_format = "PNG"
img_settings.color_mode = "RGBA"
img_settings.color_depth = "16"
img_settings.compression = 100

for mat in materials:
    bpy.ops.mesh.primitive_plane_add(size=1.0)
    plane = bpy.context.active_object
    plane.name = f"BakePlane_{mat.name}"
    bpy.context.view_layer.objects.active = plane

    plane.data.materials.append(mat)

    image = bpy.data.images.new(
        mat.name, width=1024, height=1024, alpha=True, float_buffer=True
    )
    image.filepath_raw = os.path.join(blend_dir, f"{mat.name}.png")
    image.file_format = "PNG"
    image.colorspace_settings.name = "sRGB"
    image.alpha_mode = "STRAIGHT"

    nodes = mat.node_tree.nodes
    img_node = nodes.new("ShaderNodeTexImage")
    img_node.image = image
    nodes.active = img_node

    bpy.ops.object.select_all(action="DESELECT")
    plane.select_set(True)
    bpy.context.view_layer.objects.active = plane

    print(f"Baking material: {mat.name}")
    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"})

    image.save()

    nodes.remove(img_node)
    bpy.data.objects.remove(plane, do_unlink=True)
