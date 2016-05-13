import socket

UDP_IPcpu = "172.20.20.20"        #IP to send at (CPU IP)
UDP_PORTtocpu = 9910

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

limitSwitches = 0 ##
s0 = 0
s1 = 0
s2 = 0
s3 = 0
s4 = 0
s5 = 0
err = 0 #ERR Codes will be determined later for All possible errors
positionX = 0 #From RPI
positionY = 0 # ||
directionX = 0# ||
directionY = 0# ||
excav_pos = 0 ##
bumperSwitches = 0 ##
excav_current = 0 ##2 Bytes
sys_voltage = 0 ##
sys_current = 0 ##
sys_cumpower = 0 ##
sys_power = 0
angle_voltage = 0
message = ""


excav_current = 0
left_drive_current = 0
right_drive_current = 0

#Timer for begin cycle
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

socksend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

while 1:
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
        
    socksend.sendto(message,(UDP_IPcpu,UDP_PORTtocpu))
    



