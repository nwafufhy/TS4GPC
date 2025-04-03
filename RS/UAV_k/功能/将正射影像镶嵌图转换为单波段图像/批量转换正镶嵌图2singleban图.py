import os
from tqdm import tqdm

multiband = ['Blue','Green','Panch','Red','RedEdge','NIR']

def translate_raster(path_raster, output_folder, filter_pattern='*.tif'):
    """
    处理输入文件夹中的正射影像镶嵌图，使用gdal_translate 进行转换。
 
    参数:
    path_raster: 输入文件路径。
    output_folder (str): 输出文件夹路径。
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

# 指定文件夹路径
path_folder = r"D:\work\CXZ-WN\WN_2024_origin"
 
# 目标文件名
target_filename = "正射影像镶嵌图.data.tif"

# 遍历文件夹并查找目标文件
raster_files = []
for root, dirs, files in os.walk(path_folder):
    if target_filename in files:
        raster_files.append(os.path.join(root, target_filename))

output_path_folder = r'D:\work\CXZ-WN\CXZ-WN-2024'
output_folders = []
# 使用 os.listdir() 获取 output_path_folder 下的所有项
for item in os.listdir(output_path_folder):
    # 使用 os.path.join() 构建完整路径
    full_path = os.path.join(output_path_folder, item)
    # 检查是否是文件夹
    if os.path.isdir(full_path):
        # 如果是文件夹，则添加到输出列表中
        output_folders.append(full_path)   

for i in tqdm(range(len(raster_files)),desc='正在生成singleband'):
    path_raster = raster_files[i]
    output_folder = output_folders[i]
    translate_raster(path_raster,output_folder)

