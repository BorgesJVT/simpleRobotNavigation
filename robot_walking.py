import time
import RPi.GPIO as GPIO

# (marrom) com amarelo INA
# (cinza) com azul     INB
# (roxo) com vermelho  INC
# (laranja) com verde  IND


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

try:
    while 1:
##        for dc in range(30, 51, 5):
##            C.ChangeDutyCycle(dc)
##            A.ChangeDutyCycle(dc)
##            GPIO.output(IND, GPIO.HIGH)
##            GPIO.output(INB, GPIO.HIGH)
##            time.sleep(0.5)
##
##        time.sleep(1.0)
        
##        for dc in range(50, -1, -5):
##            A.ChangeDutyCycle(dc)
##            C.ChangeDutyCycle(dc)
##            GPIO.output(INB, GPIO.HIGH)
##            GPIO.output(IND, GPIO.HIGH)
##            time.sleep(0.2)
##            print(dc)

        print("tag") # ponto morto
        A.ChangeDutyCycle(0)
        C.ChangeDutyCycle(0)
        GPIO.output(INB, GPIO.LOW)
        GPIO.output(IND, GPIO.LOW)
        time.sleep(5)

        print("tag2") # Duas rodas para frente
        A.ChangeDutyCycle(30)
        C.ChangeDutyCycle(30)
        GPIO.output(INB, GPIO.LOW)
        GPIO.output(IND, GPIO.LOW)
        time.sleep(5)

        print("tag3")# FREIO
        A.ChangeDutyCycle(100)
        C.ChangeDutyCycle(100)
        GPIO.output(INB, GPIO.HIGH)
        GPIO.output(IND, GPIO.HIGH)
        time.sleep(5)

        print("tag4") # DUAS RODAS FRENTE
        A.ChangeDutyCycle(50)
        C.ChangeDutyCycle(50)
        GPIO.output(INB, GPIO.LOW)
        GPIO.output(IND, GPIO.LOW)
        time.sleep(5)
        
except KeyboardInterrupt:
    pass
A.stop()
C.stop()
GPIO.cleanup()
