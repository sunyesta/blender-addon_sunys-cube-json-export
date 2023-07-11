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


def rgb_to_hsv(rgb):
    r, g, b = rgb[0], rgb[1], rgb[2]
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return (h, s, v)


f = open('C:/Users/Mary/Documents/Code/AutoHotkey/Other/Blocky/aj_colors.json')
valid_colors_tuple = json.load(f)
valid_colors_rgb = []
valid_colors_hsv = []
for color in valid_colors_tuple:
    valid_colors_rgb.append(mathutils.Vector(color))
    valid_colors_hsv.append(mathutils.Vector(rgb_to_hsv(color)))

calced_colors = {}


def getClosestColor(my_color):
    if my_color in calced_colors:
        return calced_colors[my_color]

    def powerVector(vec, pow):
        return mathutils.Vector((math.pow(vec.x, pow), math.pow(vec.y, pow), math.pow(vec.z, pow)))

    def calcLoss(col0_rgb, col0_hsv, col1_index):
        col1_rgb = valid_colors_rgb[col1_index]
        col1_hsv = valid_colors_hsv[col1_index]

        return (powerVector(col0_rgb, 1.8)-powerVector(col1_rgb, 1.8)).magnitude + \
            (powerVector(col0_hsv, 1.2)-powerVector(col1_hsv, 1.2)).magnitude

    my_pow = 4

    my_color_rgb = mathutils.Vector(my_color)
    my_color_hsv = mathutils.Vector(rgb_to_hsv(my_color))

    min_dis = calcLoss(my_color_rgb, my_color_hsv, 0)
    best_col = valid_colors_rgb[0]
    for val_color_index in range(len(valid_colors_rgb)):

        dis = calcLoss(my_color_rgb, my_color_hsv, val_color_index)

        if dis < min_dis:
            best_col = valid_colors_rgb[val_color_index]
            min_dis = dis

    calced_colors[my_color] = butils.toTuple(best_col)
    return calced_colors[my_color]
    return


def averageVecs(vecs):
    average_vec = mathutils.Vector((0, 0))
    for vec in vecs:
        average_vec += vec
    return average_vec/len(vecs)


def _channel_to_hex(color_val: int) -> str:
    return


def rgb_to_hex(rgb):
    # return '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])
    temp = "0x{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
    return temp


def getImagePixels(image):
    # create a copy of the image pixels
    pixels = []
    pixels[:] = image.pixels[:]
    return pixels


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


def setPixel(img, uv_pixels, uv_coord, rgb_tuple):
    """ get RGBA value for specified coordinate in UV image
    pixels    -- list of pixel data from UV texture image
    uv_coord  -- UV coordinate of desired pixel value
    """
    x = 0
    y = 1

    uv_pixels = uv_pixels
    pixel_coord = (int(uv_coord.x*img.size[x]), int(uv_coord.y*img.size[y]))
    pixelNumber = (img.size[x]*pixel_coord[y]+pixel_coord[x])
    uv_pixels[pixelNumber*4 + 0] = rgb_tuple[0]/255
    uv_pixels[pixelNumber*4 + 1] = rgb_tuple[1]/255
    uv_pixels[pixelNumber*4 + 2] = rgb_tuple[2]/255
    uv_pixels[pixelNumber*4 + 3] = 1


def previewMesh(color_dict, face_dict, uv_layer, img):
    uv_pixels = getImagePixels(img)
    for loc in face_dict:
        face = face_dict[loc]
        color = color_dict[loc]

        coords = [face.loops[0][uv_layer].uv, face.loops[1][uv_layer].uv,
                  face.loops[2][uv_layer].uv, face.loops[3][uv_layer].uv]
        # print(coords)
        uv_coord = averageVecs(coords)
        setPixel(img, uv_pixels, uv_coord, color)
    img.pixels[:] = uv_pixels


def execute(self, context):
    active_obj = bpy.context.active_object

    material_slots = active_obj.material_slots
    if len(material_slots) > 1:
        self.report({"WARNING"}, "obj must have only 1 material")
        return {"CANCELLED"}

    bpy.ops.object.editmode_toggle()
    bm = bmesh.from_edit_mesh(active_obj.data)

    cube_width = butils.cubeWidthFromPoly(
        active_obj, active_obj.data.polygons[0])

    # -- set up a dictionary that maps a cube location to one of its faces
    bm_cubeLoc_dict = butils.bm_getCubeDict(active_obj, bm, cube_width)

    mat = active_obj.material_slots[0].material

    image = None
    for n in mat.node_tree.nodes:
        if n.type == 'TEX_IMAGE':
            image = n.image

    self.report({"INFO"}, "image = "+str(image))

    if not image:
        self.report({"WARNING"}, "No image in material")
        return {"CANCELLED"}

    uv_pixels = getImagePixels(image)

    uv_layer = bm.loops.layers.uv.verify()  # get the current UV layer

    color_dict = {}
    m = 0
    # -- make color json
    for loc in bm_cubeLoc_dict:
        face = bm_cubeLoc_dict[loc]
        coords = [face.loops[0][uv_layer].uv, face.loops[1][uv_layer].uv,
                  face.loops[2][uv_layer].uv, face.loops[3][uv_layer].uv]
        # print(coords)
        uv_coord = averageVecs(coords)
        rgb = getPixel(image, uv_pixels, uv_coord)

        color_dict[loc] = rgb
        m += 1
        if m % 100 == 0:
            print(m)

    x, y, z = 0, 1, 2
    dimentions_tuple = butils.toTuple(
        butils.getFinalCubeyDimentions(active_obj, cube_width))

    grid_zyx = np.full(
        (dimentions_tuple[z]+1,  dimentions_tuple[y]+1,  dimentions_tuple[x]+1), "None", dtype="U10")

    for loc in color_dict:
        color = color_dict[loc]
        valid_color = getClosestColor(color)
        color_dict[loc] = valid_color
        hex = rgb_to_hex(valid_color)
        grid_zyx[loc[z]][loc[y]][loc[x]] = hex

    print(grid_zyx.tolist())

    with open(r'C:/Users/Mary/Downloads/color_data.json', 'w+') as outfile:
        json.dump(grid_zyx.tolist(), outfile)

    # previewMesh(color_dict, bm_cubeLoc_dict, uv_layer, image)

    return {'FINISHED'}
