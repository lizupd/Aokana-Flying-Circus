import time                 # 调用时间函数
import GetWindow            # 调用窗口索引
import HangarMenu as hm     # 调用机库识图
import pyautogui            # 调用鼠标移动
import keyboard             # 调用键盘按键
import Waitting             # 调用等待界面
import port8111             # 调用8111端口
import Fighting             # 调用战斗中图像识别
import Back                 # 返回界面识别
import Map                  # 地图识别

# 鼠标单击事件
def Click():
    pyautogui.click()
    time.sleep(0.1)
    pyautogui.mouseUp()

# CCRP开启
def ccrpStart():
    keyboard.press('o')
    time.sleep(0.1)
    keyboard.release('o')

# Esc单击事件
def Esc():
    keyboard.press('esc')
    time.sleep(0.1)
    keyboard.release('esc')

# 单击【加入战斗】
def starGame(x,y):
    pyautogui.moveTo(x + 650, y + 70)
    time.sleep(1)
    Click()

# 油门轴事件
def pushW():
    keyboard.press('w')
    time.sleep(3)
    keyboard.release('w')

# 鼠标移动事件：向上
def moveUp(m):
    keyboard.press(';')
    time.sleep(m)
    keyboard.release(';')

# 鼠标移动事件：向下
def moveDwon(m):
    keyboard.press('.')
    time.sleep(m)
    keyboard.release('.')

# 鼠标移动事件：向左
def moveL(m):
    keyboard.press(',')
    time.sleep(m)
    keyboard.release(',')
    print("左转")

# 鼠标移动事件：向右
def moveR(m):
    keyboard.press('/')
    time.sleep(m)
    keyboard.release('/')
    print("右转")

#################################################################################
#################################################################################
#################################################################################

