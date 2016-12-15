#!/usr/bin/env python
# first together

# change sleep 0.2 -> 0.15 , 
import socket
import nxt
import sys
import tty, termios
import nxt.locator
from nxt.sensor import *
from nxt.motor import *
from time import sleep


brick = nxt.locator.find_one_brick()
accel = nxt.Motor(brick, PORT_A)
direction = nxt.Motor(brick, PORT_B)
lift = nxt.Motor(brick, PORT_C)
colorleft = nxt.Color20(brick, PORT_3)
colorright = nxt.Color20(brick, PORT_2)
ultra = nxt.Ultrasonic(brick, PORT_4)              
#left = nxt.Motor(brick, PORT_B)
#right = nxt.Motor(brick, PORT_C)
#both = nxt.SynchronizedMotors(left, right, 0)
#leftboth = nxt.SynchronizedMotors(left, right, 100)
#rightboth = nxt.SynchronizedMotors(right, left, 100)
cntL=0
cntR=0
sock_flag=1
port_num =7700
yello_flag=0


print "Ready"


       
                            
             

while 1:
        if sock_flag ==1:
                HOST = '' #all available interfaces
                PORT = port_num

                #1. open Socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print ('Socket created')

                #2. bind to a address and port
                try:
                    s.bind((HOST, PORT))
                except socket.error as msg:
                    print ('Bind Failed. Error code: ' + str(msg[0]) + ' Message: ' + msg[1])
                    sys.exit()

                print ('Socket bind complete')

                #3. Listen for incoming connections
                s.listen(10)
                print ('Socket now listening')


                #keep talking with the client
                    #4. Accept connection
                while 1:
                    conn, addr = s.accept()
                    print ('Connected with ' + addr[0] + ':' + str(addr[1]))
                    #5. Read/Send

   
                    data = conn.recv(1024)
                    
                    break;
                    #conn.sendall(data)
    
                    sock_flag=0;
                    port_num= port_num+1
                conn.close()
                s.close()      
                

                
        ultraval = ultra.get_sample()
        while 1:                     
                colorL=colorleft.get_sample()
                colorR=colorright.get_sample()
                print "left forward", 'Color_L:', colorL,'ColorR:', colorR    
                if ultraval > 15:                        
                        accel.run(30, False)
                    
                
                # when the car met target1 line
                if colorL==2 or colorR==2:
                        print "blue"
                        if data == ':3' and yello_flag==0:     
                                direction.turn(120,90,False)
                                accel.run(120,False)
                                sleep(2)
                                accel.run(0, False)
                                sleep(1)
                                accel.run(-60,False)
                                direction.turn(-120,50,False)
                                sleep(1.5)

                                
                                accel.run(0, False)
                                lift.run(-5, False)
                                sleep(1.5)
                                lift.run(0, False)
                                sleep(10.5)
                                lift.run(6, False)
                                sleep(2)
                                lift.run(0, False)
                                sleep(9)
                                lift.run(-6.9, False)
                                sleep(1.6)
                                lift.run(0, False)
                                lift.idle()
                                
                                direction.turn(-120,60,False)
                                accel.run(40,False)    
                                while 1:
                                        colorL=colorleft.get_sample()                        
                                        if colorL==1 or colorL==4:
                                                break  
                                accel.run(30, False)
                                
                        elif data == ':4' and yello_flag!=0:
                                direction.turn(120,90,False)
                                accel.run(120,False)
                                sleep(2)
                                accel.run(0, False)
                                sleep(1)
                                accel.run(-60,False)
                                direction.turn(-120,50,False)
                                sleep(1.5)

                                
                                accel.run(0, False)
                                lift.run(-5, False)
                                sleep(1.5)
                                lift.run(0, False)
                                sleep(10.5)
                                lift.run(6, False)
                                sleep(2)
                                lift.run(0, False)
                                sleep(9)
                                lift.run(-6.9, False)
                                sleep(1.6)
                                lift.run(0, False)
                                lift.idle()
                                
                                direction.turn(-120,60,False)
                                accel.run(40,False)
                                while 1:
                                        colorL=colorleft.get_sample()                        
                                        if colorL==1 or colorL==4:
                                                break  
                                accel.run(30, False)
                                direction.turn(-128,90,False)
                                sleep(2)
                        
                                 
                if colorL==4 or colorR==4:
                                
                        print 'yellow yellow'
                        #path dir
                        if data==':3':
                                print 'data 3'
                                direction.turn(-128,90,False)
                        elif data==':4' and yello_flag==0:
                                accel.run(-20, False)
                                direction.turn(-128,90,False)
                                sleep(1)
                                accel.run(30, False)
                                direction.turn(127,120,False)
                                sleep(2)
                                        
                        yello_flag = yello_flag+1

                if colorL==3 or colorR==3:

                       if data==':3':
                               print 'green'
                               direction.turn(-100,90,False)

                # when left color met black line
                if colorL==1:
                        cntR=0
                        cntL+=1
                        direction.turn(-128,90,False)
                        sleep(0.15)
                        if cntL>1:
                                accel.run(-30, False)
                                direction.turn(127,90,False)
                                sleep(1)
                                cntL = 0
                                direction.turn(-128,90,False)
                                #sleep(0.5)
                                
                # when right color met black line
                elif colorR==1:
                        cntL=0
                       
                        cntR+=1
                  #  print "5",'colorL',colorL,'colorR',colorR
                        direction.turn(127,90,False)
                        sleep(0.15)
                        if cntR>1:
                                
                        #print "6",'colorL',colorL,'colorR',colorR
                        #accel.turn(-128,180,True)
                                accel.run(-20, False)
                                direction.turn(-128,90,False)
                                sleep(1)
                                cntR = 0
                                direction.turn(127,90,False)
                                #sleep(0.5)
                        
         # 4. Parking System Using turn method.
         # turn( power, tacho_units, brake, timeout, emulate):

                #parking
                if colorL==5 or colorR== 5 :
                        direction.turn(-128,90,False)
                        accel.run(-128,False)
                        sleep(3)
                        accel.run(0, False)
                        sleep(1)
                        accel.run(127,False)
                        direction.turn(127,120,False)
                        sleep(3)
                        accel.run(-128,False)
                        direction.turn(-90,60,False)
                        sleep(2)
                        accel.run(-128,False)
                        direction.turn(127,120,False)
                        sleep(2)
                        accel.run(-128,False)
                        direction.turn(-127,120,False)
                        sleep(1.5)
                        sock_flag=1
                        accel.idle()
                        break
accel.idle()
print "Finished"

