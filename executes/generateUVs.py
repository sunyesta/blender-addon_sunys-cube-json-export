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
from . import uvColorTools


def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb


def newMaterial(id):

    mat = bpy.data.materials.get(id)

    if mat is None:
        mat = bpy.data.materials.new(name=id)

    mat.use_nodes = True

    if mat.node_tree:
        mat.node_tree.links.clear()
        mat.node_tree.nodes.clear()

    return mat


def execute(self, context):
    active_obj = bpy.context.active_object

    # -- prepare object for uvs

    # only select object
    for obj in bpy.data.objects:
        obj.select_set(False)
    active_obj.select_set(True)

    # apply all modifiers
    bpy.context.view_layer.objects.active = active_obj
    bpy.ops.object.convert(target='MESH')

    # delete all materials from object
    for i in range(len(active_obj.material_slots)):
        bpy.ops.object.material_slot_remove({'object': active_obj})

    # -- unwrap all faces individually
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.mark_seam(clear=False)
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0)

    # -- get width of cube
    cube_width = butils.cubeWidthFromPoly(
        active_obj, active_obj.data.polygons[0])

    bm = bmesh.from_edit_mesh(active_obj.data)

    # -- set up a dictionary that maps a cube location to one of its faces
    bm_cubeLoc_dict = butils.bm_getCubeDict(active_obj, bm, cube_width)

    # -- select only the faces in bm_cubeLoc_dict so that only one face of each cube is selected
    for face in bm.faces:
        face.select = False

    for loc in bm_cubeLoc_dict:
        bm_face = bm_cubeLoc_dict[loc]
        bm_face.select = True

    bmesh.update_edit_mesh(mesh=active_obj.data, destructive=True)

    uv_layer = bm.loops.layers.uv.verify()  # get the current UV layer

    # calculate uv data
    pixel_margin = 2  # set this to the pixel margin you want around each cube's island
    uvs_per_col = math.ceil(math.sqrt(len(bm_cubeLoc_dict)))
    uv_area_needed_per_col = uvs_per_col + uvs_per_col*pixel_margin*2
    image_size = 1024

    # -- set size of each uv cube to 1,1

    # loop over the active face of each cube
    for loc in bm_cubeLoc_dict:
        face = bm_cubeLoc_dict[loc]

        # get the min and max points of the face's uv
        min_pt = mathutils.Vector((100, 100))
        max_pt = mathutils.Vector((-1, -1))
        for loop in face.loops:
            cur_pt = loop[uv_layer].uv
            min_pt.x = min(min_pt.x, cur_pt.x)
            min_pt.y = min(min_pt.y, cur_pt.y)

            max_pt.x = max(max_pt.x, cur_pt.x)
            max_pt.y = max(max_pt.y, cur_pt.y)

        # normalize the face's uv coords so that the min point is 0 and the max point is 1
        for loop in face.loops:
            loop[uv_layer].uv = butils.normalize(
                min_pt, max_pt, loop[uv_layer].uv)

    # -- evenly distribute uvs
    current_loc = mathutils.Vector((pixel_margin, pixel_margin))

    # loop over the active face of each cube
    i = 0
    for loc in bm_cubeLoc_dict:

        # if we reach the end of a row, we go to the next one
        if i % uvs_per_col == 0 and i != 0:
            current_loc = mathutils.Vector(
                (pixel_margin, current_loc.y+pixel_margin*2+1))

        # set face to current_loc
        face = bm_cubeLoc_dict[loc]
        for loop in face.loops:
            loop[uv_layer].uv += current_loc

        current_loc += mathutils.Vector((pixel_margin*2+1, 0))
        i += 1

    # -- scale the layout so that it is within the uv bounds
    min_pt = mathutils.Vector((0, 0))
    max_pt = mathutils.Vector(
        (uv_area_needed_per_col, uv_area_needed_per_col))
    for loc in bm_cubeLoc_dict:
        face = bm_cubeLoc_dict[loc]
        for loop in face.loops:
            loop[uv_layer].uv = butils.normalize(
                min_pt, max_pt, loop[uv_layer].uv)
            loop[uv_layer].uv *= uv_area_needed_per_col/image_size

    # -- copy active face data to the rest of the faces for each cube
    for f in bm.faces:

        cube_center = butils.bm_getCubeCenter(active_obj, f, cube_width)

        # loops of active face of cube
        ref_loops = bm_cubeLoc_dict[cube_center].loops

        for loop_index in range(len(f.loops)):
            loop = f.loops[loop_index]
            ref_loop = ref_loops[loop_index]
            loop[uv_layer].uv = ref_loop[uv_layer].uv

    bmesh.update_edit_mesh(mesh=active_obj.data, destructive=True)

    # -- create material

    # create new material
    mat_id = str(random.randint(0, 1000))
    mat = newMaterial("aj blocky"+mat_id)
    mat.use_nodes = True

    # create texture
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.interpolation = 'Closest'

    image = bpy.data.images.new(
        name="aj image"+str(mat_id), width=image_size, height=image_size)
    texImage.image = image

    # create material output
    diffuse = mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    material_output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')

    # link nodes
    mat.node_tree.links.new(
        texImage.outputs['Color'], diffuse.inputs['Color'])
    mat.node_tree.links.new(
        diffuse.outputs['BSDF'], material_output.inputs['Surface'])

    active_obj.data.materials.append(mat)

    return {'FINISHED'}
