
import math
import os
import random
import time
import sys

import numpy as np
from cv2 import cv2 as cv
from PySide2 import QtCore,QtWidgets,QtGui,QtMultimedia
from PySide2.QtMultimedia import QMediaContent,QMediaPlayer
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *



#game start
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
        cmd = 'adb shell input tap {} {}'.format(relx, rely)
        self.msg_singal.emit(cmd)
        os.system(cmd)

    def swipe_sreen(self, x1, y1, x2, y2):
        ''' 滑动屏幕(x1,y1)>(x2,y2) '''
        cmd = 'adb shell input swipe {} {} {} {} '.format(x1, y1, x2, y2)
        self.msg_singal.emit(cmd)
        os.system(cmd)

    def img_match(self, temp):
        ''' 模板匹配:屏幕中是否有指定模板 '''
        os.system('adb exec-out screencap -p > gsc.png')  # 截取屏幕 sc.png
        time_s = time.time()
        sc = cv.imread('gsc.png')
        template = cv.imread(temp)
        result = cv.matchTemplate(template, sc, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        position = max_loc
        match_degree = max_val
        self.msg_singal.emit('{} ({},{}) cost: {:.2f}'.format(match_degree, position[0], position[1], time.time()-time_s))
        if round(match_degree, 2) == 1:
            return 1
        else:
            return 0
        th, tw = template.shape[:2]
        br = (position[0]+tw, position[1]+th)  # br是矩形右下角的点的坐标
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
                time.sleep(2)
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
#geme end

class gameThread(QThread):  
    finish_signal = Signal() # 信号类型：int
    msg_signal = Signal(str)
    m_lock = QMutex()
    def __init__(self, parent=None):  
        super().__init__(parent)
        self.g = game()
        self.g.msg_singal.connect(self.msg_slot)

    @Slot(str)
    def msg_slot(self,msg):
        self.msg_signal.emit(msg)

    def run(self): 
        self.m_lock.lock()
        self.g.process()
        self.m_lock.unlock()
        self.finish_signal.emit()
    def gamepause(self):
        self.m_lock.lock()
    def gameresume(self):
        self.m_lock.unlock()

class MyWidget(QWidget):
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

        self.t = QTimer()
        self.t.timeout.connect(self.setimage)
        self.t.start(2000)
        
        self.thread = gameThread() # 创建一个线程 
        self.thread.finish_signal.connect(self.gamefinish) # 线程发过来的信号挂接到槽
        self.thread.msg_signal.connect(self.receive_msg)

        url = QUrl.fromLocalFile('DingDong.mp3')
        content = QMediaContent(url)
        self.player = QMediaPlayer()
        self.player.setMedia(content)

        self.button.clicked.connect(self.gamestart)
        self.count = 0
        
    @Slot(str)
    def receive_msg(self,msg):
        self.msgtext.append(msg)

    def setimage(self):
        os.system('adb exec-out screencap -p > sc.png')  # 截取屏幕 sc.png
        #time.sleep(0.3)
        img=QImage('sc.png')
        # self.item = QGraphicsPixmapItem(QPixmap.fromImage(img.scaled(320,180)))
        # self.scene=QGraphicsScene()
        # self.scene.addItem(self.item)
        # self.imgshow.setScene(self.scene)
        self.showlable.setPixmap(QPixmap.fromImage(img.scaled(320,180)))

    def gamestart(self):
        self.count += 1
        self.countlable.setText('{}'.format(self.count))
        self.msgtext.clear()
        self.thread.start()
        self.showMinimized()
        
    def gamefinish(self):
        self.player.play()
        self.activateWindow()
        self.showNormal()


if __name__ == "__main__":
    os.system('adb connect 127.0.0.1:7555')  # 连接mumu模拟器
    app = QApplication()
    widget = MyWidget()
    widget.show()
    retcode = app.exec_()
    os.system('adb disconnect')  # 断开连接
    sys.exit(retcode)