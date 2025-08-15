# ======== 球メッシュ生成 ========
import numpy as np
from pygltflib import GLTF2, Asset, Buffer, BufferView, Accessor, Scene, Node, Mesh, Primitive, Material
import math
import json

# ==== CZML位置 ====
lon = 139.7535093754493
lat = 35.65361100740639
height = 100  # m

# WGS84地球半径など
a = 6378137.0  # 赤道半径
e2 = 6.69437999014e-3  # 扁平率^2

# 経緯度をラジアンに
lon_rad = math.radians(lon)
lat_rad = math.radians(lat)

# 緯度における曲率半径
N = a / math.sqrt(1 - e2 * math.sin(lat_rad)**2)

# ECEF座標
cx = (N + height) * math.cos(lat_rad) * math.cos(lon_rad)
cy = (N + height) * math.cos(lat_rad) * math.sin(lon_rad)
cz = (N * (1 - e2) + height) * math.sin(lat_rad)

# ==== 球パラメータ ====
radius = 1.5  # m
segments_lat = 32
segments_lon = 64

positions = []
normals = []
indices = []

for i in range(segments_lat + 1):
    theta = np.pi * i / segments_lat
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    for j in range(segments_lon + 1):
        phi = 2 * np.pi * j / segments_lon
        sin_phi = np.sin(phi)
        cos_phi = np.cos(phi)

        x = cos_phi * sin_theta
        y = cos_theta
        z = sin_phi * sin_theta

        positions.append([cx + radius * x, cy + radius * y, cz + radius * z])
        normals.append([x, y, z])

for i in range(segments_lat):
    for j in range(segments_lon):
        first = i * (segments_lon + 1) + j
        second = first + segments_lon + 1

        indices.extend([first, second, first + 1])
        indices.extend([second, second + 1, first + 1])

positions = np.array(positions, dtype=np.float32)
normals = np.array(normals, dtype=np.float32)
indices = np.array(indices, dtype=np.uint16)

# ==== バッファ作成 ====
position_bytes = positions.tobytes()
normal_bytes = normals.tobytes()
index_bytes = indices.tobytes()
buffer_data = position_bytes + normal_bytes + index_bytes

# ==== GLTF作成 ====
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
        BufferView(buffer=0, byteOffset=0, byteLength=len(position_bytes), target=34962),
        BufferView(buffer=0, byteOffset=len(position_bytes), byteLength=len(normal_bytes), target=34962),
        BufferView(buffer=0, byteOffset=len(position_bytes) + len(normal_bytes), byteLength=len(index_bytes), target=34963)
    ],
    accessors=[
        Accessor(bufferView=0, componentType=5126, count=len(positions),
                 type="VEC3",
                 min=positions.min(axis=0).tolist(),
                 max=positions.max(axis=0).tolist()),
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
