import cv2
import numpy as np
'''Accepts BGR image as Numpy array
   Returns: (x,y) coordinates of centroid if found
            (-1,-1) if no centroid was found
            None if user hit ESC
'''
def color_detect(image):
    # Blur the image to reduce noise
    blur=cv2.medianBlur(image,5)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image for only green colors
    lower_green = np.array([40, 70, 70])
    upper_green = np.array([80, 200, 200])

    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5, 5), 0)

    # Take the moments to get the centroid
    moments = cv2.moments(bmask)

    m00 = moments['m00']
    centroid_x, centroid_y = None, None
    if m00 != 0:
        centroid_x = int(moments['m10'] / m00)
        centroid_y = int(moments['m01'] / m00)

    # Assume no centroid
    ctr = (-1, -1)

    # Use centroid if it exists
    if centroid_x != None and centroid_y != None:
        ctr = (centroid_x, centroid_y)
    else:
        ctr = (0,0)
    return ctr
def color_detect2(Img):
    HSV = cv2.cvtColor(Img, cv2.COLOR_BGR2HSV)#把BGR图像转换为HSV格式
    """
    HSV模型中颜色的参数分别是：色调（H），饱和度（S），明度（V） 
    下面两个值是要识别的颜色范围 
    """
    kernel_2 = np.ones((2,2),np.uint8)#2x2的卷积核
    kernel_3 = np.ones((3,3),np.uint8)#3x3的卷积核
    kernel_4 = np.ones((4,4),np.uint8)#4x4的卷积核

    Lower = np.array([40, 70, 70])#要识别颜色的下限
    Upper = np.array([80, 200, 200])#要识别的颜色的上限

    #mask是把HSV图片中在颜色范围内的区域变成白色，其他区域变成黑色
    mask = cv2.inRange(HSV, Lower, Upper)
    #下面四行是用卷积进行滤波
    erosion = cv2.erode(mask,kernel_4,iterations = 1)
    erosion = cv2.erode(erosion,kernel_4,iterations = 1)
    dilation = cv2.dilate(erosion,kernel_4,iterations = 1)
    dilation = cv2.dilate(dilation,kernel_4,iterations = 1)
    #target是把原图中的非目标颜色区域去掉剩下的图像
    target = cv2.bitwise_and(Img, Img, mask=dilation)
    #将滤波后的图像变成二值图像放在binary中
    ret, binary = cv2.threshold(dilation,127,255,cv2.THRESH_BINARY)

    #在binary中发现轮廓，轮廓按照面积从小到大排列
    _, contours, hierarchy = cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    p=0
    obj_list=[]
    for i in contours:#遍历所有的轮廓
        x,y,w,h = cv2.boundingRect(i)#将轮廓分解为识别对象的左上角坐标和宽、高
        #在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
        ctr = (x+w/2, y+h/2)
        rad = (w+h)/4
        obj = (ctr, rad)
        obj_list.append(obj)
        p +=1
    return [obj_list, len(contours)]