
import math
import random
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


# 游戏过程
class game(QObject):
    msg_singal = Signal(str)
    #技能1-9
    savent_skill = [40,135,230,360,450,545,675,770,865]
    #衣服技能
    clothes_skill = [880,965,1055]
    #技能选人
    skill_select = [230,540,850]

    def tap_screen(self, x, y, *delp):
        ''' 点击屏幕(x,y), delp偏移范围 '''
        if delp.count == 0:
            relx = x+random.randint(5, 10)
            rely = y+random.randint(5, 10)
        else:
            relx = x+random.randint(5, delp[0])
            rely = y+random.randint(5, delp[1])
        self.msg_singal.emit('adb shell input tap {} {}'.format(relx, rely))
        command = ["adb", "shell", "input", "tap"]
        command.append("{}".format(relx))
        command.append("{}".format(rely))
        subprocess.run(command,stdout=subprocess.PIPE)

    def swipe_sreen(self, x1, y1, x2, y2):
        ''' 滑动屏幕(x1,y1)>(x2,y2) '''
        self.msg_singal.emit('adb shell input swipe {} {} {} {} '.format(x1, y1, x2, y2))
        command = ["adb", "shell", "input", "swipe"]
        command.append("{}".format(x1))
        command.append("{}".format(y1))
        command.append("{}".format(x2))
        command.append("{}".format(y2))
        subprocess.run(command,stdout=subprocess.PIPE)

    def img_match(self, temp):
        ''' 模板匹配:屏幕中是否有指定模板 '''
        time_s = time.time()
        image_bytes = subprocess.run(["adb", "exec-out", "screencap","-p"], stdout=subprocess.PIPE).stdout
        sc = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)    
        template = cv2.imread(temp)
        result = cv2.matchTemplate(template, sc, cv2.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        position = max_loc
        match_degree = max_val
        self.msg_singal.emit('{} ({},{}) cost: {:.2f}'.format(match_degree, position[0], position[1], time.time()-time_s))
        if round(match_degree, 2) == 1:
            return 1
        else:
            return 0
        # 标记匹配区域并显示
        # th, tw = template.shape[:2]
        # br = (position[0]+tw, position[1]+th)  # br是矩形右下角的点的坐标
        # matched_img=sc[position[1]:br[1],position[0]:br[0]]
        # cv.rectangle(sc, position, br, (0, 0, 255), 2)
        # cv.namedWindow("match-" + np.str(md), cv.WINDOW_NORMAL)
        # cv.imshow("match-" + np.str(md), target)
        # cv.imshow('11',matched_img)
        # cv.waitKey()
        # cv.destroyAllWindows()

    def select_savent_skill(self, op):
        ''' 从者技能选择 '''
        self.tap_screen(self.savent_skill[op-1],550,50,50)
        time.sleep(3)

    def select_clothes_skill(self, op):
        ''' 衣服技能选择 '''
        self.tap_screen(1165,285,45,55)
        time.sleep(1)
        self.tap_screen(self.clothes_skill[op-1],285,50,50)
        time.sleep(2)

    def select_savent(self,op):
        ''' 从者选择 '''
        self.tap_screen(self.skill_select[op-1],325,190,205)
        time.sleep(3)

    def savent_change(self):
        ''' 换人专属,3号与4号交换 '''
        self.tap_screen(465,270,135,150)
        self.tap_screen(670,270,135,150)
        self.tap_screen(510,595,260,60)
        time.sleep(5)

    def card_select(self):
        ''' 从者指令卡选择，从攻击开始，宝具:1,指令卡:2,3 '''
        self.tap_screen(1090,565,80,80)
        time.sleep(2)
        self.tap_screen(350,140,130,120)
        self.tap_screen(320,430,130,120)
        self.tap_screen(575,430,130,120)

    def find_battle(self):
        ''' 找到关卡，进入，需要之前进入过一次 '''
        self.tap_screen(640,190,440,100)
        time.sleep(0.5)
        if self.img_match('mark2.png'):
            self.tap_screen(310,270,650,110)
            self.tap_screen(740,540,200,45)

    def find_helper(self):
        ''' 助战选择，开始战斗 '''
        # TODO:识别并选择助战
        self.tap_screen(1140,640,100,65)

    def battle_1(self):
        ''' 回合1 '''
        self.select_savent_skill(3)
        self.select_savent_skill(4)
        self.select_savent(1)
        self.select_savent_skill(7)
        self.select_savent(1)
        self.select_savent_skill(9)
        self.select_savent(1)
        self.card_select()

    def battle_2(self):
        ''' 回合2 '''
        self.select_savent_skill(8)
        self.select_clothes_skill(3)
        self.savent_change()
        self.select_savent_skill(7)
        self.select_savent(1)
        self.card_select()

    def battle_3(self):
        ''' 回合3 '''
        self.select_savent_skill(5)
        self.select_savent_skill(6)
        self.select_savent(1)
        self.select_savent_skill(8)
        self.select_savent_skill(9)
        self.select_clothes_skill(1)
        self.card_select()

    def battle_finish(self):
        ''' 战斗完成 '''
        self.tap_screen(500,550,400,130)#羁绊
        time.sleep(3)
        self.tap_screen(500,550,400,130)#经验
        time.sleep(2)
        self.tap_screen(980,645,260,60)#经验值

    def battle(self):
        ''' 减少等待时间 '''
        flag = 1
        while flag:
            if self.img_match('mark1.png'):
                time.sleep(4)
                self.battle_1()
                flag = 0
            else:
                self.msg_singal.emit('Wait for battle 1')
                time.sleep(2)
        time.sleep(20)
        flag = 1
        while flag:
            if self.img_match('mark1.png'):
                self.battle_2()
                flag = 0
            else:
                self.msg_singal.emit('Wait for battle 2')
                time.sleep(2)
        time.sleep(20)
        flag = 1
        while flag:
            if self.img_match('mark1.png'):
                self.battle_3()
                flag = 0
            else:
                self.msg_singal.emit('Wait for battle 3')
                time.sleep(2)
        time.sleep(20)
        flag = 1
        while flag:
            if self.img_match('mark3.png'):
                self.battle_finish()
                flag = 0
            else:
                self.msg_singal.emit('wait for battle finish')
                time.sleep(2)

    def process(self):
        t=time.time()
        self.find_helper()
        time.sleep(10)
        self.battle()
        time.sleep(3)
        flag = 1
        while flag:
            if self.img_match('mark4.png'):
                self.find_battle()
                flag = 0
            else:
                time.sleep(2)
        self.msg_singal.emit('用时: {}'.format(round((time.time()-t),0)))

# win窗口操作
class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""
    def __init__ (self):
        """Constructor"""
        self._handle = None
        self.done = False

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
        self.done = False
        if self._handle > 0:
            win32gui.SendMessage(self._handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
            win32gui.SetForegroundWindow(self._handle)
            self.done = True
        return self.done

# 游戏所在的线程
class gameThread(QThread):  
    finish_signal = Signal() # 信号类型：int
    msg_signal = Signal(str)
    m_lock = QMutex()
    def __init__(self, parent=None):  
        super().__init__(parent)
        self.w = WindowMgr()
        self.w.find_window_wildcard(".*MuMu模拟器.*")

    @Slot(str)
    def msg_slot(self,msg):
        self.msg_signal.emit(msg)

    def run(self): 
        self.m_lock.lock()
        g = game()
        g.msg_singal.connect(self.msg_slot)
        g.process()
        del g
        self.m_lock.unlock()
        self.finish_signal.emit()
        self.w.set_foreground()

    def gamepause(self):
        self.m_lock.lock()
    def gameresume(self):
        self.m_lock.unlock()

# UI更新线程
class uiThread(QThread):
    # 通过类成员对象定义信号对象
    uisignal = Signal(QPixmap)
    def __init__(self):
        super(uiThread, self).__init__()
        self.flag = True
    def run(self):
        while self.flag:
            image_bytes = subprocess.run(["adb", "exec-out", "screencap","-p"], stdout=subprocess.PIPE).stdout
            image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            image = cv2.resize(image,(320,180),cv2.INTER_AREA)
            height, width = image.shape[:2]
            bytesPerline = 3 * width
            qImg = QImage(image.data, width, height, bytesPerline, QImage.Format_RGB888).rgbSwapped()
            qPix = QPixmap.fromImage(qImg.scaled(320,180))
            self.uisignal.emit(qPix)
            del image,image_bytes,qImg,qPix,height,width,bytesPerline
    def exithread(self):
        self.flag = False

# 主窗口
class MyWidget(QWidget):
    uiexit =  Signal()
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle('FGO脚本')
        self.setFixedSize(350,430)
        self.button = QPushButton("开始")
        self.showlable = QLabel()
        self.showlable.setAlignment(Qt.AlignCenter)
        #self.imgshow = QGraphicsView(self) # 通过graphicsview显示
        self.lable = QLabel('计数')
        self.lable.setAlignment(Qt.AlignCenter)
        self.countlable = QLabel()
        self.countlable.setAlignment(Qt.AlignCenter)
        self.toplay = QHBoxLayout()
        self.toplay.addWidget(self.showlable)
        self.botlay = QHBoxLayout()
        self.botlay.addWidget(self.lable)
        self.botlay.addWidget(self.countlable)
        self.botlay.addWidget(self.button)

        self.msgtext = QTextBrowser()
        self.msgtext.setAlignment(Qt.AlignLeft)

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.toplay)
        self.layout.addLayout(self.botlay)
        self.layout.addWidget(self.msgtext)
        self.setLayout(self.layout)

        self.gthread = gameThread() # 创建一个线程 
        self.gthread.finish_signal.connect(self.gamefinish) # 线程发过来的信号挂接到槽
        self.gthread.msg_signal.connect(self.receive_msg)

        self.uithread = uiThread() # 更新UI
        self.uithread.uisignal.connect(self.setimage)
        self.uiexit.connect(self.uithread.exithread)

        url = QUrl.fromLocalFile('DingDong.mp3')
        content = QMediaContent(url)
        self.player = QMediaPlayer()
        self.player.setMedia(content)

        self.button.clicked.connect(self.gamestart)

        self.count = 0
        self.uithread.start()

    def __del__(self):
        self.uiexit.emit()
        subprocess.run(["adb", "disconnect"],stdout=subprocess.PIPE)  # 断开连接

    @Slot(str)
    def receive_msg(self,msg):
        self.msgtext.append(msg)
    @Slot(QPixmap)
    def setimage(self,pixmap):
        # 截取屏幕
        # image_bytes = subprocess.run(["adb", "exec-out", "screencap","-p"], stdout=subprocess.PIPE).stdout
        # image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        # image = cv2.resize(image,(320,180),cv2.INTER_AREA)
        # height, width = image.shape[:2]
        # bytesPerline = 3 * width
        # qImg = QImage(image.data, width, height, bytesPerline, QImage.Format_RGB888).rgbSwapped()
        # self.item = QGraphicsPixmapItem(QPixmap.fromImage(qImg.scaled(320,180)))
        # self.scene=QGraphicsScene()
        # self.scene.addItem(self.item)
        # self.imgshow.setScene(self.scene)
        # self.showlable.setPixmap(QPixmap.fromImage(qImg.scaled(320,180)))
        self.showlable.setPixmap(pixmap)

    def gamestart(self):
        self.button.setEnabled(False)
        self.count += 1
        self.countlable.setText('{}'.format(self.count))
        self.msgtext.clear()
        self.gthread.start()
        self.showMinimized()

    def gamefinish(self):
        self.player.play()
        self.button.setEnabled(True)
        self.activateWindow()
        self.showNormal()

if __name__ == "__main__":
    stdout = subprocess.run(["adb", "connect", "127.0.0.1:7555"],stdout=subprocess.PIPE).stdout  # 连接mumu模拟器
    app = QApplication()
    widget = MyWidget()
    widget.show()
    widget.msgtext.append(str(stdout,encoding="gbk"))
    retcode = app.exec_()
    del widget
    # widget.uithread.exit(0)
    # subprocess.run(["adb", "disconnect"])  # 断开连接
    sys.exit(retcode)
