import os
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsApplication
)
from qgis.gui import(
    QgsMapCanvas
)

# 初始化
QgsApplication.setPrefixPath(r"C:\OSGeo4W\apps\qgis-ltr", True)
qgs = QgsApplication([], True)
qgs.initQgis()

# 加载矢量图层
# path_vlayer_gee = r'D:\work\CXZ-WN\2023gee\2023bundaries2gee.shp'
path_vlayer_gee = r'D:\work\CXZ-WN\2024gee\2024bundaries2gee.shp'
vlayer = QgsVectorLayer(path_vlayer_gee, "plots", "ogr")
if not vlayer.isValid():
    print("Layer failed to load!")
else:
    QgsProject.instance().addMapLayer(vlayer)

# fields()您可以通过调用对象 来检索与矢量图层关联的字段的信息
# for field in vlayer.fields():
#     print(field.name(), field.typeName())

## 迭代矢量图层
features = vlayer.getFeatures()
for feature in features:
    # retrieve every feature with its geometry and attributes
    # 检索每一个特征及其形状和属性
    # print("Feature ID: ", feature.id())
    attrs = feature.attributes()
    # print(attrs)
    geom = feature.geometry()
    x = geom.asMultiPolygon()
    # print("MultiPolygon: ", x, "Area: ", geom.area())

# 提取坐标并转换为GEE格式
gee_polygon = []
for ring in x[0]:  # 由于你只有一个环，这里直接取第一个元素
    gee_ring = []
    for point in ring:
        # 提取x和y坐标
        x = point.x()
        y = point.y()
        # 将坐标添加到环中
        gee_ring.append([x, y])
    # 将环添加到多边形中
    gee_polygon.append(gee_ring)

print(gee_polygon)