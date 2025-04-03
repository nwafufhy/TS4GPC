# TS4GPC
[![Documentation Status](https://github.com/nwafufhy/TS4GPC/actions/workflows/docs.yml/badge.svg)](https://nwafufhy.github.io/TS4GPC/)
《基于多时相光谱的小麦籽粒蛋白质含量预测研究》的代码库
> TS4GPC: Time Series 4 Grop Protein Content

## 仓库结构
- TS4GPC

    - RS # 遥感数据自动化分析流程
        - Satellite # 卫星遥感
        - UAV # 无人机遥感

    - DATA # 数据模块
        - DataInitialization # 数据文件系统初始化
        - DataPreprocess # 数据预处理
            - merge.py # 数据文件合并
        - DataStructureAnalysis # 数据结构分析
        - DataStandardization # 数据标准化
        - MetaData # 元数据
            - MetaDataStandardization # 元数据标准化

    - Analysis # 数据分析
        - DescriptiveStatistics # 描述性统计分析
        - EDA # 数据探索性分析
        - ML # 机器学习
        - Dl # 深度学习

    - Model # 模型构建
        - ViT # Vision Transformer

## 环境配置
本代码库包含多个子模块，每个子模块都有自己的环境配置文件。在使用之前，请先安装相应的环境。
子模块的‘README.md’文件中包含了环境配置的详细信息。

## 数据获取与预处理
### 遥感数据自动化处理流程
本研究采用多时相（multi-temporal）遥感数据，通过卫星与无人机双平台协同观测：
1. **卫星遥感**：基于Sentinel-2多光谱数据，通过Google Earth Engine (GEE) 平台实现数据获取与预处理；
2. **无人机遥感**：基于Pix4Dmapper拼接成的正射镶嵌图，通过PyQGIS与GDAL库编写的自动化分析脚本实现特征提取。
### 时序数据自动化处理流程
### 数据结构分析（Data Structure Analysis, DSA）
### 数据标准化
### 数据预处理
## 数据分析
### 描述性统计分析
### 数据探索性分析（EDA）

## 数据分析与模型构建
### 经验模型（Empirical Model）
#### 线性模型
- 普通线性模型
- 岭回归线性模型
#### 机器学习
- 最近邻回归模型（K-Nearest Neighbors, KNN）
- 基于动态时间规整（Dynamic Time Warping, DTW）的KNN回归模型
- 决策树回归模型（Decision Tree, DT）
- 随机森林回归模型（Random Forest, RF）
- 支持向量机回归模型（Support Vector Machine, SVM）
#### 深度学习
- 多层感知机回归模型（Multi-Layer Perceptron, MLP）
- Vision Transformer回归模型（ViT）
### 半机理模型（Semiempirical Model）
- 光谱→农艺
- 农艺→GPC


## 推荐使用顺序
1. 初始化