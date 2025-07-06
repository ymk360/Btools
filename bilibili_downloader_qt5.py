import sys
import os
import clipboard
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFrame, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QWidget, QLineEdit, QLabel, QProgressBar, QListWidget,
    QListWidgetItem, QFileDialog, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class DownloadTask(QThread):
    progress_updated = pyqtSignal(object, int, str)
    finished = pyqtSignal(object, dict)

    def __init__(self, api, bvid, cid, title, save_path):
        super().__init__()
        self.api = api
        self.bvid = bvid
        self.cid = cid
        self.title = title
        self.save_path = save_path
        self.task_item = None
        self.progress_bar = None
        self.status_label = None

    def run(self):
        def progress_callback(message):
            # 解析进度信息
            if '下载进度:' in message:
                try:
                    progress_str = message.split(' - ')[1]
                    progress = float(progress_str.replace('%', ''))
                    self.progress_updated.emit(self, int(progress), message)
                except:
                    self.progress_updated.emit(self, 0, message)
            else:
                self.progress_updated.emit(self, 0, message)

        result = self.api.download_video(
            self.bvid,
            self.save_path,
            progress_callback=progress_callback
        )
        self.finished.emit(self, result)

class ApiWorker(QThread):
    result_ready = pyqtSignal(dict)  # 自定义信号用于传递结果
    finished = pyqtSignal(dict)

    def __init__(self, api, video_id):
        super().__init__()
        self.api = api
        self.video_id = video_id

    def run(self):
        try:
            video_info = self.api.get_video_info(self.video_id)
            self.result_ready.emit(video_info)
        except Exception as e:
            self.result_ready.emit({'code': -1, 'message': str(e)})
from PyQt5.QtGui import QFont, QIcon
from bilibili_api import BilibiliAPI

class BilibiliDownloaderQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Btools")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        
        # 初始化B站API
        self.api = BilibiliAPI()
        self.download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.download_tasks = []
        
        # 创建UI
        self.init_ui()
        
    def init_ui(self):
        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 侧边栏
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(60)
        self.sidebar.setStyleSheet("background-color: #1e1e1e;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setAlignment(Qt.AlignTop)
        sidebar_layout.setSpacing(20)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        
        # 侧边栏按钮
        self.buttons = {
            'search': self.create_sidebar_button('🔍', self.show_search_page),
            'download': self.create_sidebar_button('⬇', self.show_download_page),
            'settings': self.create_sidebar_button('⚙', self.show_settings_page),
            'about': self.create_sidebar_button('ℹ', self.show_about)
        }
        
        for btn in self.buttons.values():
            sidebar_layout.addWidget(btn)
        
        # 底部按钮占位
        sidebar_layout.addStretch()
        
        # 主内容区域
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #2b2b2b;")
        
        # 创建页面
        self.search_page = self.create_search_page()
        self.download_page = self.create_download_page()
        self.settings_page = self.create_settings_page()
        
        self.content_area.addWidget(self.search_page)
        self.content_area.addWidget(self.download_page)
        self.content_area.addWidget(self.settings_page)
        
        # 添加到主布局
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)
        
        # 默认显示搜索页
        self.show_search_page()
        
    def create_sidebar_button(self, text, callback):
        btn = QPushButton(text)
        btn.setFixedSize(40, 40)
        btn.setFont(QFont('Microsoft YaHei', 14))
        btn.setStyleSheet(""
            "QPushButton {background-color: #1e1e1e; border-radius: 8px; color: white;}"
            "QPushButton:hover {background-color: #404040;}"
            "QPushButton:pressed {background-color: #0078d4;}"
        )
        btn.clicked.connect(callback)
        return btn
        
    def create_search_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 搜索框区域
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: #3a3a3a; border-radius: 8px; padding: 15px;")
        self.search_layout = QHBoxLayout(search_frame)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入B站链接/AV/BV号...")
        self.search_input.setStyleSheet(""
            "background-color: #4a4a4a; border: none; border-radius: 4px; padding: 8px;"
            "color: white; font-family: 'Microsoft YaHei'; font-size: 12px;"
        )
        
        self.search_btn = QPushButton("搜索")
        self.search_btn.setStyleSheet(""
            "background-color: #0078d4; border-radius: 4px; padding: 8px 16px;"
            "color: white; font-family: 'Microsoft YaHei'; font-size: 12px;"
        )
        self.search_btn.clicked.connect(self.perform_search)
        
        self.paste_btn = QPushButton("粘贴")
        self.paste_btn.setStyleSheet(""
            "background-color: #4a4a4a; border-radius: 4px; padding: 8px 16px;"
            "color: white; font-family: 'Microsoft YaHei'; font-size: 12px;"
        )
        self.paste_btn.clicked.connect(self.paste_from_clipboard)
        
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_btn)
        self.search_layout.addWidget(self.paste_btn)
        
        # 空状态显示
        self.empty_state = QLabel("此处列为空～")
        self.empty_state.setAlignment(Qt.AlignCenter)
        self.empty_state.setStyleSheet("color: #666; font-family: 'Microsoft YaHei'; font-size: 14px;")
        
        layout.addWidget(search_frame)

        # 搜索结果区域
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setStyleSheet("border: none;")
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_scroll.setWidget(self.results_widget)
        layout.addWidget(self.results_scroll)

        # 加载指示器
        self.loading_indicator = QLabel("加载中...")
        self.loading_indicator.setAlignment(Qt.AlignCenter)
        self.loading_indicator.setStyleSheet("color: #666; font-family: 'Microsoft YaHei'; font-size: 14px;")
        self.results_layout.addWidget(self.loading_indicator)
        self.loading_indicator.hide()

        # 空状态显示
        self.empty_state = QLabel("此处列为空～")
        self.empty_state.setAlignment(Qt.AlignCenter)
        self.empty_state.setStyleSheet("color: #666; font-family: 'Microsoft YaHei'; font-size: 14px;")
        self.results_layout.addWidget(self.empty_state)
        
        layout.addStretch()
        
        return page
        
    def create_download_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 下载任务列表
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("background-color: #3a3a3a; border-radius: 8px; padding: 10px;")
        
        layout.addWidget(self.task_list)
        return page
        
    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 下载路径设置
        path_frame = QFrame()
        path_frame.setStyleSheet("background-color: #3a3a3a; border-radius: 8px; padding: 15px;")
        path_layout = QHBoxLayout(path_frame)
        
        path_label = QLabel("下载路径：")
        path_label.setStyleSheet("color: white; font-family: 'Microsoft YaHei'; font-size: 12px;")
        
        self.path_input = QLineEdit(self.download_path)
        self.path_input.setStyleSheet(""
            "background-color: #4a4a4a; border: none; border-radius: 4px; padding: 8px;"
            "color: white; font-family: 'Microsoft YaHei'; font-size: 12px;"
        )
        
        browse_btn = QPushButton("浏览")
        browse_btn.setStyleSheet(""
            "background-color: #4a4a4a; border-radius: 4px; padding: 8px 16px;"
            "color: white; font-family: 'Microsoft YaHei'; font-size: 12px;"
        )
        browse_btn.clicked.connect(self.browse_download_path)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        
        layout.addWidget(path_frame)
        layout.addStretch()
        
        return page
        
    def show_search_page(self):
        self.content_area.setCurrentIndex(0)
        self.update_sidebar_state('search')
        
    def show_download_page(self):
        self.content_area.setCurrentIndex(1)
        self.update_sidebar_state('download')
        
    def show_settings_page(self):
        self.content_area.setCurrentIndex(2)
        self.update_sidebar_state('settings')
        
    def show_about(self):
        QMessageBox.about(self, "关于", "Btools - B站视频下载工具\n版本：1.0.0")
        
    def update_sidebar_state(self, active_key):
        for key, btn in self.buttons.items():
            if key == active_key:
                btn.setStyleSheet(""
                    "QPushButton {background-color: #0078d4; border-radius: 8px; color: white;}"
                    "QPushButton:hover {background-color: #0078d4;}"
                )
            else:
                btn.setStyleSheet(""
                    "QPushButton {background-color: #1e1e1e; border-radius: 8px; color: white;}"
                    "QPushButton:hover {background-color: #404040;}"
                )
        
    def perform_search(self):
        url = self.search_input.text().strip()
        if not url:
            QMessageBox.warning(self, "提示", "请输入视频链接或ID")
            return

        # 提取视频ID
        video_id = self.api.extract_video_id(url)
        if not video_id:
            QMessageBox.warning(self, "错误", "无法提取视频ID，请检查输入")
            return

        # 获取视频信息
        video_info = self.api.get_video_info(video_id)
        if video_info['code'] != 0:
            QMessageBox.warning(self, "错误", f"获取视频信息失败: {video_info.get('message', '未知错误')}")
            return

        # 显示加载状态
        self.empty_state.hide()
        self.results_scroll.hide()
        self.loading_indicator.show()

        # 在单独的线程中处理API请求
        self.api_worker = ApiWorker(self.api, video_id)
        self.api_worker.result_ready.connect(self.on_api_request_finished)
        self.api_worker.start()

    def on_api_request_finished(self, results):
        self.loading_indicator.hide()
        if results.get('code') == 0:
            self.show_video_info(results.get('data', {}))
            self.empty_state.hide()
        else:
            self.empty_state.show()
            QMessageBox.warning(self, "错误", f"获取视频信息失败: {results.get('message', '未知错误')}")

    def show_video_info(self, video_data):
        # 清除现有结果
        for i in reversed(range(self.search_layout.count())):
            widget = self.search_layout.itemAt(i).widget()
            if widget and widget != self.search_input and widget not in [self.search_btn, self.paste_btn]:
                widget.setParent(None)

        # 创建视频信息容器
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #3a3a3a; border-radius: 8px; padding: 15px; margin-top: 15px;")
        info_layout = QVBoxLayout(info_frame)

        # 视频标题
        title_label = QLabel(f"{video_data.get('title', '未知标题')}")
        title_label.setStyleSheet("color: white; font-family: 'Microsoft YaHei'; font-size: 16px; font-weight: bold;")
        info_layout.addWidget(title_label)

        # UP主信息
        up_info = QLabel(f"UP主: {video_data.get('owner', {}).get('name', '未知UP主')}")
        up_info.setStyleSheet("color: #aaa; font-family: 'Microsoft YaHei'; font-size: 12px;")
        info_layout.addWidget(up_info)

        # 视频统计信息
        bvid = video_data.get('bvid', '')
        stats = self.api.get_video_stats(bvid) if bvid else {'view': '0', 'danmaku': '0', 'favorite': '0'}
        stats_label = QLabel(f"播放: {stats['view']} | 弹幕: {stats['danmaku']} | 收藏: {stats['favorite']}")
        stats_label.setStyleSheet("color: #aaa; font-family: 'Microsoft YaHei'; font-size: 12px; margin-top: 5px;")
        info_layout.addWidget(stats_label)

        # 分P列表
        parts = self.api.get_video_parts(bvid) if bvid else []
        if parts and len(parts) > 1:
            parts_label = QLabel("分P列表:")
            parts_label.setStyleSheet("color: white; font-family: 'Microsoft YaHei'; font-size: 14px; margin-top: 15px;")
            info_layout.addWidget(parts_label)

            for i, part in enumerate(parts):
                part_frame = QFrame()
                part_frame.setStyleSheet("background-color: #4a4a4a; border-radius: 4px; padding: 8px; margin-top: 5px;")
                part_layout = QHBoxLayout(part_frame)

                part_label = QLabel(f"P{i+1}: {part['part']}")
                part_label.setStyleSheet("color: white; font-family: 'Microsoft YaHei'; font-size: 12px; flex: 1;")

                download_btn = QPushButton("下载")
                download_btn.setStyleSheet(""
                    "background-color: #0078d4; border-radius: 4px; padding: 4px 10px;"
                    "color: white; font-family: 'Microsoft YaHei'; font-size: 12px;"
                )
                download_btn.clicked.connect(lambda checked, cid=part['cid'], title=part['part']: self.start_download(video_data['bvid'], cid, title))

                part_layout.addWidget(part_label)
                part_layout.addWidget(download_btn)
                info_layout.addWidget(part_frame)
        else:
            # 单个视频直接显示下载按钮
            download_frame = QFrame()
            download_frame.setStyleSheet("margin-top: 15px;")
            download_layout = QHBoxLayout(download_frame)

            download_btn = QPushButton("下载视频")
            download_btn.setStyleSheet(""
                "background-color: #0078d4; border-radius: 4px; padding: 8px 16px;"
                "color: white; font-family: 'Microsoft YaHei'; font-size: 14px;"
            )
            download_btn.clicked.connect(lambda checked, cid=video_data['cid'], title=video_data['title']: self.start_download(video_data['bvid'], cid, title))

            download_layout.addWidget(download_btn)
            info_layout.addWidget(download_frame)

        # 添加到搜索布局
        self.search_layout.addWidget(info_frame)

    def start_download(self, bvid, cid, title):
        # 创建下载任务
        task = DownloadTask(self.api, bvid, cid, title, self.download_path)
        task.progress_updated.connect(self.update_download_progress)
        task.finished.connect(self.download_finished)
        self.download_tasks.append(task)

        # 添加到任务列表
        self.add_download_task_to_list(title, task)
        task.start()

    def add_download_task_to_list(self, title, task):
        item = QListWidgetItem(self.task_list)
        task_widget = QFrame()
        task_widget.setStyleSheet("background-color: #3a3a3a; border-radius: 8px; padding: 10px; margin-bottom: 10px;")
        task_layout = QVBoxLayout(task_widget)

        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-family: 'Microsoft YaHei'; font-size: 14px;")
        task_layout.addWidget(title_label)

        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setStyleSheet(""
            "QProgressBar {border: none; border-radius: 4px; background-color: #4a4a4a; height: 8px;}"
            "QProgressBar::chunk {background-color: #0078d4; border-radius: 4px;}"
        )
        progress_bar.setValue(0)
        task_layout.addWidget(progress_bar)

        # 状态
        status_label = QLabel("等待下载...")
        status_label.setStyleSheet("color: #aaa; font-family: 'Microsoft YaHei'; font-size: 12px;")
        task_layout.addWidget(status_label)

        item.setSizeHint(task_widget.sizeHint())
        self.task_list.setItemWidget(item, task_widget)

        # 存储任务相关控件以便更新
        task.task_item = item
        task.progress_bar = progress_bar
        task.status_label = status_label

    def update_download_progress(self, task, progress, status):
        if hasattr(task, 'progress_bar') and hasattr(task, 'status_label'):
            task.progress_bar.setValue(progress)
            task.status_label.setText(status)

    def download_finished(self, task, result):
        if result['code'] == 0:
            task.status_label.setText(f"下载完成: {result['path']}")
        else:
            task.status_label.setText(f"下载失败: {result['message']}")
        
    def paste_from_clipboard(self):
        try:
            text = clipboard.paste()
            self.search_input.setText(text)
        except:
            QMessageBox.warning(self, "提示", "剪贴板中没有内容")
        
    def browse_download_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择下载路径")
        if path:
            self.download_path = path
            self.path_input.setText(path)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BilibiliDownloaderQt()
    window.show()
    sys.exit(app.exec_())