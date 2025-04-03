import sys
import os
import fnmatch
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
                            QTextEdit, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.setText(path)
                self.parent().handle_folder_drop(path)

class ClipTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 输入文件夹选择
        input_layout = QHBoxLayout()
        self.input_label = QLabel('输入文件夹:')
        self.input_line = DropLineEdit(self)
        self.input_btn = QPushButton('选择')
        self.input_btn.clicked.connect(self.select_input_folder)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_btn)

        # 输出文件夹
        output_layout = QHBoxLayout()
        self.output_label = QLabel('输出文件夹:')
        self.output_line = QLineEdit()
        self.output_line.setPlaceholderText('自动设置为输入文件夹下的clip子文件夹')
        self.output_line.setStyleSheet('''
            QLineEdit {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
                min-width: 300px;
                color: #666;
            }
        ''')
        self.auto_output_btn = QPushButton('自动生成')
        self.auto_output_btn.clicked.connect(self.auto_generate_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.auto_output_btn)

        # 裁剪文件选择
        clip_layout = QHBoxLayout()
        self.clip_label = QLabel('裁剪矢量文件:')
        self.clip_line = DropLineEdit(self)
        self.clip_btn = QPushButton('选择')
        self.clip_btn.clicked.connect(self.select_clip_file)
        clip_layout.addWidget(self.clip_label)
        clip_layout.addWidget(self.clip_line)
        clip_layout.addWidget(self.clip_btn)

        # 过滤模式
        filter_layout = QHBoxLayout()
        self.filter_label = QLabel('文件过滤模式:')
        self.filter_line = QLineEdit('*.tif')
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_line)

        # 执行按钮
        self.run_btn = QPushButton('执行裁剪')
        self.run_btn.clicked.connect(self.run_clip)

        # 状态栏
        self.status_bar = QTextEdit('准备就绪')
        self.status_bar.setReadOnly(True)
        self.status_bar.setStyleSheet('''
            QTextEdit {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
                font-family: Consolas, monospace;
                font-size: 10pt;
                color: #333;
            }
        ''')
        self.status_bar.setMaximumHeight(150)

        # 添加所有布局
        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(clip_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.run_btn)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.setWindowTitle('栅格裁剪工具')
        self.setGeometry(300, 300, 500, 200)

    def auto_generate_output(self):
        """自动生成输出文件夹"""
        input_folder = self.input_line.text()
        if not input_folder:
            QMessageBox.warning(self, '错误', '请先选择输入文件夹')
            return
            
        output_folder = os.path.join(input_folder, 'clip')
        self.output_line.setText(output_folder.replace('/', '\\'))
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 已创建输出文件夹: {output_folder}')
            else:
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 输出文件夹已存在: {output_folder}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法创建输出文件夹: {str(e)}')

    def handle_folder_drop(self, path):
        """处理文件夹拖放事件"""
        if self.sender() == self.input_line:
            self.input_line.setText(path)
            # 自动填充输出路径
            output_folder = os.path.join(path, 'clip')
            self.output_line.setText(output_folder.replace('/', '\\'))
            
            # 自动扫描.shp文件
            shapefiles = list(self.find_rasters(path, '*.shp'))
            if shapefiles:
                if len(shapefiles) == 1:
                    self.clip_line.setText(shapefiles[0])
                    self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                         f'自动设置输出文件夹: {output_folder}\n'
                                         f'找到并自动选择裁剪文件: {shapefiles[0]}')
                else:
                    # 让用户选择.shp文件
                    selected, ok = QInputDialog.getItem(
                        self, '选择裁剪文件', 
                        '找到多个矢量文件，请选择一个:',
                        shapefiles, 0, False)
                    if ok and selected:
                        self.clip_line.setText(selected)
                        self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                             f'自动设置输出文件夹: {output_folder}\n'
                                             f'用户选择裁剪文件: {selected}')
            else:
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                     f'自动设置输出文件夹: {output_folder}\n'
                                     f'未找到.shp文件')
        elif self.sender() == self.clip_line and path.endswith('.shp'):
            self.clip_line.setText(path)
            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放裁剪文件: {path}')

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择输入文件夹')
        if folder:
            self.input_line.setText(folder)
            # 自动填充输出路径
            output_folder = os.path.join(folder, 'clip')
            self.output_line.setText(output_folder.replace('/', '\\'))
            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 输入文件夹: {folder}\n'
                                 f'已自动填充输出路径: {output_folder}')

    def select_clip_file(self):
        file, _ = QFileDialog.getOpenFileName(self, '选择裁剪矢量文件', 
                                            filter='Shapefiles (*.shp)')
        if file:
            self.clip_line.setText(file)

    def find_rasters(self, path, filter_pattern):
        """查找符合过滤条件的文件"""
        for root, dirs, files in os.walk(path):
            for file in fnmatch.filter(files, filter_pattern):
                yield os.path.join(root, file)

    def run_clip(self):
        """执行裁剪操作"""
        input_folder = self.input_line.text()
        output_folder = self.output_line.text()
        clip_shapefile = self.clip_line.text()
        filter_pattern = self.filter_line.text()

        # 验证输入
        if not all([input_folder, output_folder, clip_shapefile]):
            QMessageBox.warning(self, '输入错误', '请填写所有必填项')
            return

        # 禁用按钮防止重复点击
        self.run_btn.setEnabled(False)
        self.status_bar.setText('正在初始化...')

        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            processed_count = 0
            raster_files = list(self.find_rasters(input_folder, filter_pattern))
            total_files = len(raster_files)
            
            if total_files == 0:
                self.status_bar.setText('未找到匹配的文件')
                QMessageBox.warning(self, '警告', '未找到匹配的文件')
                return

            for i, raster_path in enumerate(raster_files):
                raster_name = os.path.basename(raster_path)
                output_path = os.path.join(output_folder, raster_name)
                
                # 更新状态
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 正在处理 {i+1}/{total_files}\n'
                                     f'输入文件: {raster_path}\n'
                                     f'裁剪文件: {clip_shapefile}\n'
                                     f'输出文件: {output_path}\n'
                                     f'文件名: {raster_name}')
                QApplication.processEvents()  # 更新UI
                
                # 统一路径分隔符
                raster_path_win = raster_path.replace('/', '\\')
                clip_shapefile_win = clip_shapefile.replace('/', '\\')
                output_path_win = output_path.replace('/', '\\')
                cmd = f'gdalwarp -q -cutline {clip_shapefile_win} -crop_to_cutline {raster_path_win} {output_path_win}'
                os.system(cmd)
                processed_count += 1

            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 处理完成\n'
                                 f'总文件数: {total_files}\n'
                                 f'成功处理: {processed_count}\n'
                                 f'输出目录: {output_folder}')
            QMessageBox.information(self, '完成', 
                                  f'成功处理 {processed_count} 个文件')
        except Exception as e:
            current_file = raster_path if 'raster_path' in locals() else 'N/A'
            error_msg = (
                f'[{datetime.now().strftime("%H:%M:%S")}] 处理出错\n'
                f'错误信息: {str(e)}\n'
                f'当前文件: {current_file}'
            )
            self.status_bar.append(error_msg)
            QMessageBox.critical(self, '错误', 
                               f'处理过程中发生错误: {str(e)}')
        finally:
            self.run_btn.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ClipTab()
    gui.show()
    sys.exit(app.exec_())

        # 输出文件夹
        output_layout = QHBoxLayout()
        self.output_label = QLabel('输出文件夹:')
        self.output_line = QLineEdit()
        self.output_line.setPlaceholderText('自动设置为输入文件夹下的clip子文件夹')
        self.output_line.setStyleSheet('''
            QLineEdit {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
                min-width: 300px;
                color: #666;
            }
        ''')
        self.auto_output_btn = QPushButton('自动生成')
        self.auto_output_btn.clicked.connect(self.auto_generate_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.auto_output_btn)

        # 裁剪文件选择
        clip_layout = QHBoxLayout()
        self.clip_label = QLabel('裁剪矢量文件:')
        self.clip_line = DropLineEdit(self)
        self.clip_btn = QPushButton('选择')
        self.clip_btn.clicked.connect(self.select_clip_file)
        clip_layout.addWidget(self.clip_label)
        clip_layout.addWidget(self.clip_line)
        clip_layout.addWidget(self.clip_btn)

        # 过滤模式
        filter_layout = QHBoxLayout()
        self.filter_label = QLabel('文件过滤模式:')
        self.filter_line = QLineEdit('*.tif')
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_line)

        # 执行按钮
        self.run_btn = QPushButton('执行裁剪')
        self.run_btn.clicked.connect(self.run_clip)

        # 状态栏
        self.status_bar = QTextEdit('准备就绪')
        self.status_bar.setReadOnly(True)
        self.status_bar.setStyleSheet('''
            QTextEdit {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
                font-family: Consolas, monospace;
                font-size: 10pt;
                color: #333;
            }
        ''')
        self.status_bar.setMaximumHeight(150)

        # 添加所有布局
        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(clip_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.run_btn)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.setWindowTitle('栅格裁剪工具')
        self.setGeometry(300, 300, 500, 200)

    def auto_generate_output(self):
        """自动生成输出文件夹"""
        input_folder = self.input_line.text()
        if not input_folder:
            QMessageBox.warning(self, '错误', '请先选择输入文件夹')
            return
            
        output_folder = os.path.join(input_folder, 'clip')
        self.output_line.setText(output_folder.replace('/', '\\'))
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 已创建输出文件夹: {output_folder}')
            else:
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 输出文件夹已存在: {output_folder}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法创建输出文件夹: {str(e)}')

    def handle_folder_drop(self, path):
        """处理文件夹拖放事件"""
        if self.sender() == self.input_line:
            self.input_line.setText(path)
            # 自动填充输出路径
            output_folder = os.path.join(path, 'clip')
            self.output_line.setText(output_folder.replace('/', '\\'))
            
            # 自动扫描.shp文件
            shapefiles = list(self.find_rasters(path, '*.shp'))
            if shapefiles:
                if len(shapefiles) == 1:
                    self.clip_line.setText(shapefiles[0])
                    self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                         f'自动设置输出文件夹: {output_folder}\n'
                                         f'找到并自动选择裁剪文件: {shapefiles[0]}')
                else:
                    # 让用户选择.shp文件
                    selected, ok = QInputDialog.getItem(
                        self, '选择裁剪文件', 
                        '找到多个矢量文件，请选择一个:',
                        shapefiles, 0, False)
                    if ok and selected:
                        self.clip_line.setText(selected)
                        self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                             f'自动设置输出文件夹: {output_folder}\n'
                                             f'用户选择裁剪文件: {selected}')
            else:
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                     f'自动设置输出文件夹: {output_folder}\n'
                                     f'未找到.shp文件')
        elif self.sender() == self.clip_line and path.endswith('.shp'):
            self.clip_line.setText(path)
            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放裁剪文件: {path}')

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择输入文件夹')
        if folder:
            self.input_line.setText(folder)
            # 自动填充输出路径
            output_folder = os.path.join(folder, 'clip')
            self.output_line.setText(output_folder.replace('/', '\\'))
            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 输入文件夹: {folder}\n'
                                 f'已自动填充输出路径: {output_folder}')

    def select_clip_file(self):
        file, _ = QFileDialog.getOpenFileName(self, '选择裁剪矢量文件', 
                                            filter='Shapefiles (*.shp)')
        if file:
            self.clip_line.setText(file)

    def find_rasters(self, path, filter_pattern):
        """查找符合过滤条件的文件"""
        for root, dirs, files in os.walk(path):
            for file in fnmatch.filter(files, filter_pattern):
                yield os.path.join(root, file)

    def run_clip(self):
        """执行裁剪操作"""
        input_folder = self.input_line.text()
        output_folder = self.output_line.text()
        clip_shapefile = self.clip_line.text()
        filter_pattern = self.filter_line.text()

        # 验证输入
        if not all([input_folder, output_folder, clip_shapefile]):
            QMessageBox.warning(self, '输入错误', '请填写所有必填项')
            return

        # 禁用按钮防止重复点击
        self.run_btn.setEnabled(False)
        self.status_bar.setText('正在初始化...')

        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            processed_count = 0
            raster_files = list(self.find_rasters(input_folder, filter_pattern))
            total_files = len(raster_files)
            
            if total_files == 0:
                self.status_bar.setText('未找到匹配的文件')
                QMessageBox.warning(self, '警告', '未找到匹配的文件')
                return

            for i, raster_path in enumerate(raster_files):
                raster_name = os.path.basename(raster_path)
                output_path = os.path.join(output_folder, raster_name)
                
                # 更新状态
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 正在处理 {i+1}/{total_files}\n'
                                     f'输入文件: {raster_path}\n'
                                     f'裁剪文件: {clip_shapefile}\n'
                                     f'输出文件: {output_path}\n'
                                     f'文件名: {raster_name}')
                QApplication.processEvents()  # 更新UI
                
                # 统一路径分隔符
                raster_path_win = raster_path.replace('/', '\\')
                clip_shapefile_win = clip_shapefile.replace('/', '\\')
                output_path_win = output_path.replace('/', '\\')
                cmd = f'gdalwarp -q -cutline {clip_shapefile_win} -crop_to_cutline {raster_path_win} {output_path_win}'
                os.system(cmd)
                processed_count += 1

            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 处理完成\n'
                                 f'总文件数: {total_files}\n'
                                 f'成功处理: {processed_count}\n'
                                 f'输出目录: {output_folder}')
            QMessageBox.information(self, '完成', 
                                  f'成功处理 {processed_count} 个文件')
        except Exception as e:
            current_file = raster_path if 'raster_path' in locals() else 'N/A'
            error_msg = (
                f'[{datetime.now().strftime("%H:%M:%S")}] 处理出错\n'
                f'错误信息: {str(e)}\n'
                f'当前文件: {current_file}'
            )
            self.status_bar.append(error_msg)
