# -*- coding:utf-8 -*-
__author__ = 'Brick'
import cv2
import numpy as np


class TrackObject:
    """
        跟踪目标类模版
        该模版仅针对单个目标的状态及其预测方法，若跟踪多个目标请使用List和append方法添加新的跟踪目标
        该类包含跟踪目标的位置大小信息及其角点分布属性
        还包含角点提取和角点位置预测，目标位置预测和坐标变换等方法
    """
    def __init__(self, name, x, y, width, height, gray, feature_params, lk_params):
        """
           跟踪目标对象构造函数

           :param name: 跟踪目标的名称
           :param x,y: 目标中心坐标
           :param width,height: 目标框宽高
           :param gray: 当前目标所处的灰度图
           :param feature_params: 特征点提取参数
           :param lk_params: L-K光流跟踪器参数
           :return 创建一个跟踪对象
        """
        self.name=name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rad = (self.width+self.height)/2
        self.left = x-width/2
        if self.left < 0:
            self.left = 0
        self.top = y-height/2
        if self.top < 0:
            self.top = 0
        self.right = x+width/2
        if self.right > 640:
            self.right = 640
        self.bottom = y+height/2
        if self.bottom > 480:
            self.right = 480
        self.existance = True

        self.last_gray = gray
        self.locally_gray=gray[int(self.top):int(self.bottom), int(self.left):int(self.right)]

    # 设置 ShiTomasi 角点检测的默认参数
        self.feature_params = feature_params

        # 设置 lucas kanade 光流场的默认参数
        # maxLevel 为使用图像金字塔的层数
        self.lk_params = lk_params
        self.p0 = self.get_feature(self.locally_gray)
        self.p0[:,0,0]=self.p0[:,0,0]+self.left
        self.p0[:,0,1]=self.p0[:,0,1]+self.top

    def __findDistance(self, r1, c1, r2, c2):
        #获得两点距离
        d = (r1 - r2) ** 2 + (c1 - c2) ** 2
        d = d ** 0.5
        return d

    def keypointToPoint(self, kp):
        '''
        from keypoints to points
        '''
        point = np.zeros(len(kp) * 2, np.float32)
        for i in range(len(kp)):
            point[i * 2] = kp[i].pt[0]
            point[i * 2 + 1] = kp[i].pt[1]

        point = point.reshape(-1, 2)
        return point

    def get_rect(self):
        min_x = self.x - self.rad
        min_y = self.y - self.rad
        max_x = self.x + self.rad
        max_y = self.y + self.rad
        if min_x<0:
            min_x=0
        if min_y<0:
            min_y=0
        if max_x>640:
            max_x=640
        if max_y>480:
            max_y=480
        return (min_x, min_y, max_x, max_y)

    def get_feature(self, gray):
        """
        获取原始图的特征点

        :param gray: 局部灰度图
        :return feature:所提取的角点
        """
        """
        surf = cv2.xfeatures2d.SURF_create()
        kp,des = surf.detectAndCompute(gray, None)
        tmp=self.keypointToPoint(kp)
        feature = np.zeros([len(kp),1,2], np.uint16)
        feature[:, 0, 0] = 1
        feature[:, 0, 1] = 2
        
        """

        feature = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)

        return feature


    def LK_setting(self, lk_params):
        """
        LK光流法参数设置

        :param lk_params: 待设置参数字典
        """
        self.lk_params = lk_params

    def feature_setting(self, feature_params):
        """
        特征点提取参数设置

        :param lk_params: 待设置参数字典
        """
        self.feature_params=feature_params

    def object_refresh(self, nowgray):
        """
        目标位置预测函数（核心方法）
            方法实现详解：
                首先利用L-K光流法预测每一个特征点在新图像中的位置，求得新角点点集的重心，
                对于超出一定半径范围的角点予以删除，再利用minEnclosingCircle函数求得包含
                特征点集的最小圆，得到新的目标框，最后将过去的数据进行更新操作
        :param nowgray: 待预测灰度图
        :return [ctr, rad]: 目标中心和半径
        """
        self.p1, st, err = cv2.calcOpticalFlowPyrLK(self.last_gray, nowgray, self.p0, None, **self.lk_params)
        r_add, c_add = 0, 0
        for p in self.p1:
            r_add = r_add + p[0][1]
            c_add = c_add + p[0][0]

        self.x = int(1.0 * r_add / len(self.p1))
        self.y = int(1.0 * c_add / len(self.p1))

        new_corners_updated = self.p1.copy()
        tobedel = []
        for index in range(len(self.p1)):#角点删除
            if self.__findDistance(self.p1[index][0][1], self.p1[index][0][0], int(self.x), int(self.y)) > 90:
                tobedel.append(index)
        new_corners_updated = np.delete(new_corners_updated, tobedel, 0)

        if len(new_corners_updated) < 10:
            print('OBJECT LOST!')
            self.existance = False
        ctr, rad = cv2.minEnclosingCircle(new_corners_updated)
        self.x = int(ctr[0])
        self.y = int(ctr[1])
        self.rad = int(rad)
        self.width = int(2*self.rad)
        self.height = int(2*self.rad)
        self.left = self.x - self.width / 2
        if self.left < 0:
            self.left = 0
        self.top = self.y - self.height / 2
        if self.top < 0:
            self.top = 0
        self.right = self.x + self.width / 2
        if self.right > 639:
            self.right = 639
        self.bottom = self.y + self.height / 2
        if self.bottom > 479:
            self.right = 479
        if self.x <= 0 or self.y<=0 or self.x > 640 or self.y > 480:
            print('OBJECT LOST!:404')
            self.existance = False
        # updating old_corners and oldFrameGray
        self.last_gray = nowgray.copy()
        self.p0 = new_corners_updated.copy()
        return [ctr, rad]

    def draw_object(self, frame):
        #绘制目标框
        cv2.circle(frame, (int(self.x), int(self.y)), int(self.rad), (255, 0, 0), thickness=3)

    def draw_feature(self, frame):
        #绘制特征点
        for corner in self.p0:
            cv2.circle(frame, (int(corner[0][0]), int(corner[0][1])), 2, (0, 255, 0))

    def draw_center(self, frame):
        #绘制中心
        cv2.circle(frame, (int(self.x), int(self.y)), 2, (0, 255, 0))
