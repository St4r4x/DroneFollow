import time

import cv2
import numpy as np
from djitellopy import Tello

Epx=0
Epy=0
Epz=0
center_x=180
center_y=120
set_z=90


def findFace(img):
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 4)
    myFaceListC = []
    myFaceListArea = []
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cx = x + w // 2
        cy = y + h // 2
        area = w
        myFaceListArea.append(area)
        myFaceListC.append([cx, cy])
    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i], myFaceListArea[i]]
    else:
        return img, [[0, 0], 0]
     
tello = Tello()
tello.connect()
print(tello.get_battery())
tello.streamon()
tello.takeoff()
time.sleep(2)
while True:
    image = tello.get_frame_read().frame
    image = cv2.resize(image, (360,240))
    image, [[posX, posY], area] = findFace(image)
    cv2.putText(image, f'x:{posX} y:{posY} area:{area}', [50, 50], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
    cv2.imshow("image.jpg", image)
    k = cv2.waitKey(10)
    if k == 27:
        tello.land()   
    if posX!=0:
        Ex=posX-center_x
        Ey=posY-center_y
        Ez=area-set_z
        C=(0.5*Ex)+0.5*(Ex-Epx)
        D=(0.2*Ey)+0.2*(Ey-Epy)
        B=(0.5*Ez)+0.5*(Ez-Epz)
        Epx=Ex
        Epy=Ey
        Epz=Ez
        up_down_velocity=-(int(np.clip(D, -100, 100)))
        yaw_velocity= int(np.clip(C, -100, 100))
        forward_backward_velocity=-(int(np.clip(B,-100,100)))
    else:
        Ex=0
        Epx=0
        Ey=0
        Epy=0
        Ez=0
        Epz=0
        up_down_velocity=0
        yaw_velocity= 0
        forward_backward_velocity=0
    
    tello.send_rc_control(0,forward_backward_velocity,up_down_velocity,yaw_velocity) 
tello.streamoff()
