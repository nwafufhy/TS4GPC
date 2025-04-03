import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout)
from PyQt5.QtCore import Qt
from qgis.core import QgsApplication

# 导入子界面
from pyqgis.gui.ortho_to_singleband_gui import OrthoToSinglebandApp, ConversionThread
from pyqgis.gui.Load_layer_gui import MainWindow as LoadLayerApp

class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 初始化QGIS
        QgsApplication.setPrefixPath(r'D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr', True)
        self.qgs = QgsApplication([], False)
        self.qgs.initQgis()
        
        # 设置主窗口
        self.setWindowTitle("PyQGIS 综合工具")
        self.setGeometry(100, 100, 1024, 768)
        
        # 创建主部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 主布局
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # 添加图层加载选项卡
        self.layer_tab = LoadLayerApp()
        self.tabs.addTab(self.layer_tab, "图层加载")
        
        # 添加转换工具选项卡
        self.conversion_tab = OrthoToSinglebandApp()
        self.tabs.addTab(self.conversion_tab, "影像转换（multi2single）")
        
        # 添加裁剪工具选项卡
        from pyqgis.gui.clip_gui import ClipTab
        self.clip_tab = ClipTab()
        self.tabs.addTab(self.clip_tab, "栅格裁剪")
        
        # 连接信号
        self.connect_signals()
        
    def connect_signals(self):
        """连接子界面信号"""
        # 初始化conversion_thread
        self.conversion_tab.conversion_thread = ConversionThread([])
        
        # 当转换工具加载图层时，同步到图层加载界面
        self.conversion_tab.conversion_thread.load_layer_signal.connect(
            self.layer_tab.load_layers
        )
        
    def closeEvent(self, event):
        """关闭窗口时清理资源"""
        # 关闭子界面
        self.conversion_tab.close()
        self.layer_tab.close()
        
        # 清理QGIS资源
        self.qgs.exitQgis()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    sys.exit(app.exec_())