import sys
import os
import fnmatch
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
                            QTextEdit, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.setText(path)
                self.parent().handle_folder_drop(path)

class ClipTab(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.initUI()
        self.apply_style()

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 主题切换按钮
        theme_layout = QHBoxLayout()
        self.theme_btn = QPushButton('🌙 切换主题')
        self.theme_btn.clicked.connect(self.toggle_theme)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_btn)
        main_layout.addLayout(theme_layout)

        # 输入文件夹选择
        input_layout = QHBoxLayout()
        self.input_label = QLabel('📁 输入文件夹:')
        self.input_line = DropLineEdit(self)
        self.input_btn = QPushButton('📂 选择')
        self.input_btn.setToolTip('选择包含栅格文件的文件夹')
        self.input_btn.clicked.connect(self.select_input_folder)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_btn)

        # 输出文件夹
        output_layout = QHBoxLayout()
        self.output_label = QLabel('📂 输出文件夹:')
        self.output_line = QLineEdit()
        self.output_line.setPlaceholderText('自动设置为输入文件夹下的clip子文件夹')
        self.auto_output_btn = QPushButton('⚙️ 自动生成')
        self.auto_output_btn.setToolTip('自动创建输出文件夹')
        self.auto_output_btn.clicked.connect(self.auto_generate_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.auto_output_btn)

        # 裁剪文件选择
        clip_layout = QHBoxLayout()
        self.clip_label = QLabel('✂️ 裁剪矢量文件:')
        self.clip_line = DropLineEdit(self)
        self.clip_btn = QPushButton('📂 选择')
        self.clip_btn.setToolTip('选择用于裁剪的矢量文件')
        self.clip_btn.clicked.connect(self.select_clip_file)
        clip_layout.addWidget(self.clip_label)
        clip_layout.addWidget(self.clip_line)
        clip_layout.addWidget(self.clip_btn)

        # 过滤模式
        filter_layout = QHBoxLayout()
        self.filter_label = QLabel('🔍 文件过滤模式:')
        self.filter_line = QLineEdit('*.tif')
        self.filter_line.setToolTip('使用通配符过滤文件，例如 *.tif, *.img')
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_line)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # 执行按钮
        self.run_btn = QPushButton('🚀 执行裁剪')
        self.run_btn.setToolTip('开始裁剪处理')
        self.run_btn.clicked.connect(self.run_clip)

        # 状态栏
        self.status_bar = QTextEdit('🟢 准备就绪')
        self.status_bar.setReadOnly(True)
        self.status_bar.setMaximumHeight(150)

        # 添加所有布局
        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(clip_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.run_btn)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.setWindowTitle('🌍 栅格裁剪工具')
        self.setMinimumSize(600, 400)

    def apply_style(self):
        """应用样式表"""
        if self.dark_mode:
            style = '''
                QWidget {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QLineEdit, QTextEdit {
                    background-color: #3d3d3d;
                    border: 1px solid #555;
                    padding: 5px;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QProgressBar {
                    background-color: #3d3d3d;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 3px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    width: 10px;
                }
            '''
        else:
            style = '''
                QWidget {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QLineEdit, QTextEdit {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    padding: 5px;
                    color: #333333;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QProgressBar {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    width: 10px;
                }
            '''
        self.setStyleSheet(style)

    def toggle_theme(self):
        """切换主题"""
        self.dark_mode = not self.dark_mode
        self.theme_btn.setText('🌞 切换主题' if self.dark_mode else '🌙 切换主题')
        self.apply_style()

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        QApplication.processEvents()

    def log_message(self, message, type='info'):
        """记录状态信息"""
        if type == 'error':
            prefix = '🔴'
            color = '#ff4444' if self.dark_mode else '#cc0000'
        elif type == 'warning':
            prefix = '🟡'
            color = '#ffcc00' if self.dark_mode else '#ff8800'
        else:
            prefix = '🟢'
            color = '#4CAF50' if self.dark_mode else '#45a049'
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.append(f'<span style="color:{color}">[{timestamp}] {prefix} {message}</span>')
        QApplication.processEvents()
