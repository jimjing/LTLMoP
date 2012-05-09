#!/usr/bin/env python
"""
===============================================
pioneerActuator.py
===============================================
"""

import time, math, sys
import threading
from numpy import *
from numpy.linalg import norm
from socket import *

class actuatorHandler:
    def __init__(self, proj, shared_data):
        try:
            self.host = shared_data['PIONEER_ADDRESS']
        except KeyError:
            print "ERROR: You need to call Pioneer Init handler before using Pioneer Actuator Handler"
            return
            
        sys.path.append(proj.ltlmop_root)
        from lib.handlers.motionControl.__is_inside import is_inside

        host = "10.0.0.96"
        port4 = 11004
        self.buf4 = 1024
        self.addr4 = (host,port4)
        self.s4 = socket(AF_INET,SOCK_DGRAM)
        
        port22 = 11022        
        self.buf22 = 1024
        self.addr22 = (host,port22)
        self.s22 = socket(AF_INET,SOCK_DGRAM)
        
        self.proj = proj

    def _regionFromPose(self, pose):
        for i, r in enumerate(self.proj.rfi.regions):
            pointArray = [self.proj.coordmap_map2lab(x) for x in r.getPoints()]
            vertices = mat(pointArray).T 

            if is_inside([pose[0], pose[1]], vertices):
                return i

        return None

    def gotoPoint(self, point_name, max_speed_trans, max_speed_rot, threshold_trans, threshold_rot):
        """
        Drive to a point (published by a sensor handler) and-- if target pose includes orientation-- rotate in place.
        
        point_name (string): name of data published by sensor handler that contains target pose
        max_speed_trans (float): maximum translational speed (default=1)
        max_speed_rot (float): maximum rotational speed (default=0.45)
        threshold_trans (float): maximum acceptable final distance from target point (default = 0.1)
        threshold_rot (float): maximum acceptable final orientation error (default="pi/18")
        """
        
        if initial:
            self.targetPose = None
            self.moveState = "idle"
            moveThread = threading.Thread(target = self._POIMovementThread)
            moveThread.start()
        else:
            pass
    def moveFlag(self, flag_port, val):
    def setActuator(self, name, val):
        print "(ACT) Actuator %s is now %s!" % tuple(map(str, (name, val)))
        
        if name == "flag":
            if val == True:
                self.s4.sendto("T",self.addr4)
            else:
                self.s4.sendto("F",self.addr4)   
                
        elif name == "gotoPOI":
            self.proj.sensor_handler.sensor_cache["gotoPOIDone"] = False
            if int(val) == 1:
                if self.targetPose is None:
                    print "(ACT) WARNING: No targetPose set in actuator handler before actuator call."
                    return

                # Make sure that the target point is inside our current region,
                # lest we run the risk of violating a safety requirement
                pose = self.proj.pose_handler.getPose()

                current_region = self._regionFromPose(pose) 
                target_region = self._regionFromPose(self.targetPose)

                if current_region != target_region:
                    if target_region is None:
                        target_region_name = "the middle of nowhere"
                    else:
                        target_region_name = self.proj.rfi.regions[target_region].name

                    print "(ACT) WARNING: Cannot safely visit POI outside of current region (it appears to be in %s).  Ignoring!" % target_region_name
                    return
            
                self.moveState = "translate"
            else:
                self.moveState = "idle"

    def _POIMovementThread(self):
        while True:
            if self.moveState == "translate":                
                # Check if we've arrived at our destination
                pose = self.proj.pose_handler.getPose()
                diff = (self.targetPose[0]-pose[0], self.targetPose[1]-pose[1])
                arrived = norm(diff) < THRESHOLD_TRANS

                if arrived:
                    self.proj.drive_handler.setVelocity(0, 0)
                    self.moveState = "rotate" 
                else:
                    # Set the velocity vector to the difference between pose and target
                    v = diff        
                    v = 2*array(v)      
                    #print "translate %s " % str(v)

                    
                    # Clip maximum speed
                    if norm(v) > MAX_SPEED_TRANS:
                        v = MAX_SPEED_TRANS * array(v)/norm(v)                   
                    
                    self.proj.drive_handler.setVelocity(v[0], v[1], theta=pose[2])

                    time.sleep(0.05)
            elif self.moveState == "rotate":                
                # Check if we've finished rotating
                pose = self.proj.pose_handler.getPose()
                diff = self.targetPose[2] - pose[2]
                arrived = abs(diff) < THRESHOLD_ROT

                if arrived:
                    self.proj.loco_handler.sendCommand([0,0])
                    self.moveState = "idle" 
                    self.s22.sendto("T",self.addr22)
                    self.proj.sensor_handler.sensor_cache["gotoPOIDone"] = True
                else:
                    # Set our rotational velocity proportional to the offset from the target angle
                    if abs(diff) > math.pi:
                        w = 2*math.pi - diff
                    else:
                        w = diff
                    print "rotate %s " % str(w)

                    # Clip maximum speed
                    if abs(w) > MAX_SPEED_ROT:
                        w = sign(w) * MAX_SPEED_ROT

                    self.proj.loco_handler.sendCommand([0,w])

                    time.sleep(0.05)
            else:
                time.sleep(0.1)


