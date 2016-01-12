#!/usr/bin/env python
"""
====================================================
SMORESSensors.py - Sensor handler for SMORES robot
====================================================
"""

import lib.handlers.handlerTemplates as handlerTemplates

class SMORESSensorHandler(handlerTemplates.SensorHandler):
    def __init__(self, executor, shared_data):
        """
        Sensor handler for SMORES robot.
        """
        self.SMORESInitHandler = shared_data['SMORES_INIT_HANDLER']

    ###################################
    ### Available sensor functions: ###
    ###################################

