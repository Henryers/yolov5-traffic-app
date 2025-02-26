import os
import subprocess
import sys
from mysql_tool import MysqlTool
import pandas as pd
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QGraphicsScene, QTabBar, QDialog, QHBoxLayout, QLabel, \
    QVBoxLayout, QPushButton, QTableWidgetItem, QMessageBox, QGraphicsLineItem, QLineEdit
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from detect import get_dir

# 登录本系统的用户名
Username = ""


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 使用uic加载UI文件(只支持QWidget)
        # self.ui = uic.loadUi("./ui/dialog.ui")
        # 使用uic加载UI文件
        self.ui = uic.loadUi("./ui/dialog.ui", self)
        # tab
        self.tabWidget = self.ui.tabWidget
        self.login_tab1 = self.ui.login_tab1
        self.reg_tab2 = self.ui.reg_tab2
        # tab1_login
        self.login_username = self.ui.login_username
        self.login_password = self.ui.login_password
        self.login_btn = self.ui.login_btn
        self.cancel_btn1 = self.ui.cancel_btn1
        # tab2_reg
        self.reg_username = self.ui.reg_username
        self.reg_password = self.ui.reg_password
        self.reg_btn = self.ui.reg_btn
        self.cancel_btn2 = self.ui.cancel_btn2
        # 连接按钮的点击信号到槽函数
        self.login_tab1.clicked.connect(self.open1)
        self.reg_tab2.clicked.connect(self.open2)
        self.login_btn.clicked.connect(self.login)
        self.reg_btn.clicked.connect(self.register)
        self.cancel_btn1.clicked.connect(self.cancel)
        self.cancel_btn2.clicked.connect(self.cancel)
        # 设置文本为密码格式
        self.login_password.setEchoMode(QLineEdit.Password)
        self.reg_password.setEchoMode(QLineEdit.Password)
        # 隐藏所有的Tab widget页面
        self.tabBar = self.tabWidget.findChild(QTabBar)
        self.tabBar.hide()
        # 默认打开首页
        self.tabWidget.setCurrentIndex(0)

    def open1(self):
        self.tabWidget.setCurrentIndex(0)

    def open2(self):
        self.tabWidget.setCurrentIndex(1)

    def login(self):
        # 在这里添加验证用户名和密码的逻辑
        username = self.login_username.text()
        password = self.login_password.text()
        if username == None or password == None:
            # 弹出对话框提示用户
            dialog = QMessageBox()
            dialog.setWindowTitle('warning')
            dialog.setIcon(QMessageBox.Warning)
            dialog.setText('用户名或密码不能为空！')
            dialog.exec_()
            return
        # 用户登录校验
        # 连接 MySQL 数据库（使用with能确保在使用完毕后自动关闭游标和连接，以免忘记手动关闭）
        with MysqlTool() as db:
            # 执行查询数据库字段的SQL语句
            # rows = db.execute('insert into user (username, pwd) values (#{username}, #{password})', commit=True)
            sql = "select * from user where name = %s and pwd = %s"
            args = (username, password)
            rows = db.execute(sql, args)

        # 查询到1条数据，说明用户存在并且密码输入正确
        if len(rows) == 1:
            try:
                dialog = QMessageBox()
                dialog.setWindowTitle('success')
                dialog.setIcon(QMessageBox.Information)
                dialog.setText('登录成功！')
                dialog.exec_()
                self.accept()  # 登录成功，关闭对话框
                global Username
                Username = rows[0][1]  # 对登录的用户名进行赋值
            except Exception as e:
                print(e)
        # 查询不到数据（name unique 不可能有多条数据，说明用户名或密码错误）
        else:
            print('Login failed. Please try again.')
            # 弹出对话框提示用户
            dialog = QMessageBox()
            dialog.setWindowTitle('error')
            dialog.setIcon(QMessageBox.Critical)
            dialog.setText('登录失败，请重试！')
            dialog.exec_()

    def register(self):
        username = self.reg_username.text()
        password = self.reg_password.text()
        if username == None or password == None:
            # 弹出对话框提示用户
            dialog = QMessageBox()
            dialog.setWindowTitle('warning')
            dialog.setIcon(QMessageBox.Warning)
            dialog.setText('用户名或密码不能为空！')
            dialog.exec_()
            return
        # 连接 MySQL 数据库（使用with能确保在使用完毕后自动关闭游标和连接，以免忘记手动关闭）
        with MysqlTool() as db:
            # 1. 先执行查询数据库字段的SQL语句，看看用户名是否已被注册
            sql = "select * from user where name = %s"
            args = (username)
            rows = db.execute(sql, args)
            # 2. 再判断是否能插入新数据
            # 用户名已被注册
            if len(rows) == 1:
                # 弹出对话框提示用户
                dialog = QMessageBox()
                dialog.setWindowTitle('warning')
                dialog.setIcon(QMessageBox.Warning)
                dialog.setText('用户名已被使用！')
                dialog.exec_()
            # 可以正常插入
            else:
                sql = "INSERT INTO user (name, pwd) VALUES (%s, %s)"
                args = (username, password)
                db.execute(sql, args, commit=True)
                # 弹出对话框提示用户
                dialog = QMessageBox()
                dialog.setWindowTitle('success')
                dialog.setIcon(QMessageBox.Information)
                dialog.setText('注册成功！')
                dialog.exec_()

    def cancel(self):
        exit()


