# 初始化 QGIS 资源
from qgis.core import (
    QgsRasterLayer,
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

# 加载一个TIFF文件作为栅格图层
path_to_tif = r"D:\AAA-desktop\CXZ-WN\CXZ-WN-2023\CXZ-WN-230428\dsm.tif"
rlayer = QgsRasterLayer(path_to_tif, "dsm")
if not rlayer.isValid():
    print("Layer failed to load!")
else:
    QgsProject.instance().addMapLayer(rlayer)

canvas.setExtent(rlayer.extent())
canvas.setLayers([rlayer])

exitCode = qgs.exec()
# 结束程序
qgs.exitQgis()