from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsCoordinateReferenceSystem,
    QgsRasterInterface,
    Qgis,
    QgsFeedback,
    QgsProject,
    QgsField,
    QgsVariantUtils,
    QgsVectorDataProvider
)
from qgis.analysis import QgsZonalStatistics
import pandas as pd
import os
from tqdm import tqdm

QgsApplication.setPrefixPath(r'D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

def get_band(polygon_file_path,raster_file_path,band_name):

    polygon_layer = QgsVectorLayer(polygon_file_path, 'Polygons', 'ogr')
    raster_layer = QgsRasterLayer(raster_file_path, 'Raster')

    if not polygon_layer.isValid() or not raster_layer.isValid():
        raise ValueError("无法加载图层，请检查文件路径和格式。")

    # 计算多边形内的栅格平均值
    zonal_stats = QgsZonalStatistics(
        polygon_layer,
        raster_layer,
        stats=QgsZonalStatistics.Mean,
        rasterBand=1
    )
    zonal_stats.calculateStatistics(None)

    # 检索有关属性的信息
    # for field in polygon_layer.fields():
    #     print(field.name(), field.typeName())

    data = []
    features = polygon_layer.getFeatures()
    for feature in features:
        # print (feature.attributes())
        # print(f"Feature ID: {feature.id()}, Raster_mea: {feature["mean"]}" )
        data.append([feature['plot_id'],feature["mean"]])

    # # 创建DataFrame
    df = pd.DataFrame(data, columns=['id', band_name])
    # print(df.head())

    # 删除mean属性表 
    caps = polygon_layer.dataProvider().capabilities()
    # Check if a particular capability is supported:
    if caps & QgsVectorDataProvider.DeleteAttributes:
        # print('The layer supports DeleteAttributes')
        res = polygon_layer.dataProvider().deleteAttributes([3])
    return df

polygon_file_path=r'D:\work\CXZ-WN\CXZ-WN-2024\plot_clip_shp\plot.shp'
raster_file_path=
band_name
get_band(polygon_file_path,raster_file_path,band_name)