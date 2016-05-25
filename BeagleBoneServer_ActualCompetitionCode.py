#BeagleBone Black Control Server Code
#Purdue Lunabotics
#Ver. Date 5/16/2016

#Adafruit_BBIO Libary handles pin outputs for PWM GPIO ADC and UART
import Adafruit_BBIO.UART as UART       #Pin serial setup
import Adafruit_BBIO.GPIO as GPIO       #Pin In/Out support
import Adafruit_BBIO.PWM as PWM         #PWM support
import Adafruit_BBIO.ADC as ADC         #Analog to digital support

import Adafruit_CharLCD as LCD

import serial
from serial import SerialException
from select import select
import time
from time import sleep
import socket

import sys
import signal
import os

import threading

#---------------------Pin Variables------------------------------------

#Motor Controller Pins
left_drive_pwm = "P9_14"
left_drive_dir = "P9_13"

right_drive_pwm = "P8_13"
right_drive_dir = "P8_15"

excav_motor_pwm = "P9_29"
excav_motor_dir = "P9_30"

dep_actua_pwm = "P9_42"
dep_actua_dir = "P9_41"
 
#Limit Switch Pins
excav_limit_stowed = "P8_7"
excav_limit_extended = "P8_9"

dep_limit_extended = "P8_26"
dep_limit_stowed = "P9_22"

bumper_left = "P9_11"
bumper_right = "P9_15"

#ADC Pins
angle_adc = "P9_38"
volt_adc = "P9_37"
curr_adc = "P9_36"

#Encoder Pins
excav_encod_a = "P8_45"
#excav_encod_b = "P8_46"

left_drive_encod_a = "P8_41"
left_drive_encod_b = "P8_42"

right_drive_encod_a = "P8_43"
right_drive_encod_b = "P9_44"

#LCD Screen Pins
lcd_rs        = 'P8_8'
lcd_en        = 'P8_10'
lcd_d4        = 'P8_18'
lcd_d5        = 'P8_16'
lcd_d6        = 'P8_14'
lcd_d7        = 'P8_12'
lcd_backlight = 'P8_32' #Not supported

level_enable = "P9_23"

lcd_columns = 16
lcd_rows    = 2

#PWM Output setup
#Left Drive
GPIO.setup(left_drive_dir, GPIO.OUT)   #setup polarity bit
PWM.start(left_drive_pwm, 0, 10000, 0) #start PWM signal with 0 duty cycle
#Right Drive
GPIO.setup(right_drive_dir, GPIO.OUT)
PWM.start(right_drive_pwm, 0, 10000, 0)
#Deposition
PWM.start(dep_actua_pwm, 0, 10000, 0)
GPIO.setup(dep_actua_dir, GPIO.OUT)
#Bucket Elevator Motor
GPIO.setup(excav_motor_dir, GPIO.OUT)
GPIO.setup(excav_motor_pwm, GPIO.OUT)
#Bucket Elevator Actuators



GPIO.setup(level_enable,GPIO.OUT)

#Inputs Setup code
ADC.setup()

GPIO.setup(dep_limit_extended, GPIO.IN)
GPIO.setup(dep_limit_stowed, GPIO.IN)
GPIO.setup(excav_limit_stowed, GPIO.IN)
GPIO.setup(excav_limit_extended, GPIO.IN)
GPIO.setup(bumper_left,GPIO.IN)
GPIO.setup(bumper_right,GPIO.IN)

GPIO.setup(right_drive_encod_a, GPIO.IN)
GPIO.setup(right_drive_encod_b, GPIO.IN)
GPIO.setup(left_drive_encod_a, GPIO.IN)
GPIO.setup(left_drive_encod_b, GPIO.IN)
GPIO.setup(excav_encod_a, GPIO.IN)
#GPIO.setup(excav_encod_b, GPIO.IN)

angle_voltage = 0


#-----------------------------Setup Variables and Connections-------------------------------------
UDP_IPbbb = "192.168.1.31"        #IP to recieve at (BeagleBone's IP)
UDP_PORTfromcpu = 9909               #Port to listen on
UDP_PORTfromodroid = 9908

UDP_IPcpu = "192.168.1.34"        #IP to send at (CPU IP)
UDP_PORTtocpu = 9910

UDP_IPodroid = "192.168.1.33"        #IP to send at (Odriod IP)
UDP_PORTtoodroid = 9911
#Setup UDP socket to listen from

