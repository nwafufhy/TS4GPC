"""
数据加载模块 - 负责加载原始影像和GPC数据
"""

import os
import pandas as pd
import rasterio
from osgeo import gdal
import glob
from ..config.settings import *

class UAVDataLoader:
    """无人机数据加载器"""
    
    def __init__(self):
        """初始化数据加载器"""
        self.raw_data_dir = RAW_DATA_DIR
        self.gpc_data_file = GPC_DATA_FILE
        self.merged_data_file = MERGED_DATA_FILE
        
    def get_image_paths(self, year="2024"):
        """获取指定年份的所有影像路径"""
        image_paths = {}
        
        # 遍历年份目录
        year_dir = os.path.join(self.raw_data_dir, f"CXZ-WN-{year}")
        if not os.path.exists(year_dir):
            raise FileNotFoundError(f"目录不存在: {year_dir}")
            
        # 获取所有日期文件夹
        date_dirs = [d for d in os.listdir(year_dir) if os.path.isdir(os.path.join(year_dir, d))]
        
        for date_dir in date_dirs:
            date_path = os.path.join(year_dir, date_dir)
            # 查找所有TIF文件
            tif_files = glob.glob(os.path.join(date_path, "*.tif"))
            
            # 按波段组织
            date_images = {}
            for band in BANDS:
                band_files = [f for f in tif_files if band.lower() in f.lower()]
                if band_files:
                    date_images[band] = band_files[0]  # 取第一个匹配的文件
            
            # 存储该日期的所有波段
            if date_images:
                image_paths[date_dir] = date_images
                
        return image_paths
    
    def load_image(self, image_path):
        """加载单个影像"""
        try:
            with rasterio.open(image_path) as src:
                image_data = src.read(1)  # 读取第一个波段
                meta = src.meta.copy()
                return image_data, meta
        except Exception as e:
            print(f"加载影像失败: {image_path}, 错误: {e}")
            return None, None
    
    def load_gpc_data(self, year="2024"):
        """加载GPC数据"""
        try:
            # 加载合并的数据文件
            df = pd.read_csv(self.merged_data_file)
            # 筛选指定年份的数据
            year_df = df[df['year'] == int(year)]
            return year_df
        except Exception as e:
            print(f"加载GPC数据失败, 错误: {e}")
            return None