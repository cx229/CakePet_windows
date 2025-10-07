
settings_tab_style="""
    QListWidget {
        background-color: #FFFFFF;
        border: none;
        font-size: 22px;
    }
    QListWidget::item {
        height: 60px;
        border-bottom: 1px solid #DDD;
        padding-left: 10px;
    }
    QListWidget::item:selected {
        background-color: #FFFFFF;
        color: black;
        border-left: 3px solid #2196F3;
    }
"""

settings_set_style="""
    /* 设置页样式 */
    QWidget {
        font-family: "Microsoft YaHei";
        font-size: 18px;
        background-color: #f8fbff;
        color: #333333;
    }

    QScrollArea {
        background-color: #f8fbff;
        border: none;
    }

    QScrollBar:vertical {
        background-color: #e6f0ff;
        width: 15px;
        border-radius: 5px;
    }

    QScrollBar::handle:vertical {
        background-color: #4a90e2;
        border-radius: 5px;
        min-height: 30px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #3a80d2;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    /* 设置项容器 */
    .setting-item {
        background-color: #ffffff;
        border-bottom: 1px solid #e6f0ff;
        min-height: 70px;
    }

    .setting-item:last-child {
        border-bottom: none;
    }

    /* 分组标题 */
    .group-title {
        font-size: 20px;
        font-weight: bold;
        color: #2c6bb0;
        background-color: #e6f0ff;
        padding: 20px 25px;
        border-bottom: 1px solid #d0e0ff;
        margin: 0px;
    }

    /* 主标题样式 */
    .setting-title {
        font-size: 24px;
        color: #333333;
        font-weight: bold;
        margin: 0px;
        padding: 0px;
        min-height: 25px;
    }

    /* 说明文字样式 */
    .setting-description {
        font-size: 18px;
        color: #666666;
        margin: 0px 0px 0px 0px;  /* 减小标题和说明的间距 */
        padding: 0px;
        line-height: 1.5;
        font-weight: normal;
        min-height: 22px;
    }

    /* 状态文字 */
    .status-text {
        font-size: 16px;
        color: #ff6b6b;
        margin: 5px 0px 0px 0px;
        padding: 0px;
        font-style: italic;
    }

    /* 开关样式 */
    QCheckBox {
        spacing: 0px;
        padding: 0px;
        margin: 0px;
    }

    QCheckBox::indicator {
        width: 50px;
        height: 20px;
        border-radius: 16px;
        background-color: #cccccc;
        border: 5px solid #cccccc;
    }

    QCheckBox::indicator:checked {
        background-color: #4a90e2;
        border-color: #4a90e2;
    }

    QCheckBox::indicator:unchecked {
        background-color: #cccccc;
        border-color: #cccccc;
    }

    /* 开关滑块 */
    QCheckBox::indicator:checked::after {
        content: "";
        position: absolute;
        left: 32px;
        width: 28px;
        height: 28px;
        border-radius: 18px;
        background-color: white;
        margin: 2px;
    }

    QCheckBox::indicator:unchecked::after {
        content: "";
        position: absolute;
        left: 2px;
        width: 28px;
        height: 28px;
        border-radius: 18px;
        background-color: white;
        margin: 2px;
    }

    /* 滑块样式 */
    QSlider::groove:horizontal {
        height: 6px;
        background: #e0e0e0;
        border-radius: 6px;
        margin: 0px;
    }

    QSlider::handle:horizontal {
        width: 24px;
        height: 24px;
        margin: -9px 0;
        background: #ffffff;
        border: 5px solid #4a90e2;
        border-radius: 12px;
    }

    QSlider::sub-page:horizontal {
        background: #4a90e2;
        border-radius: 5px;
    }

    /* 数值标签 */
    .value-label {
        font-size: 22px;
        color: #4a90e2;
        min-width: 200px;
        text-align: center;
        margin-right: 40px;
        padding: 0px;
        font-weight: bold;
    }

    /* 滑块容器 */
    .slider-container {
        background-color: transparent;
        padding: 0px;
        margin: 0px;
    }
"""
