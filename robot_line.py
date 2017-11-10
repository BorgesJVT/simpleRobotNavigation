import time
import RPi.GPIO as GPIO

INA = 12 # marrom
INB = 7  # cinza
INC = 18 # roxo
IND = 22 # laranja
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
def drive(velRightWheel, velLeftWheel):
    constrain(velLeftWheel, -100, 100)
    constrain(velRightWheel, -100, 100)
    
    if velLeftWheel >= 0:
        A.ChangeDutyCycle(velLeftWheel)
        GPIO.output(INB, GPIO.LOW)
    else:
        GPIO.output(INB, GPIO.HIGH)
        velLeftWheel = -velLeftWheel
        velLeftWheel = translate(velLeftWheel, 0, 100, 100, 0)
        A.ChangeDutyCycle(velLeftWheel)

    if velRightWheel >= 0:
        C.ChangeDutyCycle(velRightWheel)
        GPIO.output(IND, GPIO.LOW)
    else:
        GPIO.output(IND, GPIO.HIGH)
        velRightWheel = -velRightWheel
        velRightWheel = translate(velRightWheel, 0, 100, 100, 0)
        C.ChangeDutyCycle(velRightWheel)        
    

try:
    while True:
        # forward
##        drive(100, 100)
##        time.sleep(3)
##        for vel in range(50, -1, 5):
##            drive(vel, vel)
##            time.sleep(0.5)
            
        # stop
        #print "parar"
        #drive(0, 0)
        #time.sleep(4)

        print "andar"
        #drive(40, 40)
        #time.sleep(0.1)
        drive(25, -25)
        time.sleep(2)
##        for vel in range(50, -1, 5):
##            drive(vel, vel)
##            time.sleep(0.5)
            
        # stop
        #print "parar"
        drive(25, 25)
        time.sleep(2)
           
except KeyboardInterrupt:
    pass
A.stop()
C.stop()
GPIO.cleanup()
