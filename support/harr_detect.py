# -*- coding:utf-8 -*-

__author__ = 'Brick'
import numpy as np
import cv2





class HarrDetect:
    def __init__(self, xml = 'cascade.xml'):
        self.cascade = cv2.CascadeClassifier(xml)
        self.cascade.load(xml)

    def detect(self, img, lower=np.array([20, 30, 30]) ,upper=np.array([95, 256, 256]), scaleFactor = 1.23, minNeighbors=10, minSize=(5, 5)):
        try:
            self.masked = self.color_mask(img,lower,upper)
        except:
            self.masked = img.copy()

        self.gray = cv2.cvtColor(self.masked, cv2.COLOR_BGR2GRAY)
        self.objects = self.cascade.detectMultiScale(self.gray, scaleFactor=scaleFactor, minNeighbors=minNeighbors, minSize=minSize)


        return self.objects

    def mask_show(self):
        if self.masked is not None:
            cv2.imshow("Color Filter", self.masked)

    def rect2cir(self):
        self.objects_cir=[]
        for (x,y,w,h) in self.objects:
            ctr = (int(x+1.0*w/2.0),y+1.0*h/2.0)
            rad = (w+h)/4
            self.objects_cir.append((ctr,rad))

        return self.objects_cir

    def draw_detect_rect(self,img, color=(0,0,255)):
        for (x,y,w,h) in self.objects:
            cv2.rectangle(img,(x,y),(x+w,y+h),color,2)

    def draw_detect_cir(self,img,color=(0,0,255)):
        self.objs=self.rect2cir()
        for (ctr,rad) in self.objs:
            cv2.circle(img, (int(ctr[0]), int(ctr[1])), int(rad), color, thickness=2)

    def color_mask(self ,img, lower=np.array([20, 30, 30]), upper=np.array([95, 256, 256]), erode_kernel_size=(10, 10),
                   dilate_kernel_size=(18, 18)):
        """

        :param img:
        :param lower:
        :param upper:
        :param erode_kernel_size:
        :param dilate_kernel_size:
        :return:
        """
        masked = img.copy()
        if img is not None:
            #blur = cv2.medianBlur(img, 5)
            blur = img.copy()
            hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
            # Threshold the HSV image for only green colors
            kernel = np.ones(dilate_kernel_size, np.uint8)
            kernel2 = np.ones(erode_kernel_size, np.uint8)
            # 根据滚动条数据确定卷积核大小

            mask = cv2.inRange(hsv, lower, upper)

            # Blur the mask
            bmask = cv2.GaussianBlur(mask, (5, 5), 0)
            erroding = cv2.erode(bmask, kernel2)
            erroding = cv2.erode(erroding, kernel2)
            dilation = cv2.dilate(erroding, kernel)
            dilation = cv2.medianBlur(dilation, 5)
            masked = cv2.bitwise_and(img, img, mask=dilation)

            # cv2.imshow('test', masked)
        return masked







if __name__=="__main__":
    # face_cascade = cv2.CascadeClassifier('cascade.xml')
    # face_cascade.load('cascade.xml')
    cascade = HarrDetect('/support/cascade.xml')
    cap = cv2.VideoCapture(0)
    while True:
        ret, img = cap.read()
        rows, cols, channels = img.shape
        #dst = img.copy()
        faces=cascade.detect(img)
        cascade.mask_show()
        # res = np.uint8(np.clip((1.5 * img + 10), 0, 255))
        # tmp = np.hstack((img, res))  # 两张图片横向合并（便于对比显示）

        # masked=color_mask(img)
        # gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
        # faces = face_cascade.detectMultiScale(gray, scaleFactor = 1.25, minNeighbors=27,minSize=(5,5))

        """
        Parameters:	      
            image – Matrix of the type CV_8U containing an image where objects are detected.
            scaleFactor – Parameter specifying how much the image size is reduced at each image scale.
            minNeighbors – Parameter specifying how many neighbors each candidate rectangle should have to retain it.
            flags – Parameter with the same meaning for an old cascade as in the function cvHaarDetectObjects. It is not used for a new cascade.
            minSize – Minimum possible object size. Objects smaller than that are ignored.
            maxSize – Maximum possible object size. Objects larger than that are ignored.
        """

        # for (x,y,w,h) in faces:
        #     cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        cascade.draw_detect_cir(img)
        # cv2.imshow('image', tmp)
        cv2.imshow('img',img)
        k = cv2.waitKey(30) & 0xff

        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()