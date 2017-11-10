import socket
import sys
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
        
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('192.168.43.22', 10000)
print >>sys.stderr, 'Starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

try:
    while True:
        # Wait for a connection
        print >>sys.stderr, 'Waiting for a connection'
        connection, client_address = sock.accept()
        #sock.settimeout(0)
        print >>sys.stderr, 'Connecion from', client_address
        velocity_r = "0"
        velocity_l = "0"

        # Receive the data in small chunks and retransmit it
        while True:
            
            velocity_r = connection.recv(3)
            velocity_l = connection.recv(3)

            if velocity_r:
                print >>sys.stderr, '-----Velocities-------'
                print >>sys.stderr, '     Vr = "%s"' % velocity_r
                print >>sys.stderr, '     Vl = "%s"' % velocity_l
            else:
                print >>sys.stderr, 'No more data from', client_address
                drive(0,0)
                break
 
            try:
                drive(int(velocity_r.strip('\0')), int(velocity_l.strip('\0')))
            except ValueError:
            	print '----------------------'
        
except KeyboardInterrupt:
    pass
A.stop()
C.stop()
GPIO.cleanup()