class MinObject:
    """
    简化版目标，用于参数传递降低参数量
    """
    def __init__(self, object):
        self.name = object.name
        self.ctr = (object.x, object.y)
        self.rad = object.rad
        self.existance = object.existance
    def get_object(self):
        return ctr, rad, name

    def draw_object(self, frame):
        #绘制目标框
        cv2.circle(frame, self.ctr, int(self.rad), (255, 0, 0), thickness=3)

    def draw_center(self, frame):
        #绘制中心
        cv2.circle(frame, self.ctr, 2, (0,0, 255))

# 测试代码，作为模块调用时失效
if __name__=="__main__":

    global img, img2
    global point1, point2, object1
    global object_enable
    global feature_params, lk_params
    global move_flag

    def on_mouse(event, x, y, flags, param):  # 鼠标事件
        global img, img2, point1, point2, object1
        global feature_params, lk_params, object_enable, move_flag
        img2 = img.copy()
        if event == cv2.EVENT_LBUTTONDOWN and move_flag == False:  # 左键单击
            point1 = (x, y)
            point2 = (x, y)
            move_flag = True
        elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON) and move_flag == True:
            point2 = (x, y)


        elif event == cv2.EVENT_LBUTTONUP and move_flag == True:  # 左键释放
            if point2 != point1:
                min_x = min(point1[0], point2[0])
                min_y = min(point1[1], point2[1])
                width = abs(point1[0] - point2[0])
                height = abs(point1[1] - point2[1])
                x = int(min_x + 1.0 * width / 2)
                y = int(min_y + 1.0 * height / 2)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                object1 = TrackObject('lotus', x, y, width, height, gray, feature_params, lk_params)
                object_enable = True
                move_flag = False


    object_enable=False
    move_flag = False
    point1=(0,0)
    point2=(0,0)
    URL = 'G:/BrickCV/testVideo/test.mp4'
    cap = cv2.VideoCapture(0)
    # 设置 ShiTomasi 角点检测的参数
    feature_params = dict(maxCorners=200,
                          qualityLevel=0.005,
                          minDistance=7,
                          blockSize=7)

    # 设置 lucas kanade 光流场的参数
    # maxLevel 为使用图像金字塔的层数
    lk_params = dict(winSize=(15, 15),
                     maxLevel=2,
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    cv2.namedWindow('test')
    cv2.setMouseCallback('test', on_mouse)
    while True:
        ret,img = cap.read()
        img2 = img.copy()

        if object_enable == False:#无目标时
            if point2 != point1:
                cv2.rectangle(img2, point1, point2, (255, 0, 0), 5)
            cv2.imshow('test',img2)
            cv2.waitKey(30)
        else:#存在目标时
            min_obj=MinObject(object1)
            nowgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ctr,rad = object1.object_refresh(nowgray)
            img2=img.copy()
            min_obj.draw_object(img2)
            #object1.draw_feature(img2)
            object1.draw_center(img2)
            cv2.imshow('test', img2)
            cv2.waitKey(30)

