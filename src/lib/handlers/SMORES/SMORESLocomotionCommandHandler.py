#!/usr/bin/env python
"""
==================================================================
SMORESLocomotionCommand.py - SMORES Locomotion Command Handler
==================================================================
"""
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
        print (cmd[0]+cmd[1])
        self.SMORESInitHandler.modules.move.send_torque("left", cmd[0]+cmd[1])
        self.SMORESInitHandler.modules.move.send_torque("right", cmd[0]-cmd[1])
