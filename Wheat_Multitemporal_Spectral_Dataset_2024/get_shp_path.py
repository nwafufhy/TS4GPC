'''
Author: nwafufhy hyf7753@gmail.com
Date: 2025-03-12 15:58:30
LastEditors: nwafufhy hyf7753@gmail.com
LastEditTime: 2025-03-12 16:00:23
Description: 
'''
import os

def get_shp_files(directory):
    if not os.path.exists(directory):
        raise FileNotFoundError(f"目录不存在: {directory}")
    shp_files = []
    # 遍历指定目录及其子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 检查文件扩展名是否为 .shp
            if file.endswith('.shp'):
                # 构建文件的完整路径
                file_path = os.path.join(root, file)
                shp_files.append(file_path)
    return shp_files

if __name__ == "__main__":
    base_path = r"D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\clip_shp\2024_plot_clip_shp"
    # 获取并打印所有图像路径
    shp_files = get_shp_files(base_path)

    # 打印所有 .shp 文件的完整路径
    for file_path in shp_files:
        print(file_path)