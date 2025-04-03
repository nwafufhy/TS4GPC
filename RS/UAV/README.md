## 核心业务逻辑
将不同时间下不同人物基于不同设备使用的不同飞行参数和拼接参数采集的正射投影图处理成
- 原始数据小区裁剪图
- 原始数据小区平均值
- 分辨率标准化的小区裁剪图
- 分辨率标准化的小区各项特征值
- 分辨率标准化的小区小块图（将原本740x230的图裁剪成重叠或不重叠的小块，如64x64）
- 分辨率标准化的小区小块图的各项特征值

## 步骤
1. 原始数据标准化
    计算各项特征值
2. 批量裁剪-原始小区裁剪图
    计算各项特征值
3. 分辨率标准化
    计算各项特征值
4. 裁剪成patch
    数据增强
5. 拼接
6. 制作成训练文档

## GUI工具
本模块提供了基于PyQt5的图形用户界面工具，用于简化无人机遥感数据处理流程：

1. **数据预览工具**：可视化查看原始影像和处理结果

## 仓库结构
UAV/
│
├── README.md                      # 模块说明文档
├── requirements.txt               # 环境依赖
│
├── config/                        # 配置文件
│   ├── __init__.py
│   └── settings.py                # 全局设置（路径、参数等）
│
├── core/                          # 核心功能模块
│   ├── __init__.py
│   ├── data_loader.py             # 数据加载
│   ├── standardization.py         # 数据标准化
│   ├── clipping.py                # 图像裁剪
│   ├── feature_extraction.py      # 特征提取
│   ├── patch_generation.py        # 小块图生成
│   └── dataset_builder.py         # 训练集构建
│
├── utils/                         # 工具函数
│   ├── __init__.py
│   ├── image_utils.py             # 图像处理工具
│   ├── file_utils.py              # 文件操作工具
│   └── visualization.py           # 可视化工具
│
├── gui/                           # GUI工具
│   ├── __init__.py
│   ├── main_window.py             # 主窗口
│   └── widgets/                   # 自定义控件
│
├── scripts/                       # 脚本文件
│   ├── standardize_data.py        # 数据标准化脚本
│   ├── clip_plots.py              # 小区裁剪脚本
│   ├── extract_features.py        # 特征提取脚本
│   ├── generate_patches.py        # 生成小块图脚本
│   └── build_dataset.py           # 构建数据集脚本
│
└── tests/                         # 测试代码
    ├── __init__.py
    ├── test_standardization.py
    ├── test_clipping.py
    └── test_feature_extraction.py

## 环境配置

## 使用示例