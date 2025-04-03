import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QListWidget, QFileDialog,
                            QMessageBox, QProgressBar, QTextEdit, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from qgis.core import QgsApplication, QgsRasterLayer, QgsProject
import subprocess
import os

class ConversionThread(QThread):
    """用于后台运行的转换线程"""
    progress_signal = pyqtSignal(int)
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    load_layer_signal = pyqtSignal(str)
    remove_layer_signal = pyqtSignal()
    layer_loaded = False
    
    def __init__(self, file_list, parent=None):
        super().__init__(parent)
        self.file_list = file_list
        self._is_running = True
        self.current_layer = None
        
    def set_current_layer(self, layer):
        """设置当前图层"""
        self.current_layer = layer
        
    def run(self):
        try:
            for i, file_path in enumerate(self.file_list):
                if not self._is_running:
                    break
                    
                self.output_signal.emit(f"正在处理文件: {file_path}")
                self.convert_file(file_path)
                self.progress_signal.emit(i + 1)
                
            if self._is_running:
                self.finished_signal.emit()
                
        except Exception as e:
            self.error_signal.emit(str(e))
            
    def stop(self):
        """停止转换线程"""
        self._is_running = False
        if self.current_layer:
            QgsProject.instance().removeMapLayer(self.current_layer)
            self.current_layer = None
        self.layer_loaded = False
        
    def convert_file(self, input_path):
        """转换单个文件"""
        output_dir = os.path.join(os.path.dirname(input_path), "single_bands")
        
        # 在主线程加载图层
        self.layer_loaded = False
        self.load_layer_signal.emit(input_path)
        while not self.layer_loaded:
            self.msleep(100)
            
            # 获取主线程传递的图层
            if not hasattr(self, 'current_layer') or not self.current_layer or not self.current_layer.isValid():
                self.output_signal.emit(f"无法加载栅格图层: {input_path}")
                # 跳过当前文件，继续处理下一个
                self.progress_signal.emit(
                    self.file_list.index(input_path) + 1
                )
                continue
            
            # 获取波段信息
            band_info = self.get_band_info(self.current_layer)
            if not band_info:
                self.output_signal.emit(f"无法获取波段信息: {input_path}")
                # 跳过当前文件，继续处理下一个
                self.progress_signal.emit(
                    self.file_list.index(input_path) + 1
                )
                continue
                
            # 创建输出目录
            try:
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            except Exception as e:
                self.output_signal.emit(f"无法创建输出目录 {output_dir}: {str(e)}")
                # 跳过当前文件，继续处理下一个
                self.progress_signal.emit(
                    self.file_list.index(input_path) + 1
                )
                continue
            
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        # 转换每个波段
        for band_num, info in band_info.items():
            if not self._is_running:
                break
                
            # 清理波段名称中的非法字符
            band_name = self.clean_filename(info['name'].strip())
            # 使用用户指定的格式生成文件名
            output_path = os.path.join(
                output_dir,
                f"singleband_Band_{band_num}_{band_name}.tif"
            )
            # 确保文件名以.tif结尾
            if not output_path.lower().endswith('.tif'):
                output_path += '.tif'
            
            cmd = [
                'gdal_translate',
                '-b', str(band_num),
                input_path,
                output_path
            ]
            
            # 获取文件大小信息
            size_info = subprocess.run(
                ['gdalinfo', input_path], 
                capture_output=True, 
                text=True
            )
            size_lines = [line for line in size_info.stdout.split('\n') 
                         if 'Size is' in line]
            size_str = size_lines[0].strip() if size_lines else '未知大小'
            
            # 显示波段信息
            self.output_signal.emit(f"\n波段信息:")
            self.output_signal.emit(f"波段 {band_num}: {info['name']}")
            self.output_signal.emit(f"输入文件: {size_str}")
            
            # 显示转换进度
            self.output_signal.emit("转换进度:")
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    check=True
                )
                
                # 解析并显示转换结果
                progress_lines = [line for line in result.stdout.split('\n') 
                                if '...' in line]
                if progress_lines:
                    self.output_signal.emit(progress_lines[-1].strip())
                    
                # 显示输出文件信息
                self.output_signal.emit(f"成功提取波段 {band_num} ({info['name']}) 到:")
                self.output_signal.emit(f"{output_path}")
            except subprocess.CalledProcessError as e:
                self.output_signal.emit(f"GDAL转换错误: {e.stderr}")
                # 删除可能创建的不完整输出文件
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except Exception as e:
                        self.output_signal.emit(f"无法删除不完整文件 {output_path}: {str(e)}")
                # 跳过当前波段，继续处理下一个
                continue
            except Exception as e:
                self.output_signal.emit(f"转换错误: {str(e)}")
                # 删除可能创建的不完整输出文件
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except Exception as e:
                        self.output_signal.emit(f"无法删除不完整文件 {output_path}: {str(e)}")
                # 跳过当前波段，继续处理下一个
                continue
            
        # 在主线程移除图层
        self.remove_layer_signal.emit()
        
    def get_band_info(self, layer):
        """获取波段信息"""
        try:
            band_count = layer.bandCount()
            if band_count == 0:
                raise ValueError("图层没有可用的波段信息")
                
            band_info = {}
            
            for band_num in range(1, band_count + 1):
                band_name = layer.bandName(band_num)
                if not band_name:
                    band_name = f'Band_{band_num}'
                    
                band_info[band_num] = {
                    'name': band_name,
                    'description': f"波段 {band_num}: {band_name}"
                }
            return band_info
        except Exception as e:
            self.output_signal.emit(f"获取波段信息错误: {str(e)}")
            return {}
        
    def clean_filename(self, name):
        """清理文件名中的非法字符"""
        invalid_chars = ':*?"<>|'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name.strip()

class OrthoToSinglebandApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initQgis()
        self.conversion_thread = None
        self.current_layer = None
        
    def initUI(self):
        self.setWindowTitle('多波段正射影像镶嵌图转单波段影像的批量处理工具')
        self.setGeometry(100, 100, 800, 600)
        
        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # 文件列表
        file_group = QGroupBox("文件列表 (支持拖放和自动识别文件夹中的正射影像镶嵌图)")
        file_layout = QVBoxLayout()
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.file_list.setAcceptDrops(True)
        self.file_list.dragEnterEvent = self.dragEnterEvent
        self.file_list.dragMoveEvent = self.dragMoveEvent
        self.file_list.dropEvent = self.dropEvent
        
        # 添加拖放支持
        self.setAcceptDrops(True)
        file_layout.addWidget(self.file_list)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        
        # 添加文件按钮
        self.add_btn = QPushButton('添加文件/文件夹')
        self.add_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(self.add_btn)
        
        # 移除文件按钮
        self.remove_btn = QPushButton('移除选中文件')
        self.remove_btn.clicked.connect(self.remove_files)
        btn_layout.addWidget(self.remove_btn)
        
        # 转换按钮
        self.convert_btn = QPushButton('开始转换')
        self.convert_btn.clicked.connect(self.start_conversion)
        btn_layout.addWidget(self.convert_btn)
        
        # 终止按钮
        self.stop_btn = QPushButton('终止')
        self.stop_btn.clicked.connect(self.stop_conversion)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # 输出框
        output_group = QGroupBox("运行状态")
        output_layout = QVBoxLayout()
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        output_layout.addWidget(self.output_box)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
    def initQgis(self):
        # 初始化 QGIS 环境
        self.qgs = QgsApplication([], False)
        self.qgs.setPrefixPath(r'D:\software\tool_gis\QGIS 3.34.12\apps\qgis-ltr', True)
        self.qgs.initQgis()
        
    def scan_folder(self, folder_path):
        """递归扫描文件夹中的正射影像镶嵌图tif文件"""
        tif_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if (file.lower().endswith(('.tif', '.tiff')) and 
                    "正射影像镶嵌图" in file):
                    tif_files.append(os.path.join(root, file))
        return tif_files
        
    def add_files(self):
        """添加文件或文件夹到列表"""
        options = QFileDialog.Options()
        path = QFileDialog.getExistingDirectory(
            self, 
            '选择文件夹',
            '',
            options=options
        )
        
        if path:
            # 扫描文件夹中的tif文件
            tif_files = self.scan_folder(path)
            if tif_files:
                self.file_list.addItems(tif_files)
            else:
                QMessageBox.warning(self, '警告', '所选文件夹中没有找到.tif文件')
            
    def remove_files(self):
        """移除选中的文件"""
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
            
    def start_conversion(self):
        """开始批量转换"""
        if self.file_list.count() == 0:
            QMessageBox.warning(self, '错误', '请先添加要转换的文件')
            return
            
        self.progress.setVisible(True)
        self.progress.setMaximum(self.file_list.count())
        self.progress.setValue(0)
        self.output_box.clear()
        
        # 禁用/启用按钮
        self.add_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        self.convert_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # 获取文件列表
        file_paths = [self.file_list.item(i).text() 
                     for i in range(self.file_list.count())]
        
        # 创建并启动转换线程
        self.conversion_thread = ConversionThread(file_paths)
        self.conversion_thread.progress_signal.connect(self.update_progress)
        self.conversion_thread.output_signal.connect(self.update_output)
        self.conversion_thread.finished_signal.connect(self.conversion_finished)
        self.conversion_thread.error_signal.connect(self.handle_error)
        self.conversion_thread.load_layer_signal.connect(self.load_layer)
        self.conversion_thread.remove_layer_signal.connect(self.remove_layer)
        self.conversion_thread.start()
        
    def stop_conversion(self):
        """终止转换"""
        if not self.conversion_thread or not self.conversion_thread.isRunning():
            return
            
        # 停止线程
        self.conversion_thread.stop()
        
        # 等待线程结束
        if not self.conversion_thread.wait(1000):
            self.conversion_thread.terminate()
            
        # 更新UI状态
        self.output_box.append("转换已终止")
        self.stop_btn.setEnabled(False)
        self.add_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        
        # 清理资源
        QgsProject.instance().removeAllMapLayers()
            
    def update_progress(self, value):
        """更新进度条"""
        self.progress.setValue(value)
        
    def update_output(self, text):
        """更新输出框"""
        self.output_box.append(text)
        
    def conversion_finished(self):
        """转换完成"""
        self.output_box.append("所有文件转换完成！")
        self.stop_btn.setEnabled(False)
        self.add_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        QMessageBox.information(self, '完成', '所有文件转换完成！')
        
    def handle_error(self, error_msg):
        """处理错误"""
        self.output_box.append(f"错误: {error_msg}")
        self.stop_btn.setEnabled(False)
        self.add_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        QMessageBox.critical(self, '错误', error_msg)
        
    def dragEnterEvent(self, event):
        """处理拖入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """处理拖动移动事件"""
        event.acceptProposedAction()

    def dropEvent(self, event):
        """处理文件拖放"""
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            
            # 获取拖入的文件/文件夹路径
            for url in event.mimeData().urls():
                # 统一路径格式
                path = os.path.normpath(url.toLocalFile())
                if os.path.isfile(path) and path.lower().endswith(('.tif', '.tiff')):
                    self.file_list.addItem(path)
                elif os.path.isdir(path):
                    # 扫描文件夹下的所有tif文件
                    tif_files = [os.path.normpath(p) for p in self.scan_folder(path)]
                    if tif_files:
                        self.file_list.addItems(tif_files)
                    else:
                        QMessageBox.warning(self, '警告', '拖入的文件夹中没有找到.tif文件')

    def load_layer(self, input_path):
        """在主线程中加载图层"""
        try:
            # 先清理可能存在的旧图层
            if self.conversion_thread and self.conversion_thread.current_layer:
                QgsProject.instance().removeMapLayer(self.conversion_thread.current_layer)
                self.conversion_thread.current_layer = None
                
            # 加载新图层
            layer = QgsRasterLayer(input_path, os.path.basename(input_path))
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                self.conversion_thread.set_current_layer(layer)
                self.conversion_thread.layer_loaded = True
                
                # 输出波段信息
                self.output_box.append("\n文件波段信息：")
                band_count = layer.bandCount()
                for band_num in range(1, band_count + 1):
                    band_name = layer.bandName(band_num)
                    if not band_name:
                        band_name = f'Band_{band_num}'
                    self.output_box.append(f"波段 {band_num}: {band_name}")
            else:
                self.conversion_thread.layer_loaded = False
                raise ValueError(f"无法加载栅格图层: {input_path}")
        except Exception as e:
            self.output_box.append(f"加载图层错误: {str(e)}")
            self.conversion_thread.layer_loaded = False
            self.conversion_thread.error_signal.emit(str(e))
            # 跳过当前文件，继续处理下一个
            self.conversion_thread.progress_signal.emit(
                self.conversion_thread.file_list.index(input_path) + 1
            )
            # 清理可能存在的图层资源
            if self.conversion_thread and self.conversion_thread.current_layer:
                QgsProject.instance().removeMapLayer(self.conversion_thread.current_layer)
                self.conversion_thread.current_layer = None
            
    def remove_layer(self):
        """在主线程中移除图层"""
        if self.conversion_thread and self.conversion_thread.current_layer:
            QgsProject.instance().removeMapLayer(self.conversion_thread.current_layer)
            self.conversion_thread.current_layer = None
        self.conversion_thread.layer_loaded = False
            
    def closeEvent(self, event):
        """关闭窗口时清理 QGIS 环境"""
        if self.conversion_thread:
            if self.conversion_thread.isRunning():
                self.conversion_thread.stop()
                self.conversion_thread.wait(1000)
            # 清理图层资源
            if self.conversion_thread.current_layer:
                QgsProject.instance().removeMapLayer(self.conversion_thread.current_layer)
        # 清理所有图层
        QgsProject.instance().removeAllMapLayers()
        # 退出 QGIS 环境
        self.qgs.exitQgis()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OrthoToSinglebandApp()
    window.show()
    sys.exit(app.exec_())
