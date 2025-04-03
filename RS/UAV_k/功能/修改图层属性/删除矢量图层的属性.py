from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsVectorDataProvider
)

QgsApplication.setPrefixPath(r'D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

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

def del_field_polygon(polygon_file_path= r'D:\work\CXZ-WN\clip_shp\2023_CXZ-WN-caijian\CXZ-WN-caijian.shp'):
    """
    删除矢量图层的属性
    输入：矢量图层的地址,默认为r'D:\work\CXZ-WN\clip_shp\2023_CXZ-WN-caijian\CXZ-WN-caijian.shp'
    """
    polygon_layer = QgsVectorLayer(polygon_file_path, 'Polygons', 'ogr')
    if not polygon_layer.isValid():
        raise ValueError("无法加载图层，请检查文件路径和格式。")
    
    len_field = len(polygon_layer.fields())
    caps = polygon_layer.dataProvider().capabilities()
    if caps & QgsVectorDataProvider.DeleteAttributes:
        polygon_layer.dataProvider().deleteAttributes([i for i in range(3,len_field)])

def main():
    print('删除前所有的属性')
    print_field_polygon()

    del_field_polygon()

    print('删除后所有的属性')
    print_field_polygon()

if __name__ == "__main__":
    main()
    qgs.exitQgis()