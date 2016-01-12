#!/usr/bin/env python
"""
==================================================================
SMORESLocomotionCommand.py - SMORES Locomotion Command Handler
==================================================================
"""
import sys, os


# Climb the tree to find out where we are
p = os.path.abspath(__file__)
t = ""
while t != "src":
    (p, t) = os.path.split(p)
    if p == "":
        print "I have no idea where I am; this is ridiculous"
        sys.exit(1)

sys.path.append(os.path.join(p,"src","lib"))

import lib.handlers.handlerTemplates as handlerTemplates

class SMORESLocomotionCommandHandler(handlerTemplates.LocomotionCommandHandler):
    def __init__(self, executor, shared_data):
        """
        Locomotion Command handler for SMORES robot.
        """

        self.SMORESInitHandler = shared_data['SMORES_INIT_HANDLER']

    def runBehavior(self, behavior_name):
        """
        Run the given behavior
        """
        self.SMORESInitHandler.mission_player.playBehavior(behavior_name)

if __name__ == "__main__":
    import SMORESInitHandler

    init = SMORESInitHandler.SMORESInitHandler(None, "4holo")
    loco = SMORESLocomotionCommandHandler(None, init.getSharedData())
    loco.runBehavior("LowDrive")

