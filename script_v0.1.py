
import math
import os
import random
import time

import numpy as np
from cv2 import cv2 as cv

savent_skill = [40,135,230,360,450,545,675,770,865]
clothes_skill = [880,965,1055]
skill_select = [230,540,850]

os.system('adb connect 127.0.0.1:7555')  # 连接mumu模拟器

# 转换图片格式
# adb 工具直接截图保存到电脑的二进制数据流在windows下"\n" 会被解析为"\r\n",
# 这是由于Linux系统下和Windows系统下表示的不同造成的，而Andriod使用的是Linux内核
def convert_img(path):
    with open(path, "br") as f:
        bys = f.read()
        bys_ = bys.replace(b"\r\n",b"\n")  # 二进制流中的"\r\n" 替换为"\n"
    with open(path, "bw") as f:
        f.write(bys_)

def get_screen():
    os.system('adb exec-out screencap -p > sc.png')  # 截取屏幕 sc.png
    #convert_img('sc.png')

def tap_screen(x, y, *delp):
    ''' 点击屏幕(x,y), delp偏移范围 '''
    if delp.count == 0:
        relx = x+random.randint(5, 10)
        rely = y+random.randint(5, 10)
    else:
        relx = x+random.randint(5, delp[0])
        rely = y+random.randint(5, delp[1])
    cmd = 'adb shell input tap {} {}'.format(relx, rely)
    print(cmd)
    os.system(cmd)

def swipe_sreen(x1, y1, x2, y2):
    ''' 滑动屏幕(x1,y1)>(x2,y2) '''
    cmd = 'adb shell input swipe {} {} {} {} '.format(x1, y1, x2, y2)
    print(cmd)
    os.system(cmd)

def img_match(temp):
    ''' 模板匹配:屏幕中是否有指定模板 '''
    os.system('adb exec-out screencap -p > sc.png')  # 截取屏幕 sc.png
    time_s = time.time()
    sc = cv.imread('sc.png')
    template = cv.imread(temp)
    result = cv.matchTemplate(template, sc, cv.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    position = max_loc
    match_degree = max_val
    print('{} ({},{}) cost: {:.2f}'.format(match_degree, position[0], position[1], time.time()-time_s))
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

def select_savent_skill(op):
    ''' 从者技能选择 '''
    tap_screen(savent_skill[op-1],550,50,50)
    time.sleep(3)

def select_clothes_skill(op):
    ''' 衣服技能选择 '''
    tap_screen(1165,285,45,55)
    time.sleep(1)
    tap_screen(clothes_skill[op-1],285,50,50)
    time.sleep(2)

def select_savent(op):
    ''' 从者选择 '''
    tap_screen(skill_select[op-1],325,190,205)
    time.sleep(3)

def savent_change():
    ''' 换人专属,3号与4号交换 '''
    tap_screen(465,270,135,150)
    tap_screen(670,270,135,150)
    tap_screen(510,595,260,60)
    time.sleep(5)

def card_select():
    ''' 从者指令卡选择，从攻击开始，宝具:1,指令卡:2,3 '''
    tap_screen(1090,565,80,80)
    time.sleep(2)
    tap_screen(350,140,130,120)
    tap_screen(320,430,130,120)
    tap_screen(575,430,130,120)

def start():
    ''' 桌面fgo图标 '''
    tap_screen(390, 115)

def enter_active():
    ''' 找到活动入口，进入，需要之前进入过一次 '''
    # swipe_sreen(1255,620,1255,110)
    # swipe_sreen(1255,110,1255,324)
    # swipe_sreen(960,652,960,109)
    tap_screen(670,190,510,80)
    time.sleep(2)

def find_battle():
    ''' 找到关卡，进入，需要之前进入过一次 '''
    tap_screen(640,190,440,100)
    time.sleep(0.5)
    if img_match('mark2.png'):
        tap_screen(310,270,650,110)
        tap_screen(740,540,200,45)

def find_helper():
    ''' 助战选择，开始战斗 '''
    # img_match('helper.png')
    # TODO:识别并选择助战
    tap_screen(1140,640,100,65)

def battle_1():
    ''' 回合1 '''
    select_savent_skill(3)
    select_savent_skill(4)
    select_savent(1)
    select_savent_skill(7)
    select_savent(1)
    select_savent_skill(9)
    select_savent(1)
    card_select()
    print('battle 1 finish')

def battle_2():
    ''' 回合2 '''
    select_savent_skill(8)
    select_clothes_skill(3)
    savent_change()
    select_savent_skill(7)
    select_savent(1)
    card_select()
    print('battle 2 finish')

def battle_3():
    ''' 回合3 '''
    select_savent_skill(5)
    select_savent_skill(6)
    select_savent(1)
    select_savent_skill(8)
    select_savent_skill(9)
    select_clothes_skill(1)
    card_select()

def battle_finish():
    ''' 战斗完成 '''
    tap_screen(500,550,400,130)#羁绊
    time.sleep(3)
    tap_screen(500,550,400,130)#经验
    time.sleep(2)
    tap_screen(980,645,260,60)#经验值

def battle():
    ''' 开始战斗 '''
    flag = 1
    while flag:
        if img_match('tag1.png'):
            battle_1()
            time.sleep(35)
            battle_2()
            time.sleep(35)
            battle_3()
            time.sleep(35)
            battle_finish()
            flag = 0
        else:
            time.sleep(1)
            print('Wait for battle')

def batterbattle():
    ''' 减少等待时间 '''
    flag = 1
    while flag:
        if img_match('mark1.png'):
            time.sleep(2)
            battle_1()
            flag = 0
        else:
            print('Wait for battle 1')
            time.sleep(2)
    time.sleep(20)
    flag = 1
    while flag:
        if img_match('mark1.png'):
            battle_2()
            flag = 0
        else:
            print('Wait for battle 2')
            time.sleep(2)
    time.sleep(20)
    flag = 1
    while flag:
        if img_match('mark1.png'):
            battle_3()
            flag = 0
        else:
            print('Wait for battle 3')
            time.sleep(2)
    time.sleep(20)
    flag = 1
    while flag:
        if img_match('mark3.png'):
            battle_finish()
            flag = 0
        else:
            print('wait for battle finish')
            time.sleep(2)


#img_match('tag1.png')

def process():
    t=time.time()
    find_helper()
    time.sleep(10)
    batterbattle()
    time.sleep(3)
    flag = 1
    while flag:
        if img_match('mark4.png'):
            find_battle()
            flag = 0
        else:
            time.sleep(2)
    print(round((time.time()-t),0))


process()
# get_screen()
# cv.imshow('11',cv.imread('sc.png'))
# cv.waitKey()
# cv.destroyAllWindows()
os.system('open.wav')
os.system('adb disconnect')  # 断开连接
