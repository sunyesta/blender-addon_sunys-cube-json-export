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

import os


def getImagePixels(image):
    # create a copy of the image pixels
    pixels = []
    pixels[:] = image.pixels[:]
    return pixels


def averageVecs(vecs):
    average_vec = mathutils.Vector((0, 0))
    for vec in vecs:
        average_vec += vec
    return average_vec/len(vecs)


def getPixel(img, uv_pixels, uv_coord):
    """ get RGBA value for specified coordinate in UV image
    pixels    -- list of pixel data from UV texture image
    uv_coord  -- UV coordinate of desired pixel value
    """
    x = 0
    y = 1

    uv_pixels = uv_pixels
    pixel_coord = (int(uv_coord.x*img.size[x]), int(uv_coord.y*img.size[y]))
    pixelNumber = (img.size[x]*pixel_coord[y]+pixel_coord[x])
    r = uv_pixels[pixelNumber*4 + 0]
    g = uv_pixels[pixelNumber*4 + 1]
    b = uv_pixels[pixelNumber*4 + 2]
    # a = uv_pixels[pixelNumber*4 + 3]
    return (int(r*255), int(g*255), int(b*255))


def getColorAtFace(bm_face, uv_layer, uv_pixels, image):
    coords = [bm_face.loops[0][uv_layer].uv, bm_face.loops[1][uv_layer].uv,
              bm_face.loops[2][uv_layer].uv, bm_face.loops[3][uv_layer].uv]
    # print(coords)
    uv_coord = averageVecs(coords)
    rgb = getPixel(image, uv_pixels, uv_coord)
    return rgb


def execute(self, context):
    active_obj = bpy.context.active_object

    mat = active_obj.material_slots[0].material
    image = None
    for n in mat.node_tree.nodes:
        if n.type == 'TEX_IMAGE':
            image = n.image

    if not image:
        self.report({"WARNING"}, "No image in material")
        return {"CANCELLED"}

    uv_pixels = getImagePixels(image)

    bpy.ops.object.editmode_toggle()
    bm = bmesh.from_edit_mesh(active_obj.data)

    uv_layer = bm.loops.layers.uv.verify()  # get the current UV layer

    selected_Faces = [x for x in bm.faces if x.select]

    colors = {}
    for face in selected_Faces:
        cur_color = getColorAtFace(face, uv_layer, uv_pixels, image)
        colors[cur_color] = True

    m = 0
    for face in bm.faces:
        cur_color = getColorAtFace(face, uv_layer, uv_pixels, image)
        if colors.get(cur_color):
            # print(cur_color)
            face.select = True
            m += 1
            if m % 100 == 0:
                print(m)

    bmesh.update_edit_mesh(mesh=active_obj.data, destructive=False)
    bpy.ops.ed.undo_push(message="Edit Assets")
    return {'FINISHED'}
