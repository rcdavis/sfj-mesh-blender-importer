import bpy
import struct
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class VertInfluences:
    influences: Tuple[int, int, int, int]
    weights: Tuple[float, float, float, float]

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

        # Call your mesh loading logic here
        self.report({'INFO'}, f"Importing SFJ mesh from: {filepath}")
        self.__load_sfj_mesh(filepath)
        return {'FINISHED'}

    def __load_sfj_mesh(self, filepath):
        vertices: List[AnimVertex] = []
        faces = []

        with open(filepath, "rb") as file:
            numTextures = struct.unpack('<I', file.read(4))[0]
            self.report({'INFO'}, f"The number of textures is: {numTextures}")

            numVerts = struct.unpack('<I', file.read(4))[0]
            self.report({'INFO'}, f"The number of verts is: {numVerts}")

            for i in range(numVerts):
                posx, posy, posz = struct.unpack("<fff", file.read(12))
                normx, normy, normz = struct.unpack("<fff", file.read(12))
                tanx, tany, tanz = struct.unpack("<fff", file.read(12))
                texu, texv = struct.unpack("<ff", file.read(8))

                boneInfluences: List[int] = []
                boneWeights: List[float] = []

                for curInfluence in range(4):
                    boneInfluences.append(struct.unpack("<I", file.read(4))[0])
                    boneWeights.append(struct.unpack("<f", file.read(4))[0])

                vertices.append(AnimVertex(
                    pos=(posx, posy, posz),
                    norm=(normx, normy, normz),
                    tan=(tanx, tany, tanz),
                    texCoords=(texu, texv),
                    influences=VertInfluences(
                        influences=(boneInfluences[0], boneInfluences[1], boneInfluences[2], boneInfluences[3]),
                        weights=(boneWeights[0], boneWeights[1], boneWeights[2], boneWeights[3])
                    )
                ))

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
