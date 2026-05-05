from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QStackedWidget, QLabel)

from settings.settings_styles import settings_tab_style


class TabWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def start(self):
        cur_widget = self.content_area.currentWidget()
        if cur_widget:
            cur_widget.start()

    def stop(self):
        cur_widget = self.content_area.currentWidget()
        if cur_widget:
            cur_widget.stop()

    def initUI(self):
        # 主布局 - 水平布局（左侧选项卡 + 右侧内容）
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧选项卡（使用QListWidget）
        self.tab_bar = QListWidget()
        self.tab_bar.setFixedWidth(200)  # 选项卡宽度
        self.tab_bar.setStyleSheet(settings_tab_style)

        # 右侧内容区域（使用QStackedWidget）
        self.content_area = QStackedWidget()

        # 连接选项卡点击事件
        self.tab_bar.currentRowChanged.connect(self.changeIndex)

        # 添加到主布局
        main_layout.addWidget(self.tab_bar)
        main_layout.addWidget(self.content_area)

        self.setLayout(main_layout)

        # 默认选中第一个选项卡
        self.tab_bar.setCurrentRow(0)

    def addTab(self, name, widget):
        """添加新选项卡"""
        self.tab_bar.addItem(name)
        self.content_area.addWidget(widget)

    def changeIndex(self,index):
        if index == self.content_area.currentIndex():
            return
        cur_widget=self.content_area.currentWidget()
        if cur_widget:
            cur_widget.stop()
        self.content_area.setCurrentIndex(index)
        new_widget=self.content_area.currentWidget()
        if new_widget:
            new_widget.start()


    def currentIndex(self):
        """获取当前选中的选项卡索引"""
        return self.tab_bar.currentRow()
