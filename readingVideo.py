import numpy as np
import cv2

cap = cv2.VideoCapture(0)

while(True):
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    th, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY);
    #cv2.imshow('frame', frame)
    #cv2.imshow('gray', gray)
    #cv2.imshow('binary', binary)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
