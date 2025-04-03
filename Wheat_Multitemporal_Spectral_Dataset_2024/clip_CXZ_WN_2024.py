'''
Author: nwafufhy hyf7753@gmail.com
Date: 2025-03-12 13:38:05
LastEditors: nwafufhy hyf7753@gmail.com
LastEditTime: 2025-03-12 16:20:29
Description: 使用矢量图层裁剪单波段试验田大图成单小区栅格图层
'''
from get_image_paths import get_tif_files
import os
from clip_by_features import clip_raster_by_features
from tqdm import tqdm
from qgis.core import (QgsApplication, QgsVectorLayer, QgsRasterLayer, 
                      QgsVectorFileWriter, QgsFeature, QgsGeometry)
from qgis.analysis import QgsNativeAlgorithms
import processing
import sys
from processing.core.Processing import Processing
from get_shp_path import get_shp_files
from get_clip_shapefile import get_clip_shapefile

def clip_CXZ_WN_2024(base_path, output_folder, clip_shapefile_folder):
    # 创建输出目录
    os.makedirs(output_folder, exist_ok=True)
    
    # 获取所有图像路径
    tif_files = get_tif_files(base_path)
    print(print(f"总共要裁剪{len(tif_files)}张图片"))

    # 初始化QGIS应用程序
    qgs = QgsApplication([], False)
    qgs.setPrefixPath(r"D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr", True)
    qgs.initQgis()

    # 加载处理框架
    sys.path.append(r'D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr\plugins')
    Processing.initialize()
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    
    # 添加进度条
    with tqdm(total=len(tif_files), desc="正在裁剪图像") as pbar:
        for raster_path in tif_files:
            clip_shapefile = get_clip_shapefile(raster_path, clip_shapefile_folder)
            print(f"使用的是 {clip_shapefile} 进行裁剪")
            try:
                clip_raster_by_features(raster_path, clip_shapefile, output_folder,qgs)
                pbar.update(1)
            except Exception as e:
                print(f"\n处理 {raster_path} 时出错: {str(e)}")
                continue
    
    print("\n所有图像裁剪完成！")
    
    qgs.exitQgis()

if __name__ == '__main__':
    # 获取路径列表
    base_path = r"D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\CXZ-WN-2024"
    clip_shapefile_folder = r"D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\clip_shp\2024_plot_clip_shp"
    output_folder = r'D:\work\DATA\DATA_TS4GPC\processed\clip_CXZ_WN_2024'

    clip_CXZ_WN_2024(base_path, output_folder, clip_shapefile_folder)