>>>>>>> REPLACE>
import sys
import os
import fnmatch
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
                            QTextEdit, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.setText(path)
                self.parent().handle_folder_drop(path)

class ClipTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 输入文件夹选择
        input_layout = QHBoxLayout()
        self.input_label = QLabel('输入文件夹:')
        self.input_line = DropLineEdit(self)
        self.input_btn = QPushButton('选择')
        self.input_btn.clicked.connect(self.select_input_folder)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_btn)

        # 输出文件夹
        output_layout = QHBoxLayout()
        self.output_label = QLabel('输出文件夹:')
        self.output_line = QLineEdit()
        self.output_line.setPlaceholderText('自动设置为输入文件夹下的clip子文件夹')
        self.output_line.setStyleSheet('''
            QLineEdit {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
                min-width: 300px;
                color: #666;
            }
        ''')
        self.auto_output_btn = QPushButton('自动生成')
        self.auto_output_btn.clicked.connect(self.auto_generate_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.auto_output_btn)

        # 裁剪文件选择
        clip_layout = QHBoxLayout()
        self.clip_label = QLabel('裁剪矢量文件:')
        self.clip_line = DropLineEdit(self)
        self.clip_btn = QPushButton('选择')
        self.clip_btn.clicked.connect(self.select_clip_file)
        clip_layout.addWidget(self.clip_label)
        clip_layout.addWidget(self.clip_line)
        clip_layout.addWidget(self.clip_btn)

        # 过滤模式
        filter_layout = QHBoxLayout()
        self.filter_label = QLabel('文件过滤模式:')
        self.filter_line = QLineEdit('*.tif')
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_line)

        # 执行按钮
        self.run_btn = QPushButton('执行裁剪')
        self.run_btn.clicked.connect(self.run_clip)

        # 状态栏
        self.status_bar = QTextEdit('准备就绪')
        self.status_bar.setReadOnly(True)
        self.status_bar.setStyleSheet('''
            QTextEdit {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
                font-family: Consolas, monospace;
                font-size: 10pt;
                color: #333;
            }
        ''')
        self.status_bar.setMaximumHeight(150)

        # 添加所有布局
        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(clip_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.run_btn)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.setWindowTitle('栅格裁剪工具')
        self.setGeometry(300, 300, 500, 200)

    def auto_generate_output(self):
        """自动生成输出文件夹"""
        input_folder = self.input_line.text()
        if not input_folder:
            QMessageBox.warning(self, '错误', '请先选择输入文件夹')
            return
            
        output_folder = os.path.join(input_folder, 'clip')
        self.output_line.setText(output_folder.replace('/', '\\'))
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 已创建输出文件夹: {output_folder}')
            else:
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 输出文件夹已存在: {output_folder}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法创建输出文件夹: {str(e)}')

    def handle_folder_drop(self, path):
        """处理文件夹拖放事件"""
        if self.sender() == self.input_line:
            self.input_line.setText(path)
            # 自动填充输出路径
            output_folder = os.path.join(path, 'clip')
            self.output_line.setText(output_folder.replace('/', '\\'))
            
            # 自动扫描.shp文件
            shapefiles = list(self.find_rasters(path, '*.shp'))
            if shapefiles:
                if len(shapefiles) == 1:
                    self.clip_line.setText(shapefiles[0])
                    self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                         f'自动设置输出文件夹: {output_folder}\n'
                                         f'找到并自动选择裁剪文件: {shapefiles[0]}')
                else:
                    # 让用户选择.shp文件
                    selected, ok = QInputDialog.getItem(
                        self, '选择裁剪文件', 
                        '找到多个矢量文件，请选择一个:',
                        shapefiles, 0, False)
                    if ok and selected:
                        self.clip_line.setText(selected)
                        self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                             f'自动设置输出文件夹: {output_folder}\n'
                                             f'用户选择裁剪文件: {selected}')
            else:
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                     f'自动设置输出文件夹: {output_folder}\n'
                                     f'未找到.shp文件')
        elif self.sender() == self.clip_line and path.endswith('.shp'):
            self.clip_line.setText(path)
            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放裁剪文件: {path}')

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择输入文件夹')
        if folder:
            self.input_line.setText(folder)
            # 自动填充输出路径
            output_folder = os.path.join(folder, 'clip')
            self.output_line.setText(output_folder.replace('/', '\\'))
            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 输入文件夹: {folder}\n'
                                 f'已自动填充输出路径: {output_folder}')

    def select_clip_file(self):
        file, _ = QFileDialog.getOpenFileName(self, '选择裁剪矢量文件', 
                                            filter='Shapefiles (*.shp)')
        if file:
            self.clip_line.setText(file)

    def find_rasters(self, path, filter_pattern):
        """查找符合过滤条件的文件"""
        for root, dirs, files in os.walk(path):
            for file in fnmatch.filter(files, filter_pattern):
                yield os.path.join(root, file)

    def run_clip(self):
        """执行裁剪操作"""
        input_folder = self.input_line.text()
        output_folder = self.output_line.text()
        clip_shapefile = self.clip_line.text()
        filter_pattern = self.filter_line.text()

        # 验证输入
        if not all([input_folder, output_folder, clip_shapefile]):
            QMessageBox.warning(self, '输入错误', '请填写所有必填项')
            return

        # 禁用按钮防止重复点击
        self.run_btn.setEnabled(False)
        self.status_bar.setText('正在初始化...')

        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            processed_count = 0
            raster_files = list(self.find_rasters(input_folder, filter_pattern))
            total_files = len(raster_files)
            
            if total_files == 0:
                self.status_bar.setText('未找到匹配的文件')
                QMessageBox.warning(self, '警告', '未找到匹配的文件')
                return

            for i, raster_path in enumerate(raster_files):
                raster_name = os.path.basename(raster_path)
                output_path = os.path.join(output_folder, raster_name)
                
                # 更新状态
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 正在处理 {i+1}/{total_files}\n'
                                     f'输入文件: {raster_path}\n'
                                     f'裁剪文件: {clip_shapefile}\n'
                                     f'输出文件: {output_path}\n'
                                     f'文件名: {raster_name}')
                QApplication.processEvents()  # 更新UI
                
                # 统一路径分隔符
                raster_path_win = raster_path.replace('/', '\\')
                clip_shapefile_win = clip_shapefile.replace('/', '\\')
                output_path_win = output_path.replace('/', '\\')
                cmd = f'gdalwarp -q -cutline {clip_shapefile_win} -crop_to_cutline {raster_path_win} {output_path_win}'
                os.system(cmd)
                processed_count += 1

            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 处理完成\n'
                                 f'总文件数: {total_files}\n'
                                 f'成功处理: {processed_count}\n'
                                 f'输出目录: {output_folder}')
            QMessageBox.information(self, '完成', 
                                  f'成功处理 {processed_count} 个文件')
        except Exception as e:
            current_file = raster_path if 'raster_path' in locals() else 'N/A'
            error_msg = (
                f'[{datetime.now().strftime("%H:%M:%S")}] 处理出错\n'
                f'错误信息: {str(e)}\n'
                f'当前文件: {current_file}'
            )
            self.status_bar.append(error_msg)
