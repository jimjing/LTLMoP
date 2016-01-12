#!/usr/bin/env python
"""
=================================================
SMORESInitHandler.py - SMORES Initialization Handler
=================================================
"""

import lib.handlers.handlerTemplates as handlerTemplates
from MissionPlayer import MissionPlayer

class SMORESInitHandler(handlerTemplates.InitHandler):
    def __init__(self, executor, behavior_dir):
        """
        Initialization handler for SMORES robot.

        behavior_dir (string): The directory where all behaviors are saved (default="behaviors")
        """
        self.mission_player = MissionPlayer(behavior_dir)

    def getSharedData(self):
        return {'SMORES_INIT_HANDLER': self}
