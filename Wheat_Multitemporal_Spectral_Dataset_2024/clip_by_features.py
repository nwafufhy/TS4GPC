import os
from qgis.core import (QgsApplication, QgsVectorLayer, QgsRasterLayer, 
                      QgsVectorFileWriter, QgsFeature, QgsGeometry)
from qgis.analysis import QgsNativeAlgorithms
import processing
import sys
from tqdm import tqdm
from processing.core.Processing import Processing

def clip_raster_by_features(raster_path, vector_path, output_folder,qgs=None):
    k = 0
    if qgs is None:
        # 初始化QGIS应用程序
        qgs = QgsApplication([], False)
        qgs.setPrefixPath(r"D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr", True)
        qgs.initQgis()

        # 加载处理框架
        sys.path.append(r'D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr\plugins')
        Processing.initialize()
        QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
        k = 1

    # 加载图层
    raster_layer = QgsRasterLayer(raster_path, "raster")
    vector_layer = QgsVectorLayer(vector_path, "vector", "ogr")

    # 获取文件名
    # 获取包含文件名的父目录名
    parent_dir = os.path.basename(os.path.dirname(raster_path))

    # 获取文件名（不包含扩展名）
    file_name = os.path.splitext(os.path.basename(raster_path))[0]

    # 组合成想要的字符串
    raster_name = f"{parent_dir}-{file_name}"
    
    if not raster_layer.isValid() or not vector_layer.isValid():
        print("图层加载失败")
        return
    
    # 确保输出目录存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取要素总数用于进度显示
    feature_count = vector_layer.featureCount()

    # 使用tqdm创建子进度条
    with tqdm(total=feature_count, desc=f"裁剪 {raster_name}.tif", leave=False) as pbar:
        for feature in vector_layer.getFeatures():
            # 获取要素ID
            fid = feature.id()
            try:
                # 创建临时矢量图层保存单个要素
                temp_layer_path = os.path.join(output_folder, f'temp_polygon_{fid}.shp')
                
                # 创建临时图层
                writer = QgsVectorFileWriter(temp_layer_path, 'UTF-8', 
                                        vector_layer.fields(),
                                        vector_layer.wkbType(), 
                                        vector_layer.crs(), 
                                        'ESRI Shapefile')
                
                # 写入单个要素
                writer.addFeature(feature)
                del writer
                
                fid_format = "%03d" % fid

                # 构建输出路径
                output_path = os.path.join(output_folder, f'{raster_name}-{fid_format}.tif')
                
                # 使用processing工具进行裁剪
                processing.run("gdal:cliprasterbymasklayer",
                    {
                        'INPUT': raster_layer,
                        'MASK': temp_layer_path,
                        'SOURCE_CRS': None,
                        'TARGET_CRS': None,
                        'NODATA': None,
                        'ALPHA_BAND': False,
                        'CROP_TO_CUTLINE': True,
                        'KEEP_RESOLUTION': True,
                        'SET_RESOLUTION': False,
                        'X_RESOLUTION': None,
                        'Y_RESOLUTION': None,
                        'MULTITHREADING': False,
                        'OPTIONS': '',
                        'DATA_TYPE': 0,
                        'EXTRA': '',
                        'OUTPUT': output_path
                    })
                
                # 删除临时文件
                os.remove(temp_layer_path)
                for ext in ['.dbf', '.prj', '.qpj', '.shx']:
                    temp_file = temp_layer_path.replace('.shp', ext)
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                
                # print(f"已完成要素 {fid} 的裁剪")
                
                pbar.update(1)
            except Exception as e:
                print(f"\n处理要素 {fid} 时出错: {str(e)}")
                continue
    
    if k == 1:
    # 清理QGIS应用
        qgs.exitQgis()

if __name__ == "__main__":
    # 示例用法
    raster_path = r"D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\CXZ-WN-2024\CXZ-WN-240130\Blue.tif"
    vector_path = r"D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\clip_shp\2024_plot_clip_shp\plot.shp"
    output_folder = r"D:\work\xnpanV2\personal_space\CODE\Undergraduate_Thesis_FengHaoyu_2025\Wheat_Multitemporal_Spectral_Dataset_2024\clipped_results"
    
    clip_raster_by_features(raster_path, vector_path, output_folder)