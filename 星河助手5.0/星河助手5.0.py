import os
import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QPushButton, QVBoxLayout,
    QSizePolicy, QSpacerItem, QPlainTextEdit, QLabel, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMouseEvent
from zhipuai import ZhipuAI
import datetime as dt
import ast
import platform
import tkinter as tk
from tkinter import messagebox
import psutil


class RoundedWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check)
        self.update_timer.start(100)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #2E3440;
                border-radius: 10px;
                border: none;
            }
        """)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)
        minimize_button = QPushButton("─")
        minimize_button.setFixedSize(30, 30)
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #4C566A;
                color: white;
                border-radius: 15px;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
        """)
        minimize_button.clicked.connect(self.showMinimized)
        button_layout.addWidget(minimize_button)

        close_button = QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #BF616A;
                color: white;
                border-radius: 15px;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #D08770;
            }
        """)
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)
        self.chat_scroll_area = QScrollArea(self)
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #3B4252;
                border-radius: 10px;
                border: 1px solid black;
            }
            QScrollBar:vertical {
                width: 0px;
            }
        """)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(5)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)

        self.chat_scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.chat_scroll_area)
        input_layout = QHBoxLayout()
        self.message_input = QPlainTextEdit(self)
        self.message_input.setPlaceholderText('输入消息...')
        self.message_input.setFixedHeight(60)
        self.message_input.setStyleSheet("""
            QPlainTextEdit {
                background-color: #3B4252;
                color: white;
                border-radius: 10px;
                border: 1px solid black;
                padding: 5px;
            }
            QScrollBar:vertical {
                width: 0px;
            }
            QScrollBar:horizontal {
                height: 0px;
            }
        """)
        input_layout.addWidget(self.message_input)
        send_button = QPushButton('发送')
        send_button.setFixedSize(80, 60)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: white;
                border-radius: 10px;
                border: 1px solid black;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
        """)
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)
        pcc_button = QPushButton('副驾驶')
        pcc_button.setFixedSize(80, 60)
        pcc_button.setStyleSheet("""
                    QPushButton {
                        background-color: #5E81AC;
                        color: white;
                        border-radius: 10px;
                        border: 1px solid black;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: #81A1C1;
                    }
                """)
        pcc_button.clicked.connect(self.send_pcc_message)
        input_layout.addWidget(pcc_button)
        history_button = QPushButton("历史记录")
        history_button.setFixedSize(80, 60)
        history_button.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: white;
                border-radius: 10px;
                border: 1px solid black;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
        """)
        history_button.clicked.connect(self.show_history)
        input_layout.addWidget(history_button)

        main_layout.addLayout(input_layout)
        self.resize(800, 900)
        self.center()

        self.drag_pos = None
        self.drag_edge = None
        self.resize_margin = 10

    def check(self):
        hs = open('question.txt', 'r', encoding='utf-8')
        message_ = hs.read()
        hs.close()
        if message_ != """""":
            self.send_ai_message()

    def send_pcc_message(self):
        message = self.message_input.toPlainText().strip()
        if message:
            n = dt.datetime.now()
            self.add_message("你", message)
            self.message_input.clear()
            self.chat_scroll_area.verticalScrollBar().setValue(
                self.chat_scroll_area.verticalScrollBar().maximum()
            )
            with open('聊天记录.txt', 'a', encoding='utf-8') as hs:
                hs.write(str(n) + '\n' + message + '\n\n')
            self.xinghe_pcc(message)

    def send_message(self):
        message = self.message_input.toPlainText().strip()
        if message:
            n = dt.datetime.now()
            self.add_message("你", message)
            self.message_input.clear()
            self.chat_scroll_area.verticalScrollBar().setValue(
                self.chat_scroll_area.verticalScrollBar().maximum()
            )
            with open('聊天记录.txt', 'a', encoding='utf-8') as hs:
                hs.write(str(n) + '\n' + message + '\n\n')
            with open('question.txt', 'w', encoding='utf-8') as hs:
                hs.write(message)

    def show_history(self):
        os.popen('历史记录查看.exe')

    def xinghe_pcc(self, message_):
        with open('聊天记录.txt', 'r', encoding='utf-8') as hs:
            history_ = hs.read()

        def chat_with_zhipu(question):
            client = ZhipuAI(api_key="4fee62c70f87c7e6a9507944c35f30b9.qRE9b8RnNCNx9XUM")  # 请填写您自己的APIKey
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "system",
                     "content": "你是星河助手，为用户答疑解惑，你的任务是提供专业、准确、有洞察力的建议或回答。"},
                    {"role": "user", "content": question},
                ],
            )
            answer = response.choices[0].message.content
            return answer

        information = platform.platform()
        pd = chat_with_zhipu(f'你现在要与：{user}对话。你与他的聊天记录为：{history_}，他跟你说：' + message_ + '。请用python代码实现用户后面所说，用户的操作系统信息为：' + str(information) + '，用户不一定提到的是打开电脑文件，所以根据用户的指令执行。如果用户的指令中还提到了有关电脑上查找或打开某个文件、应用，我提供了一个用户电脑所有文件的清单：all_file.txt，文件中以直接换行作为每个路径的分割符，请根据这个文件来查找用户所需的文件，all_file.txt中的文件路径与用户所描述的文件可能有所不同，可以先尝试列出几种有可能的文件名（包括用户所描述的），再用for循环遍历清单中的文件路径，并用in方法检查每一个文件路径中是否含有类似的文件名，请你试图寻找他，打开读取all_file.txt时，读取的格式为"utf-8"，如果有输出或错误信息，请把输出内容放在copilot_output.txt，把错误信息放在copilot_error.txt！') #你现在要与：{user}对话。你与他的聊天记录为：{history_}，他跟你说：' + message_ + '。请用python代码实现用户后面所说，可以根据all_file.txt中所供应的所需的文件路径，有可能文件名不是用户所描述的，请你列出几种可能的文件名，但不要忘记用户描述的文件名，进行操作；用户的操作系统信息为：' + str(information) + ' 如果用户的指令中还提到了有关电脑上查找或打开某个文件、应用，我提供了一个用户电脑所有文件的清单：all_file.txt，文件中以直接换行作为每个路径的分割符，请根据这个文件来查找用户所需的文件，all_file.txt中的文件路径与用户所描述的文件可能有所不同，比如说用户描述文件为file.exe，实际路径为D:\\path\\file.exe，可以用for循环遍历清单中的文件路径，并用in方法检查每一个文件路径中是否含有类似的文件名，请你试图寻找他，打开读取all_file.txt时，读取的格式为"utf-8"，如果有输出或错误信息，请把输出内容放在copilot_output.txt，把错误信息放在copilot_error.txt！'
        if "```python" in pd:
            py = ''''''
            output = pd.split('\n')
            f = 0
            for i in range(len(output) - 1):
                if output[i] == '```python':
                    f = 1
                    continue
                elif f == 1:
                    py += output[i] + '\n'
                    if output[i + 1] == '```':
                        break

            def find_imported_modules(code):
                imported_modules = []
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_modules.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        imported_modules.append(node.module)
                return imported_modules

            code = py
            imported_modules = find_imported_modules(code)
            print("检测到的导入模块:", imported_modules)
            import importlib
            try:
                for e in imported_modules:
                    some_module = importlib.import_module(e)
                    print('已导入' + e)
            except ModuleNotFoundError:
                print("some_module is not installed.")
                some_module = None

            print(py)
            print(output)
            try:
                exec(py)
            except Exception as e:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("错误", "星河助手执行错误：" + str(e))
                root.destroy()
                print('代码执行出错')
                with open('error_log.txt', 'a', encoding='utf-8') as log_file:
                    log_file.write(f"执行用户代码时出错: {str(e)}\n")
                    log_file.write(f"代码: {py}\n")
                    log_file.write(f"时间: {dt.datetime.now()}\n\n")

            n = dt.datetime.now()
            hs = open('聊天记录.txt', 'a', encoding='utf-8')
            hs.write(str(n) + '\n副驾功能开启：' + pd + '\n\n')
            hs.close()
            hs = open('question.txt', 'w', encoding='utf-8')
            hs.write('')
            hs.close()

    def send_ai_message(self):
        with open('question.txt', 'r', encoding='utf-8') as hs:
            message_ = hs.read()
        if not message_:
            return
        with open('聊天记录.txt', 'r', encoding='utf-8') as hs:
            history_ = hs.read()
        client = ZhipuAI(api_key="4fee62c70f87c7e6a9507944c35f30b9.qRE9b8RnNCNx9XUM")
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system",
                 "content": f"你是星河助手，为用户答疑解惑。你现在要与：{user}对话。你与他的聊天记录为：{history_}"},
                {"role": "user", "content": message_},
            ],
            stream=True
        )
        hs = open('question.txt', 'w', encoding='utf-8')
        hs.write('')
        hs.close()
        message_label = QLabel("星河助手: ")
        self.ms = '''星河助手: '''
        message_label.setStyleSheet("""
            QLabel {
                background-color: #4C566A;
                color: white;
                border-radius: 10px;
                padding: 8px;
                margin: 2px;
            }
        """)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.chat_layout.addWidget(message_label)
        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
        )

        for chunk in response:
            for i in chunk.choices[0].delta.content:
                for j in i:
                    print(j, end='')
                    self.update_ai_message(message_label, j)
                    time.sleep(0.01)
                    QApplication.processEvents()
        print('')
        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
        )
        QApplication.processEvents()
        if self.ms:
            n = dt.datetime.now()
            hs = open('聊天记录.txt', 'a', encoding='utf-8')
            hs.write(str(n) + '\n' + self.ms + '\n\n')
            hs.close()
            hs = open('question.txt', 'w', encoding='utf-8')
            hs.write('')
            hs.close()

    def update_ai_message(self, message_label, char):
        self.ms += char
        message_label.setText(self.ms)
        message_label.adjustSize()
        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
        )
        QApplication.processEvents()

    def add_message(self, sender, message):
        message_label = QLabel(f"{sender}: {message}")
        message_label.setStyleSheet("""
            QLabel {
                background-color: #4C566A;
                color: white;
                border-radius: 10px;
                padding: 8px;
                margin: 2px;
            }
        """)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.chat_layout.addWidget(message_label)

        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
            )

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()
            self.drag_edge = self.get_edge(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            if self.drag_edge:
                self.resize_window(event.globalPos())
            else:
                self.move(self.pos() + event.globalPos() - self.drag_pos)
                self.drag_pos = event.globalPos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_pos = None
            self.drag_edge = None

    def get_edge(self, pos):
        rect = self.rect()
        if pos.x() <= self.resize_margin:
            if pos.y() <= self.resize_margin:
                return "top-left"
            elif pos.y() >= rect.height() - self.resize_margin:
                return "bottom-left"
            else:
                return "left"
        elif pos.x() >= rect.width() - self.resize_margin:
            if pos.y() <= self.resize_margin:
                return "top-right"
            elif pos.y() >= rect.height() - self.resize_margin:
                return "bottom-right"
            else:
                return "right"
        elif pos.y() <= self.resize_margin:
            return "top"
        elif pos.y() >= rect.height() - self.resize_margin:
            return "bottom"
        return None
    def resize_window(self, global_pos):
        rect = self.rect()
        delta = global_pos - self.drag_pos
        geometry = self.geometry()

        if self.drag_edge == "left":
            geometry.setLeft(geometry.left() + delta.x())
        elif self.drag_edge == "right":
            geometry.setRight(geometry.right() + delta.x())
        elif self.drag_edge == "top":
            geometry.setTop(geometry.top() + delta.y())
        elif self.drag_edge == "bottom":
            geometry.setBottom(geometry.bottom() + delta.y())
        elif self.drag_edge == "top-left":
            geometry.setTopLeft(geometry.topLeft() + delta)
        elif self.drag_edge == "top-right":
            geometry.setTopRight(geometry.topRight() + delta)
        elif self.drag_edge == "bottom-left":
            geometry.setBottomLeft(geometry.bottomLeft() + delta)
        elif self.drag_edge == "bottom-right":
            geometry.setBottomRight(geometry.bottomRight() + delta)

        self.setGeometry(geometry)
        self.drag_pos = global_pos

if __name__ == "__main__":
    hs = open('cl.txt', 'w', encoding='utf-8')
    hs.write('0')
    hs.close()
    hs = open('question.txt', 'w', encoding='utf-8')
    hs.write('')
    hs.close()
    pd = os.listdir('./')
    flag = 0
    for process in psutil.process_iter():
        if process.name() == '实时扫描.exe':
            flag = 1
    if flag == 0:
        os.popen('实时扫描.exe')
    if '账号记录.txt' not in pd:
        a = open('账号记录.txt', 'w', encoding='utf-8')
        a.write('')
        a.close()
    if 'all_file.txt' not in pd:
        a = open('all_file.txt', 'w', encoding='utf-8')
        a.write('')
        a.close()
    hs = open('账号记录.txt', 'r', encoding='utf-8')
    user = hs.read()
    hs.close()
    if user == '':
        os.popen('登录窗口.exe')
    while True:
        hs = open('账号记录.txt', 'r', encoding='utf-8')
        user = hs.read()
        hs.close()
        if user != '':
            break
    app = QApplication(sys.argv)
    window = RoundedWindow()
    window.show()
    hs = open('cl.txt', 'r', encoding='utf-8')
    clp = hs.read()
    hs.close()
    sys.exit(app.exec_())