import sys
import os
import fnmatch
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
                            QTextEdit, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.setText(path)
                self.parent().handle_folder_drop(path)

class ClipTab(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.initUI()
        self.apply_style()

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 主题切换按钮
        theme_layout = QHBoxLayout()
        self.theme_btn = QPushButton('🌙 切换主题')
        self.theme_btn.clicked.connect(self.toggle_theme)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_btn)
        main_layout.addLayout(theme_layout)

        # 输入文件夹选择
        input_layout = QHBoxLayout()
        self.input_label = QLabel('📁 输入文件夹:')
        self.input_line = DropLineEdit(self)
        self.input_btn = QPushButton('📂 选择')
        self.input_btn.setToolTip('选择包含栅格文件的文件夹')
        self.input_btn.clicked.connect(self.select_input_folder)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_btn)

        # 输出文件夹
        output_layout = QHBoxLayout()
        self.output_label = QLabel('📂 输出文件夹:')
        self.output_line = QLineEdit()
        self.output_line.setPlaceholderText('自动设置为输入文件夹下的clip子文件夹')
        self.auto_output_btn = QPushButton('⚙️ 自动生成')
        self.auto_output_btn.setToolTip('自动创建输出文件夹')
        self.auto_output_btn.clicked.connect(self.auto_generate_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.auto_output_btn)

        # 裁剪文件选择
        clip_layout = QHBoxLayout()
        self.clip_label = QLabel('✂️ 裁剪矢量文件:')
        self.clip_line = DropLineEdit(self)
        self.clip_btn = QPushButton('📂 选择')
        self.clip_btn.setToolTip('选择用于裁剪的矢量文件')
        self.clip_btn.clicked.connect(self.select_clip_file)
        clip_layout.addWidget(self.clip_label)
        clip_layout.addWidget(self.clip_line)
        clip_layout.addWidget(self.clip_btn)

        # 过滤模式
        filter_layout = QHBoxLayout()
        self.filter_label = QLabel('🔍 文件过滤模式:')
        self.filter_line = QLineEdit('*.tif')
        self.filter_line.setToolTip('使用通配符过滤文件，例如 *.tif, *.img')
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_line)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # 执行按钮
        self.run_btn = QPushButton('🚀 执行裁剪')
        self.run_btn.setToolTip('开始裁剪处理')
        self.run_btn.clicked.connect(self.run_clip)

        # 状态栏
        self.status_bar = QTextEdit('🟢 准备就绪')
        self.status_bar.setReadOnly(True)
        self.status_bar.setMaximumHeight(150)

        # 添加所有布局
        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(clip_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.run_btn)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.setWindowTitle('🌍 栅格裁剪工具')
        self.setMinimumSize(600, 400)

    def apply_style(self):
        """应用样式表"""
        if self.dark_mode:
            style = '''
                QWidget {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QLineEdit, QTextEdit {
                    background-color: #3d3d3d;
                    border: 1px solid #555;
                    padding: 5px;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QProgressBar {
                    background-color: #3d3d3d;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 3px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    width: 10px;
                }
            '''
        else:
            style = '''
                QWidget {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QLineEdit, QTextEdit {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    padding: 5px;
                    color: #333333;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QProgressBar {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    width: 10px;
                }
            '''
        self.setStyleSheet(style)

    def toggle_theme(self):
        """切换主题"""
        self.dark_mode = not self.dark_mode
        self.theme_btn.setText('🌞 切换主题' if self.dark_mode else '🌙 切换主题')
        self.apply_style()

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        QApplication.processEvents()

    def log_message(self, message, type='info'):
        """记录状态信息"""
        if type == 'error':
            prefix = '🔴'
            color = '#ff4444' if self.dark_mode else '#cc0000'
        elif type == 'warning':
            prefix = '🟡'
            color = '#ffcc00' if self.dark_mode else '#ff8800'
        else:
            prefix = '🟢'
            color = '#4CAF50' if self.dark_mode else '#45a049'
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.append(f'<span style="color:{color}">[{timestamp}] {prefix} {message}</span>')
        QApplication.processEvents()
