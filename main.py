import time

import cv2
import numpy as np
from djitellopy import Tello

# Global variables
Epx = 0
Epy = 0
Epz = 0
center_x = 180
center_y = 120
set_z = 90

# Function to find the face in the image
def findFace(img):
    # Create a face cascade classifier
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Convert the image to grayscale
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 4)

    # Create a list of face coordinates and areas
    myFaceListC = []
    myFaceListArea = []

    # Iterate over the faces
    for (x, y, w, h) in faces:
        # Draw a rectangle around the face
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Calculate the center of the face
        cx = x + w // 2
        cy = y + h // 2

        # Calculate the area of the face
        area = w

        # Add the face coordinates and area to the lists
        myFaceListC.append([cx, cy])
        myFaceListArea.append(area)

    # If there are no faces, return the image and an empty list
    if len(myFaceListArea) == 0:
        return img, [[0, 0], 0]

    # Find the index of the face with the largest area
    i = myFaceListArea.index(max(myFaceListArea))

    # Return the image and the coordinates of the largest face
    return img, [myFaceListC[i], myFaceListArea[i]]

# Initialize the Tello drone
tello = Tello()
tello.connect()
print(tello.get_battery())
tello.streamon()
tello.takeoff()
time.sleep(2)

# Main loop
while True:
    # Get the image from the drone
    image = tello.get_frame_read().frame

    # Resize the image
    image = cv2.resize(image, (360, 240))

    # Find the face in the image
    image, [[posX, posY], area] = findFace(image)

    # Display the image with the face
    cv2.putText(image, f'x:{posX} y:{posY} area:{area}', [50, 50], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
    cv2.imshow("image.jpg", image)

    # Check if the user pressed ESC
    k = cv2.waitKey(10)
    if k == 27:
        break

    # If a face was found, calculate the PID control values
    if posX != 0:
        Ex = posX - center_x
        Ey = posY - center_y
        Ez = area - set_z
        C = (0.5 * Ex) + 0.5 * (Ex - Epx)
        D = (0.2 * Ey) + 0.2 * (Ey - Epy)
        B = (0.5 * Ez) + 0.5 * (Ez - Epz)
        Epx = Ex
        Epy = Ey
        Epz = Ez
        up_down_velocity = -(int(np.clip(D, -100, 100)))
        yaw_velocity = int(np.clip(C, -100, 100))
        forward_backward_velocity = -(int(np.clip(B, -100, 100)))
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
  
