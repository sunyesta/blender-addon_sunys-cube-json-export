import json
import string
from math import floor
import time
import bpy
import mathutils
from numpy import poly
import numpy as np
import math
import bmesh
import random
from . import blockyUtils as butils


def onlySelect(base_obj):
    for obj in bpy.data.objects:
        obj.select_set(False)
    base_obj.select_set(True)
    bpy.context.view_layer.objects.active = base_obj


def execute(self, context):

    selected_objects = [
        obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if len(selected_objects) < 2:
        self.report({'ERROR'}, "at least 2 meshes should be selected")
        return {'CANCELLED'}

    # save the base obj
    base_obj = bpy.context.active_object
    if base_obj.type != 'MESH':
        self.report({'ERROR'}, "Base obj must be a mesh.")
        return {'CANCELLED'}

    has_material_with_image = False
    for slot in base_obj.material_slots:
        if slot.material and slot.material.use_nodes:
            for node in slot.material.node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    has_material_with_image = True
                    break
    if not has_material_with_image:
        self.report({'ERROR'}, "base mesh must have a material with an image")
        return {'CANCELLED'}

    # select the nonactive obj as the ref_obj
    ref_objs = [obj for obj in selected_objects if obj !=
                base_obj]

    def selectRefObjs(select):
        for obj in ref_objs:
            obj.select_set(select)

    for obj in selected_objects:
        if obj.data.uv_layers.active:
            obj.data.uv_layers.active.name = 'MY UV'

    # join the reference objects into 1 mesh
    selectRefObjs(True)
    base_obj.select_set(False)

    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'}, TRANSFORM_OT_translate={"value": (0, 0, 0), "orient_axis_ortho": 'X', "orient_type": 'GLOBAL', "orient_matrix": ((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type": 'GLOBAL', "constraint_axis": (False, False, False), "mirror": False, "use_proportional_edit": False, "proportional_edit_falloff": 'SMOOTH', "proportional_size": 1,
                                  "use_proportional_connected": False, "use_proportional_projected": False, "snap": False, "snap_target": 'CLOSEST', "snap_point": (0, 0, 0), "snap_align": False, "snap_normal": (0, 0, 0), "gpencil_strokes": False, "cursor_transform": False, "texture_space": False, "remove_on_cancel": False, "view2d_edge_pan": False, "release_confirm": False, "use_accurate": False, "use_automerge_and_split": False})
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    joined_refobj = bpy.context.selected_objects[0]

    selectRefObjs(False)
    base_obj.select_set(True)
    joined_refobj.select_set(True)
    bpy.context.view_layer.objects.active = base_obj

    # create the cage obj
    cage_obj = base_obj.copy()
    cage_obj.data = base_obj.data.copy()
    cage_obj.name = "cage"
    context.collection.objects.link(cage_obj)

    # expand the cage
    onlySelect(cage_obj)
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.shrink_fatten(value=0.03, use_even_offset=False, mirror=True, use_proportional_edit=False,
                                    proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.object.editmode_toggle()

    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.context.scene.render.bake.use_cage = True
    bpy.context.scene.render.bake.cage_object = cage_obj
    bpy.context.scene.cycles.bake_type = 'DIFFUSE'

    bpy.ops.object.select_all(action='DESELECT')
    base_obj.select_set(True)
    joined_refobj.select_set(True)
    bpy.context.view_layer.objects.active = base_obj

    bpy.ops.object.bake(type='DIFFUSE', use_selected_to_active=True, cage_object=cage_obj.name,
                        save_mode='INTERNAL',  use_cage=True, target='IMAGE_TEXTURES')

    onlySelect(cage_obj)
    bpy.ops.object.delete()

    onlySelect(joined_refobj)
    bpy.ops.object.delete()

    return {'FINISHED'}
