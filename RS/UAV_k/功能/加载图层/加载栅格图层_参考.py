# 参考文献：https://blog.csdn.net/mrbaolong/article/details/107708676

import os
from qgis.core import (
    QgsRasterLayer,
    QgsProject,
    QgsApplication
)
from qgis.gui import(
    QgsMapCanvas
)

## 设置环境变量：
# GDAL_DATA 和 PROJ_LIB 是指向GDAL和Proj4库数据的路径，这些库用于处理地理空间数据的投影和格式转换。
os.environ['GDAL_DATA'] = r'C:\OSGeo4W\share\gdal'
os.environ['PROJ_LIB'] = r'C:\OSGeo4W\share\proj'

## 加载qgis资源
# Supply path to qgis install location
QgsApplication.setPrefixPath(r"C:\OSGeo4W\apps\qgis-ltr", True)
# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], True)
# Load providers
qgs.initQgis()

# 创建地图画布：
# 使用QgsMapCanvas()创建一个地图画布实例，并通过canvas.show()显示它
# gui
canvas = QgsMapCanvas()
canvas.show()

## 通过QgsRasterLayer(path_to_tif, "landuse")加载一个TIFF文件作为栅格图层。如果图层未能加载，将打印错误消息。
# get the path to a tif file
# 使用QgsProject.instance().addMapLayer(rlayer)将加载的图层添加到QGIS项目中
# "landuse"：这是一个字符串，表示图层的名称
path_to_tif = "./data/landuse.tif"
rlayer = QgsRasterLayer(path_to_tif, "landuse")
if not rlayer.isValid():
    print("Layer failed to load!")
else:
    QgsProject.instance().addMapLayer(rlayer)

## 使用canvas.setExtent(rlayer.extent())设置地图画布的范围以匹配图层的范围。
# 使用canvas.setLayers([rlayer])设置画布要显示的图层。
canvas.setExtent(rlayer.extent())
canvas.setLayers([rlayer])

# 通过qgs.exec()执行QGIS应用程序。这通常用于启动应用程序的事件循环，但在无GUI模式下可能不会按预期工作。
exitCode = qgs.exec()
qgs.exitQgis()
