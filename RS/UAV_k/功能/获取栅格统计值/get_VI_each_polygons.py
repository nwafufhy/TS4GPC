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
        data.append([feature['id'],feature["mean"]])

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


# 获取地址
polygon_file_path = r'D:\work\CXZ-WN\CXZ-WN-2023\CXZ-WN-caijian\CXZ-WN-caijian.shp'  # 替换为你的SHP文件路径
raster_folder_path = r'D:\work\CXZ-WN\CXZ-WN-2023\CXZ-WN-230219'  # 替换为你的栅格文件路径
VI_name = ['NDVI','GNDVI','LCI','NDRE','OSAVI']
# 栅格文件的扩展名是.tif
raster_file_extension = '.tif'

# 初始化一个空的DataFrame来存储结果
result_df = pd.DataFrame(columns=['id'])
for band_name in tqdm(VI_name,desc='正在计算栅格在多边形中的均值'):
    raster_file_path = os.path.join(raster_folder_path, f"{band_name}{raster_file_extension}")
    df = get_band(polygon_file_path,raster_file_path,band_name)
    # 合并到结果DataFrame中（这里使用outer join来确保所有id都保留）
    result_df = pd.merge(result_df, df, on='id', how='outer')

print(result_df.head())
# 保存结果DataFrame为CSV文件
out_multiband_csv_filr_path = os.path.join(raster_folder_path, "Vegetation_index.csv")
result_df.to_csv(out_multiband_csv_filr_path, index=False)

qgs.exitQgis()