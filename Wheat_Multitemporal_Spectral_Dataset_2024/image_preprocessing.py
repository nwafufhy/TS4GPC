import cv2
import numpy as np
from pathlib import Path
import rasterio

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

def preprocess_image(image_path, patch_size=(128, 128), overlap=0.2):
    """
    预处理图像：移除空白区域并分割成小块
    """
    with rasterio.open(image_path) as src:
        image = src.read()
        nodata = src.nodata
        transform = src.transform
        crs = src.crs
        
        # 转换为[H, W, C]格式
        image = np.moveaxis(image, 0, -1)
        
        # 如果有nodata值，将其转换为0
        if nodata is not None:
            image[image == nodata] = 0
        
        # 获取patches
        patches, positions = crop_to_patches(image, patch_size, overlap)
        
        # 如果没有找到有效的patches，尝试调整patch大小
        if not patches and patch_size[0] > 32:
            smaller_size = (patch_size[0]//2, patch_size[1]//2)
            print(f"未找到有效patch，尝试更小的尺寸: {smaller_size}")
            patches, positions = crop_to_patches(image, smaller_size, overlap)
        
        return patches, positions, transform, crs

def batch_preprocess_images(input_dir, output_dir, patch_size=(128, 128), overlap=0.2):
    """
    批量处理图像
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for image_path in input_dir.rglob('*.tif'):
        try:
            # 处理图像
            patches, positions, transform, crs = preprocess_image(
                str(image_path), patch_size, overlap
            )
            
            # 为每个patch创建文件名
            base_name = image_path.stem
            
            # 保存patches
            for idx, (patch, pos) in enumerate(zip(patches, positions)):
                output_name = f"{base_name}_patch{idx:03d}_y{pos[0]}_x{pos[1]}.tif"
                output_path = output_dir / output_name
                
                # 计算patch的地理变换矩阵
                patch_transform = rasterio.Affine(
                    transform.a, transform.b, transform.c + pos[1] * transform.a,
                    transform.d, transform.e, transform.f + pos[0] * transform.e
                )
                
                # 保存patch
                with rasterio.open(
                    str(output_path),
                    'w',
                    driver='GTiff',
                    height=patch_size[0],
                    width=patch_size[1],
                    count=patch.shape[2],
                    dtype=patch.dtype,
                    crs=crs,
                    transform=patch_transform,
                ) as dst:
                    for i in range(patch.shape[2]):
                        dst.write(patch[:, :, i], i + 1)
            
            print(f"已处理: {image_path.name}, 生成 {len(patches)} 个patches")
            
        except Exception as e:
            print(f"处理 {image_path.name} 时出错: {str(e)}")

if __name__ == "__main__":
    input_dir = r"D:\work\DATA\DATA_TS4GPC\processed\clip_CXZ_WN_2024"
    output_dir = r"D:\work\DATA\DATA_TS4GPC\processed\clip_CXZ_WN_2024_patches_v1"
    batch_preprocess_images(input_dir, output_dir, patch_size=(64, 64), overlap=0.2)