import mathutils as mu
import bpy


def getFinalCubeyDimentions(obj_eval, cube_width):
    if cube_width == 0:
        return mu.Vector((0, 0, 0))

    dimentions = mu.Vector(
        obj_eval.bound_box[6]) - mu.Vector(obj_eval.bound_box[0])
    dimentions /= cube_width
    return dimentions


def normalize(min_val, max_val, cur_val):
    print("max min:", max_val, min_val)
    numerator = (cur_val-min_val)
    denominator = (max_val-min_val)

    return mu.Vector((numerator.x/denominator.x, numerator.y/denominator.y))


def toTuple(vec):
    return (
        round(vec.x), round(vec.y), round(vec.z))


def cubeWidthFromPoly(obj, polygon):
    base_vert = obj.data.vertices[polygon.vertices[0]]
    other_vert_1 = obj.data.vertices[polygon.vertices[1]]
    other_vert_2 = obj.data.vertices[polygon.vertices[2]]

    dis1 = (base_vert.co-other_vert_1.co).magnitude
    dis2 = (base_vert.co-other_vert_2.co).magnitude

    width = min(dis1, dis2)

    return width


def cubeWidthFromObj(eval_obj):
    # -- get obj data after modifiers applied

    if len(eval_obj.data.polygons) == 0:
        return 0

    return cubeWidthFromPoly(
        eval_obj, eval_obj.data.polygons[0])


def getCubeCenter(obj_eval, polygon, cube_width):
    face_center = polygon.center
    normal = polygon.normal
    cube_center = face_center - (normal*cube_width/2)
    cube_center /= cube_width  # normalize the cube center
    print(cube_center)
    min_loc = mu.Vector(toTuple(mu.Vector(
        obj_eval.bound_box[0])/cube_width))
    cube_center -= min_loc

    return toTuple(cube_center)


def bm_getCubeCenter(obj_eval, bm_face, cube_width):
    face_center = bm_face.calc_center_bounds()
    normal = bm_face.normal
    cube_center = face_center - (normal*cube_width/2)
    cube_center /= cube_width  # normalize the cube center

    min_loc = mu.Vector(toTuple(mu.Vector(
        obj_eval.bound_box[0])/cube_width))
    cube_center -= min_loc

    return toTuple(cube_center)


def getCubeDict(obj_eval, cubeWidth):
    locations_dict = {}
    i = 0
    # loop through all polys
    for polygon in obj_eval.data.polygons:
        cube_center_tuple = getCubeCenter(obj_eval, polygon, cubeWidth)

        locations_dict[cube_center_tuple] = polygon
        i += 1

    return locations_dict


def bm_getCubeDict(obj_eval, bm, cubeWidth):
    locations_dict = {}
    i = 0
    # loop through all polys
    for face in bm.faces:
        cube_center_tuple = bm_getCubeCenter(obj_eval, face, cubeWidth)

        locations_dict[cube_center_tuple] = face
        i += 1

    return locations_dict
