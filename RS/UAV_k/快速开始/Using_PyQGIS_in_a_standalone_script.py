# 参考文献：https://docs.qgis.org/3.34/en/docs/pyqgis_developer_cookbook/intro.html
from qgis.core import *
# 导入qgis.core模块

# 在脚本开头初始化 QGIS 资源
# Supply path to qgis install location
# QgsApplication.setPrefixPath("/path/to/qgis/installation", True)
QgsApplication.setPrefixPath('D:/QGIS/apps/qgis-ltr', True)
# 前缀路径是 QGIS 在您的系统上的安装位置。
# 它是通过调用setPrefixPath()方法在脚本中配置的。 
# setPrefixPath() 的第二个参数设置为True，指定要使用默认路径
# QGIS 的安装路径因平台而异；为您的系统找到它的最简单方法是使用QGIS 中的 Python 控制台中的脚本并查看运行的输出：
# QgsApplication.prefixPath()
# 'D:/QGIS/apps/qgis-ltr'

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)
# 配置前缀路径后，我们 QgsApplication在变量中保存对的引用qgs。
# 第二个参数设置为False，指定我们不打算使用 GUI，因为我们正在编写独立脚本。

# Load providers
qgs.initQgis()
# QgsApplication 配置完成后，我们通过调用方法来加载 QGIS 数据提供程序和图层注册表

# 可以编写脚本的其余部分
# Write your code here to load some layers, use processing
# algorithms, etc.
print('hello pyqgis')

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
qgs.exitQgis()
# 最后，我们通过调用exitQgis() 从内存中删除数据提供者和图层注册表来结束。