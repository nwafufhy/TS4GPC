"""
数据集构建模块 - 负责构建训练数据集
"""

import os
import pandas as pd
import numpy as np
import glob
import json
from ..config.settings import *

class DatasetBuilder:
    """数据集构建器"""
    
    def __init__(self):
        """初始化数据集构建器"""
        self.patches_dir = PATCHES_DIR
        self.merged_patches_dir = MERGED_PATCHES_DIR
        self.gpc_data_file = GPC_DATA_FILE
        
    def merge_temporal_patches(self, plot_id, patch_id, dates, bands, output_dir):
        """
        合并不同时间点的小块图
        
        参数:
            plot_id: 小区ID
            patch_id: 小块ID
            dates: 日期列表
            bands: 波段列表
            output_dir: 输出目录
        """
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 构建输出文件名
            output_path = os.path.join(output_dir, f"CX-WN-2024_{plot_id:03d}_patch{patch_id:03d}_merged.tif")
            
            # 收集所有时间点的所有波段图像路径
            image_paths = []
            for date in dates:
                date_bands = []
                for band in bands:
                    # 构建文件路径模式
                    pattern = os.path.join(
                        self.patches_dir, 
                        f"CXZ-WN-{date}-{band}-{plot_id:03d}_patch{patch_id:03d}.tif"
                    )
                    
                    # 查找匹配的文件
                    matching_files = glob.glob(pattern)
                    if matching_files:
                        date_bands.append(matching_files[0])
                    else:
                        print(f"警告: 未找到匹配的文件: {pattern}")
                        return False, None
                
                # 添加该日期的所有波段
                image_paths.extend(date_bands)
            
            # 读取并合并所有图像
            import rasterio
            from rasterio.merge import merge
            
            # 打开第一个图像获取元数据
            with rasterio.open(image_paths[0]) as src:
                meta = src.meta.copy()
                
                # 更新元数据以支持多波段
                meta.update(count=len(image_paths))
                
                # 创建输出文件
                with rasterio.open(output_path, 'w', **meta) as dst:
                    for i, path in enumerate(image_paths, 1):
                        with rasterio.open(path) as src:
                            dst.write(src.read(1), i)
            
            return True, output_path
        except Exception as e:
            print(f"合并时间序列小块图失败, 小区ID: {plot_id}, 小块ID: {patch_id}, 错误: {e}")
            return False, None
    
    def create_dataset_index(self, output_file, split_ratio=0.8):
        """
        创建数据集索引文件
        
        参数:
            output_file: 输出文件路径
            split_ratio: 训练集比例
        """
        try:
            # 加载GPC数据
            gpc_df = pd.read_csv(self.gpc_data_file)
            
            # 查找所有合并后的小块图
            merged_files = glob.glob(os.path.join(self.merged_patches_dir, "*.tif"))
            
            # 解析文件名获取小区ID
            dataset = []
            for file_path in merged_files:
                filename = os.path.basename(file_path)
                # 从文件名中提取小区ID
                parts = filename.split('_')
                if len(parts) >= 2:
                    try:
                        plot_id = int(parts[1])
                        
                        # 查找对应的GPC值
                        gpc_value = None
                        if plot_id in gpc_df['plot_id'].values:
                            gpc_value = float(gpc_df[gpc_df['plot_id'] == plot_id]['gpc'].values[0])
                        
                        if gpc_value is not None:
                            dataset.append({
                                'image_path': file_path,
                                'plot_id': plot_id,
                                'gpc': gpc_value
                            })
                    except:
                        continue
            
            # 随机打乱数据集
            np.random.shuffle(dataset)