UART.setup("UART5")
sleep(0.1)
serEleAng = serial.Serial(port = "/dev/ttyO5", baudrate = 9600)
serEleAng.close()
serEleAng.open()
if serEleAng.isOpen():
    print "Open"
    serEleAng.write(serial.to_bytes('\xAA'))
    sleep(0.1)
    serEleAng.write(serial.to_bytes('\x83'))
    sleep(0.1)

UART.setup("UART1")
sleep(0.1)
serEle = serial.Serial(port = "/dev/ttyO1", baudrate = 9600)
serEle.close()
serEle.open()
if serEle.isOpen():
    print "Open"
    serEle.write(serial.to_bytes('\xAA'))
    sleep(0.1)
    serEle.write(serial.to_bytes('\x83'))
    sleep(0.1)
    
#--------------------------------- Temp and Permant Holder Vars for Comms----------------
MASK = 128
BYTEMAX = 255
BYTE2MAX = 65535
BIT15MAX = 32768
EXCAV_MAXRPM = 100
EXCAV_MAXCURRENT = 40
LEFT_MAXRPM = 100
LEFT_MAXCURRENT = 40
RIGHT_MAXRPM = 100
RIGHT_MAXCURRENT = 40
SYS_MAXVOLT = 30
SYS_MAXCURRENT = 40
SYS_MAXPOWER = 1000
SYS_MAXCUMPOW = 500

bucketWeight = 0 ##
err = 0 #ERR Codes will be determined later for All possible errors
positionX = 0 #From RPI
positionY = 0 # ||
directionX = 0# ||
directionY = 0# ||
dep_pos = 0 ##
excav_pos = 0 ##
bumper_pos = 0 ##
excav_rpm = 0 ##2 Bytes
excav_current = 0 ##2 Bytes
left_drive_rpm = 0 ##
left_drive_current = 0 ##
right_drive_rpm = 0 ##
right_drive_current = 0 ##
sys_voltage = 0 ##
sys_current = 0 ##
sys_cumpower = 0 ##
sys_power = 0

s0 = 0
s1 = 0
s2 = 0
s3 = 0
s4 = 0
s5 = 0

message = ""


inputs = []
sockAuto = None
old_state = ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','','0','0','0']

#----------LCD Screen setup
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

#Current controller state global variables
BucketEle_Up = False        #Boolean: is the button to raise the bucket elevator pressed?
BucketEle_Down = False      #Boolean: is the button to lower the bucket elevator pressed?
BucketEle_Run = 0           #Integer: 0 = stop 1 = 100, -1 = -100
BucketEle_ccw = False
BucketEle_cw = False

stow_elevator = False
runExcavator = False

Bucket_Up = False           #Boolean: is the button to raise the deposition bucket pressed?
Bucket_Down = False         #Boolean: is the button to raise the deposition bucket pressed?

Motor_Left = 0              #Integer Left Motor speed -100 to 100
Motor_Right = 0             #Integer Right Motor speed -100 to 100

minPercent = .25

old_bools = 0

Run = True                  #Run main loop until start button    
autoAngle = False

excav_current = 0
left_drive_current = 0
right_drive_current = 0

#Timer for begin cycle
curr = time.clock()
newcurr = 0
cycles_per_sec = 0

#Encoder Counters
left_drive_count = 0
right_drive_count = 0
excav_count = 0

left_drive_rpm = 0
right_drive_rpm = 0
excav_rpm = 0

#Limit Positions
excav_pos = 1
dep_pos = 1
bumper_pos = 0

#Encoder Pulse Events


#------------------------Motor Update Functions------------------------------


#Updates current state of Left Drive Motor by passing the current Motor_Left speed
#Input: Motor_Left - a number between -100 and 100 that controls motor's duty cycle.
#Output: left_drive_dir - High/Low for PWM polarity
#        left_drive_pwm - Left Motor's PWM signal with given duty cycle
        
def updateLeftMotor():
    
    #verify -100 to 100 bounds
    val = Motor_Left
    if val > 100:
        val = 100
    elif val < -100:
        val = -100

    #Checks for polarity
    if val > 0:
        GPIO.output(left_drive_dir, GPIO.LOW) 
    else:
        GPIO.output(left_drive_dir, GPIO.HIGH)

    #starts a PWM signal on pin P9_14, of cycle val, with pol polarity
    PWM.set_duty_cycle(left_drive_pwm, abs(val))


#Updates current state of Right Drive Motor by passing the current Motor_Right speed
#Input: Motor_Right - a number between -100 and 100 that controls motor's duty cycle.
#Output: right_drive_dir - High/Low for PWM polarity
#        right_drive_pwm - Left Motor's PWM signal with given duty cycle

