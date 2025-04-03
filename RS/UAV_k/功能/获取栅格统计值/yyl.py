# 使用reduce逐个合并DataFrame
from functools import reduce
import gc
from 功能.获取栅格统计值.get_shp_path import get_shp_files

## 计算一批新无人机的VI
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

def init_qgis():
    qgs = QgsApplication([], False)
    qgs.setPrefixPath(r'D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr', True)
    qgs.initQgis()
    return qgs

def get_band(polygon_file_path, raster_file_path, band_name):
    # 移除QGIS初始化和退出
    try:
        polygon_layer = QgsVectorLayer(polygon_file_path, 'Polygons', 'ogr')
        raster_layer = QgsRasterLayer(raster_file_path, 'Raster')

        if not polygon_layer.isValid() or not raster_layer.isValid():
            raise ValueError("无法加载图层，请检查文件路径和格式。")

        zonal_stats = QgsZonalStatistics(
            polygon_layer,
            raster_layer,
            stats=QgsZonalStatistics.Mean,
            rasterBand=1
        )
        zonal_stats.calculateStatistics(None)

        data = []
        features = polygon_layer.getFeatures()
        for feature in features:
            data.append([feature['id'], feature["mean"]])

        df = pd.DataFrame(data, columns=['id', band_name])

        # 删除mean属性表
        caps = polygon_layer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.DeleteAttributes:
            res = polygon_layer.dataProvider().deleteAttributes([3])

        # 优化数据类型
        df['id'] = df['id'].astype('int32')
        df[band_name] = df[band_name].astype('float32')

        return df
    
    finally:
        # 只清理图层，不退出QGIS
        del polygon_layer
        del raster_layer
        gc.collect()

def batch_get_band(raster_folder_path, polygon_file_path, time):
    multiband_name = ['Blue','Green','NIR','Red','RedEdge']
    raster_file_extension = '.tif'
    temp_file = os.path.join(raster_folder_path, "temp_merged.csv")
    
    # 分阶段合并
    for i, band_name in enumerate(tqdm(multiband_name, desc=f'正在处理{time}的栅格数据')):
        raster_file_path = os.path.join(raster_folder_path, f"{band_name}{raster_file_extension}")
        try:
            # 处理当前波段
            df = get_band(polygon_file_path, raster_file_path, band_name)
            print(f"{band_name}完成")
            
            # 如果是第一个波段，直接保存为临时文件
            if i == 0:
                df.to_csv(temp_file, index=False)
                del df
                gc.collect()
                continue
                
            # 分块合并数据
            chunksize = 1000  # 根据内存情况调整
            reader = pd.read_csv(temp_file, chunksize=chunksize)
            
            # 创建新的临时文件
            new_temp = temp_file + ".new"
            with pd.HDFStore(new_temp, mode='w', complevel=9, complib='blosc') as store:
                for chunk_idx, chunk in enumerate(reader):
                    merged = pd.merge(chunk, df, on='id', how='inner')
                    store.append(f'chunk{chunk_idx}', merged, index=False)
                    del merged
                    gc.collect()
                    
            # 替换旧临时文件
            os.remove(temp_file)
            os.rename(new_temp, temp_file)
            del df, reader
            gc.collect()
            
        except Exception as e:
            print(f"处理{band_name}时发生错误：{str(e)}")
            continue

    # 最终保存结果
    if os.path.exists(temp_file):
        result_df = pd.read_csv(temp_file)
        out_path = os.path.join(raster_folder_path, "multiband.csv")
        result_df.to_csv(out_path, index=False)
        os.remove(temp_file)
        del result_df
        gc.collect()

def main():
    # 在主函数开始时初始化QGIS
    qgs = QgsApplication([], False)
    qgs.setPrefixPath(r'D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr', True)
    qgs.initQgis()

    try:
        polygon_file_path = r'D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\clip_shp\2024_plot_clip_shp'
        l_time = ['0312','0401','0409','0412']
        list_shp_files = get_shp_files(polygon_file_path)

        for time in tqdm(l_time, desc='正在批量获取multiband'):
            raster_folder_path = rf'D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\CXZ-WN-2024\CXZ-WN-24{time}'
            for shp_file in list_shp_files:
                if time in shp_file:
                    clip_shapefile = shp_file
                    break
                else:
                    clip_shapefile = rf"{polygon_file_path}\plot.shp"
            print(f"使用的是 {clip_shapefile} 进行裁剪")
            batch_get_band(raster_folder_path, polygon_file_path, time)
    
    finally:
        # 在主函数结束时退出QGIS
        qgs.exitQgis()

if __name__ == "__main__":
    main()