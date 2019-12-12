#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
#
# Results:  When you run this program, the GoPiGo3 will reccognize objects in its vicinity and travel to them.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #    
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import picamera
import numpy as np
import threading
import queue
import io
import IPython
from PIL import Image
from sklearn.cluster import KMeans
import math
import csv
import cv2 as cv 
import easygopigo3 as easy# import the GoPiGo3 drivers
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time

#List of declarations primarily used to determine distances and command the robot to move
GPG = easy.EasyGoPiGo3()
#LTD = GPG.left_target_degrees
#RTD = GPG.right_target_degrees
ds = GPG.init_distance_sensor()
ccw = False
top = 5
count = 1
degree = 0
distance = 0
i = 90
trvld = 860
trnDeg = 0

frames = queue.Queue()#The queue where frames captured by the Piamera are stored and subseqeuntly feed to Yolo. 

# List of global variables to be accessed by multiple threads
dist = 0
angle = 0
analyze = False
vstd = 1
footprint = -1
count = 1
class LinkedList():
    
    def __init__(self):

        
        self.head = Node()
        self.tail = self.head
        self.cur = self.head
        self.next = self.cur.next
        self.prev =self.head.prev



    def delete(self, cur):
        self.cur = cur
        if ((self.cur == self.head) & (self.next == True) ):
            self.cur = self.cur.next
            self.head.next = None
            self.head = self.cur
            self.cur.prev = None

        elif (not(self.cur == self.head) and not(self.cur == None)):
            self.cur.prev.next= self.cur.next
            if not(self.cur.next == None):
                self.cur.next.prev = self.cur.prev
            hldr = self.cur.prev
            self.cur.next = None
            self.cur.prev = None
            self.cur =  hldr

    def Add(self):
        toAdd = Node()
        toAdd.prev = self.tail
        self.tail.next = toAdd
        self.tail = toAdd

    def getSize(self):
        size = 1
        cur = self.head
        while not(cur == self.tail):
            cur = cur.next
            size = size + 1
            
        return size


class Node():

    
    def __init__(self):

        global count
        self.index = count
        self.next = None
        self.prev = None
        self.angle = 0
        self.dist = 0
        self.vstd = -1
        count = count + 1

class Brain(threading.Thread):
    
    def __init__(self):

        
        super().__init__()
        self.directions = []
        global dist
        global angle
        global whereAt
        global ds

    def clearcpy(self):
        global resourc
        cur = resourc.head
        cur2 = cur
        i = 0
        while not(cur == None):
            cur2 = cur.next
            while not(cur2 == None):
                if ((cur.dist <= cur2.dist+6 and cur.dist>= cur2.dist-6) or (cur.angle <= (cur2.angle +30) and cur.angle >= (cur2.angle - 30))):
                    cur2 = resourc.delete(cur2)
                    print("del")
                if not(cur2==None):
                    cur2 = cur2.next
            cur = cur.next

        
    def unvisited(self):
        global resourc
        cur = resourc.head
        while not (cur == None) :
            if cur.vstd == 0 :
                return True
            cur = cur.next
        return False

    def Confirm(self, turn):#A function that uses the image processor to confirm is something is indeed a object and if so, the assigns it a node within the linkedlist
         #A function call is made to the current image processor thread
        resourc.tail.dist = ((ds.read_mm()/10) )#After the function call the current node is initialized with sensor values
        resourc.tail.angle = ((turn * 11)) # the 4 is to offset the gopigo3 underturning
        resourc.tail.vstd = 0
        resourc.Add()#The resourc LinkedList is lengthened and the new empty node is now the current in preparation for the next call of this function


    def getFirst(self):
        global dist
        global angle
        global walkTo
        global resourc
        
        if not(resourc == None):
            shortest = resourc.head
            cur = resourc.head
            while not(cur == None):
                if (cur.vstd == 0):
                    if cur.dist < shortest.dist :
                        shortest = cur
                cur = cur.next
                walkTo = shortest
                dist = (shortest.dist ) 
                angle = shortest.angle
                if angle > 180 :
                    angle = -(360 - angle)
        print(str(dist) +" " + str(angle))
        FeetThr.walk()
        print("just arrived")


    def calcShortest(self):
        global dist
        global walkTo
        global resourc
        global whereAt
        if (whereAt == None):
            print("visiting the first node")
            if not(resourc.head.next == None):
                self.getFirst()
            else:
                print("there are no objects under 100 centimeters to visit are detect")

        elif not(whereAt == None):
            print("calculating node with shortest distance")
            shortest = 10000
            result = shortest
            j = 0
            cur = resourc.head
            while not(cur == None):
                if(cur.vstd == 0 and not(cur.dist == 0)):
                    radian1 = math.radians(cur.angle)
                    radian2 = math.radians(whereAt.angle)
                    result = math.sqrt(((cur.dist**2) + (whereAt.dist**2))-(2 * cur.dist * whereAt.dist * math.cos(radian1 - radian2) ))
                    if j == 0: 
                        shortest = result
                    else:
                        if result < shortest:
                            shortest = result
                            walkTo = cur
                            
                    j = j + 1
                cur = cur.next
            dist = shortest + 6
            if j == 0:
                print("didn't run calc")


    def searchnext(self):
            print("searching for distance that matches the next node")
            global dist
            global angle
            w = -1
            self.calcShortest()
            while True :
                GPG.orbit(10, 14)
                print(dist)   
                GPG.stop()

                if (((ds.read_mm() / 10) <= (dist +7)) and ((ds.read_mm() / 10) >= (dist - 6))):
                    break
                
            GPG.stop()
            angle = math.atan2(dist , 8)
            angle = (180 - math.degrees(angle))
            angle = w*(angle)
            FeetThr.walk()