>>>>>>> REPLACE>
import sys
import os
import fnmatch
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
                            QTextEdit, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.setText(path)
                self.parent().handle_folder_drop(path)

class ClipTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 输入文件夹选择
        input_layout = QHBoxLayout()
        self.input_label = QLabel('输入文件夹:')
        self.input_line = DropLineEdit(self)
        self.input_btn = QPushButton('选择')
        self.input_btn.clicked.connect(self.select_input_folder)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_btn)

        # 输出文件夹
        output_layout = QHBoxLayout()
        self.output_label = QLabel('输出文件夹:')
        self.output_line = QLineEdit()
        self.output_line.setPlaceholderText('自动设置为输入文件夹下的clip子文件夹')
        self.output_line.setStyleSheet('''
            QLineEdit {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
                min-width: 300px;
                color: #666;
            }
        ''')
        self.auto_output_btn = QPushButton('自动生成')
        self.auto_output_btn.clicked.connect(self.auto_generate_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.auto_output_btn)

        # 裁剪文件选择
        clip_layout = QHBoxLayout()
        self.clip_label = QLabel('裁剪矢量文件:')
        self.clip_line = DropLineEdit(self)
        self.clip_btn = QPushButton('选择')
        self.clip_btn.clicked.connect(self.select_clip_file)
        clip_layout.addWidget(self.clip_label)
        clip_layout.addWidget(self.clip_line)
        clip_layout.addWidget(self.clip_btn)

        # 过滤模式
        filter_layout = QHBoxLayout()
        self.filter_label = QLabel('文件过滤模式:')
        self.filter_line = QLineEdit('*.tif')
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_line)

        # 执行按钮
        self.run_btn = QPushButton('执行裁剪')
        self.run_btn.clicked.connect(self.run_clip)

        # 状态栏
        self.status_bar = QTextEdit('准备就绪')
        self.status_bar.setReadOnly(True)
        self.status_bar.setStyleSheet('''
            QTextEdit {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
                font-family: Consolas, monospace;
                font-size: 10pt;
                color: #333;
            }
        ''')
        self.status_bar.setMaximumHeight(150)

        # 添加所有布局
        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(clip_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.run_btn)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.setWindowTitle('栅格裁剪工具')
        self.setGeometry(300, 300, 500, 200)

    def auto_generate_output(self):
        """自动生成输出文件夹"""
        input_folder = self.input_line.text()
        if not input_folder:
            QMessageBox.warning(self, '错误', '请先选择输入文件夹')
            return
            
        output_folder = os.path.join(input_folder, 'clip')
        self.output_line.setText(output_folder.replace('/', '\\'))
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 已创建输出文件夹: {output_folder}')
            else:
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 输出文件夹已存在: {output_folder}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法创建输出文件夹: {str(e)}')

    def handle_folder_drop(self, path):
        """处理文件夹拖放事件"""
        if self.sender() == self.input_line:
            self.input_line.setText(path)
            # 自动填充输出路径
            output_folder = os.path.join(path, 'clip')
            self.output_line.setText(output_folder.replace('/', '\\'))
            
            # 自动扫描.shp文件
            shapefiles = list(self.find_rasters(path, '*.shp'))
            if shapefiles:
                if len(shapefiles) == 1:
                    self.clip_line.setText(shapefiles[0])
                    self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                         f'自动设置输出文件夹: {output_folder}\n'
                                         f'找到并自动选择裁剪文件: {shapefiles[0]}')
                else:
                    # 让用户选择.shp文件
                    selected, ok = QInputDialog.getItem(
                        self, '选择裁剪文件', 
                        '找到多个矢量文件，请选择一个:',
                        shapefiles, 0, False)
                    if ok and selected:
                        self.clip_line.setText(selected)
                        self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                             f'自动设置输出文件夹: {output_folder}\n'
                                             f'用户选择裁剪文件: {selected}')
            else:
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                     f'自动设置输出文件夹: {output_folder}\n'
                                     f'未找到.shp文件')
        elif self.sender() == self.clip_line and path.endswith('.shp'):
            self.clip_line.setText(path)
            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放裁剪文件: {path}')

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择输入文件夹')
        if folder:
            self.input_line.setText(folder)
            # 自动填充输出路径
            output_folder = os.path.join(folder, 'clip')
            self.output_line.setText(output_folder.replace('/', '\\'))
            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 输入文件夹: {folder}\n'
                                 f'已自动填充输出路径: {output_folder}')

    def select_clip_file(self):
        file, _ = QFileDialog.getOpenFileName(self, '选择裁剪矢量文件', 
                                            filter='Shapefiles (*.shp)')
        if file:
            self.clip_line.setText(file)

    def find_rasters(self, path, filter_pattern):
        """查找符合过滤条件的文件"""
        for root, dirs, files in os.walk(path):
            for file in fnmatch.filter(files, filter_pattern):
                yield os.path.join(root, file)

    def run_clip(self):
        """执行裁剪操作"""
        input_folder = self.input_line.text()
        output_folder = self.output_line.text()
        clip_shapefile = self.clip_line.text()
        filter_pattern = self.filter_line.text()

        # 验证输入
        if not all([input_folder, output_folder, clip_shapefile]):
            QMessageBox.warning(self, '输入错误', '请填写所有必填项')
            return

        # 禁用按钮防止重复点击
        self.run_btn.setEnabled(False)
        self.status_bar.setText('正在初始化...')

        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            processed_count = 0
            raster_files = list(self.find_rasters(input_folder, filter_pattern))
            total_files = len(raster_files)
            
            if total_files == 0:
                self.status_bar.setText('未找到匹配的文件')
                QMessageBox.warning(self, '警告', '未找到匹配的文件')
                return

            for i, raster_path in enumerate(raster_files):
                raster_name = os.path.basename(raster_path)
                output_path = os.path.join(output_folder, raster_name)
                
                # 更新状态
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 正在处理 {i+1}/{total_files}\n'
                                     f'输入文件: {raster_path}\n'
                                     f'裁剪文件: {clip_shapefile}\n'
                                     f'输出文件: {output_path}\n'
                                     f'文件名: {raster_name}')
                QApplication.processEvents()  # 更新UI
                
                # 统一路径分隔符
                raster_path_win = raster_path.replace('/', '\\')
                clip_shapefile_win = clip_shapefile.replace('/', '\\')
                output_path_win = output_path.replace('/', '\\')
                cmd = f'gdalwarp -q -cutline {clip_shapefile_win} -crop_to_cutline {raster_path_win} {output_path_win}'
                os.system(cmd)
                processed_count += 1

            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 处理完成\n'
                                 f'总文件数: {total_files}\n'
                                 f'成功处理: {processed_count}\n'
                                 f'输出目录: {output_folder}')
            QMessageBox.information(self, '完成', 
                                  f'成功处理 {processed_count} 个文件')
        except Exception as e:
            current_file = raster_path if 'raster_path' in locals() else 'N/A'
            error_msg = (
                f'[{datetime.now().strftime("%H:%M:%S")}] 处理出错\n'
                f'错误信息: {str(e)}\n'
                f'当前文件: {current_file}'
            )
            self.status_bar.append(error_msg)
