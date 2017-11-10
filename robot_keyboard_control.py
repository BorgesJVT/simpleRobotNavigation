import time
import RPi.GPIO as GPIO
import usb.core
import usb.util

# (cinza) com azul     INA
# (marrom) com amarelo INB
# (laranja) com vermelho  INC
# (roxo) com verde  IND

INA = 12  # cinza
INB = 7 # marrom
INC = 18 # LARANJA
IND = 22 # ROXO
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
def drive(velRightWheel, velLeftWheel):
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

    
USB_IF      = 0 # Interface
USB_TIMEOUT = 5 # Timeout in MS

USB_VENDOR  = 0x046d # Rii
USB_PRODUCT = 0xc534 # Mini Wireless Keyboard

BTN_LEFT  = 80
BTN_RIGHT = 79
BTN_DOWN  = 81
BTN_UP    = 82
BTN_STOP  = 44 # Space

dev = usb.core.find(idVendor=USB_VENDOR, idProduct=USB_PRODUCT)

endpoint = dev[0][(0,0)][0]

if dev.is_kernel_driver_active(USB_IF) is True:
  dev.detach_kernel_driver(USB_IF)

usb.util.claim_interface(dev, USB_IF)

while True:
    control = None
    try:
        control = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, USB_TIMEOUT)
        print(control)
    except:
        pass

    if control != None:
        if BTN_DOWN in control:
            drive(-30, -30)

        if BTN_UP in control:
            drive(30, 30)

        if BTN_LEFT in control:
            drive(-20, 20)

        if BTN_RIGHT in control:
            drive(20, -20)

        if BTN_STOP in control:
            drive(0, 0)
            
##        # stop
##        drive(0, 0)
##        time.sleep(4)
##
##        drive(50, 50)
##        time.sleep(4)

time.sleep(0.02) # Let CTRL+C actually exit
A.stop()
C.stop()
GPIO.cleanup()
