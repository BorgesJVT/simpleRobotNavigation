import numpy as np
import cv2
import time
import RPi.GPIO as GPIO

INA = 12
INB = 7
INC = 18
IND = 22
GPIO.setmode(GPIO.BOARD)
GPIO.setup(INA, GPIO.OUT)
GPIO.setup(INB, GPIO.OUT)
GPIO.setup(INC, GPIO.OUT)
GPIO.setup(IND, GPIO.OUT)

A = GPIO.PWM(INA, 50) #frequency = 50Hz
A.start(0)

C = GPIO.PWM(INC, 50) #frequency = 50Hz
C.start(0)

def constrain(value, lowerLimit, upperLimit):
    if value > upperLimit:
        return upperLimit
    elif value < lowerLimit:
        return lowerLimit
    else:
        return value
        

# This function map a value inside a specific range A
# into value inside another specific range B
def translate(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    valueScaled = float(value - leftMin) / float(leftSpan)
    return rightMin + (valueScaled * rightSpan)

# This function is resposible for control the wheels
# velocity from -100 ~ 100
def drive(velLeftWheel, velRightWheel):
    constrain(velLeftWheel, -100, 100)
    constrain(velRightWheel, -100, 100)
    
    if velLeftWheel > 0:
        velLeftWheel = translate(velLeftWheel, 0, 100, 100, 0)
        A.ChangeDutyCycle(velLeftWheel)
        GPIO.output(INB, GPIO.HIGH)

    else:
        GPIO.output(INB, GPIO.LOW)
        velLeftWheel = -velLeftWheel
        A.ChangeDutyCycle(velLeftWheel)

    if velRightWheel > 0:
        velRightWheel = translate(velRightWheel, 0, 100, 100, 0)
        C.ChangeDutyCycle(velRightWheel)
        GPIO.output(IND, GPIO.HIGH)
    else:
        GPIO.output(IND, GPIO.LOW)
        velRightWheel = -velRightWheel
        C.ChangeDutyCycle(velRightWheel)        
    

cap = cv2.VideoCapture(0)
try:
    
    while(True):
        ret, frame = cap.read()

        if frame is None:
            continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        th, binary = cv2.threshold(gray, 77, 255, cv2.THRESH_BINARY)
        #print binary.shape
        rows, cols = binary.shape
        baseLeft = binary[240:rows, 1:200]
        baseCentral = binary[240:rows, 201:440]
        baseRight = binary[240:rows, 441:640]
        #cv2.imshow('frame', frame)
        #cv2.imshow('gray', gray)
        #cv2.imshow('binary', binary)
        #cv2.imshow('base1', baseLeft)
        #cv2.imshow('base2', baseCentral)
        #cv2.imshow('base3', baseRight)

        #print baseCentral.mean()
        #print baseLeft.mean()
        #print baseRight.mean()
        #time.sleep(1)
        if baseCentral.mean() < 100 and baseRight.mean() > 220 and baseRight.mean() > 220:
            #drive(40, 40)
            #time.sleep(0.1)
            drive(25, 25)
            #time.sleep(1)
            print "forward"
        elif baseLeft.mean() > baseRight.mean():
            #drive(40, 40)
            #time.sleep(0.1)
            drive(25, 30)
            #time.sleep(1)
            print "right"
        elif baseLeft.mean() < baseRight.mean():
            #drive(40, 40)
            #time.sleep(0.1)
            drive(30, 25)
            #time.sleep(1)
            print "left"
        else:
            drive(0, 0)
            print baseCentral.mean()
            print baseLeft.mean()
            print baseRight.mean()
            print "---------------"

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

except KeyboardInterrupt:
    pass
A.stop()
C.stop()
GPIO.cleanup()
