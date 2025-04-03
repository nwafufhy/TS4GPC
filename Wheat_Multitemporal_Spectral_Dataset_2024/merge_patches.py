import rasterio
import numpy as np
from pathlib import Path
from tqdm import tqdm
from get_image_paths import get_tif_files, get_list_time_band
import os
import json

def get_merge_combinations(input_dir):
    """获取所有需要合并的组合"""
    # 存储信息的字典
    dates = set()
    bands = set()
    sequences = set()
    patch_ranges = {}  # 存储每个组合的patch范围
    
    # 扫描所有文件获取信息
    for file_path in Path(input_dir).glob('*.tif'):
        parts = file_path.stem.split('_')
        name_parts = parts[0].split('-')  # ['CXZ', 'WN', '240130', 'Blue', '000']
        
        date = name_parts[2]      # '240130'
        band = name_parts[3]      # 'Blue'
        sequence = name_parts[4]  # '000'
        patch_num = int(parts[1].replace('patch', ''))  # 将'patch000'转换为0
        
        dates.add(date)
        bands.add(band)
        sequences.add(sequence)
        
        # 记录每个组合的patch范围
        key = (date, band, sequence)
        if key not in patch_ranges:
            patch_ranges[key] = set()
        patch_ranges[key].add(patch_num)
    
    # 生成合并列表
    merge_list = []
    dates = sorted(list(dates))
    # bands = sorted(list(bands))
    bands = ['Blue', 'Green', 'NIR', 'Red', 'RedEdge']
    sequences = sorted(list(sequences))
    
    # 对每个序列号和每个patch号都生成一个合并列表
    for sequence in sequences:
        sequence_list = []
        d = dates[0]
        b = bands[0]
        key = (d, b, sequence)
        if key in patch_ranges:
            # 获取该组合的所有patch编号
            patch_nums = sorted(list(patch_ranges[key]))
            # print(patch_nums)
            for patch_num in patch_nums:
                # print('patch_num:',patch_num)
                patch_list = []
                for date in dates:
                    date_list = []
                    for band in bands:
                        # 生成该组合的所有文件名
                        filenames = f"CXZ-WN-{date}-{band}-{sequence}_patch{patch_num:03d}.tif"
                        date_list.append(filenames)
                    patch_list.append(date_list)
                sequence_list.append(patch_list)
        if sequence_list:  # 只有当有完整的时间序列时才添加
            merge_list.append(sequence_list)
    
    # 打印示例
    if merge_list:
        print("\n第一个合并组合的前两个时间点示例:")
        for patch_list in merge_list[0][:2]:
            print(patch_list)
    
    return merge_list

def merge_tif(input_dir, merge_list, output_dir):
    """
    处理所有时序多光谱数据并保存拼接结果
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 计算总处理数量
    total_combinations = sum(len(plot_data) for plot_data in merge_list)

    # 创建总进度条
    with tqdm(total=total_combinations, desc="处理图像组合") as pbar:
        # 遍历所有组合
        for plot_idx, plot_data in enumerate(merge_list):
            for patch_idx, patch_data in enumerate(plot_data):
                try:
                    # 读取第一个文件获取基本信息
                    first_file = input_dir / patch_data[0][0]
                    with rasterio.open(first_file) as src:
                        height = src.height
                        width = src.width
                        profile = src.profile.copy()

                    # 创建数组存储数据 [T, B, H, W]
                    temporal_data = np.zeros((len(patch_data), len(patch_data[0]), height, width), 
                                        dtype=np.float32)

                    # 读取所有数据
                    for t, time_files in enumerate(patch_data):
                        for b, file_name in enumerate(time_files):
                            file_path = input_dir / file_name
                            with rasterio.open(file_path) as src:
                                temporal_data[t, b] = src.read(1)

                    # 对每个时间点的波段图像进行横向拼接
                    time_combined_images = []
                    for t in range(temporal_data.shape[0]):
                        # 归一化当前时间点的所有波段数据
                        time_images = temporal_data[t]
                        vmin = np.percentile(time_images, 1)
                        vmax = np.percentile(time_images, 99)
                        normalized_images = np.clip((time_images - vmin) / (vmax - vmin), 0, 1)
                        
                        # 沿着水平方向拼接
                        combined_image = np.hstack(normalized_images)
                        time_combined_images.append(combined_image)

                    # 将不同时间点的拼接图像纵向排列
                    final_image = np.vstack(time_combined_images)

                    # 更新 profile
                    profile.update(
                        width=final_image.shape[1],
                        height=final_image.shape[0],
                        count=1,
                        dtype='float32'
                    )

                    # 构建输出文件名
                    name_parts = patch_data[0][0].split('_')[0].split('-')
                    plot_id = name_parts[4]
                    patch_num = patch_data[0][0].split('_')[1].replace('.tif', '')
                    output_path = output_dir / f"CX-WN-2024_{plot_id}_{patch_num}_merged.tif"

                    # 保存文件
                    with rasterio.open(output_path, 'w', **profile) as dst:
                        dst.write(final_image[np.newaxis, :, :])

                    print(f"成功处理并保存: {output_path}")

                except Exception as e:
                    print(f"处理 plot {plot_idx}, patch {patch_idx} 时出错: {e}")
                finally:
                    pbar.update(1)


if __name__ == "__main__":
    input_dir = r"D:\work\DATA\DATA_TS4GPC\processed\clip_CXZ_WN_2024_patches_v1"
    output_dir = r"D:\work\DATA\DATA_TS4GPC\processed\clip_CXZ_WN_2024_patches_merged_v1"

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    merge_list = get_merge_combinations(input_dir)
    # 可以将合并列表保存为JSON文件以便后续使用
    output_file = "merge_combinations_v1.json"
    with open(output_file, 'w') as f:
        json.dump(merge_list, f, indent=2)
        
    merge_tif(input_dir, merge_list, output_dir)
    