from . import env
from . import sceneConfig
from . import operators
from . import ui

name = env.name
print("name = ", name)
bl_info = {
    "name": "sunys cube json export 1",  # WARNING: change this in env!
    "author": "Mary",
    "version": (1, 0, 1),
    "description": "",
    "blender": (3, 5, 0),
    "location": "View3D > Sidebar > Suny > sunys cube json export 1",
    "warning": "",
    "category": "Mesh",
    "tracker_url": "",
    "wiki_url": ""
}

# ORDER IS IMPORTANT !
modules = [
    sceneConfig,
    operators,
    ui
]


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()


if __name__ == "__main__":
    register()
