# 根据1111科研日志的2023各日期的裁剪情况统计发现：0502只有multibandraster
# 需要提取singlebandraster
# 整理数据，数据命名格式如下：

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
import calculate_vegetation_indices

QgsApplication.setPrefixPath(r'D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

def get_band(polygon_file_path,raster_file_path):

    multiband_name = ['Blue','Green','Red','RedEdge','NIR']
    result_df = pd.DataFrame(columns=['id'])

    print(polygon_file_path)
    print(raster_file_path)

    polygon_layer = QgsVectorLayer(polygon_file_path, 'Polygons', 'ogr')
    raster_layer = QgsRasterLayer(raster_file_path, 'Raster')

    if not polygon_layer.isValid() or not raster_layer.isValid():
        raise ValueError("无法加载图层，请检查文件路径和格式。")
    
    # 删除mean属性表 
    caps = polygon_layer.dataProvider().capabilities()
    # Check if a particular capability is supported:
    if caps & QgsVectorDataProvider.DeleteAttributes:
        # print('The layer supports DeleteAttributes')
        res = polygon_layer.dataProvider().deleteAttributes([3,4,5,6,7,8])#管它有啥先删掉再说

    for i , index in enumerate([1,2,4,5,6]):
    # 计算多边形内的栅格平均值
        zonal_stats = QgsZonalStatistics(
            polygon_layer,
            raster_layer,
            stats=QgsZonalStatistics.Mean,
            rasterBand=index
        )
        zonal_stats.calculateStatistics(None)

        band_name = multiband_name[i]

        # 检索有关属性的信息
        for field in polygon_layer.fields():
            print(field.name(), field.typeName())

        data = []
        features = polygon_layer.getFeatures()
        for feature in features:
            # print (feature.attributes())
            # print(f"Feature ID: {feature.id()}, Raster_mea: {feature["mean"]}" )
            data.append([feature.id(),feature["mean"]])

        # # 创建DataFrame
        df = pd.DataFrame(data, columns=['id',band_name])
        result_df = pd.merge(result_df, df, on='id', how='outer')

        # 删除mean属性表 
        caps = polygon_layer.dataProvider().capabilities()
        # Check if a particular capability is supported:
        if caps & QgsVectorDataProvider.DeleteAttributes:
            # print('The layer supports DeleteAttributes')
            res = polygon_layer.dataProvider().deleteAttributes([3])
    
    result_df.to_csv(r'D:\work\官村无人机影像\关村0718\multibands.csv', index=False)
    df = pd.read_csv(r'D:\work\官村无人机影像\关村0718\multibands.csv')
    B,G,R,RE,NIR = df.iloc[:,1],df.iloc[:,2],df.iloc[:,3],df.iloc[:,4],df.iloc[:,5]
    dir_vi = calculate_vegetation_indices.calculate_vegetation_indices(R, G, B, RE, NIR)
    df_vi = pd.DataFrame(dir_vi)
    df_vi.to_csv(r'D:\work\官村无人机影像\关村0718\VI.csv', index=False)


# 获取地址
polygon_file_path = r'D:\work\官村无人机影像\关村0718\0718划材料.shp'  # 替换为你的SHP文件路径
raster_folder_path = r'D:\work\官村无人机影像\关村0718\正射影像镶嵌图.data.tif' 
time = 'try'

get_band(polygon_file_path,raster_folder_path)

qgs.exitQgis()