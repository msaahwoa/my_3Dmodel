from pygltflib import GLTF2, Scene, Node, Mesh, Buffer, BufferView, Accessor, Asset, Material, Primitive
import numpy as np
import json

# ======== 3m立方体の頂点座標 ========
positions = np.array([
    [-1.5, -1.5, -1.5],
    [ 1.5, -1.5, -1.5],
    [ 1.5,  1.5, -1.5],
    [-1.5,  1.5, -1.5],
    [-1.5, -1.5,  1.5],
    [ 1.5, -1.5,  1.5],
    [ 1.5,  1.5,  1.5],
    [-1.5,  1.5,  1.5],
], dtype=np.float32)

indices = np.array([
    0,1,2, 2,3,0,  # bottom
    4,5,6, 6,7,4,  # top
    0,1,5, 5,4,0,  # front
    2,3,7, 7,6,2,  # back
    0,3,7, 7,4,0,  # left
    1,2,6, 6,5,1   # right
], dtype=np.uint16)

# ======== 法線ベクトル ========
# 立方体の各面ごとに法線を定義
normals = np.array([
    [ 0,  0, -1], [ 0,  0, -1], [ 0,  0, -1], [ 0,  0, -1],  # bottom
    [ 0,  0,  1], [ 0,  0,  1], [ 0,  0,  1], [ 0,  0,  1],  # top
], dtype=np.float32)

# ======== バイナリバッファ作成 ========
position_bytes = positions.tobytes()
normal_bytes = normals.tobytes()
index_bytes = indices.tobytes()
buffer_data = position_bytes + normal_bytes + index_bytes

# ======== GLTF2 オブジェクト作成 ========
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
        BufferView(buffer=0, byteOffset=0, byteLength=len(position_bytes)),  # positions
        BufferView(buffer=0, byteOffset=len(position_bytes), byteLength=len(normal_bytes)),  # normals
        BufferView(buffer=0, byteOffset=len(position_bytes) + len(normal_bytes), byteLength=len(index_bytes))  # indices
    ],
    accessors=[
        Accessor(bufferView=0, componentType=5126, count=len(positions),
                 type="VEC3", min=[-1.5, -1.5, -1.5], max=[1.5, 1.5, 1.5]),
        Accessor(bufferView=1, componentType=5126, count=len(normals),
                 type="VEC3"),
        Accessor(bufferView=2, componentType=5123, count=len(indices), type="SCALAR")
    ],
    extensionsUsed=["KHR_materials_unlit"]
)

# バイナリデータを埋め込み
gltf.set_binary_blob(buffer_data)

# GLB 保存
gltf.save_binary("cube.glb")

# ======== CZML 作成 ========
longitude = 139.7535093754493
latitude = 35.65361100740639
height = 10

czml = [
    {
        "id": "document",
        "version": "1.0"
    },
    {
        "id": "cube1",
        "name": "Red Cube",
        "position": {
            "cartographicDegrees": [longitude, latitude, height]
        },
        "model": {
            "gltf": "cube.glb",  # 同じフォルダに配置
            "scale": 1.0,
            "minimumPixelSize": 1
        }
    }
]

with open("cube.czml", "w", encoding="utf-8") as f:
    json.dump(czml, f, ensure_ascii=False, indent=2)

print("cube.glb と cube.czml を同じフォルダに置いて PLATEAU に読み込んでください。")
