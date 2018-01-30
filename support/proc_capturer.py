# -*- coding:utf-8 -*-

__author__ = 'Brick'
"""
opencv主线程是最下面的cam_loop()
"""
import cv2
import sys
import time
from support import optical_flow as otf
from support import color_detect as cdt
from support import harr_detect as hdt
from support.kalman import KalmanFilter


class BrickCV:
    def __init__(self):
        self.detect_flag = 1
        self.detect_flag_last = self.detect_flag
        self.del_all = False
        self.err_count = 0
        self.start_and_stop = True
        self.global_init()
        self.start_and_stop_last = True
        self.fps = 16

    def on_mouse(self, event, x, y, flags, param):
        """
        鼠标回调函数
        :param event:鼠标事件
        :param x:鼠标坐标
        :param y:鼠标坐标
        :param flags:系统标志位
        :param param:系统传入参数
        :return:
        """

        self.img2 = self.img.copy()
        if event == cv2.EVENT_LBUTTONDOWN and self.move_flag == False:  # 左键单击
            self.point1 = (x, y)
            self.point2 = (x, y)
            self.move_flag = True
        elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON) and self.move_flag == True:
            self.point2 = (x, y)


        elif event == cv2.EVENT_LBUTTONUP and self.move_flag == True:  # 左键释放
            if self.point2 != self.point1:
                min_x = min(self.point1[0], self.point2[0])
                min_y = min(self.point1[1], self.point2[1])
                width = abs(self.point1[0] - self.point2[0])
                height = abs(self.point1[1] - self.point2[1])
                x = int(min_x + 1.0 * width / 2)
                y = int(min_y + 1.0 * height / 2)
                gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
                self.object1 = otf.TrackObject('lotus', x, y, width, height, gray, self.feature_params, self.lk_params)
                self.min_obj = otf.MinObject(self.object1)
                self.object_enable = True
                self.move_flag = False
                self.obj_list.append(self.min_obj)
                #obj_q.put(self.obj_list)
                # obj_q.put(self.min_obj)

    def msg_handle(self, mas_q):
        """
        指令消息队列处理函数
        :param mas_q:指令消息队列
        :return:
        """

        if mas_q.empty() == False:
            msg = mas_q.get()
            if msg == 'Mouse':
                self.object_enable = False
                self.detect_flag = 0
            elif msg == 'Color':
                self.object_enable = False
                self.detect_flag = 1
            elif msg == 'Harr':
                self.object_enable = False
                self.detect_flag = 2
            elif msg == 'SSD':
                self.detect_flag = 3

            elif msg == 'YOLO':
                self.detect_flag = 4

            elif msg =='Start':
                self.start_and_stop = True
                print('\033[1;35m [BrickCV/Debug]Detecter and Tracker is Start!\033[0m')


            elif msg =='Stop':
                self.start_and_stop = False
                print('\033[1;35m [BrickCV/Debug]Detecter and Tracker is Stop!\033[0m')

            elif msg[:3] == 'URL':

                url=msg[3:]
                try:
                    if url!= '0':
                        del self.cap
                        self.cap = cv2.VideoCapture(url)
                    else:
                        del self.cap
                        self.cap = cv2.VideoCapture(0)
                except:
                    print('Path error!')
                    self.cap = cv2.VideoCapture(0)
            elif msg=='Clear':
                try:
                    self.object1.existance = False
                except:
                    print('Object is empty!')
            elif msg == 'kill all':
                self.del_all=True

    def img2gui(self,the_q,img):
        """
        将图像显示在主窗口
        :param the_q: 图像消息队列
        :param self.img: 待显示图像
        :return:
        """
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            the_q.put(img)

    def global_init(self):
        """
        初始化全局变量
        :return:
        """

        self.move_flag=False
        self.object_enable=False
        self.obj_list=[]
        self.feature_params = dict(maxCorners=200,
                              qualityLevel=0.05,
                              minDistance=7,
                              blockSize=7)

        # 设置 lucas kanade 光流场的参数
        # maxLevel 为使用图像金字塔的层数
        self.lk_params = dict(winSize=(15, 15),
                         maxLevel=2,
                         criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        self.point1 = (0,0)
        self.point2 = (0,0)
        self.object1 = None
        self.min_obj = None

    def mouse_detect_handle(self,the_q, obj_q):
        """
        鼠标框选处理函数
        :param the_q: 图像消息队列
        :param obj_q: 目标消息队列
        :return:
        """

        self.img2 = self.img.copy()
        try:
            if self.detect_flag_last != 0:
                cv2.namedWindow('Mouse Capture')
                cv2.setMouseCallback('Mouse Capture', self.on_mouse)

            if self.object_enable == False and self.start_and_stop == True:  # 无目标时
                try:
                    if self.point2 != self.point1:
                        size=(abs(self.point2[0] - self.point1[0]),abs(self.point2[1] - self.point1[1]))
                        ctr=(int(self.point1[0]+size[0]/2),int(self.point1[1]+size[1]/2))
                        rad=int(1.0*(size[0]+size[1])/4.0)
                        cv2.circle(self.img2, ctr, int(rad), (0, 200, 0), thickness=3)
                except:
                    print('\033[1;31;40m BrickCVError[001]: mouse_detect error! \033[0m!')

            else:  # 存在目标时

                nowgray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
                if self.start_and_stop == True:
                    ctr, rad = self.object1.object_refresh(nowgray)
                self.min_obj = otf.MinObject(self.object1)
                self.min_obj.draw_object(self.img2)
                # self.object1.draw_feature(self.img2)
                self.min_obj.draw_center(self.img2)
                self.obj_list[0]=self.min_obj

                if self.object1.existance==False:
                    del self.object1
                    self.obj_list.clear()
                    self.object_enable = False
                    self.point2 = self.point1 = (0,0)
                else:
                    obj_q.put(self.obj_list)
        except:
            if self.start_and_stop == False:
                if self.start_and_stop_last == True:
                    print('\033[1;35m [BrickCV/Debug]Detecter and Tracker have stop!\033[0m')
            else:
                print('\033[1;31m BrickCVError[005]: Mouse_tracker error! \033[0m')

                        # if self.start_and_stop == False:
                        #     if self.start_and_stop_last == True:
                        #         print('\033[1;35m Object is empty!!\033[0m')
                        # else:
                        #     print('\033[1;31m BrickCVError[002]: mouse_tracker error! \033[0m')

        cv2.putText(self.img2, 'FPS %0.2f' % self.fps, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color=(10, 190, 235),
                    thickness=2)
        cv2.imshow('Mouse Capture', self.img2)
        self.img2gui(the_q, self.img2)
        cv2.waitKey(20)

    def color_detect_handle(self, the_q, obj_q):

        try:
            self.img2 = self.img.copy()
            if self.object_enable == False and self.start_and_stop == True:  # 无目标时
                obj, num = cdt.color_detect2(self.img2)
                if num > 0:
                    ctr = obj[0][0]
                    rad = obj[0][1]

                    if ctr[0]>0 and ctr[0] < 640 and ctr[1] > 0 and ctr[1] < 480 and rad > 20:

                        nowgray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
                        self.object1 = otf.TrackObject('lotus', int(ctr[0]), int(ctr[1]), rad*2, rad*2, nowgray, self.feature_params, self.lk_params)
                        self.min_obj = otf.MinObject(self.object1)
                        self.obj_list.append(self.min_obj)
                        self.object_enable = True

            else:  # 存在目标时

                nowgray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
                if self.start_and_stop == True:
                    ctr, rad = self.object1.object_refresh(nowgray)


                self.min_obj = otf.MinObject(self.object1)
                self.min_obj.draw_object(self.img2)
                self.min_obj.draw_center(self.img2)
                self.obj_list[0] = self.min_obj
                obj_q.put(self.obj_list)
                if self.object1.existance==False:
                    del self.object1
                    self.obj_list.clear()
                    self.object_enable = False
        except:
            if self.start_and_stop == False:
                if self.start_and_stop_last == True:
                    print('\033[1;35m [BrickCV/Debug]Object is empty!!\033[0m')
            else:
                print('\033[1;31m BrickCVError[005]: color_handle error! \033[0m')

        cv2.putText(self.img2, 'FPS %0.2f' % self.fps, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color=(10, 190, 235),
                    thickness=2)
        self.img2gui(the_q, self.img2)
        cv2.waitKey(20)

    def harr_detect_handle(self, the_q, obj_q):
        self.img2 = self.img.copy()
        try:
            if self.object_enable == False and self.start_and_stop == True: # 无目标时
                self.cascade = hdt.HarrDetect('support/cascade.xml')
                self.confirm = hdt.HarrDetect('support/cascade.xml')
                tmp = self.cascade.detect(self.img2)
                objs = self.cascade.rect2cir()
                if len(objs) > 0:
                    (ctr,rad) = objs[0]
                    if ctr[0]>0 and ctr[0] < 640 and ctr[1] > 0 and ctr[1] < 480 :

                        nowgray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
                        self.object1 = otf.TrackObject('lotus', int(ctr[0]), int(ctr[1]), rad*2, rad*2, nowgray, self.feature_params, self.lk_params)
                        self.min_obj = otf.MinObject(self.object1)
                        self.obj_list.append(self.min_obj)
                        self.object_enable = True


            else:  # 存在目标时
                nowgray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
                if self.start_and_stop == True:
                    ctr, rad = self.object1.object_refresh(nowgray)

                self.min_obj = otf.MinObject(self.object1)
                self.min_obj.draw_object(self.img2)
                self.min_obj.draw_center(self.img2)
                self.obj_list[0] = self.min_obj
                obj_q.put(self.obj_list)
                if self.start_and_stop == True:
                    (min_x,min_y,max_x,max_y) = self.object1.get_rect()
                    search=self.img2[int(min_y):int(max_y),int(min_x):int(max_x)]
                    _ = self.confirm.detect(search)
                    tmps = self.confirm.rect2cir()

                    if len(tmps) == 0:
                        self.err_count=self.err_count+1
                        if self.err_count>40:
                            self.object1.existance = False
                            self.err_count = 0
                        else:
                            self.err_count = 0

                if self.object1.existance==False:
                    del self.object1
                    self.obj_list.clear()
                    self.object_enable = False
        except:
            if self.start_and_stop == False:
                if self.start_and_stop_last == True:
                    print('\033[1;35m [BrickCV/Debug]Object is empty!!\033[0m')
            else:
                print('\033[1;31m BrickCVError[005]: harr_tracker error! \033[0m')

        cv2.putText(self.img2, 'FPS %0.2f' % self.fps, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color=(10, 190, 235),
                    thickness=2)
        self.img2gui(the_q, self.img2)
        cv2.waitKey(20)

    def cam_loop(self, the_q, mas_q, obj_q, event):
        """
        opencv主线程
        :param the_q: 图像消息队列
        :param mas_q: 指令接收消息队列
        :param obj_q: 目标数据消息队列
        :param event: GUI同步事件
        :return:
        """


        self.cap = cv2.VideoCapture(0)
        a=0
        while True:
            start_time = time.time()
            if self.del_all == True:
                break
            _, self.img = self.cap.read()
            self.img = cv2.flip(self.img, 1)
            if self.img is not None:
                self.msg_handle(mas_q)

                if self.detect_flag==0:
                    self.mouse_detect_handle(the_q, obj_q)
                elif self.detect_flag==1:
                    if self.detect_flag_last == 0:
                        cv2.destroyWindow('Mouse Capture')
                        self.img2gui(the_q, self.img)
                    self.color_detect_handle(the_q, obj_q)
                elif self.detect_flag==2:
                    if self.detect_flag_last == 0:
                        cv2.destroyWindow('Mouse Capture')
                        self.img2gui(the_q, self.img)

                    self.harr_detect_handle(the_q, obj_q)
                else:
                    if self.detect_flag_last == 0:
                        cv2.destroyWindow('Mouse Capture')
                        self.img2gui(the_q, self.img)

                    if self.object1 != None:
                        del self.object1
                        self.object1 = None
                        self.global_init()
                    self.img2gui(the_q, self.img)
                self.detect_flag_last = self.detect_flag
                self.start_and_stop_last = self.start_and_stop
                end_time = time.time()
                self.fps=1/(end_time - start_time)


                event.set()



