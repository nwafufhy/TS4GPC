# 参考文献：https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/vector.html

# 初始化 QGIS 资源
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsApplication,
    QgsWkbTypes
)
from qgis.gui import(
    QgsMapCanvas
)

QgsApplication.setPrefixPath('D:/QGIS/apps/qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# 脚本正文
# 使用QgsMapCanvas()创建一个地图画布实例，并通过canvas.show()显示它
# canvas = QgsMapCanvas()
# canvas.show()

# 加载一个shp文件作为矢量图层
path_to_airports_layer = r"D:\AAA-desktop\CXZ-WN\CXZ-WN-2023\CXZ-WN-caijian\CXZ-WN-caijian.shp"
vlayer = QgsVectorLayer(path_to_airports_layer, "plots", "ogr")
if not vlayer.isValid():
    print("Layer failed to load!")
else:
    QgsProject.instance().addMapLayer(vlayer)

# fields()您可以通过调用对象 来检索与矢量图层关联的字段的信息
for field in vlayer.fields():
    print(field.name(), field.typeName())

## 迭代矢量图层
features = vlayer.getFeatures()
for feature in features:
    # retrieve every feature with its geometry and attributes
    # 检索每一个特征及其形状和属性
    print("Feature ID: ", feature.id())
    # fetch geometry
    # 获取几何
    # show some information about the feature geometry
    geom = feature.geometry()
    geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
    if geom.type() == QgsWkbTypes.PointGeometry:
        # the geometry type can be of single or multi type
        # 几何类型可以是单一的或者多类型的
        if geomSingleType:
            x = geom.asPoint()
            print("Point: ", x)
        else:
            x = geom.asMultiPoint()
            print("MultiPoint: ", x)
    elif geom.type() == QgsWkbTypes.LineGeometry:
        if geomSingleType:
            x = geom.asPolyline()
            print("Line: ", x, "length: ", geom.length())
        else:
            x = geom.asMultiPolyline()
            print("MultiLine: ", x, "length: ", geom.length())
    elif geom.type() == QgsWkbTypes.PolygonGeometry:
        if geomSingleType:
            x = geom.asPolygon()
            print("Polygon: ", x, "Area: ", geom.area())
        else:
            x = geom.asMultiPolygon()
            print("MultiPolygon: ", x, "Area: ", geom.area())
    else:
        print("Unknown or invalid geometry")
    # fetch attributes
    # 获取属性
    attrs = feature.attributes()
    # attrs is a list. It contains all the attribute values of this feature
    print(attrs)
    # for this test only print the first feature
    break

## 选择特征
# 选择所有特征，selectAll()
# 使用表达式选择，请使用下列selectByExpression()
# 更改选择颜色，您可以使用setSelectionColor()
# 将要素添加到给定层的选定要素列表
# layer.removeSelection()

## 访问属性
# 通过名称来引用属性
# print(feature['name'])

# canvas.setExtent(vlayer.extent())
# canvas.setLayers([vlayer])
# exitCode = qgs.exec()

# 结束程序
qgs.exitQgis()