import sys
import os
import fnmatch
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
                            QTextEdit, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.setText(path)
                self.parent().handle_folder_drop(path)

class ClipTab(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.initUI()
        self.apply_style()

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 主题切换按钮
        theme_layout = QHBoxLayout()
        self.theme_btn = QPushButton('🌙 切换主题')
        self.theme_btn.clicked.connect(self.toggle_theme)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_btn)
        main_layout.addLayout(theme_layout)

        # 输入文件夹选择
        input_layout = QHBoxLayout()
        self.input_label = QLabel('📁 输入文件夹:')
        self.input_line = DropLineEdit(self)
        self.input_btn = QPushButton('📂 选择')
        self.input_btn.setToolTip('选择包含栅格文件的文件夹')
        self.input_btn.clicked.connect(self.select_input_folder)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_btn)

        # 输出文件夹
        output_layout = QHBoxLayout()
        self.output_label = QLabel('📂 输出文件夹:')
        self.output_line = QLineEdit()
        self.output_line.setPlaceholderText('自动设置为输入文件夹下的clip子文件夹')
        self.auto_output_btn = QPushButton('⚙️ 自动生成')
        self.auto_output_btn.setToolTip('自动创建输出文件夹')
        self.auto_output_btn.clicked.connect(self.auto_generate_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.auto_output_btn)

        # 裁剪文件选择
        clip_layout = QHBoxLayout()
        self.clip_label = QLabel('✂️ 裁剪矢量文件:')
        self.clip_line = DropLineEdit(self)
        self.clip_btn = QPushButton('📂 选择')
        self.clip_btn.setToolTip('选择用于裁剪的矢量文件')
        self.clip_btn.clicked.connect(self.select_clip_file)
        clip_layout.addWidget(self.clip_label)
        clip_layout.addWidget(self.clip_line)
        clip_layout.addWidget(self.clip_btn)

        # 过滤模式
        filter_layout = QHBoxLayout()
        self.filter_label = QLabel('🔍 文件过滤模式:')
        self.filter_line = QLineEdit('*.tif')
        self.filter_line.setToolTip('使用通配符过滤文件，例如 *.tif, *.img')
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_line)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # 执行按钮
        self.run_btn = QPushButton('🚀 执行裁剪')
        self.run_btn.setToolTip('开始裁剪处理')
        self.run_btn.clicked.connect(self.run_clip)

        # 状态栏
        self.status_bar = QTextEdit('🟢 准备就绪')
        self.status_bar.setReadOnly(True)
        self.status_bar.setMaximumHeight(150)

        # 添加所有布局
        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(clip_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.run_btn)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.setWindowTitle('🌍 栅格裁剪工具')
        self.setMinimumSize(600, 400)

    def apply_style(self):
        """应用样式表"""
        if self.dark_mode:
            style = '''
                QWidget {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QLineEdit, QTextEdit {
                    background-color: #3d3d3d;
                    border: 1px solid #555;
                    padding: 5px;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QProgressBar {
                    background-color: #3d3d3d;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 3px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    width: 10px;
                }
            '''
        else:
            style = '''
                QWidget {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QLineEdit, QTextEdit {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    padding: 5px;
                    color: #333333;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QProgressBar {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    width: 10px;
                }
            '''
        self.setStyleSheet(style)

    def toggle_theme(self):
        """切换主题"""
        self.dark_mode = not self.dark_mode
        self.theme_btn.setText('🌞 切换主题' if self.dark_mode else '🌙 切换主题')
        self.apply_style()

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        QApplication.processEvents()

    def log_message(self, message, type='info'):
        """记录状态信息"""
        if type == 'error':
            prefix = '🔴'
            color = '#ff4444' if self.dark_mode else '#cc0000'
        elif type == 'warning':
            prefix = '🟡'
            color = '#ffcc00' if self.dark_mode else '#ff8800'
        else:
            prefix = '🟢'
            color = '#4CAF50' if self.dark_mode else '#45a049'
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.append(f'<span style="color:{color}">[{timestamp}] {prefix} {message}</span>')
        QApplication.processEvents()
