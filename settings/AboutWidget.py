from PyQt5.QtWidgets import (QLabel, QWidget,
                             QVBoxLayout)


class AboutWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def start(self):
        pass
    def stop(self):
        pass


    def initUI(self):
        layout = QVBoxLayout()

        text = """
                关于本项目
                版本: 25100922
                角色：崩铁-刃-芝麻酥
                作者: 初心cx
                感谢，部分素材图片来源: 芝麻球促销（作者，半江离）
                感谢，部分桌宠模式项目: Shimeji（作者，Kilkakon）"""
        layout.addWidget(QLabel(text, self))
        layout.addStretch()
        self.setLayout(layout)
