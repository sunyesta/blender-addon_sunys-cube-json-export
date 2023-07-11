import bpy

from . import env
from . import operators
from . import sceneConfig


class objectPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = env.name
    bl_idname = "OBJECT_PT_"+env.id
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = env.bl_category  # the tab name
    bl_context = "objectmode"

    def draw(self, context):  # the stuff in the panel
        layout = self.layout

        row = layout.row()
        row.operator(operators.GetBlocks.bl_idname,
                     text="GetBlocks")

        row = layout.row()
        row.operator(operators.ExportColors.bl_idname,
                     text="ExportColors")

        row = layout.row()
        row.operator(operators.AddRemeshModifier.bl_idname,
                     text="AddRemeshModifier")
        row.prop(sceneConfig.getSceneProps(), "size")
        row.prop(sceneConfig.getSceneProps(), "axis")
        row.prop(sceneConfig.getSceneProps(), "joinselected")

        row = layout.row()
        row.operator(operators.GenerateUVs.bl_idname,
                     text="GenerateUVs")

        row = layout.row()
        row.operator(operators.Bake.bl_idname,
                     text="Bake")

        row = layout.row()
        row.operator(operators.SelectSimilarColor.bl_idname,
                     text="SelectSimilarColor")

        row = layout.row()
        row.operator(operators.OpenDocs.bl_idname,
                     text="OpenDocs")


classes = [objectPanel]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
