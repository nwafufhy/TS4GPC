"""
format_plot_ids.py - QGIS Python脚本

功能描述:
本脚本用于批量重命名shapefile中的plot_id字段值，为每个ID添加前导零使其成为3位数字。
主要功能包括：
1. 初始化QGIS环境
2. 加载指定的shapefile矢量图层
3. 遍历所有要素，将plot_id字段值转换为3位数字格式（如001, 002等）
4. 保存修改后的属性值

实现方式:
- 使用QGIS Python API (qgis.core) 操作矢量数据
- 通过QgsVectorDataProvider修改要素属性
- 使用zfill()方法实现数字补零

使用方法:
1. 修改path_to_vlayer变量指向目标shapefile路径
2. 运行脚本即可自动完成ID重命名

注意事项:
- 需要正确配置QGIS环境路径
- 目标shapefile必须包含plot_id字段
"""
# 初始化 QGIS 资源
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsApplication,
    QgsVectorDataProvider,
    QgsField
)
from qgis.gui import(
    QgsMapCanvas
)
from qgis.PyQt.QtCore import QVariant

QgsApplication.setPrefixPath('D:/QGIS/apps/qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# 脚本正文
# 使用QgsMapCanvas()创建一个地图画布实例，并通过canvas.show()显示它
# canvas = QgsMapCanvas()
# canvas.show()

# 加载一个shp文件作为矢量图层
path_to_vlayer = r"D:\work\CXZ-WN\CXZ-WN-2024\plot_clip_shp\plot.shp"
vlayer = QgsVectorLayer(path_to_vlayer, "plots", "ogr")
if not vlayer.isValid():
    print("无法加载矢量图层!")
else:
    QgsProject.instance().addMapLayer(vlayer)

caps = vlayer.dataProvider().capabilities()
# if caps & QgsVectorDataProvider.AddAttributes:
#     res = vlayer.dataProvider().addAttributes(
#         [QgsField("plot_id", QVariant.String)])

# fields()您可以通过调用对象 来检索与矢量图层关联的字段的信息
for field in vlayer.fields():
    print(field.name(), field.typeName())

features = vlayer.getFeatures()
for feature in features:
    if caps & QgsVectorDataProvider.ChangeAttributeValues:
        plot_id_name = str(feature.id() + 1).zfill(3)
        # attrs = { 1 : plot_id_name, 1 : 123 }
        attrs = { 1 : plot_id_name}
        vlayer.dataProvider().changeAttributeValues({ feature.id() : attrs })
    # retrieve every feature with its geometry and attributes
    # 检索每一个特征及其形状和属性
    # print("plot_id: ", feature['plot_id'])

features = vlayer.getFeatures()
for feature in features:
    print("plot_id: ", feature['plot_id'])
# canvas.setExtent(vlayer.extent())
# canvas.setLayers([vlayer])
# exitCode = qgs.exec()

# 结束程序
qgs.exitQgis()
