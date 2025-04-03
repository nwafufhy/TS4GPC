import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                            QVBoxLayout, QLineEdit, QLabel, QFileDialog,
                            QHBoxLayout, QAbstractItemView, QPushButton,
                            QListWidget, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt
import os
from qgis.core import (QgsVectorLayer, QgsRasterLayer, QgsProject, QgsApplication,
                      QgsCoordinateTransform)
from qgis.gui import QgsMapCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 初始化QGIS
        QgsApplication.setPrefixPath(r'D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr', True)
        self.qgs = QgsApplication([], False)
        self.qgs.initQgis()
        
        # 设置主窗口
        self.setWindowTitle("基于pyqgis的矢量/栅格图层的极速加载器")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建主部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 布局
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # 文件路径输入框
        self.file_path_label = QLabel("拖放SHP/TIF文件到这里：")
        layout.addWidget(self.file_path_label)
        
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.file_path_input.setPlaceholderText("拖放SHP/TIF文件或点击选择（支持多选和文件夹自动识别）")
        self.file_path_input.mousePressEvent = self.open_file_dialog
        layout.addWidget(self.file_path_input)
        
        # 创建水平布局用于图层控制和画布
        h_layout = QHBoxLayout()
        
        # 图层管理面板
        layer_panel = QWidget()
        layer_panel.setMaximumWidth(300)
        panel_layout = QVBoxLayout()
        
        # 图层列表
        self.layer_list = QListWidget()
        self.layer_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        panel_layout.addWidget(QLabel("已加载图层:"))
        panel_layout.addWidget(self.layer_list)
        
        # 图层控制按钮
        btn_layout = QHBoxLayout()
        self.move_up_btn = QPushButton("上移")
        self.move_up_btn.clicked.connect(self.move_layer_up)
        btn_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("下移")
        self.move_down_btn.clicked.connect(self.move_layer_down)
        btn_layout.addWidget(self.move_down_btn)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.delete_layer)
        btn_layout.addWidget(self.delete_btn)
        
        panel_layout.addLayout(btn_layout)
        
        # 添加属性显示框
        self.property_display = QTextEdit()
        self.property_display.setReadOnly(True)
        self.property_display.setMinimumHeight(200)
        panel_layout.addWidget(QLabel("图层属性:"))
        panel_layout.addWidget(self.property_display)
        
        # 连接图层选择事件
        self.layer_list.itemSelectionChanged.connect(self.show_layer_properties)
        
        layer_panel.setLayout(panel_layout)
        h_layout.addWidget(layer_panel)
        
        # 地图画布
        self.canvas = QgsMapCanvas()
        h_layout.addWidget(self.canvas)
        
        layout.addLayout(h_layout)
        
        # 状态栏
        self.statusBar().showMessage("准备就绪")
        
        # 启用拖放
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        file_paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                if path.endswith('.shp') or path.endswith('.tif') or path.endswith('.tiff'):
                    file_paths.append(path)
            elif os.path.isdir(path):
                # 遍历文件夹查找GIS文件
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file_path.endswith('.shp') or file_path.endswith('.tif') or file_path.endswith('.tiff'):
                            file_paths.append(file_path)
        
        if file_paths:
            self.file_path_input.setText(", ".join(file_paths))
            self.load_layers(file_paths)
                
    def load_layers(self, paths):
        layers = []
        for path in paths:
            if path.endswith('.shp'):
                layer_name = os.path.splitext(os.path.basename(path))[0]
                layer = QgsVectorLayer(path, layer_name, "ogr")
                if not layer.isValid():
                    self.statusBar().showMessage(f"无法加载矢量图层: {path}")
                    continue
            else:  # 栅格文件
                layer_name = os.path.splitext(os.path.basename(path))[0]
                layer = QgsRasterLayer(path, layer_name)
                if not layer.isValid():
                    self.statusBar().showMessage(f"无法加载栅格图层: {path}")
                    continue
            
            QgsProject.instance().addMapLayer(layer)
            layers.append(layer)
            self.layer_list.addItem(layer.name())
        
        if layers:
            # 设置画布范围以包含所有图层
            extent = None
            canvas_crs = self.canvas.mapSettings().destinationCrs()
            
            for layer in layers:
                layer_extent = layer.extent()
                
                # 如果图层CRS与画布CRS不同，进行坐标转换
                if layer.crs() != canvas_crs:
                    transform = QgsCoordinateTransform(
                        layer.crs(),
                        canvas_crs,
                        QgsProject.instance()
                    )
                    layer_extent = transform.transformBoundingBox(layer_extent)
                
                if extent is None:
                    extent = layer_extent
                else:
                    extent.combineExtentWith(layer_extent)
                    
                # 保持图层原有CRS，仅进行显示转换
                if layer.crs() != canvas_crs:
                    transform = QgsCoordinateTransform(
                        layer.crs(),
                        canvas_crs,
                        QgsProject.instance()
                    )
                    layer_extent = transform.transformBoundingBox(layer_extent)
                
            # 获取当前所有图层
            current_layers = self.canvas.layers()
            # 合并新旧图层，确保不重复
            all_layers = list(set(current_layers + layers))
            
            # 设置画布CRS为第一个图层的CRS
            if not self.canvas.mapSettings().destinationCrs().isValid():
                self.canvas.setDestinationCrs(layers[0].crs())
            
            # 确保矢量图层在栅格图层之上
            all_layers.sort(key=lambda l: isinstance(l, QgsRasterLayer))
            
            self.canvas.setExtent(extent)
            self.canvas.setLayers(all_layers)
            
            # 强制刷新并确保所有图层可见
            for layer in all_layers:
                layer.setOpacity(1.0)
                layer.triggerRepaint()
                
            self.canvas.refreshAllLayers()
            self.statusBar().showMessage(f"成功加载 {len(layers)} 个图层，当前共 {len(all_layers)} 个图层")
        
    def closeEvent(self, event):
        # 清理QGIS资源
        self.qgs.exitQgis()
        event.accept()
        
    def open_file_dialog(self, event):
        # 打开文件选择对话框
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择SHP/TIF文件（可多选）",
            "",
            "GIS Files (*.shp *.tif *.tiff)"
        )
        if file_paths:
            self.file_path_input.setText(", ".join(file_paths))
            self.load_layers(file_paths)

    def move_layer_up(self):
        current_row = self.layer_list.currentRow()
        if current_row > 0:
            # 移动列表项
            item = self.layer_list.takeItem(current_row)
            self.layer_list.insertItem(current_row - 1, item)
            self.layer_list.setCurrentRow(current_row - 1)
            
            # 更新图层顺序
            self.update_layer_order()
            self.canvas.refresh()  # 强制刷新画布
    
    def move_layer_down(self):
        current_row = self.layer_list.currentRow()
        if current_row < self.layer_list.count() - 1:
            # 移动列表项
            item = self.layer_list.takeItem(current_row)
            self.layer_list.insertItem(current_row + 1, item)
            self.layer_list.setCurrentRow(current_row + 1)
            
            # 更新图层顺序
            self.update_layer_order()
    
    def update_layer_order(self):
        layers = []
        for i in range(self.layer_list.count()):
            layer_name = self.layer_list.item(i).text()
            layer = QgsProject.instance().mapLayersByName(layer_name)[0]
            layers.append(layer)
        
        self.canvas.setLayers(layers)
        self.statusBar().showMessage("图层顺序已更新")
        
    def show_layer_properties(self):
        """显示当前选中图层的属性信息"""
        selected_items = self.layer_list.selectedItems()
        if not selected_items:
            self.property_display.clear()
            return
            
        layer_name = selected_items[0].text()
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        
        properties = []
        
        if isinstance(layer, QgsRasterLayer):
            # 显示栅格图层属性
            properties.append(f"栅格图层: {layer_name}")
            properties.append(f"路径: {layer.source()}")
            properties.append(f"分辨率: {layer.width()} x {layer.height()} 像素")
            properties.append(f"范围: {layer.extent().toString()}")
            properties.append(f"波段数: {layer.bandCount()}")
            for i in range(1, layer.bandCount() + 1):
                properties.append(f"波段 {i}: {layer.bandName(i)}")
            properties.append(f"渲染类型: {layer.renderer().type()}")
            
        elif isinstance(layer, QgsVectorLayer):
            # 显示矢量图层属性
            properties.append(f"矢量图层: {layer_name}")
            properties.append(f"路径: {layer.source()}")
            geometry_type = layer.geometryType()
            geometry_names = {
                0: "点 (Point)",
                1: "线 (Line)",
                2: "面 (Polygon)",
                3: "未知几何类型 (Unknown)"
            }
            properties.append(f"几何类型: {geometry_names.get(geometry_type, '未知')}")
            properties.append(f"要素数量: {layer.featureCount()}")
            properties.append("\n字段信息:")
            for field in layer.fields():
                properties.append(f"- {field.name()} ({field.typeName()})")
            
        self.property_display.setText("\n".join(properties))
        
    def delete_layer(self):
        # 获取选中的图层项
        selected_items = self.layer_list.selectedItems()
        if not selected_items:
            self.statusBar().showMessage("请先选择要删除的图层")
            return
            
        # 确认删除
        reply = QMessageBox.question(
            self,
            '确认删除',
            f'确定要删除这 {len(selected_items)} 个图层吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 删除图层
            for item in selected_items:
                layer_name = item.text()
                layer = QgsProject.instance().mapLayersByName(layer_name)[0]
                QgsProject.instance().removeMapLayer(layer.id())
                self.layer_list.takeItem(self.layer_list.row(item))
            
            # 更新画布
            self.update_layer_order()
            self.canvas.refresh()  # 强制刷新画布
            self.statusBar().showMessage(f"成功删除 {len(selected_items)} 个图层")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
