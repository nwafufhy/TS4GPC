import os

multiband = ['Blue','Green','Panch','Red','RedEdge','NIR']

def translate_raster(path_raster, output_folder, filter_pattern='*.tif'):
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
 
    for i,raster_name in enumerate(multiband):
        output_path = os.path.join(output_folder,raster_name + '.tif')
        cmd = f'gdal_translate -b {i+1} {path_raster} {output_path}'
        try:
            os.system(cmd)
            print(f"Processed {path_raster} to {output_path}")
        except Exception as e:
            print(f"Error processing {path_raster}: {e}")

path_raster = r"D:\work\CXZ-WN\CXZ-WN-2023\CXZ-WN-230502_clip\正射影像镶嵌图.data.tif"
output_folder = r"D:\work\CXZ-WN\CXZ-WN-2023\CXZ-WN-230502_clip_translate"

translate_raster(path_raster, output_folder)