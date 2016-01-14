#!/usr/bin/env python
"""
=================================================
SMORESInitHandler.py - SMORES Initialization Handler
=================================================
"""

import lib.handlers.handlerTemplates as handlerTemplates


class SMORESInitHandler(handlerTemplates.InitHandler):
    def __init__(self, executor, smores_lib_path, module_id):
        """
        Initialization handler for SMORES robot.

        smores_lib_path (string): The directory where the SmoresModule library exists
        module_id (int): The id of the module (default=1)
        """
        #import sys
        #sys.path.append(smores_lib_path)
        #
        # Create a MissionPlayer object to send behaviors:
        import MissionPlayer
        self.MissionPlayer = MissionPlayer.MissionPlayer('test')  
        # Give LTLMoP access to one of the modules for diff drive (this is a hack):
        drivingModuleNumber = 12 
        dockingModuleNumber = 11
        self.drivingModule = self.MissionPlayer.c.mods[drivingModuleNumber]
        self.dockingModule = self.MissionPlayer.c.mods[dockingModuleNumber]

    def getSharedData(self):
        return {'SMORES_INIT_HANDLER': self}
