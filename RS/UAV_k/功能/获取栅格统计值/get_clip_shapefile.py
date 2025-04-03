'''
Author: nwafufhy hyf7753@gmail.com
Date: 2025-03-25 18:08:11
LastEditors: nwafufhy hyf7753@gmail.com
LastEditTime: 2025-03-25 18:08:11
Description: 
'''
import os
from 功能.获取栅格统计值.get_shp_path import get_shp_files

def get_clip_shapefile(path, clip_shapefile_folder):
    # 提取时间信息
    parts = path.split(os.sep)
    # print(parts)
    for part in parts:
        if "CXZ-WN-" in part and len(part) > 11:
            # print(part)
            time_info = part.split("-")[-1]

    list_shp_files = get_shp_files(clip_shapefile_folder)
    for shp_file in list_shp_files:
        if time_info in shp_file:
            clip_shapefile = shp_file
            break
        else:
            clip_shapefile = rf"{clip_shapefile_folder}\plot.shp"
    return clip_shapefile

if __name__ == "__main__":

    path = r'D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\CXZ-WN-2024\CXZ-WN-240230\Blue.tif'
    clip_shapefile_folder = r"D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\clip_shp\2024_plot_clip_shp"
    clip_shapefile = get_clip_shapefile(path, clip_shapefile_folder)
    print(clip_shapefile)