def updateRightMotor():
    
    #verify -100 to 100 bounds
    val = Motor_Right
    if val > 100:
        val = 100
    elif val < -100:
        val = -100

    #Checks for polarity
    if val > 0:
        GPIO.output(right_drive_dir, GPIO.HIGH) 
    else:
        GPIO.output(right_drive_dir, GPIO.LOW)

    #sets duty cycle of a PWM signal on pin P9_42
    PWM.set_duty_cycle(right_drive_pwm, abs(val))

#send PWM signal and direction bit to control bucket elevator motor run.
#X for Excavate, B for Backwards	
def updateElevatorMot():
    if(BucketEle_Run > 0):
        GPIO.output(excav_motor_pwm, GPIO.HIGH)
        GPIO.output(excav_motor_dir, GPIO.HIGH)
    elif(BucketEle_Run < 0):
        GPIO.output(excav_motor_dir, GPIO.LOW)
        GPIO.output(excav_motor_pwm, GPIO.HIGH)
    elif(BucketEle_Run == 0):
        GPIO.output(excav_motor_pwm, GPIO.LOW)


#Send commands on serial tty4 to control bucket elevator vertical pos
def updateElevatorPos():
    global serEle
    #If up and down or neither up nor down then don't run
    if((BucketEle_Up and BucketEle_Down) or ((not BucketEle_Up) and not BucketEle_Down)):
        serEle.write(serial.to_bytes('\x92'))
        serEle.write(serial.to_bytes('\x20'))
        #print "nothing pos"
    #else if extend if up
    elif (BucketEle_Up):
        serEle.write(serial.to_bytes('\x85'))
	serEle.write(serial.to_bytes('\x00'))
	# 20% duty cycle for linear actuator at 12VDC
	serEle.write(serial.to_bytes(chr(100)))
	#print "up"
    #else if retract
    else:
        serEle.write(serial.to_bytes('\x8A'))
	serEle.write(serial.to_bytes(chr(100)))
	#print "down"

        
#Run deposition bin actuators
#Actuators need to be run at 50% for 12V
def updateBucketPos():
    #if bucket up and bucket down or if neither bucket up nor bucket down, then stop
    if((Bucket_Up and Bucket_Down) or (not Bucket_Up and not Bucket_Down)):
        PWM.set_duty_cycle(dep_actua_pwm, 0)
    #else if bucket up, extend at 50%
    elif (Bucket_Up):
        GPIO.output(dep_actua_dir, GPIO.LOW)
        PWM.set_duty_cycle(dep_actua_pwm, 50)
    #else retract at 50%
    else:
        GPIO.output(dep_actua_dir, GPIO.HIGH)
        PWM.set_duty_cycle(dep_actua_pwm, 50)

#Send commands on serial tty5 to control bucket elevator angle pos
def updateElevatorAngle():
    global serEleAng
    #If up and down or neither up nor down then don't run
    if((BucketEle_ccw and BucketEle_cw) or ((not BucketEle_ccw) and not BucketEle_cw)):
        serEleAng.write(serial.to_bytes('\x92'))
        serEleAng.write(serial.to_bytes('\x20'))
        #print "nothing"
    #else if extend if up
    elif (BucketEle_cw):
        serEleAng.write(serial.to_bytes('\x85'))
	serEleAng.write(serial.to_bytes('\x00'))
	serEleAng.write(serial.to_bytes(chr(75)))
	#print "CW"
    #else if retract
    else:
        serEleAng.write(serial.to_bytes('\x86'))
        serEleAng.write(serial.to_bytes('\x00'))
	serEleAng.write(serial.to_bytes(chr(75)))
	#print "CCW"
       

        
#------------------------Pin Input Update Functions------------------------------
        
#update variables related to excavation and deposition positions
#0 for stowed 1 for ambiguous, 2 for extended
def updateLimitSensors():
    global excav_pos
    global dep_pos
    global bumper_pos
    global s0
    global s1
    global s2
    global s3
    global s4
    global s5
    
    
    if not GPIO.input(excav_limit_stowed): #s0
        excav_pos = 0
        s0 = 1
        s1 = 0
        #print "excav 0"
    elif not GPIO.input(excav_limit_extended): #s1
        excav_pos = 2
        s0 = 0
        s1 = 1
        #print "excav 2"
    else:
        s0 = 0
        s1 = 0
        excav_pos = 1

    if not GPIO.input(dep_limit_extended): #s2
        #print "dep 2"
        s2 = 1
        s3 = 0
        dep_pos = 2
    elif not GPIO.input(dep_limit_stowed): #s3
        dep_pos = 0
        s2 = 0
        s3 = 1
        #print "dep 0"
    else:
        dep_pos = 1
        s2 = 0
        s3 = 0

    bumper_pos = 0 
    if not GPIO.input(bumper_left): #s4
        bumper_pos = 1
        s4 = 1
        #print "bump 1"
    else:
        s4 = 0
    if not GPIO.input(bumper_right): #s5
        bumper_pos = bumper_pos + 2
        s5 = 1
        #print "bump 2"
    else:
        s5 = 0

        





