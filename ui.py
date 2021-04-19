# -*- coding: utf-8 -*-

import base64
import os
import re
import subprocess
import sys
import time

import numpy as np
from cv2 import cv2
from PySide2 import QtCore, QtGui, QtMultimedia, QtWidgets
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtMultimedia import QMediaContent, QMediaPlayer
from PySide2.QtWidgets import *
from win32 import win32gui 
from win32.lib import win32con


# 继承QThread
class Runthread(QThread):
    #  通过类成员对象定义信号对象
    sendate = Signal(bytes)

    def __init__(self):
        super(Runthread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        while True:
            image_bytes = subprocess.run(["adb", "exec-out", "screencap","-p"], stdout=subprocess.PIPE).stdout
            self.sendate.emit(image_bytes)

class Ui_Form(QWidget):
    def setupUi(self):
        self.setObjectName("Form")
        self.resize(478, 355)
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(200, 310, 71, 31))
        self.pushButton.setObjectName("pushButton")
        self.label_sc = QtWidgets.QLabel(self)
        self.label_sc.setGeometry(QtCore.QRect(10, 10, 451, 291))
        self.label_sc.setStyleSheet("background-color: rgb(255, 255, 255);border-color: rgb(255, 255, 255);")
        self.label_sc.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_sc.setText("")
        self.label_sc.setObjectName("label_sc")
        self.label_sc.setAlignment(Qt.AlignCenter)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(10, 320, 54, 12))
        self.label.setObjectName("label")
        self.label_count = QtWidgets.QLabel(self)
        self.label_count.setGeometry(QtCore.QRect(70, 320, 54, 12))
        self.label_count.setText("")
        self.label_count.setObjectName("label_count")
        self.checkBox = QtWidgets.QCheckBox(self)
        self.checkBox.setGeometry(QtCore.QRect(390, 310, 71, 16))
        self.checkBox.setObjectName("checkBox")

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.thread = Runthread()
        self.thread.sendate.connect(self.setimg)

        self.pushButton.clicked.connect(self.startui)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.pushButton.setText(QtWidgets.QApplication.translate("Form", "开始", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Form", "已完成：", None, -1))
        self.checkBox.setText(QtWidgets.QApplication.translate("Form", "置顶", None, -1))

    def startui(self):
        if self.thread.isRunning():
            self.thread.exit(0)
            self.pushButton.setText(QtWidgets.QApplication.translate("Form", "开始", None, -1))
        else:
            self.thread.start()
            self.pushButton.setText(QtWidgets.QApplication.translate("Form", "结束", None, -1))

    def setimg(self,image_bytes):
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        image = cv2.resize(image,(320,180),cv2.INTER_AREA)
        height, width = image.shape[:2]
        qImg = QImage(image.data, width, height, 3 * width, QImage.Format_RGB888).rgbSwapped()
        w.label_sc.setPixmap(QPixmap.fromImage(qImg))


class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""
    def __init__ (self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name = None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        '''Pass to win32gui.EnumWindows() to check all the opened windows'''
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) != None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        done = False
        if self._handle > 0:
            win32gui.SendMessage(self._handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
            win32gui.SetForegroundWindow(self._handle)
            print(self._handle)
            done = True
        return done

    def set_minisize(self):
        """set the window minisize"""
        win32gui.ShowWindow(self._handle,2)
        # done = False
        # if self._handle > 0:
        #     win32gui.SendMessage(self._handle, win32con.WM_CLOSE)
        #     win32gui.CloseWindow(self._handle)
        #     print(self._handle)
        #     done = True
        # return done

if __name__ == '__main__':
    app = QApplication()
    w = Ui_Form()
    w.setupUi()
    w.show()
    retcode = app.exec_()
    sys.exit(retcode)
