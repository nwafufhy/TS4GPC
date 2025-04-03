# 参考文献：https://blog.csdn.net/mrbaolong/article/details/107708632

import os
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsApplication
)
from qgis.gui import(
    QgsMapCanvas
)
os.environ['GDAL_DATA'] = r'C:\OSGeo4W\share\gdal'
os.environ['PROJ_LIB'] = r'C:\OSGeo4W\share\proj'
# Supply path to qgis install location
QgsApplication.setPrefixPath(r"C:\OSGeo4W\apps\qgis-ltr", True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], True)

# Load providers
qgs.initQgis()
# gui
canvas = QgsMapCanvas()
canvas.show()
# get the path to the shapefile 
path_to_airports_layer = r"D:\AAA-desktop\CXZ-WN\CXZ-WN-2023\CXZ-WN-caijian\CXZ-WN-caijian.shp"

# The format is:
# vlayer = QgsVectorLayer(data_source, layer_name, provider_name)
# provider_name数据源标识符是一个字符串，它特定于每个矢量数据提供者。
# GDAL 库（Shapefile 和许多其他文件格式）用ogr
# 其他标识符见：https://docs.qgis.org/3.34/en/docs/pyqgis_developer_cookbook/loadlayer.html

vlayer = QgsVectorLayer(path_to_airports_layer, "plots", "ogr")
if not vlayer.isValid():
    print("Layer failed to load!")
else:
    QgsProject.instance().addMapLayer(vlayer)

canvas.setExtent(vlayer.extent())
canvas.setLayers([vlayer])
exitCode = qgs.exec()
qgs.exitQgis()
