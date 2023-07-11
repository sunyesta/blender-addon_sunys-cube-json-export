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
from . import blockyUtils as butils


def execute(self, context):

    active_obj = context.active_object

    # -- get obj data after modifiers applied
    depsgraph = context.evaluated_depsgraph_get()
    active_obj_eval = active_obj.evaluated_get(depsgraph)

    # -- get cube_width of each cube
    cube_width = butils.cubeWidthFromObj(
        active_obj_eval)

    if cube_width == 0:
        self.report({"WARNING"}, "cube width = 0 " +
                    str(butils.toTuple(dimentions)))
        return {"CANCELLED"}

    # ERROR HANDLING
    max_width = 61
    dimentions = butils.getFinalCubeyDimentions(active_obj, cube_width)

    if dimentions.x > max_width:
        # bpy.ops.ed.undo()
        self.report({"WARNING"}, "Too wide on the X axis! " +
                    str(butils.toTuple(dimentions)))
        return {"CANCELLED"}

    if dimentions.y > max_width:
        # bpy.ops.ed.undo()
        self.report({"WARNING"}, "Too wide on the Y axis!")
        return {"CANCELLED"}

    if dimentions.z > max_width:
        # bpy.ops.ed.undo()
        self.report({"WARNING"}, "Too tall!")
        return {"CANCELLED"}
    ###

    locations_dict = butils.getCubeDict(active_obj_eval, cube_width)

    x = 0
    y = 1
    z = 2

    dimentions_tuple = butils.toTuple(dimentions)

    grid_zyx = np.zeros(
        (dimentions_tuple[z]+1,  dimentions_tuple[y]+1,  dimentions_tuple[x]+1), dtype=int)

    #
    for loc in locations_dict:

        # mark each spot where a cube exists
        grid_zyx[loc[z]][loc[y]][loc[x]] = 1

        # DEBUG
        # bpy.ops.mesh.primitive_cube_add(
        #     size=1, enter_editmode=False, align='WORLD', location=mathutils.Vector(loc), scale=(1, 1, 1))

    for z_layer in grid_zyx:
        for y_index in range(0, len(z_layer)-1, 2):
            forward_y_layer = z_layer[y_index]
            backward_y_layer = z_layer[y_index+1]

            y_layers = [forward_y_layer, backward_y_layer]
            end_index = [-1, -1]

            stop = 1
            for y_layer_index in range(len(y_layers)):
                y_layer = y_layers[y_layer_index]
                for x_index in range(len(y_layer)-1, -1, -1):
                    x_val = y_layer[x_index]
                    if x_val == 1:
                        break

                    prev_x_val = y_layer[x_index-1]
                    if prev_x_val == 1 or x_index == 0:
                        end_index[y_layer_index] = x_index

            max_end_index = max(end_index)
            if max_end_index == -1:
                pass
            else:
                forward_y_layer[max_end_index] = -1
                backward_y_layer[max_end_index] = -1

    # write results to JSON
    with open(r'C:\Users\Mary\Downloads\json_data.json', 'w+') as outfile:
        json.dump(grid_zyx.tolist(), outfile)

    startstr = "start at x = " + \
        str(round(dimentions_tuple[x]/2)) + \
        "   y = "+str(round(dimentions_tuple[y]/2))

    self.report({"INFO"}, "Exported JSON, dimentions = " +
                str(dimentions_tuple) + "blocks = " + str(len(locations_dict))+"   price = " + str(len(locations_dict)/7)+startstr)

    return {'FINISHED'}
