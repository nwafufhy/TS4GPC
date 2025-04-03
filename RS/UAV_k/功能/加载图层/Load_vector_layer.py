# 初始化 QGIS 资源
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsApplication
)
from qgis.gui import(
    QgsMapCanvas
)

QgsApplication.setPrefixPath('D:/QGIS/apps/qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# 脚本正文
# 使用QgsMapCanvas()创建一个地图画布实例，并通过canvas.show()显示它
canvas = QgsMapCanvas()
canvas.show()

# 加载一个shp文件作为矢量图层
path_to_vlayer = r"D:\work\DATA\CXZ-WN\clip_shp\2023_CXZ-WN-caijian\CXZ-WN-caijian.shp"
vlayer = QgsVectorLayer(path_to_vlayer, "plots", "ogr")
if not vlayer.isValid():
    print("无法加载矢量图层!")
else:
    QgsProject.instance().addMapLayer(vlayer)

canvas.setExtent(vlayer.extent())
canvas.setLayers([vlayer])
exitCode = qgs.exec()

# 结束程序
qgs.exitQgis()