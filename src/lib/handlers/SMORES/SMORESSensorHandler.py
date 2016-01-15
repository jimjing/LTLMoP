#!/usr/bin/env python
"""
====================================================
SMORESSensors.py - Sensor handler for SMORES robot
====================================================
"""
### LTLMoP imports:
import lib.handlers.handlerTemplates as handlerTemplates
### Other imports:
from math import sqrt
# Import AprilPoseHandler to get access to the apriltag info:
import sys
sys.path.insert(0, '../share/pose')
import AprilPoseHandler

class SMORESSensorHandler(handlerTemplates.SensorHandler):
    '''
    Sensor Handler for SMORES.
    '''
    
    def __init__(self, executor, shared_data):
        """
        Sensor handler for SMORES robot.
        """
        self.SMORESInitHandler = shared_data['SMORES_INIT_HANDLER']
        #self.AprilPoseHandler = executor.hsub.getHandlerInstanceByType(handlerTemplates.PoseHandler)
        self.AprilPoseHandler = AprilPoseHandler.AprilPoseHandler(0)
    def _distance(self, pose1, pose2):
        ''' Distance function for two (x,y,theta) poses. '''
        dx = pose1[0] - pose2[0]
        dy = pose1[1] - pose2[1]
        return sqrt( dx*dx + dy*dy )

    ###################################
    ### Available sensor functions: ###
    ###################################

    def isTagPresent(self, tagNumber, initial=False):
        '''
        Returns True if tag is present, False otherwise
        '''
        tagPose   = self.AprilPoseHandler.getPose(False, tagNumber)
        if not tagPose:
            return False # this means the tag has never been seen.
        elif tagPose[0] == 0 and tagPose[1] == 0:
            return False # this means the tag has been seen, but isn't seen now.
        else:
            return True

    def isNearTag(self, tagNumber, initial=False):
        """
        Determine if the robot is near the specified tag.

        tagNumber (int): The number of the tag
        """
        THRESHOLD = 0.25
        if initial:
            pass # no initialization necessary for this function
        else:
            robotPose = self.AprilPoseHandler.getPose()
            tagPose   = self.AprilPoseHandler.getPose(False, tagNumber)
            #print( 'robotPose: ' + str(robotPose))
            if not tagPose:
                return False # if AprilPoseHandler hasn't seen the tag, don't trigger
            if tagPose[0] == 0 and tagPose[1] == 0:
                return False
            #print( 'tagPose: ' + str(tagPose))
            d = self._distance(robotPose, tagPose)
            #print( str(tagNumber) + ": " + str(d) )
            return d < THRESHOLD 