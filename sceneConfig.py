# Layout of code is from zenbbq

import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty, PointerProperty, EnumProperty


class SceneProps(PropertyGroup):
    size: IntProperty(name="size",
                           description="size of remesh",
                           min=4,
                           max=1000,
                           default=61)

    axis: bpy.props.EnumProperty(name="axis",
                                      description="axis that the remesh operator will constrain it's size to",
                                      items=[
                                          ('OP1', 'x', ''), ('OP2', 'y', ''), ('OP3', 'z', '')]
                                 )

    joinSelected: bpy.props.BoolProperty(
        name="joinselected")


def register():

    # register scene props
    bpy.utils.register_class(SceneProps)
    bpy.types.Scene.sunyscubejsonexporty = PointerProperty(
        type=SceneProps)


def unregister():

    # unregister scene props
    bpy.utils.unregister_class(SceneProps)
    # del bpy.types.Scene.sunyscubejsonexporty


# @ propClassName = class name (not name="")
def getSceneProp(propClassName):
    return getattr(bpy.context.scene.sunyscubejsonexporty, propClassName)


def getSceneProps():
    return bpy.context.scene.sunyscubejsonexporty

# userConfig = bpy.context.scene.ZBBQ_PreviewRenderUserConfig
# ZBBQ_PreviewRenderConfigForSaving


# getattr(bpy.context.scene.sunyscubejsonexporty,"low prefix")
