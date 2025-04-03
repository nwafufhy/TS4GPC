'''
Author: nwafufhy hyf7753@gmail.com
Date: 2025-03-11 21:59:09
LastEditors: nwafufhy hyf7753@gmail.com
LastEditTime: 2025-03-11 22:13:27
Description: 
'''
import os
from get_image_paths import get_tif_files
def clip_plot(base_path, output_folder, clip_shapefile):
    """
    处理输入文件夹中的栅格文件，使用 gdalwarp 进行裁剪。
    """
    # 获取并打印所有图像路径
    tif_files = get_tif_files(base_path)
 
    for raster_path in tif_files:
        raster_name = os.path.basename(raster_path)  # 获取文件名
        output_path = os.path.join(output_folder, 'clip_' + raster_name)
        cmd = f'gdalwarp -q -cutline {clip_shapefile} -crop_to_cutline {raster_path} {output_path}'
        try:
            os.system(cmd)
            print(f"Processed {raster_path} to {output_path}")
        except Exception as e:
            print(f"Error processing {raster_path}: {e}")
        break

if __name__ == '__main__':
    # 获取路径列表
    base_path = r"D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\CXZ-WN-2024"
    clip_shapefile = r"D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\clip_shp\2024_plot_clip_shp\plot.shp"
    output_folder = 'clip_plot'

    clip_plot(base_path, output_folder, clip_shapefile)