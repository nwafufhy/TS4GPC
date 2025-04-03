# 初始化 QGIS 资源
from qgis.core import *
from qgis.gui import(
    QgsMapCanvas
)
import numpy as np

QgsApplication.setPrefixPath('D:/QGIS/apps/qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# 加载一个TIFF文件作为栅格图层
path_to_tif = r"D:\AAA-desktop\CXZ-WN\CXZ-WN-2024\CXZ-WN-240130\正射影像镶嵌图.data.tif"
rlayer = QgsRasterLayer(path_to_tif, "multi_band_rasters")
if not rlayer.isValid():
    print("Layer failed to load!")
else:
    QgsProject.instance().addMapLayer(rlayer)

# 获取栅格的类型
# get the raster type: 0 = GrayOrUndefined (single band), 1 = Palette (single band), 2 = Multiband
if rlayer.rasterType() == 2:
    print('raster type = Multiband')   
# 获取栅格的总频带数
# get the total band count of the raster
num_bands = rlayer.bandCount()
print('栅格的总频带数为：',num_bands)
# 获取所有波段的名字
for num in range(1,num_bands+1):
    print(rlayer.bandName(num))   

path_raster = r"D:\AAA-desktop\CXZ-WN\CXZ-WN-2024\CXZ-WN-240130\正射影像镶嵌图.data.tif"
path_result = r"D:\AAA-desktop\CXZ-WN\CXZ-WN-2024\CXZ-WN-240130\Blue.tif"
gdal_translate -b 1 path_raster path_result

# 结束程序
qgs.exitQgis()