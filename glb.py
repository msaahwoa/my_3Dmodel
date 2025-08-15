from pygltflib import GLTF2, Scene, Node, Mesh, Buffer, BufferView, Accessor, Asset, Material, Primitive
import numpy as np
import json

# ======== 3m立方体 (面ごとに独立した頂点) ========
# 1面4頂点 × 6面 = 24頂点
positions = np.array([
    # bottom (z = -1.5)
    [-1.5, -1.5, -1.5],
    [ 1.5, -1.5, -1.5],
    [ 1.5,  1.5, -1.5],
    [-1.5,  1.5, -1.5],

    # top (z = +1.5)
    [-1.5, -1.5,  1.5],
    [ 1.5, -1.5,  1.5],
    [ 1.5,  1.5,  1.5],
    [-1.5,  1.5,  1.5],

    # front (y = -1.5)
    [-1.5, -1.5, -1.5],
    [ 1.5, -1.5, -1.5],
    [ 1.5, -1.5,  1.5],
    [-1.5, -1.5,  1.5],

    # back (y = +1.5)
    [-1.5,  1.5, -1.5],
    [ 1.5,  1.5, -1.5],
    [ 1.5,  1.5,  1.5],
    [-1.5,  1.5,  1.5],

    # left (x = -1.5)
    [-1.5, -1.5, -1.5],
    [-1.5,  1.5, -1.5],
    [-1.5,  1.5,  1.5],
    [-1.5, -1.5,  1.5],

    # right (x = +1.5)
    [ 1.5, -1.5, -1.5],
    [ 1.5,  1.5, -1.5],
    [ 1.5,  1.5,  1.5],
    [ 1.5, -1.5,  1.5],
], dtype=np.float32)

# ======== 法線ベクトル（各面の方向） ========
normals = np.array(
    [[0, 0, -1]] * 4 +   # bottom
    [[0, 0,  1]] * 4 +   # top
    [[0, -1, 0]] * 4 +   # front
    [[0,  1, 0]] * 4 +   # back
    [[-1, 0, 0]] * 4 +   # left
    [[ 1, 0, 0]] * 4,    # right
    dtype=np.float32
)

# ======== インデックス（各面を2枚の三角形に分割） ========
indices = np.array([
    0, 1, 2, 2, 3, 0,        # bottom
    4, 5, 6, 6, 7, 4,        # top
    8, 9, 10, 10, 11, 8,     # front
    12, 13, 14, 14, 15, 12,  # back
    16, 17, 18, 18, 19, 16,  # left
    20, 21, 22, 22, 23, 20   # right
], dtype=np.uint16)

# ======== バッファ作成 ========
position_bytes = positions.tobytes()
normal_bytes = normals.tobytes()
index_bytes = indices.tobytes()
buffer_data = position_bytes + normal_bytes + index_bytes

# ======== GLTF2 オブジェクト ========
gltf = GLTF2(
    asset=Asset(version="2.0"),
    buffers=[Buffer(byteLength=len(buffer_data))],
    scenes=[Scene(nodes=[0])],
    nodes=[Node(mesh=0)],
    meshes=[Mesh(primitives=[Primitive(
        attributes={"POSITION": 0, "NORMAL": 1},
        indices=2,
        material=0
    )])],
    materials=[Material(
        pbrMetallicRoughness={"baseColorFactor": [1.0, 0.0, 0.0, 1.0]},
        extensions={"KHR_materials_unlit": {}}
    )],
    bufferViews=[
        BufferView(buffer=0, byteOffset=0, byteLength=len(position_bytes), target=34962),  # positions
        BufferView(buffer=0, byteOffset=len(position_bytes), byteLength=len(normal_bytes), target=34962),  # normals
        BufferView(buffer=0, byteOffset=len(position_bytes) + len(normal_bytes), byteLength=len(index_bytes), target=34963)  # indices
    ],
    accessors=[
        Accessor(bufferView=0, componentType=5126, count=len(positions),
                 type="VEC3", min=[-1.5, -1.5, -1.5], max=[1.5, 1.5, 1.5]),
        Accessor(bufferView=1, componentType=5126, count=len(normals), type="VEC3"),
        Accessor(bufferView=2, componentType=5123, count=len(indices), type="SCALAR")
    ],
    extensionsUsed=["KHR_materials_unlit"]
)

gltf.set_binary_blob(buffer_data)
gltf.save_binary("cube.glb")

# ======== CZML作成 ========
longitude = 139.7535093754493
latitude = 35.65361100740639
height = 10

czml = [
    {"id": "document", "version": "1.0"},
    {
        "id": "cube1",
        "name": "Red Cube",
        "position": {"cartographicDegrees": [longitude, latitude, height]},
        "model": {
            "gltf": "https://msaahwoa.github.io/my_3Dmodel/cube.glb",  # URLに変えてもOK
            "scale": 1.0,
            "minimumPixelSize": 1
        }
    }
]

with open("cube.czml", "w", encoding="utf-8") as f:
    json.dump(czml, f, ensure_ascii=False, indent=2)

print("cube.glb と cube.czml を同じフォルダに置いて PLATEAU に読み込んでください。")
