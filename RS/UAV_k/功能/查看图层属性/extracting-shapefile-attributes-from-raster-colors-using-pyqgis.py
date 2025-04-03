# 参考文献：https://gis.stackexchange.com/questions/93629/extracting-shapefile-attributes-from-raster-colors-using-pyqgis

# 初始化 QGIS 资源
from qgis.core import *

QgsApplication.setPrefixPath('D:/QGIS/apps/qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# 加载一个shp文件作为矢量图层
path_to_vlayer = r"D:\AAA-desktop\CXZ-WN\CXZ-WN-2023\CXZ-WN-caijian\CXZ-WN-caijian.shp"
vlayer = QgsVectorLayer(path_to_vlayer, "plots", "ogr")
if not vlayer.isValid():
    print("Layer failed to load!")
else:
    QgsProject.instance().addMapLayer(vlayer)

# 加载一个TIFF文件作为栅格图层
path_to_tif = r"D:\AAA-desktop\CXZ-WN\CXZ-WN-2023\CXZ-WN-230428\dsm.tif"
rlayer = QgsRasterLayer(path_to_tif, "dsm")
if not rlayer.isValid():
    print("Layer failed to load!")
else:
    QgsProject.instance().addMapLayer(rlayer)

# number of bands (raster)
print(rlayer.bandCount())
# iterating over the layer
# for plot in vlayer.getFeatures():
#     # geometry of plot
#     geom  = plot.geometry()
#     # centroid of each plot
#     # 每个田块的质心
#     x,y = geom.centroid().asPoint()
#     # raster value 
#     # print(rlayer.dataProvider().identify(QgsPoint(x,y), QgsRaster.IdentifyFormatValue).results())
#     # print(x,y)
print(summary(vlayer))

# 结束程序
qgs.exitQgis()