#-------------------------Data And Connection Handling-----------------------------------

##def parseData(data):
##    global BucketEle_Up
##    global BucketEle_Down
##    global BucketEle_Run
##    global Bucket_Up
##    global Bucket_Down
##    global BucketEle_cw
##    global BucketEle_ccw
##    global Motor_Left
##    global Motor_Right
##    global Run
##    global old_state
##    global digAngle
##    
##    trigger_scale = 1         #Amount of the speed controlled by "boost" trigger
##    minPercent = .25            #minimum speed of drive motors in relation to opposite motor's input
##
##    data_list = data.split(',')     #data string is parsed into string list using ',' delimiter
##	
##    Bucket_Up = '1' == data_list[0]
##    Bucket_Down = '1' == data_list[1]
##    if(excav_current < 20):
##        BucketEle_Up = '1' == data_list[15]
##        BucketEle_Down = '1' == data_list[12]
##    else:
##        BucketEle_Up = True
##
##    BucketEle_ccw = '1' == data_list[8]
##    BucketEle_cw  = '1' == data_list[9]
##
##    if(old_state[14] == '0' and data_list[14] == '1'):
##        if(not BucketEle_Run == 0):
##            BucketEle_Run = 0
##        else:
##            BucketEle_Run = 1
##
##    if(old_state[13] == '0' and data_list[13] == '1'):
##        if(not BucketEle_Run == 0):
##            BucketEle_Run = 0
##        else:
##            BucketEle_Run = -1
##
##    if(old_state[5] == '0' and data_list[5] == '1' and autoAngle == False):
##        digAngle = threading.Thread(target=goToDigAngle)
##        digAngle.start()
##
##    Run = '1' != data_list[4]
##    
##    #speed_mult ranges from 1 to 1.5 based on right trigger state
##    speed_Mult = 1 + int(data_list[19])* (trigger_scale - 1) /255
##
##    Motor_Left = (speed_Mult * int(data_list[17]))//(32769 * trigger_scale / 100)
##    
##    if Motor_Left < 20 and Motor_Left > -20:    #deadzone handling
##        Motor_Left = 0
##        
##    Motor_Right = (speed_Mult * int(data_list[18]))//(32769 * trigger_scale / 100)
##    
##    if Motor_Right < 20 and Motor_Right > -20:
##        Motor_Right = 0
##
##    #Set motors to minimum speed as a proportion of other motor
##    #to avoid too much load on a single motor
##    if(abs(Motor_Right) < abs(Motor_Left * minPercent)):
##        Motor_Right = Motor_Left * minPercent - (Motor_Left * minPercent) % 1;
##
##    if(abs(Motor_Left) < abs(Motor_Right * minPercent)):
##        Motor_Left = Motor_Right * minPercent - (Motor_Right * minPercent) % 1;
##
##    if(Bucket_Up):
##        Motor_Left = 0
##        Motor_Right = 0
##
##    if((bumper_pos == 1 or bumper_pos == 3) and Motor_Left < 0):
##        Motor_Left = 0
##
##    if((bumper_pos == 2 or bumper_pos == 3) and Motor_Right < 0):
##        Motor_Right = 0
##
##    old_state = data_list
    

