# 参考文献：https://gis.stackexchange.com/questions/237149/multiband-to-single-band-raster

# 使用gdal_translate新的工作流程，它位于：
# Raster > Conversion > Rearrange bands...

path_raster = r"D:\AAA-desktop\CXZ-WN\CXZ-WN-2024\CXZ-WN-240130\正射影像镶嵌图.data.tif"
path_result = r"D:\AAA-desktop\CXZ-WN\CXZ-WN-2024\CXZ-WN-240130\Blue.tif"

gdal_translate path_raster -b 1 path_result
# 要获得频段 2，请替换-b 1为-b 2等。
# 注意：您可能需要启用GdalTools插件

# 可能有用的参考文献：
# https://docs.qgis.org/3.34/en/docs/user_manual/processing_algs/gdal/rasterconversion.html
# https://gdal.org/en/latest/programs/gdal_translate.html
# 不知道如何运行