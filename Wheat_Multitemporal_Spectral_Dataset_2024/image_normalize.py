import cv2
import os
from pathlib import Path
import rasterio
import numpy as np

def normalize_resolution(image, target_resolution=(580, 160)):
    """
    将图像降采样到目标分辨率
    Args:
        image: 输入图像 [H, W, C]
        target_resolution: 目标分辨率 (height, width)
    Returns:
        normalized_image: 降采样后的图像
    """
    current_h, current_w = image.shape[:2]
    
    # 计算缩放比例
    scale_h = target_resolution[0] / current_h
    scale_w = target_resolution[1] / current_w
    scale = min(scale_h, scale_w)
    
    # 计算新的尺寸
    new_h = int(current_h * scale)
    new_w = int(current_w * scale)
    
    # 使用双线性插值进行降采样
    normalized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    return normalized_image

def batch_normalize_images(input_dir, output_dir, target_resolution=(580, 160)):
    """
    批量处理图像并保存
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for image_path in input_dir.rglob('*.tif'):
        try:
            # 读取tif文件
            with rasterio.open(str(image_path)) as src:
                # 获取图像信息
                count = src.count
                if count == 0:
                    print(f"跳过空图像: {image_path.name}")
                    continue
                
                # 读取图像数据
                image = src.read()
                transform = src.transform
                crs = src.crs
                
                # 处理图像维度
                if len(image.shape) > 3:
                    image = image.squeeze()
                
                # 确保图像是3D格式 [C, H, W]
                if len(image.shape) == 2:
                    image = np.expand_dims(image, axis=0)
                elif len(image.shape) == 1:
                    image = np.expand_dims(image, axis=(0, 1))
                
                # 转换为[H, W, C]格式用于resize
                image = np.moveaxis(image, 0, -1)
                
                # 打印调试信息
                print(f"处理前shape: {image.shape}")
                
                # 归一化分辨率
                normalized_image = normalize_resolution(image, target_resolution)
                
                # 打印调试信息
                print(f"归一化后shape: {normalized_image.shape}")
                
                # 转回[C, H, W]格式
                normalized_image = np.moveaxis(normalized_image, -1, 0)
                
                # 确保输出维度正确
                if len(normalized_image.shape) != 3:
                    print(f"警告: 输出维度不正确 {normalized_image.shape}")
                    continue
                
                # 构建输出路径
                output_path = output_dir / image_path.name
                
                # 更新变换矩阵
                scale_h = normalized_image.shape[1] / src.height
                scale_w = normalized_image.shape[2] / src.width
                new_transform = rasterio.Affine(
                    transform.a / scale_w, transform.b, transform.c,
                    transform.d, transform.e / scale_h, transform.f
                )
                
                # 保存归一化后的图像
                with rasterio.open(
                    str(output_path),
                    'w',
                    driver='GTiff',
                    height=normalized_image.shape[1],
                    width=normalized_image.shape[2],
                    count=normalized_image.shape[0],
                    dtype=normalized_image.dtype,
                    crs=crs,
                    transform=new_transform,
                ) as dst:
                    dst.write(normalized_image)
                
            print(f"已处理: {image_path.name}, 最终shape={normalized_image.shape}")
            
        except Exception as e:
            print(f"处理 {image_path.name} 时出错: {str(e)}")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    input_dir = r"D:\work\DATA\DATA_TS4GPC\processed\clip_CXZ_WN_2024"
    output_dir = r"D:\work\DATA\DATA_TS4GPC\processed\clip_CXZ_WN_2024_normalized"
    batch_normalize_images(input_dir, output_dir)