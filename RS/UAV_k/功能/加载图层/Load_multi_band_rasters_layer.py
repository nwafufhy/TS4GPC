# 参考代码：https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/raster.html

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
# canvas = QgsMapCanvas()
# canvas.show()

# 加载一个TIFF文件作为栅格图层
path_to_tif = r'D:\work\官村无人机影像\关村0718\正射影像镶嵌图.data.tif' 
rlayer = QgsRasterLayer(path_to_tif, "multi_band_rasters")
if not rlayer.isValid():
    print("Layer failed to load!")
else:
    QgsProject.instance().addMapLayer(rlayer)

## 获取层的详细信息
rlayer = QgsProject.instance().mapLayersByName('multi_band_rasters')[0]
# get the resolution of the raster in layer unit
# 获取栅格的分辨率
print(rlayer.width(), rlayer.height())
# get the extent of the layer as QgsRectangle
# 获取图层的范围
print(rlayer.extent())
# get the extent of the layer as Strings
# 以字符串的方式获取
print(rlayer.extent().toString())
# 获取栅格的类型
# get the raster type: 0 = GrayOrUndefined (single band), 1 = Palette (single band), 2 = Multiband
print(rlayer.rasterType())
# 获取栅格的总频带数
# get the total band count of the raster
print(rlayer.bandCount())
# 获取第一个波段的名字
# get the first band name of the raster
print(rlayer.bandName(1))
print(rlayer.bandName(2))
print(rlayer.bandName(3))
print(rlayer.bandName(4))
print(rlayer.bandName(5))
print(rlayer.bandName(6))
print(rlayer.bandName(7))
# 获取所有可用的元数据
# get all the available metadata as a QgsLayerMetadata object
print(rlayer.metadata())
# dir()#可以查询能对该对象使用的方法

# 查询当前渲染器：
print(rlayer.renderer())
print(rlayer.renderer().type())

# 设置渲染器
# 默认情况下，QGIS 将前三个波段映射到红色、绿色和蓝色以创建彩色图像（这是MultiBandColor绘图样式）。
# 在某些情况下，您可能需要覆盖这些设置。以下代码互换红色波段（1）和绿色波段（2）： 
# rlayer_multi = QgsProject.instance().mapLayersByName('multiband')[0]
# rlayer_multi.renderer().setGreenBand(1)
# rlayer_multi.renderer().setRedBand(2)
# 如果只需要一个波段来可视化栅格，则可以选择单波段绘图，可以是灰度级也可以是伪彩色。
# 我们必须使用triggerRepaint() 来更新地图并查看结果：
# rlayer_multi.triggerRepaint()
# rlayer.triggerRepaint()

## 查询值
# val, res = rlayer.dataProvider().sample(QgsPointXY(20.50, -34), 1)
# # 1是波段编号，括号里的数字是坐标
# # 查询栅格值的另一种方法是使用identify()返回 QgsRasterIdentifyResult对象的方法。
# ident = rlayer.dataProvider().identify(QgsPointXY(20.5, -34), QgsRaster.IdentifyFormatValue)

# if ident.isValid():
#   print(ident.results())
# Valid是有效的意思

## 编辑栅格数据


# canvas.setExtent(rlayer.extent())
# canvas.setLayers([rlayer])

# exitCode = qgs.exec()
#可以等待我查看
# 结束程序
qgs.exitQgis()