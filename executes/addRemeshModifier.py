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
from ..sceneConfig import getSceneProps


def binary_search(func, low, high, x, increment):

    # Check base case
    if high >= low:

        mid = (high + low) / 2

        # If element is present at the middle itself
        if func(mid) == x:
            return mid

        # If element is smaller than mid, then it can only
        # be present in left subarray
        elif func(mid) > x:
            return binary_search(func, low, mid - increment, x, increment)

        # Else the element can only be present in right subarray
        else:
            return binary_search(func, mid + increment, high, x, increment)

    else:
        # Element is not present in the array
        return -1


def execute(self, context):

    props = getSceneProps()
    target_size = props.size
    axis = props.axis
    joinSelected = props.joinSelected

    axis_num = -1
    if axis == "OP1":
        axis_num = 0
    elif axis == "OP2":
        axis_num = 1
    elif axis == "OP3":
        axis_num = 2

    if joinSelected:
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.join()
        bpy.ops.mesh.print3d_clean_non_manifold()

    active_obj = bpy.context.active_object

    diff = active_obj.scale-mathutils.Vector((1, 1, 1))
    if diff.magnitude != 0:
        self.report({"WARNING"}, "please apply scale first! ")
        return {"CANCELLED"}

    rot = active_obj.rotation_euler
    if rot[0] != 0 or rot[1] != 0 or rot[2] != 0:
        self.report({"WARNING"}, "please apply rotation first! ")
        return {"CANCELLED"}

    smooth_name = "remesh smooth"
    smooth_remesh_mod = active_obj.modifiers.get(smooth_name)
    if smooth_remesh_mod:
        active_obj.modifiers.remove(smooth_remesh_mod)

    block_name = "block remesh"
    block_remesh_mod = active_obj.modifiers.get(block_name) or active_obj.modifiers.new(
        name=block_name, type='REMESH')
    block_remesh_mod.mode = 'BLOCKS'

    # -- get obj data after modifiers applied

    block_remesh_mod.octree_depth = 2

    def getDimention():
        time.sleep(0.1)
        depsgraph = context.evaluated_depsgraph_get()
        active_obj_eval = active_obj.evaluated_get(depsgraph)
        cube_width = butils.cubeWidthFromObj(active_obj_eval)
        return butils.getFinalCubeyDimentions(active_obj_eval, cube_width)[axis_num]

    def getDimentionAtScale(scale):
        block_remesh_mod.scale = scale
        dimention = getDimention()
        return dimention

    while getDimention() < target_size:
        block_remesh_mod.octree_depth += 1

    binary_search(getDimentionAtScale, .1, .99, target_size, .001)

    depsgraph = context.evaluated_depsgraph_get()
    active_obj_eval = active_obj.evaluated_get(depsgraph)
    cube_width = butils.cubeWidthFromPoly(
        active_obj_eval, active_obj_eval.data.polygons[0])

    smooth_remesh_mod = active_obj.modifiers.get(smooth_name) or active_obj.modifiers.new(
        name=smooth_name, type='REMESH')
    smooth_remesh_mod.mode = 'VOXEL'
    smooth_remesh_mod.voxel_size = 0.01

    bpy.ops.object.modifier_move_up(modifier=smooth_name)

    self.report({"INFO"}, "dimentions = " +
                str(butils.toTuple(butils.getFinalCubeyDimentions(
                    active_obj_eval, cube_width))))

    bpy.ops.ed.undo_push(message="Edit Assets")
    return {'FINISHED'}
