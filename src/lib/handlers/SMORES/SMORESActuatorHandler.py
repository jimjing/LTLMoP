#!/usr/bin/env python
"""
===============================================
SMORESActuator.py - SMORES Actuator Handler
===============================================
"""

import lib.handlers.handlerTemplates as handlerTemplates
#
import time
#
class SMORESActuatorHandler(handlerTemplates.ActuatorHandler):
    speed = 50 #drive speed
    rd = 1     #right direction
    ld = -1    # left direction

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
            self.SMORESInitHandler.MissionPlayer.playBehavior(behavior_name)

    def oneModulePush(self, initial=False):
        '''
        make a single module push forward for 2 seconds, then pull back

        '''
        numRepeats = 3
        if initial:
            pass
        else:
            m = self.SMORESInitHandler.drivingModule
            for i in xrange(numRepeats):
                m.move.command_velocity('right', self.rd*self.speed, 2)
                time.sleep(0.05)
                m.move.command_velocity('left', self.ld*self.speed, 2)
                time.sleep(0.05)
            # wait
            time.sleep(2)
            # go back:
            for i in xrange(numRepeats):
                m.move.command_velocity('right', -self.rd*self.speed, 2)
                time.sleep(0.05)
                m.move.command_velocity('left', -self.ld*self.speed, 2)
                time.sleep(0.05)


    def spin(self, initial=False):
        '''
        make a single module spin around 

        '''
        numRepeats = 3
        if initial:
            pass
        else:
            m = self.SMORESInitHandler.drivingModule
            for i in xrange(numRepeats):
                m.move.command_velocity('right', self.rd*self.speed, 2)
                time.sleep(0.05)
                m.move.command_velocity('left', -self.ld*self.speed, 2)
                time.sleep(0.05)

    def dock(self, initial=False):
        '''
        make module re-dock to cluster 

        '''
        numRepeats = 3
        if initial:
            pass
        else:
            m = self.SMORESInitHandler.drivingModule
            d = self.SMORESInitHandler.dockingModule
            # drive forward:
            for i in xrange(numRepeats):
                m.move.command_velocity('right', self.rd*self.speed, 2)
                time.sleep(0.05)
                m.move.command_velocity('left', self.ld*self.speed, 2)
                time.sleep(0.05)
            # turn on magnets:
            for i in xrange(numRepeats):
                m.mag.control('top', 'on')
                d.mag.control('top', 'on')


    def undock(self, initial=False):
        '''
        make module undock from cluster 

        '''
        numRepeats = 3
        if initial:
            pass
        else:
            m = self.SMORESInitHandler.drivingModule
            d = self.SMORESInitHandler.dockingModule
            # turn off magnets:
            for i in xrange(numRepeats):
                m.mag.control('top', 'off')
                d.mag.control('top', 'off')
            # drive forward:
            for i in xrange(numRepeats):
                m.move.command_velocity('right', self.rd*self.speed, 2)
                time.sleep(0.05)
                m.move.command_velocity('left', self.ld*self.speed, 2)
                time.sleep(0.05)
            