"""
特征提取模块 - 负责计算植被指数和其他特征
"""

import os
import numpy as np
import pandas as pd
import rasterio
from ..config.settings import BANDS

class FeatureExtractor:
    """特征提取器"""
    
    def __init__(self):
        """初始化特征提取器"""
        pass
    
    def calculate_ndvi(self, red_path, nir_path, output_path=None):
        """
        计算NDVI (归一化植被指数)
        
        参数:
            red_path: 红波段影像路径
            nir_path: 近红外波段影像路径
            output_path: 输出路径，如果为None则只返回计算结果不保存
        """
        try:
            # 读取红波段和近红外波段
            with rasterio.open(red_path) as red_src:
                red = red_src.read(1).astype(np.float32)
                meta = red_src.meta.copy()
                
            with rasterio.open(nir_path) as nir_src:
                nir = nir_src.read(1).astype(np.float32)
                
            # 计算NDVI
            ndvi = np.zeros_like(red)
            valid_mask = (red + nir) > 0
            ndvi[valid_mask] = (nir[valid_mask] - red[valid_mask]) / (nir[valid_mask] + red[valid_mask])
            
            # 保存结果
            if output_path:
                meta.update(dtype='float32')
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with rasterio.open(output_path, 'w', **meta) as dst:
                    dst.write(ndvi.reshape(1, *ndvi.shape))
                    
            return True, ndvi
        except Exception as e:
            print(f"计算NDVI失败, 错误: {e}")
            return False, None
    
    def calculate_gndvi(self, green_path, nir_path, output_path=None):
        """
        计算GNDVI (绿色归一化植被指数)
        
        参数:
            green_path: 绿波段影像路径
            nir_path: 近红外波段影像路径
            output_path: 输出路径，如果为None则只返回计算结果不保存
        """
        try:
            # 读取绿波段和近红外波段
            with rasterio.open(green_path) as green_src:
                green = green_src.read(1).astype(np.float32)
                meta = green_src.meta.copy()
                
            with rasterio.open(nir_path) as nir_src:
                nir = nir_src.read(1).astype(np.float32)
                
            # 计算GNDVI
            gndvi = np.zeros_like(green)
            valid_mask = (green + nir) > 0
            gndvi[valid_mask] = (nir[valid_mask] - green[valid_mask]) / (nir[valid_mask] + green[valid_mask])
            
            # 保存结果
            if output_path:
                meta.update(dtype='float32')
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with rasterio.open(output_path, 'w', **meta) as dst:
                    dst.write(gndvi.reshape(1, *gndvi.shape))
                    
            return True, gndvi
        except Exception as e:
            print(f"计算GNDVI失败, 错误: {e}")
            return False, None
    
    def calculate_statistics(self, image_path):
        """
        计算影像的统计特征
        
        参数:
            image_path: 影像路径
        
        返回:
            字典，包含均值、标准差、最小值、最大值等统计量
        """
        try:
            with rasterio.open(image_path) as src:
                image = src.read(1)
                
                # 计算统计量
                stats = {
                    'mean': float(np.mean(image)),
                    'std': float(np.std(image)),
                    'min': float(np.min(image)),
                    'max': float(np.max(image)),
                    'median': float(np.median(image)),
                    'p25': float(np.percentile(image, 25)),
                    'p75': float(np.percentile(image, 75))
                }
                
                return True, stats
        except Exception as e:
            print(f"计算统计特征失败: {image_path}, 错误: {e}")
            return False, None
    
    def extract_all_features(self, image_paths, output_csv=None):
        """
        提取所有特征并保存到CSV
        
        参数:
            image_paths: 字典，包含不同波段的影像路径
            output_csv: 输出CSV路径
        """
        try:
            features = {}
            
            # 计算各波段统计特征
            for band, path in image_paths.items():
                success, stats = self.calculate_statistics(path)
                if success:
                    for stat_name, value in stats.items():
                        features[f"{band}_{stat_name}"] = value
            
            # 计算NDVI
            if 'Red' in image_paths and 'NIR' in image_paths:
                success, ndvi = self.calculate_ndvi(image_paths['Red'], image_paths['NIR'])
                if success:
                    features['NDVI_mean'] = float(np.mean(ndvi))
                    features['NDVI_std'] = float(np.std(ndvi))
            
            # 计算GNDVI
            if 'Green' in image_paths and 'NIR' in image_paths:
                success, gndvi = self.calculate_gndvi(image_paths['Green'], image_paths['NIR'])
                if success:
                    features['GNDVI_mean'] = float(np.mean(gndvi))
                    features['GNDVI_std'] = float(np.std(gndvi))
            
            # 保存到CSV
            if output_csv and features:
                df = pd.DataFrame([features])
                os.makedirs(os.path.dirname(output_csv), exist_ok=True)
                df.to_csv(output_csv, index=False)
            
            return True, features
        except Exception as e:
            print(f"提取特征失败, 错误: {e}")
            return False, None