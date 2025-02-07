#!/usr/bin/env python
import math

import rospy
import time

from Adafruit_MotorHAT import Adafruit_MotorHAT
from std_msgs.msg import String
from std_msgs.msg import Float32MultiArray
from sensor_msgs.msg import Joy


# initialization

def moveForward(distance, speed, direction):
    speed_l = -1*speed
    speed_r = -1*(speed+0.004)
    if direction < 0:
        speed_l = -1*speed_l
        speed_r = -1*speed_r
    for i in range(int(20*distance/59.7)):
        msg = Float32MultiArray()
        msg.data = [move, speed_l, speed_r]
        ctr_pub.publish(msg)
        time.sleep(0.1)

    msg.data = [stop, speed_l, speed_r]
    ctr_pub.publish(msg)
    time.sleep(1.0)

def rotate(angles, speed, direction):
    speed_l = -1*speed
    speed_r = -1*(speed)
    if direction == "clockwise":
        speed_r*=-1
    else:
        speed_l*=-1
    msg = Float32MultiArray()
    c = 10.5
    if angles > math.pi - math.pi/10:
        c = 8
    if angles < math.pi/2 - math.pi/10:
        c = 13
    for i in range(int(c*angles/math.pi)):   # mapp steps (11 for pi?) to required angle
        msg.data = [move, speed_l, speed_r]
        ctr_pub.publish(msg)
        time.sleep(0.1)

    msg.data = [stop, speed_l, speed_r]
    ctr_pub.publish(msg)
    time.sleep(1.0)

def getDistance(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)

def getAngleToRotate(initialAngle, FinalAngle):
    FinalAngle = FinalAngle % (2*math.pi)
    initialAngle = initialAngle % (2*math.pi)
    return (FinalAngle - initialAngle)%(2*math.pi)

## Assuming we are getting angles from 0 to 360, NOPE, we're getting -pi/2 to pi/2 imo
def getAngleForTravel(x1,x2,y1,y2):
    eps = 10**(-10)
    num = y2-y1
    den = x2-x1
    atan = math.atan((y2-y1)/((x2-x1)+eps))
    if atan<0:
        if num>0 or den<0:
            atan = atan + math.pi
    else:
        if num<0 or den<0:
            atan+= math.pi
    return atan % (2*math.pi)




def moveRobot(x1,y1,initialAngle, x2, y2, finalAngle):
    angleForTravel = getAngleForTravel(x1,x2,y1,y2)
    print(angleForTravel, "angle for travel")
    angleToBeRotated = getAngleToRotate(initialAngle, angleForTravel)
    print(angleToBeRotated, " angle to be rotated")
    if angleToBeRotated >=1.5*math.pi or angleToBeRotated <= 0.5*math.pi:
        if angleToBeRotated >= 1.5*math.pi:
            angleToBeRotated -= 2*math.pi
            orientation = "clockwise"
        else:
            orientation = "anticlockwise"
        direction = 1
    else:
        if angleToBeRotated >= math.pi:
            angleToBeRotated -= math.pi
            orientation = "anticlockwise"
            direction = -1
        else:
            angleToBeRotated -= math.pi
            orientation = "clockwise"
            direction = -1
    print(angleToBeRotated, orientation, direction)
    rotate(abs(angleToBeRotated),0.7,orientation)

    if direction < 0 :
        angleForTravel = (angleForTravel + math.pi)%(2*math.pi)
    distance = getDistance(x1,y1,x2,y2)
    moveForward(distance*100,0.7,direction)
    finalRotation = getAngleToRotate(angleForTravel, finalAngle)
    if finalRotation > 2*math.pi - 0.09:
        finalRotation = 0.00
    print(finalRotation, "finalRotation")
    if angleToBeRotated >math.pi:
        orientation = "clockwise"
        angleToBeRotated = 2*math.pi - angleToBeRotated
    else:
        orientation = "anticlockwise"
    rotate(abs(finalRotation), 0.7, orientation)
    print()




if __name__ == '__main__':
    # setup ros node
    
    rospy.init_node('jetbot_test')
    ctr_pub = rospy.Publisher('/ctrl_cmd', Float32MultiArray, queue_size=1)

    move = 0.0
    stop = 1.0

    WAYPOINTS = [[0,0,0],[-1,0,0],[-1,1,1.57],[-2,1,0],[-2,2,-1.57],[-1,1,-0.78],[0,0,0]]
    # WAYPOINTS = [[-1,1,0],[-2,1,0],[-2,2,-1.57]]

    for i in range(1,len(WAYPOINTS)):
        initialPoint = WAYPOINTS[i-1]
        finalPoint = WAYPOINTS[i]
        x1 = initialPoint[0]
        y1 = initialPoint[1]
        initialAngle = initialPoint[2]
        x2 = finalPoint[0]
        y2 = finalPoint[1]
        finalAngle = finalPoint[2]
        moveRobot(x1,y1,initialAngle,x2,y2,finalAngle)
        time.sleep(2.0)

### SGC013382






