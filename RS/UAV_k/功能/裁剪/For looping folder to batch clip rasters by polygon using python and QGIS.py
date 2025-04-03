# 参考文献：https://gis.stackexchange.com/questions/75086/for-looping-folder-to-batch-clip-rasters-by-polygon-using-python-and-qgis

import os
import fnmatch
 
def find_rasters(path, filter_pattern):
    """
    在指定路径下查找符合过滤条件的文件。
 
    参数:
    path (str): 要搜索的目录路径。
    filter_pattern (str): 用于匹配文件名的模式（例如 '*.tif'）。
 
    返回:
    生成器，产生匹配的文件名。
    """
    for root, dirs, files in os.walk(path):
        for file in fnmatch.filter(files, filter_pattern):
            yield os.path.join(root, file)  # 返回文件的完整路径
 
def process_rasters(input_folder, output_folder, clip_shapefile, filter_pattern='*.tif'):
    """
    处理输入文件夹中的栅格文件，使用 gdalwarp 进行裁剪。
 
    参数:
    input_folder (str): 输入文件夹路径。
    output_folder (str): 输出文件夹路径。
    clip_shapefile (str): 裁剪用的矢量文件路径。
    filter_pattern (str): 文件过滤模式，默认为 '*.tif'。
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # 如果输出文件夹不存在，则创建
 
    for raster_path in find_rasters(input_folder, filter_pattern):
        raster_name = os.path.basename(raster_path)  # 获取文件名
        output_path = os.path.join(output_folder, 'clip_' + raster_name)
        cmd = f'gdalwarp -q -cutline {clip_shapefile} -crop_to_cutline {raster_path} {output_path}'
        try:
            os.system(cmd)
            print(f"Processed {raster_path} to {output_path}")
        except Exception as e:
            print(f"Error processing {raster_path}: {e}")
 
# 定义环境变量
INPUT_FOLDER = '/path/to/input/folder'
OUTPUT_FOLDER = '/path/to/output/folder'
CLIP = '/path/to/clip/shapefile.shp'
 
# 调用函数处理栅格文件
process_rasters(INPUT_FOLDER, OUTPUT_FOLDER, CLIP)