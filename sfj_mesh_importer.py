import bpy
import struct
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class VertInfluences:
    influences: List[int]
    weights: List[float]

@dataclass
class AnimVertex:
    pos: Tuple[float, float, float]
    norm: Tuple[float, float, float]
    tan: Tuple[float, float, float]
    texCoords: Tuple[float, float]
    influences: VertInfluences

class MeshImportProperties(bpy.types.PropertyGroup):
    filepath: bpy.props.StringProperty(
        name="Mesh File",
        description="Path to the SFJ .mesh file",
        subtype="FILE_PATH"
    )

class MESH_PT_SFJImporter(bpy.types.Panel):
    bl_label = "SFJ Mesh Importer"
    bl_idname = "MESH_PT_sfj_mesh_importer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mesh Tools'

    def draw(self, context):
        layout = self.layout
        props = context.scene.mesh_importer_props

        layout.prop(props, "filepath")
        layout.operator("sfj_mesh.import_custom", text="Import SFJ Mesh")

class MESH_OT_ImportSFJ(bpy.types.Operator):
    bl_idname = "sfj_mesh.import_custom"
    bl_label = "Import SFJ Mesh"

    def execute(self, context):
        props = context.scene.mesh_importer_props
        filepath = props.filepath

        self.report({'INFO'}, f"Importing SFJ mesh from: {filepath}")
        self.__load_sfj_mesh(filepath)
        return {'FINISHED'}

    def __load_sfj_mesh(self, filepath):
        vertices: List[AnimVertex] = []
        faces = []

        with open(filepath, "rb") as file:
            numTextures = struct.unpack('<I', file.read(4))[0]

            numVerts = struct.unpack('<I', file.read(4))[0]

            for i in range(numVerts):
                posx, posy, posz = struct.unpack("<fff", file.read(12))
                normx, normy, normz = struct.unpack("<fff", file.read(12))
                tanx, tany, tanz = struct.unpack("<fff", file.read(12))
                texu, texv = struct.unpack("<ff", file.read(8))

                numInfluences = struct.unpack('<I', file.read(4))[0]

                boneInfluences = [0] * numInfluences
                boneWeights = [0.0] * numInfluences
                for curInfluence in range(numInfluences):
                    influence, weight = struct.unpack("<If", file.read(8))
                    boneInfluences[curInfluence] = influence
                    boneWeights[curInfluence] = weight

                vertices.append(AnimVertex(
                    pos=(posx, posy, posz),
                    norm=(normx, normy, normz),
                    tan=(tanx, tany, tanz),
                    texCoords=(texu, texv),
                    influences=VertInfluences(
                        influences=boneInfluences,
                        weights=boneWeights
                    )
                ))

            numFaces = struct.unpack('<I', file.read(4))[0]
            indices = list(struct.unpack(f"<{numFaces * 3}I", file.read(4 * numFaces * 3)))
            faces = [indices[i:i+3] for i in range(0, len(indices), 3)]

        positions = list(map(lambda v: v.pos, vertices))
        mesh = bpy.data.meshes.new("SFJMesh")
        mesh.from_pydata(positions, [], faces)
        mesh.update()

        obj = bpy.data.objects.new("SFJMesh", mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

classes = [MeshImportProperties, MESH_PT_SFJImporter, MESH_OT_ImportSFJ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mesh_importer_props = bpy.props.PointerProperty(type=MeshImportProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.mesh_importer_props

if __name__ == "__main__":
    register()