def parseData(data):
    global BucketEle_Up
    global BucketEle_Down
    global BucketEle_Run
    global BucketEle_cw
    global BucketEle_ccw
    global Bucket_Up
    global Bucket_Down
    global Motor_Left
    global Motor_Right
    global Run
    global old_bools
    global servo
    
    bools = ord(data[1]) #DO NOT CHANGE
    
    #--ONLY CHANGE LEFT SIDE--
    a = (bools & MASK) >> 7
    b = (bools & (MASK>>1)) >> 6
    back = (bools & (MASK>>2)) >> 5
    leftBumper = (bools & (MASK>>3)) >> 4
    rightBumper = (bools & (MASK>>4)) >> 3
    down = (bools & (MASK>>5)) >> 2
    left = (bools & (MASK>>6)) >> 1
    right = (bools & (MASK>>7))
    
    bools = ord(data[2]) #DO NOT CHANGE
    up = (bools & MASK) >> 7
    start = (bools & (MASK>>1)) >> 6
    x = (bools & (MASK>>2)) >> 5
    y = (bools & (MASK>>3)) >> 4
    leftNegative = (bools & (MASK>>4)) >> 3
    rightNegative = (bools & (MASK>>5)) >> 2
    leftStick = ord(data[3])
    rightStick = ord(data[4])
    leftTrigger = ord(data[5])
    rightTrigger = ord(data[6])
    #----------------------
    if(leftNegative == 1):
        leftStick = leftStick * -1

    if(rightNegative == 1):
        rightStick = rightStick * -1
        
    #print a, b, back, leftBumper, rightBumper, down, left, right, up, start, x, y

    BucketEle_ccw = 1 == leftBumper
    BucketEle_cw  = 1 == rightBumper

##    print BucketEle_ccw
##    print BucketEle_cw
    
    Bucket_Up = 1 == up
    Bucket_Down = 1 == down
    if(excav_current < 20):
        BucketEle_Up = 1 == y   
        BucketEle_Down = 1 == a
    else:
        BucketEle_Up = True
        BucketEle_Down = False
    

    Run = 1 != start

    if((old_bools & (MASK>>2)) >> 5 == 0 and x == 1):
        if(not BucketEle_Run == 0):
            BucketEle_Run = 0
        else:
            BucketEle_Run = 1

    if((old_bools & (MASK>>1)) >> 6 == 0 and b == 1):
        if(not BucketEle_Run == 0):
            BucketEle_Run = 0
        else:
            BucketEle_Run = -1

    if((old_bools & (MASK>>2)) >> 5 == 0 and back == 1 and autoAngle == False):
        digAngle = threading.Thread(target=goToDigAngle)
        digAngle.start()
        
    Motor_Left = int(leftStick * 100 / 255)
    if Motor_Left < 20 and Motor_Left > -20:    #deadzone handling
        Motor_Left = 0
        
    Motor_Right = int(rightStick * 100/255)
    if Motor_Right < 20 and Motor_Right > -20:
        Motor_Right = 0

    if(abs(Motor_Right) < abs(Motor_Left * minPercent)):
        Motor_Right = Motor_Left * minPercent - (Motor_Left * minPercent) % 1;

    if(abs(Motor_Left) < abs(Motor_Right * minPercent)):
        Motor_Left = Motor_Right * minPercent - (Motor_Right * minPercent) % 1;

    old_bools = bools

    if(Bucket_Up):
        Motor_Left = 0
        Motor_Right = 0

    if((bumper_pos == 1 or bumper_pos == 3) and Motor_Left < 0):
        Motor_Left = 0

    if((bumper_pos == 2 or bumper_pos == 3) and Motor_Right < 0):
        Motor_Right = 0

    
#helper program to test for present serial
def getSerialOrNone(port):
    try:
       return serial.Serial(port , baudrate = 9600)
    except:
       return None

