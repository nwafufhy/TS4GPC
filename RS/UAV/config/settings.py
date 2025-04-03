"""
UAV遥感数据处理全局配置
从配置文件加载设置
"""

import os
import json
import sys

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "uav_config.json")
DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "uav_config_default.json")

def load_config(config_path=None):
    """
    加载配置文件
    
    参数:
        config_path: 配置文件路径，如果为None则使用默认路径
    
    返回:
        配置字典
    """
    if config_path is None:
        config_path = CONFIG_FILE
    
    # 如果指定的配置文件不存在，尝试使用默认配置
    if not os.path.exists(config_path) and os.path.exists(DEFAULT_CONFIG_FILE):
        print(f"警告: 配置文件 {config_path} 不存在，使用默认配置")
        config_path = DEFAULT_CONFIG_FILE
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"错误: 无法加载配置文件 {config_path}: {e}")
        # 如果无法加载配置文件，返回空字典
        return {}

# 加载配置
config = load_config()

# 基础路径
BASE_DIR = config.get('paths', {}).get('base_dir', r"D:\work\xnpanV2\personal_space\program\TS4GPC")
DATA_DIR = config.get('paths', {}).get('data_dir', os.path.join(BASE_DIR, "DATA"))
RAW_DATA_DIR = config.get('paths', {}).get('raw_data_dir', r"D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN")
PROCESSED_DATA_DIR = config.get('paths', {}).get('processed_data_dir', r"D:\work\DATA\DATA_TS4GPC\processed")

# 输出路径
OUTPUT_DIR = config.get('paths', {}).get('output_dir', os.path.join(BASE_DIR, "Wheat_Multitemporal_Spectral_Dataset_2024"))
CLIPPED_PLOTS_DIR = config.get('paths', {}).get('clipped_plots_dir', os.path.join(PROCESSED_DATA_DIR, "clip_CXZ_WN_2024"))
PATCHES_DIR = config.get('paths', {}).get('patches_dir', os.path.join(PROCESSED_DATA_DIR, "clip_CXZ_WN_2024_patches"))
MERGED_PATCHES_DIR = config.get('paths', {}).get('merged_patches_dir', os.path.join(PROCESSED_DATA_DIR, "clip_CXZ_WN_2024_patches_merged"))

# 矢量数据
PLOT_SHAPEFILE = config.get('paths', {}).get('plot_shapefile', r"D:\work\DATA\DATA_TS4GPC\raw\UAV\CXZ-WN\clip_shp\2024_plot_clip_shp\plot.shp")

# 数据参数
BANDS = config.get('data_params', {}).get('bands', ["Blue", "Green", "Red", "RedEdge", "NIR"])
DATES = config.get('data_params', {}).get('dates', [])
PATCH_SIZE = config.get('data_params', {}).get('patch_size', 64)
PATCH_OVERLAP = config.get('data_params', {}).get('patch_overlap', 0)  # 0表示不重叠，正数表示重叠像素数

# GPC数据
GPC_DATA_FILE = config.get('paths', {}).get('gpc_data_file', os.path.join(PROCESSED_DATA_DIR, "gpc_data.csv"))
MERGED_DATA_FILE = config.get('paths', {}).get('merged_data_file', os.path.join(PROCESSED_DATA_DIR, "mergeANDprocessedANDxiuzheng_data_CXZ_WN_2023-2024.csv"))

# 标准化参数
TARGET_RESOLUTION = config.get('processing_params', {}).get('target_resolution', 0.03)  # 目标分辨率(米/像素)

def save_config(config_dict, config_path=None):
    """
    保存配置到文件
    
    参数:
        config_dict: 配置字典
        config_path: 配置文件路径，如果为None则使用默认路径
    
    返回:
        是否保存成功
    """
    if config_path is None:
        config_path = CONFIG_FILE
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"错误: 无法保存配置文件 {config_path}: {e}")
        return False

def get_current_config():
    """
    获取当前配置
    
    返回:
        当前配置字典
    """
    return {
        "paths": {
            "base_dir": BASE_DIR,
            "data_dir": DATA_DIR,
            "raw_data_dir": RAW_DATA_DIR,
            "processed_data_dir": PROCESSED_DATA_DIR,
            "output_dir": OUTPUT_DIR,
            "clipped_plots_dir": CLIPPED_PLOTS_DIR,
            "patches_dir": PATCHES_DIR,
            "merged_patches_dir": MERGED_PATCHES_DIR,
            "plot_shapefile": PLOT_SHAPEFILE,
            "gpc_data_file": GPC_DATA_FILE,
            "merged_data_file": MERGED_DATA_FILE
        },
        "data_params": {
            "bands": BANDS,
            "dates": DATES,
            "patch_size": PATCH_SIZE,
            "patch_overlap": PATCH_OVERLAP
        },
        "processing_params": {
            "target_resolution": TARGET_RESOLUTION
        }
    }

# 创建默认配置文件（如果不存在）
if not os.path.exists(CONFIG_FILE) and not os.path.exists(DEFAULT_CONFIG_FILE):
    save_config(get_current_config(), DEFAULT_CONFIG_FILE)