import os
from qgis.core import QgsApplication, QgsRasterLayer, QgsProject
import subprocess

# 初始化 QGIS 环境
QgsApplication.setPrefixPath(r'D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

def load_raster(path):
    """加载栅格图层并返回图层对象"""
    layer = QgsRasterLayer(path, os.path.basename(path))
    if not layer.isValid():
        raise ValueError(f"无法加载栅格图层: {path}")
    return layer

def get_band_info(layer):
    """获取波段信息"""
    band_count = layer.bandCount()
    band_info = {}
    
    # 获取波段信息
    for band_num in range(1, band_count + 1):
        # 直接从图层获取波段名称
        band_name = layer.bandName(band_num)
        
        # 如果元数据中没有，尝试从图层获取
        if not band_name:
            band_name = layer.bandName(band_num)
            
        # 如果还是没有名称，使用默认编号
        if not band_name:
            band_name = f'Band_{band_num}'
            
        band_info[band_num] = {
            'name': band_name,
            'description': f"波段 {band_num}: {band_name}"
        }
    return band_info

def clean_filename(name):
    """清理文件名中的非法字符"""
    # 替换 Windows 文件名中的非法字符
    invalid_chars = ':*?"<>|'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip()

def split_bands(input_path, output_dir, band_info):
    """将多波段图像分离为单波段图像"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    for band_num, info in band_info.items():
        # 清理波段名称
        clean_band_name = clean_filename(info['name'])
        output_path = os.path.join(
            output_dir,
            f"{base_name}_{clean_band_name}.tif"
        )
        
        # 使用 gdal_translate 提取单个波段
        cmd = [
            'gdal_translate',
            '-b', str(band_num),  # 指定波段编号
            input_path,
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"成功提取波段 {band_num} ({info['name']}) 到 {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"提取波段 {band_num} 失败: {e}")

def main():
    # 输入路径
    input_path = r"D:\work\DATA\官村无人机影像\关村240620大图\正射影像镶嵌图.data.tif"
    
    # 自动创建输出目录
    output_dir = os.path.join(os.path.dirname(input_path), "single_bands")
    
    try:
        # 加载栅格图层
        layer = load_raster(input_path)
        QgsProject.instance().addMapLayer(layer)
        
        # 获取波段信息
        band_info = get_band_info(layer)
        print("波段信息:")
        for band_num, info in band_info.items():
            print(f"波段 {band_num}: {info['name']}")
        
        # 分离波段
        split_bands(input_path, output_dir, band_info)
        
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
    finally:
        # 清理 QGIS 环境
        qgs.exitQgis()

if __name__ == "__main__":
    main()