>>>>>>> REPLACE>
import sys
import os
import fnmatch
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
                            QTextEdit, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.setText(path)
                self.parent().handle_folder_drop(path)

class ClipTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 输入文件夹选择
        input_layout = QHBoxLayout()
        self.input_label = QLabel('输入文件夹:')
        self.input_line = DropLineEdit(self)
        self.input_btn = QPushButton('选择')
        self.input_btn.clicked.connect(self.select_input_folder)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_btn)

        # 输出文件夹
        output_layout = QHBoxLayout()
        self.output_label = QLabel('输出文件夹:')
        self.output_line = QLineEdit()
        self.output_line.setPlaceholderText('自动设置为输入文件夹下的clip子文件夹')
        self.output_line.setStyleSheet('''
            QLineEdit {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
                min-width: 300px;
                color: #666;
            }
        ''')
        self.auto_output_btn = QPushButton('自动生成')
        self.auto_output_btn.clicked.connect(self.auto_generate_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.auto_output_btn)

        # 裁剪文件选择
        clip_layout = QHBoxLayout()
        self.clip_label = QLabel('裁剪矢量文件:')
        self.clip_line = DropLineEdit(self)
        self.clip_btn = QPushButton('选择')
        self.clip_btn.clicked.connect(self.select_clip_file)
        clip_layout.addWidget(self.clip_label)
        clip_layout.addWidget(self.clip_line)
        clip_layout.addWidget(self.clip_btn)

        # 过滤模式
        filter_layout = QHBoxLayout()
        self.filter_label = QLabel('文件过滤模式:')
        self.filter_line = QLineEdit('*.tif')
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_line)

        # 执行按钮
        self.run_btn = QPushButton('执行裁剪')
        self.run_btn.clicked.connect(self.run_clip)

        # 状态栏
        self.status_bar = QTextEdit('准备就绪')
        self.status_bar.setReadOnly(True)
        self.status_bar.setStyleSheet('''
            QTextEdit {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
                font-family: Consolas, monospace;
                font-size: 10pt;
                color: #333;
            }
        ''')
        self.status_bar.setMaximumHeight(150)

        # 添加所有布局
        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(clip_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.run_btn)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.setWindowTitle('栅格裁剪工具')
        self.setGeometry(300, 300, 500, 200)

    def auto_generate_output(self):
        """自动生成输出文件夹"""
        input_folder = self.input_line.text()
        if not input_folder:
            QMessageBox.warning(self, '错误', '请先选择输入文件夹')
            return
            
        output_folder = os.path.join(input_folder, 'clip')
        self.output_line.setText(output_folder.replace('/', '\\'))
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 已创建输出文件夹: {output_folder}')
            else:
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 输出文件夹已存在: {output_folder}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法创建输出文件夹: {str(e)}')

    def handle_folder_drop(self, path):
        """处理文件夹拖放事件"""
        if self.sender() == self.input_line:
            self.input_line.setText(path)
            # 自动填充输出路径
            output_folder = os.path.join(path, 'clip')
            self.output_line.setText(output_folder.replace('/', '\\'))
            
            # 自动扫描.shp文件
            shapefiles = list(self.find_rasters(path, '*.shp'))
            if shapefiles:
                if len(shapefiles) == 1:
                    self.clip_line.setText(shapefiles[0])
                    self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                         f'自动设置输出文件夹: {output_folder}\n'
                                         f'找到并自动选择裁剪文件: {shapefiles[0]}')
                else:
                    # 让用户选择.shp文件
                    selected, ok = QInputDialog.getItem(
                        self, '选择裁剪文件', 
                        '找到多个矢量文件，请选择一个:',
                        shapefiles, 0, False)
                    if ok and selected:
                        self.clip_line.setText(selected)
                        self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                             f'自动设置输出文件夹: {output_folder}\n'
                                             f'用户选择裁剪文件: {selected}')
            else:
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放输入文件夹: {path}\n'
                                     f'自动设置输出文件夹: {output_folder}\n'
                                     f'未找到.shp文件')
        elif self.sender() == self.clip_line and path.endswith('.shp'):
            self.clip_line.setText(path)
            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 拖放裁剪文件: {path}')

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择输入文件夹')
        if folder:
            self.input_line.setText(folder)
            # 自动填充输出路径
            output_folder = os.path.join(folder, 'clip')
            self.output_line.setText(output_folder.replace('/', '\\'))
            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 输入文件夹: {folder}\n'
                                 f'已自动填充输出路径: {output_folder}')

    def select_clip_file(self):
        file, _ = QFileDialog.getOpenFileName(self, '选择裁剪矢量文件', 
                                            filter='Shapefiles (*.shp)')
        if file:
            self.clip_line.setText(file)

    def find_rasters(self, path, filter_pattern):
        """查找符合过滤条件的文件"""
        for root, dirs, files in os.walk(path):
            for file in fnmatch.filter(files, filter_pattern):
                yield os.path.join(root, file)

    def run_clip(self):
        """执行裁剪操作"""
        input_folder = self.input_line.text()
        output_folder = self.output_line.text()
        clip_shapefile = self.clip_line.text()
        filter_pattern = self.filter_line.text()

        # 验证输入
        if not all([input_folder, output_folder, clip_shapefile]):
            QMessageBox.warning(self, '输入错误', '请填写所有必填项')
            return

        # 禁用按钮防止重复点击
        self.run_btn.setEnabled(False)
        self.status_bar.setText('正在初始化...')

        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            processed_count = 0
            raster_files = list(self.find_rasters(input_folder, filter_pattern))
            total_files = len(raster_files)
            
            if total_files == 0:
                self.status_bar.setText('未找到匹配的文件')
                QMessageBox.warning(self, '警告', '未找到匹配的文件')
                return

            for i, raster_path in enumerate(raster_files):
                raster_name = os.path.basename(raster_path)
                output_path = os.path.join(output_folder, raster_name)
                
                # 更新状态
                self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 正在处理 {i+1}/{total_files}\n'
                                     f'输入文件: {raster_path}\n'
                                     f'裁剪文件: {clip_shapefile}\n'
                                     f'输出文件: {output_path}\n'
                                     f'文件名: {raster_name}')
                QApplication.processEvents()  # 更新UI
                
                # 统一路径分隔符
                raster_path_win = raster_path.replace('/', '\\')
                clip_shapefile_win = clip_shapefile.replace('/', '\\')
                output_path_win = output_path.replace('/', '\\')
                cmd = f'gdalwarp -q -cutline {clip_shapefile_win} -crop_to_cutline {raster_path_win} {output_path_win}'
                os.system(cmd)
                processed_count += 1

            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 处理完成\n'
                                 f'总文件数: {total_files}\n'
                                 f'成功处理: {processed_count}\n'
                                 f'输出目录: {output_folder}')
            QMessageBox.information(self, '完成', 
                                  f'成功处理 {processed_count} 个文件')
        except Exception as e:
            current_file = raster_path if 'raster_path' in locals() else 'N/A'
            self.status_bar.append(f'[{datetime.now().strftime("%H:%M:%S")}] 处理出错\n'
                                 f'错误信息: {str(e)}\n'
                                 f'当前文件: {current_file}')
            QMessageBox.critical(self, '错误', 
                               f'处理过程中发生错误: {str(e)}')
        finally:
            self.run_btn.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ClipTab()
    gui.show()
    sys.exit(app.exec_())