class CustomGridScene(QGraphicsScene):
    def draw_grid(self):
        # Draw horizontal lines
        for i in range(0, 210, 10):
            line = QGraphicsLineItem(0, i, 210, i)
            self.addItem(line)
        # Draw vertical lines
        for i in range(0, 210, 10):
            line = QGraphicsLineItem(i, 0, i, 210)
            self.addItem(line)


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        不想要配置数据库的话，把下面三行代码注释掉就行~
        """
        # 显示登录对话框
        login_dialog = LoginDialog()
        result = login_dialog.exec_()
        # 检查登录对话框返回结果
        if result == QDialog.Accepted:
            # 加载qt-designer中设计的ui文件
            self.ui = uic.loadUi("./ui/traffic-detect.ui")
            # 菜单下拉框
            self.actiondefault = self.ui.actiondefault
            self.actionblack = self.ui.actionblack
            self.actionwhite = self.ui.actionwhite
            self.actionblue = self.ui.actionblue
            self.actionintro = self.ui.actionintroduction
            self.actionversion = self.ui.actionversion
            self.actionexit = self.ui.actionexit
            # 侧边栏
            self.tabWidget = self.ui.tabWidget
            self.photo_btn = self.ui.photo_btn
            self.video_btn = self.ui.video_btn
            self.cap_btn = self.ui.cap_btn
            self.test1_btn = self.ui.test1_btn
            self.test2_btn = self.ui.test2_btn
            self.test3_btn = self.ui.test3_btn
            # username
            self.username = self.ui.username
            global Username
            print(str(Username))
            self.username.setText(str(Username))
            # tab1_photo
            self.raw_img = self.ui.raw_image
            self.res_img = self.ui.res_image
            self.select_btn = self.ui.select_btn
            self.show_btn = self.ui.show_btn
            self.conf1 = self.ui.conf1
            self.conf1.setRange(0.0, 1.0)  # 设置范围
            self.conf1.setSingleStep(0.01)  # 设置步长
            self.conf1.setValue(0.25)  # 设置初始值
            self.IOU1 = self.ui.IOU1
            self.IOU1.setRange(0.0, 1.0)  # 设置范围
            self.IOU1.setSingleStep(0.01)  # 设置步长
            self.IOU1.setValue(0.45)  # 设置初始值
            self.class1 = self.ui.class1
            self.class_nums1 = self.ui.class_nums1  # 物体检测词频计数
            # tab2_video1
            self.video1 = self.ui.video1
            self.choose_video = self.ui.choose_video
            self.play_pause1 = self.ui.play_pause1
            # 创建一个媒体播放器对象和一个视频窗口对象
            self.media_player1 = QMediaPlayer()
            # 将视频窗口设置为媒体播放器的显示窗口
            self.media_player1.setVideoOutput(self.video1)
            # 进度条
            self.media_player1.durationChanged.connect(self.getDuration1)
            self.media_player1.positionChanged.connect(self.getPosition1)
            self.ui.slider1.sliderMoved.connect(self.updatePosition1)
            # tab2_video2
            self.video2 = self.ui.video2
            self.show_video = self.ui.show_video
            self.play_pause2 = self.ui.play_pause2
            # 创建一个媒体播放器对象和一个视频窗口对象
            self.media_player2 = QMediaPlayer()
            # 将视频窗口设置为媒体播放器的显示窗口
            self.media_player2.setVideoOutput(self.video2)
            # 进度条
            self.media_player2.durationChanged.connect(self.getDuration2)
            self.media_player2.positionChanged.connect(self.getPosition2)
            self.ui.slider2.sliderMoved.connect(self.updatePosition2)
            # tab2_data
            self.conf2 = self.ui.conf2
            self.conf2.setRange(0.0, 1.0)  # 设置范围
            self.conf2.setSingleStep(0.01)  # 设置步长
            self.conf2.setValue(0.25)  # 设置初始值
            self.IOU2 = self.ui.IOU2
            self.IOU2.setRange(0.0, 1.0)  # 设置范围
            self.IOU2.setSingleStep(0.01)  # 设置步长
            self.IOU2.setValue(0.45)  # 设置初始值
            self.class2 = self.ui.class2
            self.class_nums2 = self.ui.class_nums2  # 物体检测词频计数
            self.show_cn = self.ui.show_cn
            # 创建一个定时器
            self.counter = 0
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.updateText)
            self.show_cn.clicked.connect(self.startTimer)
            # tab3_camera
            self.camera_btn = self.ui.camera_btn
            self.label = self.ui.label
            # tab4_test
            self.xlsx = self.ui.xlsx
            self.selectxlsx_btn = self.ui.selectxlsx_btn
            self.df = 0
            self.subdf = 0
            self.day = self.ui.day
            self.day_btn = self.ui.day_btn
            self.show_month = self.ui.show_month
            self.show_day = self.ui.show_day
            self.show_row = self.ui.show_row
            self.show_col = self.ui.show_col
            # tab5_chart
            self.chart5_1 = self.ui.chart5_1
            self.chart5_2 = self.ui.chart5_2
            self.chart5_3 = self.ui.chart5_3
            self.export5_1 = self.ui.export5_1
            self.export5_2 = self.ui.export5_2
            self.export5_3 = self.ui.export5_3
            self.max5_1 = self.ui.max5_1
            self.max5_2 = self.ui.max5_2
            self.max5_3 = self.ui.max5_3
            self.min5_1 = self.ui.min5_1
            self.min5_2 = self.ui.min5_2
            self.min5_3 = self.ui.min5_3
            # tab6_graph
            self.chart6_1 = self.ui.chart6_1
            self.chart6_2 = self.ui.chart6_2
            self.chart6_3 = self.ui.chart6_3
            self.export6_1 = self.ui.export6_1
            self.export6_2 = self.ui.export6_2
            self.export6_3 = self.ui.export6_3
            self.data6_1 = self.ui.data6_1
            self.data6_2 = self.ui.data6_2
            self.data6_3 = self.ui.data6_3
            # click
            self.photo_btn.clicked.connect(self.open1)
            self.video_btn.clicked.connect(self.open2)
            self.cap_btn.clicked.connect(self.open3)
            self.test1_btn.clicked.connect(self.open4)
            self.test2_btn.clicked.connect(self.open5)
            self.test3_btn.clicked.connect(self.open6)
            self.select_btn.clicked.connect(self.select_image)
            self.show_btn.clicked.connect(self.detect_objects)
            self.choose_video.clicked.connect(self.chooseVideo)
            self.show_video.clicked.connect(self.showVideo)
            self.play_pause1.clicked.connect(self.playPause1)
            self.play_pause2.clicked.connect(self.playPause2)
            self.camera_btn.clicked.connect(self.detect_camera)
            self.selectxlsx_btn.clicked.connect(self.select_dataset)
            self.day_btn.clicked.connect(self.select_day)
            # 隐藏所有的Tab widget页面
            self.tabBar = self.tabWidget.findChild(QTabBar)
            self.tabBar.hide()
            # 默认打开首页
            self.tabWidget.setCurrentIndex(0)
            # 菜单栏点击事件
            self.actionwhite.triggered.connect(self.menu_white)
            self.actionblack.triggered.connect(self.menu_black)
            self.actionblue.triggered.connect(self.menu_blue)
            self.actiondefault.triggered.connect(self.menu_default)
            self.actionintro.triggered.connect(self.menu_intro)
            self.actionversion.triggered.connect(self.menu_version)
            self.actionexit.triggered.connect(self.myexit)
            # 保存图表
            self.export5_1.clicked.connect(self.export_chart5_1)
            self.export5_2.clicked.connect(self.export_chart5_2)
            self.export5_3.clicked.connect(self.export_chart5_3)
            self.export6_1.clicked.connect(self.export_chart6_1)
            self.export6_2.clicked.connect(self.export_chart6_2)
            self.export6_3.clicked.connect(self.export_chart6_3)

    def menu_white(self):
        print('light')
        stylesheet1 = f"QMainWindow{{background-color: rgb(250,250,250)}}"
        stylesheet2 = f"QWidget{{background-color: rgb(250,250,250)}}"
        self.ui.setStyleSheet(stylesheet1)
        self.ui.centralwidget.setStyleSheet(stylesheet2)

    def menu_black(self):
        print('dark')
        stylesheet1 = f"QMainWindow{{background-color: rgb(50,50,50)}}"
        stylesheet2 = f"QWidget{{background-color: rgb(50,50,50)}}"
        self.ui.setStyleSheet(stylesheet1)
        self.ui.centralwidget.setStyleSheet(stylesheet2)

    def menu_blue(self):
        print('blue')
        stylesheet1 = f"QMainWindow{{background-color: rgb(230,245,255)}}"
        stylesheet2 = f"QWidget{{background-color: rgb(230,245,255)}}"
        self.ui.setStyleSheet(stylesheet1)
        self.ui.centralwidget.setStyleSheet(stylesheet2)

    def menu_default(self):
        print('default')
        stylesheet1 = f"QMainWindow{{background-color: rgb(240,240,240)}}"
        stylesheet2 = f"QWidget{{background-color: rgb(240,240,240)}}"
        self.ui.setStyleSheet(stylesheet1)
        self.ui.centralwidget.setStyleSheet(stylesheet2)

    def menu_intro(self):
        print('intro')
        try:
            dialog = QDialog()
            dialog.setWindowTitle('introduction')
            dialog.setFixedSize(1000, 800)  # 设置对话框大小
            # 总体水平布局
            layout = QHBoxLayout(dialog)
            # 左侧的 QLabel，用于显示图片
            image_label = QLabel()
            pixmap = QPixmap('./data/images/traffic.jpg')  # 替换为您的图片路径
            pixmap = pixmap.scaled(400, 330)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)
            # 设置标题字体
            font = QFont()
            font.setPointSize(16)  # 设置字体大小
            font.setBold(True)  # 加粗
            # 创建 QPalette 对象并设置文本颜色
            palette = QPalette()
            # 设置为橙色
            palette.setColor(QPalette.WindowText, QColor(255, 100, 0))
            # 右侧的 QVBoxLayout，用于显示文字
            text_layout = QVBoxLayout()
            label1 = QLabel("基于YOLOv5的交通道路")
            label1.setAlignment(Qt.AlignCenter)  # 居中对齐
            label1.setFont(font)
            label2 = QLabel("目标检测和数据分析")
            label2.setAlignment(Qt.AlignCenter)  # 居中对齐
            label2.setFont(font)
            label3 = QLabel("本软件致力于为交通道路数据研究，")
            label3.setAlignment(Qt.AlignCenter)  # 居中对齐
            label3.setPalette(palette)
            label4 = QLabel("通过YOLOv5框架进行交通目标检测，")
            label4.setAlignment(Qt.AlignCenter)  # 居中对齐
            label4.setPalette(palette)
            label5 = QLabel("同时对交通数据集进行多种分析处理。")
            label5.setAlignment(Qt.AlignCenter)  # 居中对齐
            label5.setPalette(palette)
            text_layout.addSpacing(100)  # 设置间距为100
            text_layout.addWidget(label1)
            text_layout.addWidget(label2)
            text_layout.addSpacing(80)  # 设置间距为50
            text_layout.addWidget(label3)
            text_layout.addWidget(label4)
            text_layout.addWidget(label5)
            text_layout.addSpacing(100)  # 设置间距为100
            # 关闭按钮
            btn = QPushButton('关闭', dialog)
            btn.setFixedSize(150, 60)
            # 连接关闭信号
            btn.clicked.connect(dialog.close)
            text_layout.addWidget(btn, alignment=Qt.AlignCenter)
            layout.addLayout(text_layout)
            # 加载对话框图标
            dialog.setWindowIcon(QIcon("./data/images/bus.jpg"))
            # 显示对话框，而不是一闪而过
            dialog.exec()
        except Exception as e:
            print(e)

    def menu_version(self):
        print('version')
        try:
            dialog = QDialog()
            dialog.setWindowTitle('version')
            dialog.setFixedSize(1000, 800)  # 设置对话框大小
            # 总体水平布局
            layout = QHBoxLayout(dialog)
            # 左侧的 QLabel，用于显示图片
            image_label = QLabel()
            pixmap = QPixmap('./data/images/traffic.jpg')  # 替换为您的图片路径
            pixmap = pixmap.scaled(400, 330)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)
            # 设置标题字体
            font = QFont()
            font.setPointSize(12)  # 设置字体大小
            font.setBold(True)  # 加粗
            # 设置主要文字字体
            font1 = QFont()
            font1.setPointSize(14)  # 设置字体大小
            font1.setBold(True)  # 加粗
            # 创建 QPalette 对象并设置文本颜色
            palette = QPalette()
            # 设置为橙色
            palette.setColor(QPalette.WindowText, QColor(255, 100, 0))
            # 右侧的 QVBoxLayout，用于显示文字
            text_layout = QVBoxLayout()
            label1 = QLabel("基于YOLOv5的交通道路")
            label1.setAlignment(Qt.AlignCenter)  # 居中对齐
            label1.setFont(font)
            label2 = QLabel("目标检测和数据分析")
            label2.setAlignment(Qt.AlignCenter)  # 居中对齐
            label2.setFont(font)
            label3 = QLabel("版本:  1.0")
            label3.setAlignment(Qt.AlignCenter)  # 居中对齐
            label3.setFont(font)
            label3.setPalette(palette)
            label4 = QLabel("时间:  2024年03月18日")
            label4.setAlignment(Qt.AlignCenter)  # 居中对齐
            label4.setFont(font)
            label4.setPalette(palette)
            text_layout.addSpacing(100)  # 设置间距为10
            text_layout.addWidget(label1)
            text_layout.addWidget(label2)
            text_layout.addSpacing(80)  # 设置间距为10
            text_layout.addWidget(label3)
            text_layout.addWidget(label4)
            text_layout.addSpacing(100)  # 设置间距为10
            btn = QPushButton('关闭', dialog)
            btn.setFixedSize(150, 60)
            btn.clicked.connect(dialog.close)
            text_layout.addWidget(btn, alignment=Qt.AlignCenter)
            layout.addLayout(text_layout)
            # 加载对话框图标
            dialog.setWindowIcon(QIcon('./data/images/bus.jpg'))
            # 显示对话框，而不是一闪而过
            dialog.exec()
        except Exception as e:
            print(e)

    # tab
    def open1(self):
        self.tabWidget.setCurrentIndex(0)

    def open2(self):
        self.tabWidget.setCurrentIndex(1)

    def open3(self):
        self.tabWidget.setCurrentIndex(2)

    def open4(self):
        self.tabWidget.setCurrentIndex(3)

    def open5(self):
        self.tabWidget.setCurrentIndex(4)
        if type(self.df) == int:
            print("未加载数据表xlsx/csv")
            # 弹出提示框
            dialog = QMessageBox()
            dialog.setWindowTitle('warning')
            dialog.setIcon(QMessageBox.Warning)
            dialog.setText("请先选择数据集！")
            dialog.exec_()
            return
        try:
            # 绘制chart5_1
            self.figure5_1 = Figure(figsize=(6, 4))
            self.myax1 = self.figure5_1.add_subplot(111)
            self.canvas = FigureCanvas(self.figure5_1)
            # 根据元素tag分类，统计不同大小车的数量
            num1 = self.df['less 5.2m'].sum()
            num2 = self.df['5.21m - 6.6m'].sum()
            num3 = self.df['6.61m - 11.6m'].sum()
            num4 = self.df['above 11.6m'].sum()
            print(num1)
            # 找到最值
            max_value = max(num1, num2, num3, num4)
            min_value = min(num1, num2, num3, num4)
            self.max5_1.setText(str(max_value))
            self.min5_1.setText(str(min_value))
            # 创建饼状图
            labels = ['small car', 'middle car', 'big car', 'truck']
            sizes = [num1, num2, num3, num4]
            self.myax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                           colors=['#cccc00', 'skyblue', 'lightgreen', '#cc1199'])
            # 添加标题
            self.myax1.set_title('Distribution of Different Vehicles')
            # 添加标签和标题
            self.canvas.draw()
            scene = QGraphicsScene(self)
            scene.addWidget(self.canvas)
            # 将 QGraphicsScene 设置到 QGraphicsView 中
            self.chart5_1.setScene(scene)
            # 绘制chart5_2
            self.figure5_2 = Figure(figsize=(6, 5))
            self.myax2 = self.figure5_2.add_subplot(111)
            self.canvas = FigureCanvas(self.figure5_2)
            # self.df['Local Date'] = pd.to_datetime(self.df['Local Date'])
            # Calculate average speed for each date
            average_speed_per_date = self.df.groupby('Local Date')['Speed Value'].mean().reset_index()
            max_value = self.df['Speed Value'].max()
            min_value = self.df['Speed Value'].min()
            self.max5_2.setText(str(max_value))
            self.min5_2.setText(str(min_value))
            self.myax2.plot(average_speed_per_date['Local Date'], average_speed_per_date['Speed Value'],
                            color='#008822', marker='o')
            self.myax2.set_title('Average Speed Per Date')
            # 设置x坐标轴上的日期刻度
            self.myax2.set_xticks([0, 5, 10, 15, 20, 25, 30])
            self.myax2.set_xticklabels(['1d', '6d', '11d', '16d', '21d', '26d', '31d'], rotation=30, fontsize='small')
            self.myax2.set_xlabel('different times a day')
            self.myax2.set_ylabel('Average Speed')
            # self.myax2.grid(True)
            # 添加标签和标题
            self.canvas.draw()
            scene = CustomGridScene(self)
            scene.draw_grid()
            # scene = QGraphicsScene(self)
            scene.addWidget(self.canvas)
            # 将 QGraphicsScene 设置到 QGraphicsView 中
            self.chart5_2.setScene(scene)
            # 绘制chart5_3
            self.figure5_3 = Figure(figsize=(18, 5))
            self.myax3 = self.figure5_3.add_subplot(111)
            self.canvas = FigureCanvas(self.figure5_3)
            max_value = self.df['Total Carriageway Flow'].max()
            min_value = self.df['Total Carriageway Flow'].min()
            self.max5_3.setText(str(max_value))
            self.min5_3.setText(str(min_value))
            # 绘制速度和加速度随时间的变化曲线
            self.myax3.set_title('all time vehicles nums')
            # 合并 Local Date 和 Local Time 字段成一个新的 datetime 字段
            # 将'Datetime'列转换为指定格式的字符串
            # 例如，将日期时间格式化为"YYYY-MM-DD HH:MM:SS"的形式
            # self.df['Datetime'] = self.df['Datetime'].dt.strftime('%Y-%m-%d')
            self.df['Datetime'] = pd.to_datetime(self.df['Local Date'] + ' ' + self.df['Local Time'])
            self.df['Datetime'] = pd.to_datetime(self.df['Datetime'])
            self.myax3.plot(self.df['Datetime'], self.df['Total Carriageway Flow'], color='#006699', label='FlowNums')
            # plt.plot(data1['local_elapsed_time'], data1['speed'], label='Speed2')
            self.myax3.set_xlabel('Time (s)')
            # 设置x坐标轴上的日期刻度
            xticks_interval = 192
            self.myax3.set_xticks(self.df['Datetime'][::xticks_interval])
            self.myax3.set_xticklabels(self.df['Datetime'][::xticks_interval], rotation=10, fontsize='small')
            self.myax3.set_ylabel('Total flow vehicles')
            self.myax3.legend()
            self.canvas.draw()
            scene = QGraphicsScene(self)
            scene.addWidget(self.canvas)
            # 将 QGraphicsScene 设置到 QGraphicsView 中
            self.chart5_3.setScene(scene)
        except Exception as e:
            print(e)

    def open6(self):
        self.tabWidget.setCurrentIndex(5)
        if type(self.subdf) == int:
            print("未加载数据子表xlsx/csv")
            # 弹出提示框
            dialog = QMessageBox()
            dialog.setWindowTitle('warning')
            dialog.setIcon(QMessageBox.Warning)
            dialog.setText("请先选择数据集！")
            dialog.exec_()
            return
        try:
            # 绘制chart6_1
            self.figure6_1 = Figure(figsize=(6, 5))
            self.myax1 = self.figure6_1.add_subplot(111)
            self.canvas = FigureCanvas(self.figure6_1)
            # 根据元素tag分类，统计不同大小车的数量
            num1 = self.subdf['less 5.2m'].sum()
            num2 = self.subdf['5.21m - 6.6m'].sum()
            num3 = self.subdf['6.61m - 11.6m'].sum()
            num4 = self.subdf['above 11.6m'].sum()
            # 创建柱状图
            labels = ['small car', 'middle car', 'big car', 'truck']
            sizes = [num1, num2, num3, num4]
            colors = ['lightcoral', 'skyblue', 'lightgreen', '#00cc99']
            self.myax1.bar(labels, sizes, color=colors)
            # 添加标题
            self.myax1.set_title('Distribution of Different Vehicles')
            # 添加标签和标题
            self.canvas.draw()
            scene = QGraphicsScene(self)
            scene.addWidget(self.canvas)
            # 将 QGraphicsScene 设置到 QGraphicsView 中
            self.chart6_1.setScene(scene)
            # 绘制chart6_2
            self.figure6_2 = Figure(figsize=(8, 5))
            self.myax2 = self.figure6_2.add_subplot(111)
            self.canvas = FigureCanvas(self.figure6_2)
            # 绘制速度随时间的变化曲线
            self.myax2.set_title('speed of different time a day')
            self.myax2.plot(self.subdf['Local Time'], self.subdf['Speed Value'], color='#0099ff', label='Speed')
            # plt.plot(data1['local_elapsed_time'], data1['speed'], label='Speed2')
            self.myax2.set_xlabel('Time (s)')
            # 设置x坐标轴上的日期刻度
            xticks_interval = 12
            self.myax2.set_xticks(self.subdf['Local Time'][::xticks_interval])
            self.myax2.set_xticklabels(['1h', '4h', '7h', '10h', '13h', '16h', '19h', '22h'], rotation=30,
                                       fontsize='small')
            self.myax2.set_ylabel('Average Speed(km/h)')
            self.myax2.legend()
            self.canvas.draw()
            scene = QGraphicsScene(self)
            scene.addWidget(self.canvas)
            # 将 QGraphicsScene 设置到 QGraphicsView 中
            self.chart6_2.setScene(scene)
            # 绘制chart6_3
            self.figure6_3 = Figure(figsize=(14, 4))
            self.myax3 = self.figure6_3.add_subplot(111)
            self.canvas = FigureCanvas(self.figure6_3)
            # 绘制速度随时间的变化曲线
            self.myax3.set_title('The number of different types of vehicles in a day')
            self.myax3.plot(self.subdf['Local Time'], self.subdf['less 5.2m'], color='#00aaee', label='small car')
            # 绘制折线图（多加一个y轴出来）
            # self.myax4 = self.myax3.twinx()
            self.myax3.plot(self.subdf['Local Time'], self.subdf['5.21m - 6.6m'], color='#660055', label='middle car')
            # self.myax5 = self.myax3.twinx()
            self.myax3.plot(self.subdf['Local Time'], self.subdf['6.61m - 11.6m'], color='#dddd22', label='big car')
            # self.myax6 = self.myax3.twinx()
            self.myax3.plot(self.subdf['Local Time'], self.subdf['above 11.6m'], color='green', label='truck')
            self.myax3.set_xlabel('Time (s)')
            # 设置x坐标轴上的日期刻度
            xticks_interval = 12
            self.myax3.set_xticks(self.subdf['Local Time'][::xticks_interval])
            self.myax3.set_xticklabels(['1h', '4h', '7h', '10h', '13h', '16h', '19h', '22h'], rotation=30,
                                       fontsize='small')
            self.myax3.set_ylabel('different vehicles’ numbers')
            self.myax3.legend()
            self.canvas.draw()
            scene = QGraphicsScene(self)
            scene.addWidget(self.canvas)
            # 将 QGraphicsScene 设置到 QGraphicsView 中
            self.chart6_3.setScene(scene)
            # 设置显示参数
            self.data6_1.setText(str(self.subdf['Total Carriageway Flow'].sum()))
            self.data6_2.setText(str(self.subdf['Total Carriageway Flow'].max()))
            # 找到最大值所在的索引
            max_index = self.subdf['Total Carriageway Flow'].idxmax()
            self.data6_3.setText(str(self.subdf.loc[max_index][1]))
        except Exception as e:
            print(e)

    # tab1_photo
    def select_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Open Image File', '', 'Images (*.png *.jpg *.bmp)')
        if file_path:
            self.image_path = file_path
            self.load_image()

    def load_image(self):
        scene = QGraphicsScene()
        img = QPixmap(self.image_path)
        # img = img.scaled(450, 400)
        scene.addPixmap(img)
        self.raw_img.setScene(scene)

    def show_image(self):
        scene = QGraphicsScene()
        img = QPixmap(self.image_path)
        # img = img.scaled(450, 400)
        scene.addPixmap(img)
        self.res_img.setScene(scene)

    def detect_objects(self):
        if not self.image_path:
            return
        conf1 = self.conf1.value()
        conf1 = float("{:.2f}".format(conf1))
        IOU1 = self.IOU1.value()
        IOU1 = float("{:.2f}".format(IOU1))
        if self.class1.text() == '':
            class1 = -1
        else:
            class1 = int(self.class1.text())
        # Run YOLOv5 detection on the selected image
        command = [
            'python', 'detect.py',
            '--weights', 'yolov5s.pt',
            '--source', self.image_path,
            '--conf-thres', conf1,
            '--iou-thres', IOU1,
            '--classes', class1,
            '--imgsz', '640',
            '--device', 'cpu'
        ]
        print(command)
        try:
            # 调用目标检测的相关封装函数
            my_dir, return_list = get_dir(command)
            my_dir = str(my_dir)
            print(my_dir, return_list)
            if len(return_list) == 0:
                print("什么都没有检测到")
                return
            display_str = ""
            # 图片只有一帧，必定是return_list[0]
            for key, value in return_list[0].items():
                display_str += f"{key}: {value}\n\n"
            self.class_nums1.setText(display_str)
            file_name = os.path.basename(self.image_path)
            file_path = my_dir + "\\" + file_name
        except Exception as e:
            print(e)
        if file_path:
            print(file_path)
            self.image_path = file_path
            self.show_image()

    # tab2_btn事件
    # 选择视频1
    def chooseVideo(self):
        try:
            # 拿到视频路径，存到video_path里
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, 'Open Video File', '', 'Videos (*.mp4 *.avi)')
            if file_path:
                self.video_path = file_path
                print("绝对 / 相对路径？ file_path:  " + file_path)
                self.media_player1.setMedia(QMediaContent(QUrl(file_path)))
                self.media_player1.play()
        except Exception as e:
            print(e)

    # 播放/暂停
    def playPause1(self):
        if self.media_player1.state() == 1:
            self.media_player1.pause()
        else:
            self.media_player1.play()

    # 视频总时长获取
    def getDuration1(self, d):
        '''d是获取到的视频总时长（ms）'''
        self.ui.slider1.setRange(0, d)
        self.ui.slider1.setEnabled(True)
        self.displayTime1(d)

    # 视频实时位置获取
    def getPosition1(self, p):
        self.ui.slider1.setValue(p)
        self.displayTime1(self.ui.slider1.maximum() - p)

    # 显示剩余时间
    def displayTime1(self, ms):
        minutes = int(ms / 60000)
        seconds = int((ms - minutes * 60000) / 1000)
        self.ui.time1.setText('{}:{}'.format(minutes, seconds))

    # 用进度条更新视频位置
    def updatePosition1(self, v):
        self.media_player1.setPosition(v)
        self.displayTime1(self.ui.slider1.maximum() - v)

    # 选择视频2
    def showVideo(self):
        # 先处理，得到结果视频
        if not self.video_path:
            return
        conf2 = self.conf2.value()
        conf2 = float("{:.2f}".format(conf2))
        print("Current value:", conf2)
        print(type(conf2))
        IOU2 = self.IOU2.value()
        IOU2 = float("{:.2f}".format(IOU2))
        if self.class2.text() == '':
            class2 = -1
        else:
            class2 = int(self.class2.text())
        # Run YOLOv5 detection on the selected image
        command = [
            'python', 'detect.py',
            '--weights', 'yolov5s.pt',
            '--source', self.video_path,
            '--conf-thres', conf2,
            '--iou-thres', IOU2,
            '--classes', class2,
            '--device', 'cpu'
        ]
        print(command)
        try:
            my_dir, return_list = get_dir(command)
            my_dir = str(my_dir)
            print(my_dir, return_list)
            self.display_list = []
            for item in return_list:
                per_frame_display_str = ""
                for key, value in item.items():
                    per_frame_display_str += f"{key}: {value}\n\n"
                self.display_list.append(per_frame_display_str)
            print(self.display_list)
            # self.class_nums2.setText(self.display_list)
            print(self.video_path)
            file_name = os.path.basename(self.video_path)
            print(file_name)
            file_path = my_dir + "\\" + file_name
        except Exception as e:
            print(e)
        # 再将视频进行播放
        try:
            if file_path:
                print(file_path)
                base_path = "D:/MyCode/public_project/yolov5-traffic-app/"
                # 使用 os.path.join 拼接路径
                full_path = QUrl.fromLocalFile(os.path.join(base_path, file_path)).toString()
                print("拼接好的路径：" + full_path)
                self.media_player2.setMedia(QMediaContent(QUrl(full_path)))
                self.media_player2.play()
        except Exception as e:
            print(e)

    # 播放/暂停
    def playPause2(self):
        if self.media_player2.state() == 1:
            self.media_player2.pause()
        else:
            self.media_player2.play()

    # 视频总时长获取
    def getDuration2(self, d):
        '''d是获取到的视频总时长（ms）'''
        self.ui.slider2.setRange(0, d)
        self.ui.slider2.setEnabled(True)
        self.displayTime2(d)

    # 视频实时位置获取
    def getPosition2(self, p):
        self.ui.slider2.setValue(p)
        self.displayTime2(self.ui.slider2.maximum() - p)

    # 显示剩余时间
    def displayTime2(self, ms):
        minutes = int(ms / 60000)
        seconds = int((ms - minutes * 60000) / 1000)
        self.ui.time2.setText('{}:{}'.format(minutes, seconds))

    # 用进度条更新视频位置
    def updatePosition2(self, v):
        self.media_player2.setPosition(v)
        self.displayTime2(self.ui.slider2.maximum() - v)

    def startTimer(self):
        self.counter = 0
        # 点击按钮后开始定时器
        self.timer.start(35)  # 每秒触发一次 timeout 事件

    def updateText(self):
        # 更新文本框中显示的内容为列表中的下一个元素
        if self.counter < len(self.display_list):
            self.class_nums2.setText(str(self.display_list[self.counter]))
            self.counter += 1
            print(self.counter)
        else:
            self.timer.stop()  # 当列表中的元素都显示完毕后停止定时器
            print(self.timer)

    # 使用摄像头进行实时检测
    def detect_camera(self):
        command = [
            'python', 'detect.py',
            '--weights', 'yolov5s.pt',
            '--source', '0',
            '--device', 'cpu'
        ]
        subprocess.run(command, shell=True, text=True)

    def select_dataset(self):
        # 打开文件对话框，选择要读取的文件
        file_path, _ = QFileDialog.getOpenFileName(None, '选择要读取的文件', '.',
                                                   'Excel Files (*.xlsx *.xls);;CSV Files (*.csv)')
        if file_path:
            if file_path.endswith('.xlsx'):
                print("正在读取 Excel 文件，请稍候...")
                try:
                    xlsx_file = pd.ExcelFile(file_path)
                    self.df = pd.read_excel(xlsx_file)
                except Exception as e:
                    print(e)
                print("读取成功！")
            elif file_path.endswith('.csv'):
                # 读取 csv 文件
                print("正在读取 CSV 文件，请稍候...")
                self.df = pd.read_csv(file_path)
                print("读取成功！")
            try:
                # 显示月份
                self.show_month.setText(self.df['Local Date'][0][:7])
                # 设置表格的行数和列数并显示
                self.xlsx.setRowCount(self.df.shape[0])
                self.xlsx.setColumnCount(self.df.shape[1])
                self.show_row.setText(str(self.df.shape[0]))
                self.show_col.setText(str(self.df.shape[1]))
                # 设置列标签
                self.xlsx.setHorizontalHeaderLabels(self.df.columns.tolist())
                # 填充表格
                for i in range(self.df.shape[0]):
                    for j in range(self.df.shape[1]):
                        item = QTableWidgetItem(str(self.df.iloc[i, j]))
                        self.xlsx.setItem(i, j, item)
            except Exception as e:
                print("请输入有效的数字！", e)
        else:
            print('用户取消了数据集选择操作')
            return

    def select_day(self):
        try:
            # 必须先选了数据集，才能进行这里的进一步操作
            if type(self.df) == int:
                print("未加载数据表xlsx/csv")
                # 弹出提示框
                dialog = QMessageBox()
                dialog.setWindowTitle('warning')
                dialog.setIcon(QMessageBox.Warning)
                dialog.setText("请先选择数据集！")
                dialog.exec_()
                return
            # 截取所选天数的部分
            day = self.day.text()
            print(day)
            # 显示到右边侧边栏上
            self.show_day.setText(day)
            self.subdf = self.df[self.df['Local Date'].str.endswith(day)]
            # 设置表格的行数和列数并显示
            self.xlsx.setRowCount(self.subdf.shape[0])
            self.xlsx.setColumnCount(self.subdf.shape[1])
            self.show_row.setText(str(self.subdf.shape[0]))
            self.show_col.setText(str(self.subdf.shape[1]))
            # 设置列标签
            self.xlsx.setHorizontalHeaderLabels(self.subdf.columns.tolist())
            # 填充表格
            for i in range(self.subdf.shape[0]):
                for j in range(self.subdf.shape[1]):
                    item = QTableWidgetItem(str(self.subdf.iloc[i, j]))
                    self.xlsx.setItem(i, j, item)
        except Exception as e:
            print("请输入有效的数字！", e)

    def export_chart5_1(self):
        # 拿到想要导出的路径
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Chart Image', '', 'Images (*.png *.jpg *.bmp)')
        if file_path:
            # 保存为图片
            self.figure5_1.savefig(file_path)
        else:
            print('用户取消了保存图片操作')
            return

    def export_chart5_2(self):
        # 拿到想要导出的路径
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Chart Image', '', 'Images (*.png *.jpg *.bmp)')
        if file_path:
            # 保存为图片
            self.figure5_2.savefig(file_path)
        else:
            print('用户取消了保存图片操作')
            return

    def export_chart5_3(self):
        # 拿到想要导出的路径
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Chart Image', '', 'Images (*.png *.jpg *.bmp)')
        if file_path:
            # 保存为图片
            self.figure5_3.savefig(file_path)
        else:
            print('用户取消了保存图片操作')
            return

    def export_chart6_1(self):
        # 拿到想要导出的路径
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Chart Image', '', 'Images (*.png *.jpg *.bmp)')
        if file_path:
            # 保存为图片
            self.figure6_1.savefig(file_path)
        else:
            print('用户取消了保存图片操作')
            return

    def export_chart6_2(self):
        # 拿到想要导出的路径
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Chart Image', '', 'Images (*.png *.jpg *.bmp)')
        if file_path:
            # 保存为图片
            self.figure6_2.savefig(file_path)
        else:
            print('用户取消了保存图片操作')
            return

    def export_chart6_3(self):
        # 拿到想要导出的路径
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Chart Image', '', 'Images (*.png *.jpg *.bmp)')
        if file_path:
            # 保存为图片
            self.figure6_3.savefig(file_path)
        else:
            print('用户取消了保存图片操作')
            return

    # 退出函数
    def myexit(self):
        exit()


if __name__ == "__main__":
    # 创建应用程序对象
    app = QApplication(sys.argv)
    # 创建自定义的窗口MyWindow对象，初始化相关属性和方法
    win = MyWindow()
    # 显示图形界面
    win.ui.show()
    # 启动应用程序的事件循环，可不断见监听点击事件等
    app.exec()