class Neural(threading.Thread):
    '''
    Thread-safe class to process a stream of jpeg sequences from a given queue.
    '''
    def __init__(self, thread_stopper):
        '''
        thread_stopper -> Is the event which stops the thread when set.
        frames -> The queue from which jpeg images come (in numpy.array format).
        lock -> Mutex for the queue.
        '''
        super().__init__()
        self.thread_stopper = thread_stopper
        global frames
        global analyze
        self.incoming = None
        self.count = 0
        # Load Yolo
        self.net = cv.dnn.readNet("yolov3.weights", "yolov3.cfg")
        self.classes = ['bottle']
        #with open("coco.names" , "r") as f:
            #self.classes  = [line.strip() for line in f.readlines()]
        self.vs = VideoStream(usePiCamera =True).start()
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        self.font = cv.FONT_ITALIC

        




    def check(self , v, c ):
        
        v= v*1.5
        time.sleep(.2)
        fps = FPS().start()
        img = self.vs.read()
        img = imutils.resize(img , width=400)
        cv.imwrite("object"+str(self.count) + ".1"+".jpg",img)        


        height, width, channels = img.shape
  
        blob = cv.dnn.blobFromImage(img, 0.00392, (416, 416), (0,0,255), True, crop=False)

        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        class_ids = []
        confidences = []
        _pixels = []
        label = ("(" + str(ds.read_mm())+","+str(c * 10) + ") is a object" )

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.7:
                            center_x = int(detection[0] * width)
                            center_y = int(detection[1] * height)
                            width = int(detection[2] * width)
                            height = int(detection[3] * height)
                            
                            x = int(center_x - width/2)
                            y = int(center_y - height/2)
                            cv.circle(img, (center_x, center_y),10, (0,255,0),2)
                            cv.putText(img, label, (x-10, y + 30), self.font, 1, (255,255,255), 1)
                            confidences.append(float(confidence))
                            class_ids.append(class_id)
            

        cv.imwrite("object"+str(self.count) + ".2"+".jpg",img)        
        self.count = self.count + 1
        return True

    
  #Feet , for moving and stuff.
class Feet(threading.Thread):    

    def __init__(self, thread_stopper):

        super().__init__()
        self.thread_stopper = thread_stopper
        global whereAt
        global walkTo
        global analyze
        global dist
        global angle
        global vstd
        global footprint
        
    def search(self):
        global resourc
        cur = resourc.head# here we attempt to viiew the last recorded object to determine if enough degrees has been turned to view a ne wobject. during design it was discovered that determining when a new object is in view is a tricky constraint.
        c = 0

        while not( c == 36) :# - if a full rotation has been made or not
                c = c + 1
                GPG.orbit(12 , 0)# if the 'if statement' has executed, Rob's turning is interruptted but the leftover degrees needed for a full rotation are in the encoder
                time.sleep(.2)
                v = ds.read_mm()
                v = v/10
                z = 0
                print(str(v) + " Centimeters")
                if z == 0:# Z is simply used to determine if an objec has already been detected. due to the fact that the first node of the resourc linked list has an angle of 0
                    if  v < 85:
                        if (cur.dist == 0):

                            EyeThr.check(v , c)
                            GPG.stop()# if it is a object, then the robot stops
                            print("Confirmed!")
                            BrainThr.Confirm(c) #The keras YOLOv3 model confirms if detectable objects exist in the view , if it is this function also logs its position
                            z = 1
                            
                        
                if  v < 85:
                    if (not(c*10 <= (30+cur.angle) and c * 10 >= (cur.angle-30))) :
                        EyeThr.check(v, c)
                        GPG.stop()# if it is a object, then the robot stops
                        print("Confirmed!")
                        BrainThr.Confirm(c)# The keras YOLOv3 model confirms if detectable objects exist in the view , if it is this function also logs its position
                        cur = cur.next
               
        GPG.stop()            
        #BrainThr.clearcpy()
        print("Number of nodes to visit =" + str(resourc.getSize()-1))

    def walk(self):
        global whereAt
        global walkTo
        global dist
        global angle
        global vstd
        angle = int(math.ceil(angle))
        if angle > 180:
            angle = -(360 - angle)
        GPG.reset_motor_encoder
        #if not(angle == 0):
         #   s = (float(angle) / float(abs(angle)))
        GPG.turn_degrees(angle)# Commands the GoPiGo3 to rotate to the direction of the nearest object
        if not(dist==0):
            s = 1
            while not(((ds.read_mm() / 10) <= (dist + 5)) and ((ds.read_mm() / 10) >= (dist - 6))):
                GPG.turn_degrees(9 * s)
            GPG.turn_degrees(6)
            GPG.drive_cm(dist)#Commands the GoPiGo to walk to the nearest object
            walkTo.vstd = vstd
            vstd = vstd + 1
            whereAt = walkTo
        #else return






#main or, "try" loop.
print(cv.__version__)
thread_stopper = threading.Event()
resourc = LinkedList()
cur = resourc.head
whereAt = None
walkTo = None

FeetThr = Feet(thread_stopper)
BrainThr = Brain()
EyeThr = Neural(thread_stopper)

EyeThr.start()#Starts the YOLOv3 Keras Thread
BrainThr.start()#Starts the thread responsible for schecduling between the Imagethread and Feetthread
FeetThr.start()#Starts the feet thread which is necessary for all movement
time.sleep(.2)

FeetThr.search()
BrainThr.calcShortest()
print("First node visited")
angle = -90
dist = 0
FeetThr.walk()
while BrainThr.unvisited() == True :
    print("Looking for next target")
    BrainThr.searchnext()
    angle = -90
    dist = 0
    FeetThr.walk()


