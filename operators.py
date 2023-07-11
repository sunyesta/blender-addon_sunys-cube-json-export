import bpy
import webbrowser

from . import env
from . import sceneConfig


from .executes import addRemeshModifier
from .executes import bake
from .executes import blockyUtils
from .executes import exportColors
from .executes import generateUVs
from .executes import getBlocks
from .executes import selectSimilarColor
from .executes import uvColorTools

# ============= OBJECT MODE =============

# regex to get the operator class names: class (.*)\(


class GetBlocks(bpy.types.Operator):
    """Tooltip"""
    bl_idname = env.id + \
        ".getblocks"  # must be all lowercase  # best to put plugin name then obperator name # must be all lowercase
    bl_label = "getblocks"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        return getBlocks.execute(self, context)


class AddRemeshModifier(bpy.types.Operator):
    """Tooltip"""
    bl_idname = env.id + \
        ".addremeshmodifier"  # must be all lowercase  # best to put plugin name then obperator name # must be all lowercase
    bl_label = "addremeshmodifier"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        return addRemeshModifier.execute(self, context)


class Bake(bpy.types.Operator):
    """Tooltip"""
    bl_idname = env.id + \
        ".bake"  # must be all lowercase  # best to put plugin name then obperator name # must be all lowercase
    bl_label = "bake"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        return bake.execute(self, context)


class BlockyUtils(bpy.types.Operator):
    """Tooltip"""
    bl_idname = env.id + \
        ".blockyutils"  # must be all lowercase  # best to put plugin name then obperator name # must be all lowercase
    bl_label = "blockyutils"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        return blockyUtils.execute(self, context)


class ExportColors(bpy.types.Operator):
    """Tooltip"""
    bl_idname = env.id + \
        ".exportcolors"  # must be all lowercase  # best to put plugin name then obperator name # must be all lowercase
    bl_label = "exportcolors"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        return exportColors.execute(self, context)


class GenerateUVs(bpy.types.Operator):
    """Tooltip"""
    bl_idname = env.id + \
        ".generateuvs"  # must be all lowercase  # best to put plugin name then obperator name # must be all lowercase
    bl_label = "generateuvs"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        return generateUVs.execute(self, context)


class SelectSimilarColor(bpy.types.Operator):
    """Tooltip"""
    bl_idname = env.id + \
        ".selectsimilarcolor"  # must be all lowercase  # best to put plugin name then obperator name # must be all lowercase
    bl_label = "selectsimilarcolor"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        return selectSimilarColor.execute(self, context)


class UvColorTools(bpy.types.Operator):
    """Tooltip"""
    bl_idname = env.id + \
        ".uvcolortools"  # must be all lowercase  # best to put plugin name then obperator name # must be all lowercase
    bl_label = "uvcolortools"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        return uvColorTools.execute(self, context)


class OpenDocs(bpy.types.Operator):
    bl_idname = env.id + \
        ".opendocs"  # must be all lowercase  # best to put plugin name then obperator name # must be all lowercase
    bl_label = "opendocs"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        webbrowser.open("https://github.com/")
        return {'FINISHED'}

# ============= EDIT MODE =============


# ============= REGISTRATION =============
classes = [GetBlocks, AddRemeshModifier, Bake, BlockyUtils,
           ExportColors, GenerateUVs, SelectSimilarColor, UvColorTools, OpenDocs]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
