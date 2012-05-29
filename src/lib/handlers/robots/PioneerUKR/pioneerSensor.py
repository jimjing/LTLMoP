#!/usr/bin/env python
import socket, sys, os, json
from struct import *
import threading, time
from regions import Point, Color
import copy

"""
===========================================
skeletonSensor.py - Skeleton Sensor Handler
===========================================
"""

class _MapUpdateThread(threading.Thread):
    def __init__(self, proj, port, *args, **kwds):
        sys.path.append(os.path.join(proj.ltlmop_root, "lib"))

        self.port = port
        self.map_basename = proj.getFilenamePrefix() 
        self.project_root = proj.project_root
        self.regionList = set([r.name for r in proj.rfiold.regions])
        self.regionAddedFlag = threading.Event()
        self.addedRegions = []
        self.regionRemovedFlag = threading.Event()
        self.removedRegions = []
        self.coordmap_lab2map = proj.coordmap_lab2map

        super(_MapUpdateThread, self).__init__(*args, **kwds)

    def run(self):
        import regions

        # Wait for any new maps
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.port))

        map_number = 1

        while True:
            s.listen(0)
            conn, addr = s.accept()
            mapdata = conn.recv(65535)
            conn.close()

            rfi = regions.RegionFileInterface(transitions=[])

            r_data = json.loads(mapdata)
            rfi.regions = []
            for reg in r_data:
                r = regions.Region()
                r.setData(reg)
                r.pointArray = map(self.coordmap_lab2map, r.pointArray)
                r.pointArray = [Point(*p) for p in r.pointArray]
                r.recalcBoundingBox()
                rfi.regions.append(r)

            # When we receive one, write it to a new regions file 
            reg_filename = "%s.update%d.regions" % (self.map_basename, map_number)

            rfi.writeFile(reg_filename)

            print "Wrote region file %s." % reg_filename

            # Tell simGUI to update
            print "REGIONS:" + reg_filename

            newRegionList = set([r.name for r in rfi.regions])

            # Check for any substantive changes
            self.addedRegions = newRegionList - self.regionList
            self.removedRegions = self.regionList - newRegionList
            
            # vvv this code doesn't work unless both functions are subscribed to vvv
            # Wait for the any old flags to be received by the other thread
            #if self.regionAddedFlag.isSet() or self.regionRemovedFlag.isSet():
            #    print "WARNING: received new map before previous delta was fully processed"
            #while self.regionAddedFlag.isSet() or self.regionRemovedFlag.isSet():
            #    time.sleep(0.01)

            if self.addedRegions:
                print "added: " + str(self.addedRegions)
                self.regionAddedFlag.set()
            if self.removedRegions:
                print "removed: " + str(self.removedRegions)
                self.regionRemovedFlag.set()

            self.regionList = newRegionList
            
            map_number += 1

class sensorHandler:
    def __init__(self, proj, shared_data, map_listen_port):
        """
        Sensor handler for communicating with C# program on Pioneer.

        map_listen_port (int): TCP port to receive map updates on (default=12345)
        """
        self.host = "10.0.0.96"
        self.ports = {'tempNewRegion': 11002,
                    'hazardous': 11006,
#                    'pink': 11012,
#                    'blue': 11014,
                    'assignment': 11016,
                    'newOffice': 11018,
                    'detectPOI': 11020,
                    'map': int(map_listen_port)}
        self.MAX_PACKET_SIZE = 1024
        self.MIN_POLL_PERIOD = 0.01; # s
        
        self.proj = proj
        self.sensor_cache = {}
        
        # create sockets
        self.sockets = {}
        for s_name in self.ports.keys():
            self.sockets[s_name] = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.sockets[s_name].settimeout(0.1)

        #pollThread = threading.Thread(target = self._pollSensors)
        #pollThread.start()
        
        self.sensor_cache["gotoPOIDone"] = False

        self.mapThread = _MapUpdateThread(proj, self.ports['map'])
        self.mapThread.daemon = True
        self.mapThread.start()

        self.addedRegions = []
        self.removedRegions = []


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
            
    def regionAdded(self, initial):
        """ Return true if a region was added in the last map update """

        if initial:
            print "RA init"
            return

        if self.mapThread.regionAddedFlag.isSet():
            print "RA true"
            self.addedRegions = copy.deepcopy(self.mapThread.addedRegions)
            self.mapThread.regionAddedFlag.clear()
            return True
        else:
            return False

    def regionRemoved(self, initial):
        """ Return true if a region was removed in the last map update """

        if initial:
            return

        if self.mapThread.regionRemovedFlag.isSet():
            self.removedRegions = copy.deepcopy(self.mapThread.removedRegions)
            self.mapThread.regionRemovedFlag.clear()
            return True
        else:
            return False

       


