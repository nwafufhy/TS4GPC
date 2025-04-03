## QGIS初始化
from qgis.core import (
    QgsApplication,
    QgsVectorLayer
)

QgsApplication.setPrefixPath(r'D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

def print_feature_polygon(polygon_file_path= r'D:\work\CXZ-WN\clip_shp\2023_CXZ-WN-caijian\CXZ-WN-caijian.shp'):
    """
    打印矢量图层的所有特征
    输入：矢量图层的地址,默认为r'D:\work\CXZ-WN\clip_shp\2023_CXZ-WN-caijian\CXZ-WN-caijian.shp'
    """
    polygon_layer = QgsVectorLayer(polygon_file_path, 'Polygons', 'ogr')
    if not polygon_layer.isValid():
        raise ValueError("无法加载图层，请检查文件路径和格式。")
    
    features = polygon_layer.getFeatures()
    for feature in features:
        print (feature.attributes())

def print_field_polygon(polygon_file_path= r'D:\work\CXZ-WN\clip_shp\2023_CXZ-WN-caijian\CXZ-WN-caijian.shp'):
    """
    检索有关属性的信息
    输入：矢量图层的地址,默认为r'D:\work\CXZ-WN\clip_shp\2023_CXZ-WN-caijian\CXZ-WN-caijian.shp'
    """
    polygon_layer = QgsVectorLayer(polygon_file_path, 'Polygons', 'ogr')
    if not polygon_layer.isValid():
        raise ValueError("无法加载图层，请检查文件路径和格式。")
    for field in polygon_layer.fields():
        print(field.name(), field.typeName())
    print(len(polygon_layer.fields()))
    
def main():
    print_field_polygon()
    input1 = input('是否打印矢量图层的所有特征y/n')
    if input1 == 'y':
        print_feature_polygon() 

# 这里的 if __name__ == "__main__": 是一个常用的Python惯用法，它检查当前脚本是否作为主程序运行（而不是被导入到另一个脚本中）。如果是，那么它将调用 main() 函数。
if __name__ == "__main__":
    main()
    qgs.exitQgis()