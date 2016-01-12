#!/usr/bin/env python
"""
===============================================
SMORESActuator.py - SMORES Actuator Handler
===============================================
"""

import lib.handlers.handlerTemplates as handlerTemplates

class SMORESActuatorHandler(handlerTemplates.ActuatorHandler):
    def __init__(self, executor, shared_data):
        """
        Actuator handler for SMORES robot.
        """
        self.SMORESInitHandler = shared_data['SMORES_INIT_HANDLER']

    #####################################
    ### Available actuator functions: ###
    #####################################


    def runBehavior(self, behavior_name, initial=False):
        """
        Run the given behavior

        behavior_name (string): The name of the behavior to run
        """

        if initial:
            pass
        else:
            self.SMORESInitHandler.mission_player.playBehavior(behavior_name)

