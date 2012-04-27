#!/usr/bin/env python
import socket
from struct import *
import threading, time

"""
===========================================
skeletonSensor.py - Skeleton Sensor Handler
===========================================
"""

class sensorHandler:
    def __init__(self, proj, shared_data):
        self.host = "10.0.0.96"
        self.ports = {'tempNewRegion': 11002,
                    'hazardous': 11006,
#                    'pink': 11012,
#                    'blue': 11014,
                    'assignment': 11016,
                    'newOffice': 11018,
                    'detectPOI': 11020}
        self.MAX_PACKET_SIZE = 1024
        self.MIN_POLL_PERIOD = 0.01; # s
        
        self.proj = proj
        self.sensor_cache = {}
        
        # create sockets
        self.sockets = {}
        for s_name in self.ports.keys():
            self.sockets[s_name] = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.sockets[s_name].settimeout(0.1)

        pollThread = threading.Thread(target = self._pollSensors)
        pollThread.start()
        
        self.sensor_cache["gotoPOIDone"] = False


    def _pollSensors(self):
        while 1:
            for s_name in self.sockets.keys():
                tic = time.time()
                
                #print "send request", s_name
                # request data
                self.sockets[s_name].sendto(s_name, (self.host, self.ports[s_name]))
                
                try:
                    # receive data
                    data,addr = self.sockets[s_name].recvfrom(self.MAX_PACKET_SIZE)
                    if s_name == 'detectPOI':
                        receivedDoubleList = []
                        for i in range(0,4):
                            unpackedDataDouble = unpack_from('d',data,i*8)[0]
                            receivedDoubleList.append(unpackedDataDouble)
                        newPOI, x, y, theta = receivedDoubleList[0:4]
                        self.sensor_cache[s_name] = (newPOI != 0)
                        if(newPOI != 0):
                            self.proj.actuator_handler.targetPose = (x,y,theta)
                        #print "targetX= %s" % str(x)
                    else:
                        self.sensor_cache[s_name] = (data == "T")
                    #print "recvd request"
                except socket.timeout:
                    print "WARNING: timeout receiving from sensor %s" % (s_name)
                
                while (time.time() - tic) < self.MIN_POLL_PERIOD:
                    time.sleep(0.002)
                    
                #print "nap over"
            
    def getSensorValue(self, sensor_name):
        # wait for initial values at the beginning
        while sensor_name not in self.sensor_cache:
            print "(SENS) waiting for initial %s..." % sensor_name
            time.sleep(0.1)
            
        #print "past initial", sensor_name
        return self.sensor_cache[sensor_name]

       


