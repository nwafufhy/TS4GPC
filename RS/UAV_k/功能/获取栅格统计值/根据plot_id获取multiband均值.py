# 运行该程序时要使用D:\software\tool_gis\QGIS 3.34.12\bin\python-qgis-ltr.bat该解释器

## QGIS初始化
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
    """
    获取单个小区的栅格平均值
    输入：
    小区矢量图层的地址
    试验区栅格图层的地址
    要获取的通道的名称
    """
    # 加载图层
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

    # 构建df
    data = []
    features = polygon_layer.getFeatures()
    for feature in features:
        data.append([feature['id'],feature["mean"]])
    df = pd.DataFrame(data, columns=['id', band_name])

    # 删除mean属性表 
    caps = polygon_layer.dataProvider().capabilities()
    if caps & QgsVectorDataProvider.DeleteAttributes:
        polygon_layer.dataProvider().deleteAttributes([3])

    return df

def batch_get_band(raster_folder_path):
    """
    批量获取多光谱所有通道的值
    """
    multiband_name = ['Blue','Green','NIR','Red','RedEdge']
    # 栅格文件的扩展名是.tif
    raster_file_extension = '.tif'
    # 初始化一个空的DataFrame来存储结果
    result_df = pd.DataFrame(columns=['id'])
    for band_name in multiband_name:
        raster_file_path = os.path.join(raster_folder_path, f"{band_name}{raster_file_extension}")
        print(f'正在计算{raster_file_path}的各小区栅格平均值')
        df = get_band(polygon_file_path,raster_file_path,band_name)
        # 合并到结果DataFrame中（这里使用outer join来确保所有id都保留）
        result_df = pd.merge(result_df, df, on='id', how='outer')

    # 保存结果DataFrame为CSV文件
    out_multiband_csv_filr_path = os.path.join(raster_folder_path, "multiband.csv")
    result_df.to_csv(out_multiband_csv_filr_path, index=False)

# 获取地址
polygon_file_path = r'D:\work\CXZ-WN\clip_shp\2023_CXZ-WN-caijian\CXZ-WN-caijian.shp'  # 替换为你的SHP文件路径
output_path_folder = r'D:\work\CXZ-WN\CXZ-WN-2023'
print(f'正在批量获取{output_path_folder}内所有日期下的各小区的栅格平均值，使用的小区矢量图层是{polygon_file_path}')
output_folders = []
# 使用 os.listdir() 获取 output_path_folder 下的所有项
for item in os.listdir(output_path_folder):
    # 使用 os.path.join() 构建完整路径
    full_path = os.path.join(output_path_folder, item)
    # 检查是否是文件夹
    if os.path.isdir(full_path):
        # 如果是文件夹，则添加到输出列表中
        output_folders.append(full_path) 

for raster_folder_path in tqdm(output_folders,desc='总进度条'): 
    batch_get_band(raster_folder_path)

qgs.exitQgis()