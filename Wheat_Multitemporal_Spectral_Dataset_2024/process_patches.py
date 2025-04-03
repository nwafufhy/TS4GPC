## 这是v1版本

import cv2
import numpy as np
import rasterio
from pathlib import Path
import os
from tqdm import tqdm

# 保存生成的patches为tif文件
def save_patches_as_tif(patches, image_path,output_dir):
    base_name = Path(image_path).stem
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, patch in enumerate(patches):
        # 构建文件名
        filename = output_dir / f"{base_name}_patch{i:03d}.tif"
        # 定义文件的元数据
        profile = {
            'driver': 'GTiff',
            'height': patch.shape[0],
            'width': patch.shape[1],
            'count': 1,  # 单波段图像
            'dtype': patch.dtype,
            'crs': None,  # 若有地理参考信息，这里替换为相应的CRS
            'transform': rasterio.Affine(1, 0, 0, 0, -1, 0)  # 简单的仿射变换，可根据实际情况修改
        }
        # 保存patch为tif文件
        with rasterio.open(filename, 'w', **profile) as dst:
            dst.write(patch, 1)

def read_image(image_path):
    with rasterio.open(image_path) as src:
        # 读取图像数据
        image = src.read()
        
        # 获取nodata值
        nodata = src.nodata
        
        # 创建掩码，排除nodata值（通常是-1000）
        mask = image != nodata if nodata is not None else image != -1000

        # 使用掩码获取有效值的范围
        valid_data = image[mask]
        min_val = valid_data.min()
        max_val = valid_data.max()

        # 转换为显示格式
        display = np.moveaxis(image, 0, -1).squeeze()

        # 将nodata值替换为有效数据的最小值
        display[~mask.squeeze()] = min_val

        # 归一化到0-1范围
        display = (display - min_val) / (max_val - min_val)
        return display
    
def normalize_resolution(image, target_resolution=(580, 160)):
    """
    将图像降采样到目标分辨率
    Args:
        image: 输入图像 [H, W, C]
        target_resolution: 目标分辨率 (height, width)
    Returns:
        normalized_image: 降采样后的图像
    """
    # 直接使用目标尺寸，不保持宽高比
    normalized_image = cv2.resize(image, (target_resolution[1], target_resolution[0]), 
                                interpolation=cv2.INTER_LINEAR)
    return normalized_image

def crop_to_patches(image, patch_size=(64, 64), overlap=0.2, valid_threshold=0.95):
    """
    将图像裁剪成小块，沿着图像中线采样
    """
    h, w = image.shape[:2]
    stride_h = int(patch_size[0] * (1 - overlap))
    
    patches = []
    positions = []
    
    # 计算非零区域的掩码
    mask = ~(image == 0)
    
    # 找出每一行的有效区域范围
    midline_points = []
    
    # 先计算出图像的中线位置
    for y in range(0, h - patch_size[0] + 1, stride_h):
        # 获取当前行的掩码
        row_mask = mask[y:y+1, :].squeeze()
        if np.sum(row_mask) > 0:  # 确保该行有有效像素
            # 找出该行的有效区域起始和结束位置
            valid_indices = np.where(row_mask)[0]
            start_x, end_x = valid_indices[0], valid_indices[-1]
            
            # 计算中点位置
            mid_x = (start_x + end_x) // 2
            
            # 确保patch完全在图像内
            mid_x = max(patch_size[1] // 2, min(mid_x, w - patch_size[1] // 2))
            
            midline_points.append((y, mid_x - patch_size[1] // 2))
    
    # 沿着中线采样patches
    for y, x in midline_points:
        patch = image[y:y + patch_size[0], x:x + patch_size[1]]
        patch_mask = mask[y:y + patch_size[0], x:x + patch_size[1]]
        
        # 计算有效像素比例
        valid_ratio = np.sum(patch_mask) / (patch_size[0] * patch_size[1])
        
        # 检查是否符合要求
        if valid_ratio >= valid_threshold:
            patch_std = np.std(patch)
            if patch_std > 0.03:
                patches.append(patch)
                positions.append((y, x))
    
    return patches, positions

if __name__ == "__main__":
    input_dir = Path(r"D:\work\DATA\DATA_TS4GPC\processed\clip_CXZ_WN_2024")
    output_dir = Path(r"D:\work\DATA\DATA_TS4GPC\processed\clip_CXZ_WN_2024_patches_v1")
    output_dir.mkdir(parents=True, exist_ok=True)
    target_resolution=(580, 160)
    patch_size=(64, 64)

    # 获取文件总数
    total_files = len(list(input_dir.glob('*.tif')))
    print(f"总共发现 {total_files} 个图像待处理")

    for file_path in tqdm(input_dir.glob('*.tif'), total=total_files, desc="处理图像"):
        try:
            # 在这里处理每个文件路径
            display = read_image(file_path)
            normalized = normalize_resolution(display, target_resolution)
            # 对标准化后的图像进行裁剪
            patches, positions = crop_to_patches(normalized, patch_size, overlap=0.2, valid_threshold=0.95)
            # 保存patches为tif文件
            save_patches_as_tif(patches, file_path,output_dir)
            tqdm.write(f"成功处理 {file_path.name}，生成 {len(patches)} 个patches")
        except Exception as e:
            tqdm.write(f"处理 {file_path.name} 时发生错误: {e}")