flag = 0
while True:
    x, y = GetWindow.returData()   # 调用模块获得窗口坐标

    bollen = 0
    # 机库界面循环
    while True:
        if flag == 1:       # 已点击开始战斗
            break
        elif flag == 4:
            break
        # 将窗口坐标传入机库识图模块,获得机库识图模块返回值，值为1则成功，值为0则失败
        Bollen = hm.cooData(x, y)
        if Bollen == 0:
            starGame(x, y)
            time.sleep(1)
            Esc()
            time.sleep(1)
        else:
            print("图像识别成功")
            break

    if flag == 1:  # 已点击开始战斗
        print("已开始战斗")
    elif flag == 4:
        print("已开始战斗")
    else:
        bollen = 0
        while bollen == 0:
            # 点击开始游戏
            starGame(x, y)
            time.sleep(1)
            bollen = Back.imgRed(x, y)
            if bollen == 0:
                break
            elif bollen == 1:  # 载具锁定
                print("载具被锁定")
                pyautogui.moveTo(x + 640, y + 415)
                Click()
                time.sleep(60)
                flag = 2  # 载具锁定

    bollen = Waitting.waitSearch(x, y)
    pyautogui.moveTo(x + 950, y + 710)
    Click()
    time.sleep(5)

    # 取消按钮搜索
    while True:
        bollen = Waitting.startCancel(x, y)
        if bollen == 1:
            print("正在等待开始")
            time.sleep(1)
        else:
            break
    ############################################################
    #   战斗界面循环
    death = 0
    flag = 0    # 设立判断
    x, y = Fighting.getWin()    # 重新获得游戏窗口坐标
    throttle = 0
    while True:
        # 死亡判断
        if death == 1 and flag != 0:
            print("载具被摧毁")
            break

        # 起飞事件
        num = 0
        while throttle < 110 and flag == 0:    # 判断节流阀位置
            if num == 5:
                break
            elif flag == 1:
                break
            print(f"节流阀：{throttle} 正在加力;")
            pushW()
            Vy, Hm, throttle, IAS = port8111.getState()
            h1, h2 = Map.foundMap()
            num += 1

        while True:
            Vy, Hm, throttle, IAS = port8111.getState()
            print(f"空速：{IAS} 高度：{Hm} 爬升率：{Vy} 节流阀：{throttle}")

            if throttle == 0 and IAS < 100:    # 判断是否死亡
                death = 1
                print(f"节流阀：{throttle} 空速：{IAS} 可能死亡")
                time.sleep(3)
                break
            elif IAS < 250 and flag == 0:     # 判断是否具有起飞速度
                print(f"空速：{IAS} 无法起飞")
                break
            elif Hm < h1:      # 判断水平高度
                if Vy < 5:      # 判断爬升率
                    moveUp(m=0.05)
                    print("开始爬升")
                    break
                elif 7 > Vy > 5:
                    moveUp(m=0.01)
                    print("起飞微调")
                    break
                elif Vy > 15:
                    moveDwon(m=0.05)
                    print("起飞微调")
                    break
            elif Hm > h1 and flag == 0:
                flag = 1   # 标记为1 表示已经起飞过一次了
            elif h1 < Hm < h2:   # 稳定飞行区间
                if Vy < -3:
                    moveUp(m=0.01)
                    print("开始爬升")
                    break
                elif Vy > 10:
                    moveDwon(m=0.05)
                    print("开始下降")
                    break
                elif 10 > Vy > 5:
                    moveDwon(m=0.01)
                    print("微调下降")
                    break
                else:
                    print("保持高度")

                # CCRP寻路区
                if flag == 1:
                    aimX = Fighting.ccrp2(x, y)         # 获得准星坐标
                    if aimX is None:
                        aimX = Fighting.ccrp4(x, y)     # 获得准星坐标
                        if aimX is None:
                            flag = 1  # 下次再寻找准星
                            print("未找到准星")
                        elif aimX is not None:
                            flag = 2  # 准备开启CCRP
                    elif aimX is not  None:
                        flag = 2  # 准备开启CCRP
                if aimX is not None and flag == 2:    # 已获得屏幕中间坐标
                    flag = 3
                    ccrpStart()
                elif aimX is None:
                    break
                ccrpX = Fighting.ccrp1(x, y)    # 获得ccrp坐标
                if ccrpX is not None and aimX is not None:    # 已获得ccrp坐标
                    flag = 4
                    keyboard.press('u')     # 空格猴子
                    while ccrpX is not None:
                        if (ccrpX - aimX) > 50:    # 点在右边远处
                            moveR(m=0.05)
                            time.sleep(1)
                        elif (aimX - ccrpX) > 50:  # 点在左边远处
                            moveL(m=0.05)
                            time.sleep(1)
                        elif 2 < (ccrpX - aimX) < 50:  # 点在右边近处
                            moveR(m=0.01)
                            time.sleep(1)
                        elif 2 < (aimX - ccrpX) < 50:  # 点在左边近处
                            moveL(m=0.01)
                            time.sleep(1)
                        ccrpX = Fighting.ccrp1(x, y)
                    if ccrpX is None:
                        time.sleep(10)
                        keyboard.release('u')
                        h1 = 4500
                        h2 = 5500
                else:
                    flag = 3
            elif Hm > h2 and Vy > 0:  # 开始下降
                moveDwon(m=0.05)
                print("开始下降")

    # 判断处于哪一个界面
    x, y = Fighting.getWin()    # 重新获得游戏窗口坐标
    flag = 0
    num = 0
    while num < 5:
        back = Back.imgFound(x, y)
        if back == 1:       # 返回基地
            pyautogui.moveTo(x + 1000, y + 710)
            Click()
            print("返回基地")
            time.sleep(5)
        elif back == 2:     # 加入战斗
            pyautogui.moveTo(x + 640, y + 650)
            Click()
            print("重新加入战斗")
            time.sleep(1)
            flag = 1        # 已点击加入战斗
            bollen = Back.imgRed(x, y)
            if bollen == 1:     # 载具锁定
                print("载具被锁定")
                pyautogui.moveTo(x + 640, y + 415)
                Click()
                time.sleep(3)
                flag = 2        # 载具锁定
                break
            else:
                print("已重新开始")
                break
        elif back == 3:     # 确定
            pyautogui.moveTo(x + 640, y + 650)
            Click()
            time.sleep(3)
            flag = 3            # 研发
            bollen = Back.imgBuy(x, y)
            while bollen == 1:
                Esc()
                print("关闭购买")
                time.sleep(3)
                bollen = Back.imgBuy(x, y)

            bollen = Back.imgStart(x, y)
            while bollen != 1:
                pyautogui.moveTo(x + 1200, y + 565)
                Click()
                print("研发")
                bollen = Back.imgStart(x, y)
            flag = 4            # 研发完毕，加入战斗
            break
        num += 1

