import os
import pandas as pd
import numpy as np
from pathlib import Path

class WheatDatasetPreparation:
    def __init__(self):
        # 设置路径
        self.clipped_images_path = r'D:\work\DATA\DATA_TS4GPC\processed\clip_CXZ_WN_2024'
        self.gpc_data_path = r'D:\work\DATA\DATA_TS4GPC\processed\mergeANDprocessedANDxiuzheng_data_CXZ_WN_2023-2024.csv'
        self.output_path = r'D:\work\xnpanV2\personal_space\CODE\Undergraduate_Thesis_FengHaoyu_2025\Wheat_Multitemporal_Spectral_Dataset_2024\dataset_index'
        
        # 创建输出目录
        os.makedirs(self.output_path, exist_ok=True)
        
    def load_gpc_data(self):
        """加载GPC数据"""
        df = pd.read_csv(self.gpc_data_path)
        # 筛选2024年的数据
        df_2024 = df[df['year'] == 2024].copy()
        return df_2024
    
    def get_image_paths(self):
        """获取所有裁剪后的图像路径"""
        image_dict = {}  # {plot_id: {time: {band: path}}}
        
        for root, _, files in os.walk(self.clipped_images_path):
            for file in files:
                if file.endswith('.tif'):
                    # 解析文件名获取信息
                    # 例如：CXZ-WN-240130-Blue-001.tif
                    parts = file.split('-')
                    if len(parts) >= 5:
                        time = parts[2]  # 240130
                        band = parts[3]  # Blue
                        plot_id = int(parts[4].split('.')[0])  # 001
                        
                        if plot_id not in image_dict:
                            image_dict[plot_id] = {}
                        if time not in image_dict[plot_id]:
                            image_dict[plot_id][time] = {}
                            
                        image_dict[plot_id][time][band] = os.path.join(root, file)
        
        return image_dict
    
    def create_dataset_index(self):
        """创建数据集索引文件"""
        gpc_data = self.load_gpc_data()
        image_paths = self.get_image_paths()
        
        dataset_records = []
        for plot_id in image_paths:
            plot_data = {
                'plot_id': plot_id,
                'gpc': gpc_data[gpc_data['plot_id'] == plot_id]['GPC'].values[0],
                'image_paths': image_paths[plot_id]
            }
            dataset_records.append(plot_data)
        
        # 保存为JSON格式
        import json
        output_file = os.path.join(self.output_path, 'dataset_index.json')
        with open(output_file, 'w') as f:
            json.dump(dataset_records, f, indent=4)
        
        print(f"数据集索引文件已保存至: {output_file}")
        return dataset_records

if __name__ == '__main__':
    dataset_prep = WheatDatasetPreparation()
    dataset_records = dataset_prep.create_dataset_index()