def getSocketOrNone(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.bind((ip, port))
        return sock
    except socket.error, msg:
        return None

def shutdown():
    print 'Shutting Down\n'
    GPIO.output(left_drive_dir, GPIO.LOW)
    GPIO.output(right_drive_dir, GPIO.LOW)
    GPIO.output(dep_actua_dir, GPIO.LOW)
    GPIO.output(excav_motor_dir, GPIO.LOW)
    GPIO.output(excav_motor_pwm, GPIO.LOW)
    
    PWM.set_duty_cycle(dep_actua_pwm, 0)
    PWM.set_duty_cycle(left_drive_pwm, 0)
    PWM.set_duty_cycle(right_drive_pwm, 0)
    

    serEle.write(serial.to_bytes('\x92'))
    serEle.write(serial.to_bytes('\x20'))
    serEleAng.write(serial.to_bytes('\x92'))
    serEleAng.write(serial.to_bytes('\x20'))

    
def signal_handler(signal, frame):
    global Run
    print 'You pressed Ctrl+C!'
    Run = False
    shutdown()
    sleep(0.5)
    GPIO.cleanup()
    os._exit(0)



#Parses Data Logger String to update System Voltage Current Power and Total Power
def updateSystemPower(text):
    global sys_voltage
    global sys_current
    global sys_cumpower
    global sys_power
    
    try:
        sys_voltage = float(text[1:8])
        sys_current = float(text[11:17])
        sys_power = float(text[20:26])
        sys_cumpower = float(text[29:35])
        lcd.home()
        sleep(0.1)
        lcd.message(str(sys_cumpower) + "WH")
        print(str(sys_cumpower) + "WH")
    except:
        print "Data Logger Parse Fail!\n"
        print text[1:8]
        print text[11:17]
        print text[20:26]
        print text[29:35]
        

        
#-------------------------Thread Functions-----------------------------

#Try to create socket to ODroid until success or Run = False
#
def connectAutoSocket():
    global sockAuto
    while(sockAuto == None and Run == True):
        sockAuto = getSocketOrNone(UDP_IPbbb,UDP_PORTfromodroid)
        if(sockAuto == None):
            print "Odroid Socket Failed"
            sleep(1)

#Constantly listen for messages from laptop, if recieved, then update 
def laptopListener():
    global Motor_Left
    global Motor_Right
    global inputs
    global sockAuto
    global positionX
    global positionY
    global directionX
    global directionY

    autoSockConnect = threading.Thread(target=connectAutoSocket)    
    
    sockLap = None
    while(sockLap is None and Run):
        sockLap = getSocketOrNone(UDP_IPbbb,UDP_PORTfromcpu)
        if(sockLap == None):
            print "Laptop Socket Failed"
            sleep(0.5)

    

    if(Run == True):
        autoSockConnect.start()
        
    inputs = [sockLap]
    timeout = time.clock()
 
    while(Run):
        inputready,outputready,exceptready = select(inputs,[],[],0)
        for s in inputready:
            ##Inputs from the laptop
            if s is sockLap:
                dataIn, addr = s.recvfrom(1024) # buffer size is 1024 bytes
                autoOn = ord(dataIn[0])
                autoOn = 0
                if autoOn == 0:
                    parseData(dataIn)

##                    if(Bucket_Up or GPIO.input(excav_limit_stowed) == 1): #don't run drivetrain at the same time as deposition bucket
##                        
##                        Motor_Left = 0
##                        Motor_Right = 0
                    #Test Message to verify connection and accuracy
                    #print "received message:", Motor_Left, Motor_Right
                    
                    updateLeftMotor()
                    updateRightMotor()
                    updateBucketPos()
                    updateElevatorPos()
                    updateElevatorMot()
                    if(autoAngle == False):
                        updateElevatorAngle()

##                    if(not runExcavator):
##                        updateElevatorMot()
##                        if(not stow_elevator):
##                            updateElevatorPos()

                    timeout = time.clock()
            elif s is sockAuto:
                autoDataIn, addr = s.recvfrom(1024) # buffer size is 1024 bytes
                autoOn = ord(autoDataIn[0])

                positionX = ord(autoDataIn(7))
                positionY = ord(autoDataIn(8))
                directionX = ord(autoDataIn(9))
                directionY = ord(autoDataIn(10))
                
                if autoOn == 1:
                    print "Fail"
                    parseData(autoDataIn)

                    if(Bucket_Up or GPIO.input(excav_limit_stowed) == 1): #don't run drivetrain at the same time as deposition bucket
                        Motor_Left = 0
                        Motor_Right = 0
                    #Test Message to verify connection and accuracy
                    print "received message:", Motor_Left, Motor_Right
                    
                    updateLeftMotor()
                    updateRightMotor()
                    updateBucketPos()
                    updateElevatorAngle()

                    if(not runExcavator):
                        updateElevatorMot()
                        if(not stow_elevator):
                            updateElevatorPos()

                    timeout = time.clock()
                    
        if(time.clock() - timeout > 1):   #If no messages for 1 sec stop all motors
            shutdown()
            sleep(1)
        sleep(0.01)
        
    try:
        sockLap.close()
        print "Laptop Socket Closed"
    except:
        print "No Laptop Socket To Close"
    try:
        sockAuto.close()
        print "Autonomy Socket Closed"
    except:
        print "No Autonomy Socket To Close"
        
                        

#constantly listen for messages from datalogger, if recieved then update lcd and relevant vars
def dataLoggerListener():
    global loggerText
    
    timestart = time.time()
    ser = None

    while(ser is None and Run):
        ser = getSerialOrNone("/dev/ttyUSB0")

    if(ser is not None):        
        ser.close()
        ser.open()
        if ser.isOpen():
            sleep(0.1)
            ser.write("/r")
            sleep(1)
            ser.flush()
            while(Run):
                updateLimitSensors()
                if(ser.inWaiting() != 0):
                    loggerText = ser.readline()
                    #print loggerText
                    updateSystemPower(loggerText)
                sleep(0.4)
        try:        
            ser.close()
            print "Serial Closed"
        except:
            print "No Serial To Close"

            
#Periodically sends out messages to the laptop to update status
def sendUpdate():
    socksend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while(Run):
        
        #outLeftRPM = int(left_drive_rpm * BYTE2MAX / LEFT_MAXRPM)
        outExcCurrent = int(excav_current * BYTE2MAX / EXCAV_MAXCURRENT)
        #outLeftCurrent = int(left_drive_current * BYTE2MAX / LEFT_MAXCURRENT)
        #outRightRPM = int(right_drive_rpm * BYTE2MAX / RIGHT_MAXRPM)                                       
        #outRightCurrent = int(right_drive_current * BYTE2MAX / RIGHT_MAXCURRENT)
        #outExcRPM = int(excav_rpm * BYTE2MAX / EXCAV_MAXRPM)        
        outSysVoltage = int(sys_voltage * BYTE2MAX / SYS_MAXVOLT)
        outSysCurrent = int(sys_current * BYTE2MAX / SYS_MAXCURRENT)
        outSysPower   = int(sys_power   * BYTE2MAX / SYS_MAXPOWER)
        outSysCumPower= int(sys_cumpower* BYTE2MAX / SYS_MAXCUMPOW)

        excAngle = int(angle_voltage * 100)
        #2 back limit switches
        #2 bin limit switches
        #2 exc limit switches

        theNegs = 0
        
        if(excav_current < 0): #EXC CURRENT           2BYTES!!!
            theNegs += (1<<7)
            outExcCurrent = outExcCurrent * -1
        
        limitSwitches = (s0<<7)+(s1<<6)+(s2<<5)+(s3<<4)+(s4<<3)+(s5<<2)
        
        #Compile Message
        message = chr(limitSwitches)
        
        message = message+chr((outSysCurrent&(BYTEMAX<<8))>>8)
        message = message+chr(outSysCurrent&BYTEMAX)

        message = message+chr(err)
        message = message+chr(positionX)
        message = message+chr(positionY)
        message = message+chr(directionX)
        message = message+chr(directionY)

        message = message+chr((outSysCumPower&(BYTEMAX<<8))>>8)
        message = message+chr(outSysCumPower&BYTEMAX)

        message = message+chr(excAngle)

        message = message+chr((outSysVoltage&(BYTEMAX<<8))>>8)
        message = message+chr(outSysVoltage&BYTEMAX)

        message = message+chr((outExcCurrent&(BYTEMAX<<8))>>8)
        message = message+chr(outExcCurrent&BYTEMAX)
        
        message = message+chr(theNegs)

        #print "HELLO"
        
        try:
            socksend.sendto(message,(UDP_IPcpu,UDP_PORTtocpu))
        except:
            print "Send Failed"
        

        sleep(0.1)

    
#tracks encoder pulses and periodically updates rpm counters
def encoderListener():
    global excav_rpm
    global left_drive_rpm
    global right_drive_rpm

    GPIO.add_event_detect(right_drive_encod_a, GPIO.RISING)
    GPIO.add_event_detect(left_drive_encod_a, GPIO.RISING)
    GPIO.add_event_detect(excav_encod_a, GPIO.RISING)

    timemarker = time.time()
    excav_count = 0
    left_drive_count = 0
    right_drive_count = 0
    count = 0
    while(Run):
        delay = time.time() - timemarker
        if(delay > 0.25):
        #update measure rpms
            excav_rpm = excav_count*60.0/48/(delay)
            left_drive_rpm = left_drive_count*60.0/48/(delay)
            right_drive_rpm = right_drive_count*60.0/48/(delay)
            
            print left_drive_rpm, right_drive_rpm, excav_rpm
            
            excav_count = 0
            left_drive_count = 0
            right_drive_count = 0
            timemarker = time.time()

                

        #Detect Encoder Pulses
        if GPIO.event_detected(excav_encod_a):
            excav_count = excav_count + 1

        if GPIO.event_detected(right_drive_encod_a):
            if GPIO.input(right_drive_encod_b):
                right_drive_count = right_drive_count - 1
            else:
                right_drive_count = right_drive_count + 1

        if GPIO.event_detected(left_drive_encod_a):
            if GPIO.input(left_drive_encod_b):
                left_drive_count = left_drive_count + 1
            else:
                left_drive_count = left_drive_count - 1

        sleep(0.001)
    
def excavationControl():
    global stow_elevator
    global runExcavator
    highCurrent = 8
    lowCurrent = 4
    
    while(Run):
        if(runExcavator):
            while(runExcavator and Run):
                print "Digging"
                PWM.set_duty_cycle(excav_motor_pwm, 100)
                GPIO.output(excav_motor_dir, GPIO.LOW)
                if(excav_current < lowCurrent):
                    print "Down"
                    GPIO.output(excav_actua_dir,GPIO.HIGH)
                    GPIO.output(excav_actua_pwm, GPIO.HIGH)
                elif(excav_current > highCurrent):
                    print "UP"
                    GPIO.output(excav_dir,GPIO.LOW)
                    GPIO.output(excav_actua_pwm, GPIO.HIGH)
                else:
                    GPIO.output(excav_actua_pwm, GPIO.LOW)
                sleep(0.1)
        sleep(0.1)
    
 #Read voltage from current sensor on motor controllers
def pollCurrentSensors():
    global excav_current
    global volt_12
    global angle_voltage

    maxCount = 5
    
    curr_list = [0] * maxCount
    volt_list = [0] * maxCount
    angle_list = [0] * maxCount

    curr_voltage = 0
    
    count = 0
    mark = time.time()
    while(Run):

        value = ADC.read(angle_adc)
        sleep(0.01)
        value = ADC.read(angle_adc)
        sleep(0.01)
        angle_list[count] = ((value * 1.8)-.2)/1.6

        value = ADC.read(volt_adc)
        sleep(0.01)
        value = ADC.read(volt_adc)
        sleep(0.01)
        volt_list[count] = ((value * 1.8)*7.82)

        value = ADC.read(curr_adc)
        sleep(0.01)
        value = ADC.read(curr_adc)
        sleep(0.01)
        curr_list[count] = ((value * 1.8)*6.67676)
        
        count = count + 1

        if(count > (maxCount-1)):
            count = 0

        

        if(mark + 0.5 < time.time()):
            angle_voltage = sum(angle_list)/float(maxCount)
            volt_12 = sum(volt_list)/float(maxCount)
            curr_voltage = sum(curr_list)/float(maxCount)

            excav_current = (curr_voltage-(volt_12-12)-6)/.048
            #print "Excavator Angle: ", angle_voltage, "   Excavator Current: ",excav_current , volt_12, curr_voltage
            #print , excav_current
            mark = time.time()
        sleep(0.025)

def goToDigAngle():
    global serEleAng
    global autoAngle

    autoAngle = True
    goal = 0.76
    diff = angle_voltage - goal
    print "-------"
    print diff
    print "-------"
    while(abs(diff)> 0.01 and Run == True):
        speed = int(diff * 1000)
        if(speed < 0):
            print "ccw"
            if(speed < -75):
                speed = -75
            if(diff > -0.10):
                speed = 30
            serEleAng.write(serial.to_bytes('\x86'))
            serEleAng.write(serial.to_bytes('\x00'))
            serEleAng.write(serial.to_bytes(chr(abs(speed))))
            
        elif(speed > 0):
            print "cw"
            if(speed > 75):
                speed = 75
            if(diff < 0.10):
                speed = 35
            serEleAng.write(serial.to_bytes('\x85'))
            serEleAng.write(serial.to_bytes('\x00'))
            serEleAng.write(serial.to_bytes(chr(abs(speed))))
        diff = angle_voltage - goal
        sleep(0.20)
    autoAngle = False

    serEleAng.write(serial.to_bytes('\x92'))
    serEleAng.write(serial.to_bytes('\x20'))




#----------------------------------Main Function-----------------------------------
#   Start Threads/ report status
#   Updates Global Vars
#   Updates relevent outputs
#

encoders = threading.Thread(target=encoderListener)
##encoders.start()
laptop = threading.Thread(target=laptopListener)
laptop.start()
dataLogger = threading.Thread(target=dataLoggerListener)
dataLogger.start()
outputs = threading.Thread(target=sendUpdate)
outputs.start()
excavator = threading.Thread(target=excavationControl)
##excavator.start()
adcPolling = threading.Thread(target=pollCurrentSensors)
adcPolling.start()


signal.signal(signal.SIGINT, signal_handler)

GPIO.output(level_enable, GPIO.HIGH)
exTimer = time.clock()

#This loop persists the main function to listen for kill
while(Run):
    #print dep_pos, excav_pos, bumper_pos
##    if(time.clock()- exTimer > 5):
##        runExcavator = not runExcavator
##        print "SWITCH", runExcavator
##        exTimer = time.clock()
    
    sleep(0.5)
    continue





    
    













