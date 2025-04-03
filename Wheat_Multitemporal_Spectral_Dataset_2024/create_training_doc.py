import pandas as pd
from pathlib import Path
import json

def create_training_doc(image_dir, gpc_file, output_file):
    """创建训练文档"""
    # 读取GPC数据
    gpc_data = pd.read_csv(gpc_file)
    
    # 获取所有图像文件
    image_dir = Path(image_dir)
    image_files = list(image_dir.glob('CX-WN-2024_*_patch*_merged.tif'))
    
    # 创建训练文档
    training_data = []
    for img_path in image_files:
        try:
            # 解析文件名获取plot_id
            # 文件名格式: CX-WN-2024_000_patch000_merged.tif
            parts = img_path.stem.split('_')  # ['CX-WN-2024', '000', 'patch000', 'merged']
            plot_id = int(parts[1])  # 获取plot_id (000)
            
            # 检查plot_id是否在GPC数据中
            if plot_id < len(gpc_data):
                gpc_value = gpc_data.iloc[plot_id]['品质_蛋白']
                
                # 创建数据项
                data_item = {
                    'image_path': str(img_path),
                    'plot_id': plot_id,
                    'patch_id': int(parts[2].replace('patch', '')),  # 获取patch编号
                    'gpc_value': float(gpc_value)
                }
                training_data.append(data_item)
        except Exception as e:
            print(f"处理文件 {img_path.name} 时出错: {str(e)}")
            continue
    
    # 按plot_id和patch_id排序
    training_data.sort(key=lambda x: (x['plot_id'], x['patch_id']))
    
    # 保存为JSON文件
    with open(output_file, 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"共处理 {len(training_data)} 个样本")
    print(f"训练文档已保存至: {output_file}")
    
    # 返回一些基本统计信息
    gpc_values = [item['gpc_value'] for item in training_data]
    if gpc_values:
        print(f"\nGPC值统计:")
        print(f"最小值: {min(gpc_values):.2f}")
        print(f"最大值: {max(gpc_values):.2f}")
        print(f"平均值: {sum(gpc_values)/len(gpc_values):.2f}")

if __name__ == "__main__":
    # 设置路径
    image_dir = r"D:\work\DATA\DATA_TS4GPC\processed\clip_CXZ_WN_2024_patches_merged_v1"
    gpc_file = r'D:\work\DATA\DATA_TS4GPC\processed\gpc_data.csv'
    output_file = r"train_doc_v1.json"
    
    # 创建训练文档
    create_training_doc(image_dir, gpc_file, output_file)