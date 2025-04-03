import os
from tqdm import tqdm

# 指定文件夹路径
path_folder = r"D:\work\CXZ-WN\WN_2024_origin"
 
# 目标文件名
target_filename = "正射影像镶嵌图.data.tif"
 
# 遍历文件夹并查找目标文件
raster_files = []
raster_folder = []
for root, dirs, files in os.walk(path_folder):
    if target_filename in files:
        raster_files.append(os.path.join(root, target_filename))
        raster_folder.append(root)

# 打印找到的文件的完整路径
# for file_path in raster_folder:
#     print(file_path)

# 使用 os.path.dirname 获取去掉文件名后的目录路径
# 但因为 root 本身就是目录路径，所以直接记录 root 即可
# 如果想要确保是文件所在的直接父目录（不考虑子目录中的同名文件），则不需要额外操作
# 因为 os.walk 已经是在逐级遍历，root 就是当前文件所在的目录

# output_path = os.path.join(path_folder,'single.tif')

def cmd_gdal_translate_single(path_raster,output_path):
    cmd = f'gdal_translate -b 1 {path_raster} {output_path}'
    try:
        os.system(cmd)
        print(f"Processed {path_raster} to {output_path}")
    except Exception as e:
        print(f"Error processing {path_raster}: {e}")

for i in tqdm(range(len(raster_files)),desc='正在生成每个时间点的singleband图用于查看'):
    path_raster = raster_files[i]
    output_folder = raster_folder[i]
    output_raster = os.path.join(output_folder,'single.tif')
    cmd_gdal_translate_single(path_raster,output_raster)