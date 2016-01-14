#!/usr/bin/env python
"""
==================================================================
SMORESLocomotionCommand.py - SMORES Locomotion Command Handler
==================================================================
"""

import time
import lib.handlers.handlerTemplates as handlerTemplates

class SMORESLocomotionCommandHandler(handlerTemplates.LocomotionCommandHandler):
    def __init__(self, executor, shared_data):
        """
        Locomotion Command handler for SMORES robot.
        """

        self.SMORESInitHandler = shared_data['SMORES_INIT_HANDLER']

    def sendCommand(self, cmd):
        """
        Run the given behavior
        """
        omegaScale = 100
        vScale = 200
        lDir = 1
        rDir = -1 #right is flipped relative driving direction

        omegaVal = omegaScale * cmd[1]
        vVal = vScale * cmd[0]
        leftVal = vVal + omegaVal
        rightVal = vVal - omegaVal  
        #print ('left: '+str(leftVal) + ' right: '+str(rightVal))
        self.SMORESInitHandler.drivingModule.move.send_torque("left", lDir*leftVal)
        time.sleep(0.05)
        self.SMORESInitHandler.drivingModule.move.send_torque("right", rDir*rightVal)
        time.sleep(0.05)
