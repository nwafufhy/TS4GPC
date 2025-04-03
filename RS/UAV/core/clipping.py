"""
图像裁剪模块 - 负责小区裁剪和小块图生成
"""

import os
import numpy as np
import rasterio
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import box
from ..config.settings import PLOT_SHAPEFILE, PATCH_SIZE, PATCH_OVERLAP

class ImageClipper:
    """影像裁剪处理器"""
    
    def __init__(self):
        """初始化裁剪处理器"""
        self.plot_shapefile = PLOT_SHAPEFILE
        self.patch_size = PATCH_SIZE
        self.patch_overlap = PATCH_OVERLAP
        
    def load_plot_shapes(self):
        """加载小区矢量数据"""
        try:
            gdf = gpd.read_file(self.plot_shapefile)
            return gdf
        except Exception as e:
            print(f"加载小区矢量数据失败, 错误: {e}")
            return None
    
    def clip_by_plot(self, image_path, output_dir, plot_id, plot_geometry):
        """
        按小区裁剪影像
        
        参数:
            image_path: 输入影像路径
            output_dir: 输出目录
            plot_id: 小区ID
            plot_geometry: 小区几何形状
        """
        try:
            # 提取文件名信息
            filename = os.path.basename(image_path)
            base_name = os.path.splitext(filename)[0]
            
            # 构建输出路径
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{base_name}-{plot_id:03d}.tif")
            
            # 打开影像
            with rasterio.open(image_path) as src:
                # 检查几何形状的坐标系是否与影像一致
                if plot_geometry.crs != src.crs:
                    plot_geometry = plot_geometry.to_crs(src.crs)
                
                # 执行裁剪
                out_image, out_transform = mask(src, [plot_geometry], crop=True)
                
                # 更新元数据
                out_meta = src.meta.copy()
                out_meta.update({
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform
                })
                
                # 保存裁剪结果
                with rasterio.open(output_path, "w", **out_meta) as dest:
                    dest.write(out_image)
                    
            return True, output_path
        except Exception as e:
            print(f"小区裁剪失败: {image_path}, 小区ID: {plot_id}, 错误: {e}")
            return False, None
    
    def generate_patches(self, image_path, output_dir, plot_id, patch_size=None, overlap=None):
        """
        将小区影像切分为小块图
        
        参数:
            image_path: 输入影像路径
            output_dir: 输出目录
            plot_id: 小区ID
            patch_size: 小块大小
            overlap: 重叠像素数
        """
        if patch_size is None:
            patch_size = self.patch_size
        if overlap is None:
            overlap = self.patch_overlap
            
        try:
            # 打开影像
            with rasterio.open(image_path) as src:
                image = src.read(1)
                meta = src.meta.copy()
                
                # 提取文件名信息
                filename = os.path.basename(image_path)
                base_name = os.path.splitext(filename)[0]
                
                # 计算步长
                stride = patch_size - overlap
                
                # 创建输出目录
                os.makedirs(output_dir, exist_ok=True)
                
                # 生成小块
                patch_paths = []
                patch_idx = 0
                
                for y in range(0, image.shape[0] - patch_size + 1, stride):
                    for x in range(0, image.shape[1] - patch_size + 1, stride):
                        # 提取小块
                        patch = image[y:y+patch_size, x:x+patch_size]
                        
                        # 构建输出路径
                        output_path = os.path.join(
                            output_dir, 
                            f"{base_name}_{plot_id:03d}_patch{patch_idx:03d}.tif"
                        )
                        
                        # 更新元数据
                        patch_meta = meta.copy()
                        patch_meta.update({
                            "height": patch_size,
                            "width": patch_size,
                            "transform": rasterio.transform.from_origin(
                                src.transform.xoff + x * src.transform.a,
                                src.transform.yoff + y * src.transform.e,
                                src.transform.a,
                                src.transform.e
                            )
                        })
                        
                        # 保存小块
                        with rasterio.open(output_path, "w", **patch_meta) as dest:
                            dest.write(patch.reshape(1, patch_size, patch_size))
                            
                        patch_paths.append(output_path)
                        patch_idx += 1
                        
            return True, patch_paths
        except Exception as e:
            print(f"生成小块图失败: {image_path}, 小区ID: {plot_id}, 错误: {e}")
            return False, None