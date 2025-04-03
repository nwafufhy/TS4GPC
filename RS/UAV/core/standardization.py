"""
数据标准化模块 - 负责影像的分辨率和辐射标准化
"""

import os
import numpy as np
from osgeo import gdal
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from ..config.settings import TARGET_RESOLUTION

class ImageStandardizer:
    """影像标准化处理器"""
    
    def __init__(self):
        """初始化标准化处理器"""
        self.target_resolution = TARGET_RESOLUTION
        
    def standardize_resolution(self, input_path, output_path, resolution=None):
        """
        将影像重采样到标准分辨率
        
        参数:
            input_path: 输入影像路径
            output_path: 输出影像路径
            resolution: 目标分辨率，如果为None则使用默认值
        """
        if resolution is None:
            resolution = self.target_resolution
            
        try:
            # 打开源数据集
            with rasterio.open(input_path) as src:
                # 计算目标仿射变换和尺寸
                dst_transform, dst_width, dst_height = calculate_default_transform(
                    src.crs, src.crs, src.width, src.height, 
                    *src.bounds, resolution=(resolution, resolution)
                )
                
                # 更新元数据
                dst_kwargs = src.meta.copy()
                dst_kwargs.update({
                    'crs': src.crs,
                    'transform': dst_transform,
                    'width': dst_width,
                    'height': dst_height
                })
                
                # 创建目标文件
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with rasterio.open(output_path, 'w', **dst_kwargs) as dst:
                    # 对每个波段进行重投影和重采样
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=dst_transform,
                            dst_crs=src.crs,
                            resampling=Resampling.bilinear
                        )
                        
            return True, output_path
        except Exception as e:
            print(f"标准化分辨率失败: {input_path}, 错误: {e}")
            return False, None
    
    def normalize_radiometry(self, input_path, output_path=None):
        """
        辐射归一化处理
        
        参数:
            input_path: 输入影像路径
            output_path: 输出影像路径，如果为None则覆盖原文件
        """
        if output_path is None:
            output_path = input_path
            
        try:
            # 打开影像
            with rasterio.open(input_path) as src:
                image = src.read(1)
                
                # 计算2%和98%分位数
                p2, p98 = np.percentile(image[image > 0], (2, 98))
                
                # 线性拉伸到0-1范围
                image_normalized = np.clip((image - p2) / (p98 - p2), 0, 1)
                
                # 保存结果
                meta = src.meta.copy()
                meta.update(dtype='float32')
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with rasterio.open(output_path, 'w', **meta) as dst:
                    dst.write(image_normalized.astype(np.float32), 1)
                    
            return True, output_path
        except Exception as e:
            print(f"辐射归一化失败: {input_path}, 错误: {e}")
            return False, None