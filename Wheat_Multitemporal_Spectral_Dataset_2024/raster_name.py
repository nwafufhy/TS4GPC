'''
Author: nwafufhy hyf7753@gmail.com
Date: 2025-03-12 14:03:20
LastEditors: nwafufhy hyf7753@gmail.com
LastEditTime: 2025-03-12 14:03:20
Description: 
'''
import os

# 给定的文件路径
file_path = r"D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\CXZ-WN-2024\CXZ-WN-240130\Blue.tif"

# 获取包含文件名的父目录名
parent_dir = os.path.basename(os.path.dirname(file_path))

# 获取文件名（不包含扩展名）
file_name = os.path.splitext(os.path.basename(file_path))[0]

# 组合成想要的字符串
result = f"{parent_dir}-{file_name}"

print(result)