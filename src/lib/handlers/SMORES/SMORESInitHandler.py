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
        import sys
        sys.path.append(smores_lib_path)
        from SmoresModule import SmoresModule

        self.module = SmoresModule.SmoresModule(module_id)

    def getSharedData(self):
        return {'SMORES_INIT_HANDLER': self}
