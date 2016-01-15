#!/usr/bin/env python
"""
===============================================
SMORESActuator.py - SMORES Actuator Handler
===============================================
"""

import lib.handlers.handlerTemplates as handlerTemplates
#
import time
from numpy import pi
#
class SMORESActuatorHandler(handlerTemplates.ActuatorHandler):
    speed = 60 #drive speed
    rd = -1     #right direction
    ld = 1    # left direction

    def __init__(self, executor, shared_data):
        """
        Actuator handler for SMORES robot.
        """
        self.SMORESInitHandler = shared_data['SMORES_INIT_HANDLER']

    #####################################
    ### Available actuator functions: ###
    #####################################


    def runBehavior(self, behavior_name, actuatorVal, initial=False):
        """
        Run the given behavior

        behavior_name (string): The name of the behavior to run
        """
        if not actuatorVal:
            return
        if initial:
            pass
        else:
            self.SMORESInitHandler.MissionPlayer.playBehavior(behavior_name)

    ####

    def pickUp4holo(self, actuatorVal, intial=False):
        """
        Commands 4holo robot to sit down, drive under the box, and pick it up.
        """
        if not actuatorVal:
            return
        if initial:
            pass
        else:
            # sit down:
            print "Sit down"
            self.SMORESInitHandler.MissionPlayer.playBehavior('SitDown')
            # LowDriveForward:
            print('LowDriveForward')
            self.SMORESInitHandler.MissionPlayer.playBehavior('LowDriveForward')
            # Standup
            print('StandUp')
            self.SMORESInitHandler.MissionPlayer.playBehavior('StandUp')

    def moveBox4holo(self, actuatorVal, intial=False):
        """
        Commands 4holo robot to drive with the box, put it down, back up, and stand up 
        """
        if not actuatorVal:
            return
        if initial:
            pass
        else:
            # Stand Up:
            print "StandUp"
            self.SMORESInitHandler.MissionPlayer.playBehavior('StandUp')
            # TurnForward:
            print('TurnForward')
            self.SMORESInitHandler.MissionPlayer.playBehavior('TurnForward')
            # HighDriveForward
            print('HighDriveForward')
            self.SMORESInitHandler.MissionPlayer.playBehavior('HighDriveForward')
            # TurnNeutral:
            print "TurnNeutral"
            self.SMORESInitHandler.MissionPlayer.playBehavior('TurnNeutral')
            # SitDown:
            print('SitDown')
            self.SMORESInitHandler.MissionPlayer.playBehavior('SitDown')
            # LowDriveBackward 
            print('LowDriveBackward')
            self.SMORESInitHandler.MissionPlayer.playBehavior('LowDriveBackward')
            # Stand Up:
            print "StandUp"
            self.SMORESInitHandler.MissionPlayer.playBehavior('StandUp')

    def driveToDock4holo(self, actuatorVal, intial=False):
        """
        Commands 4holo robot to drive with the box, put it down, back up, and stand up 
        """
        if not actuatorVal:
            return
        if initial:
            pass
        else:
            # TurnLeft:
            print "TurnLeft"
            self.SMORESInitHandler.MissionPlayer.playBehavior('TurnLeft')
            # HighDriveLeft:
            print('HighDriveLeft')
            self.SMORESInitHandler.MissionPlayer.playBehavior('HighDriveLeft')

    ####

    def oneModulePush(self, actuatorVal, initial=False):
        '''
        make a single module push forward for 2 seconds, then pull back

        '''
        if not actuatorVal:
            return
        numRepeats = 3
        if initial:
            pass
        else:
            m = self.SMORESInitHandler.drivingModule
            for i in xrange(numRepeats):
                m.move.command_velocity('right', self.rd*self.speed, 6)
                time.sleep(0.05)
                m.move.command_velocity('left', self.ld*self.speed, 6)
                time.sleep(0.05)
            # wait
            time.sleep(6)
            # go back:
            for i in xrange(numRepeats):
                m.move.command_velocity('right', -self.rd*self.speed, 6)
                time.sleep(0.05)
                m.move.command_velocity('left', -self.ld*self.speed, 6)
                time.sleep(0.05)
            time.sleep(6)


    def spin(self, actuatorVal, initial=False):
        '''
        make a single module spin around 

        '''
        if not actuatorVal:
            return
        numRepeats = 3
        if initial:
            pass
        else:
            m = self.SMORESInitHandler.drivingModule
            # first, stop:
            for i in xrange(numRepeats):
                m.move.command_velocity('right', 0, 2)
                time.sleep(0.05)
                m.move.command_velocity('left', 0, 2)
                time.sleep(0.05)
            time.sleep(2)
            # then, back up
            for i in xrange(numRepeats):
                m.move.command_velocity('right', -self.rd*self.speed, 2)
                time.sleep(0.05)
                m.move.command_velocity('left', -self.ld*self.speed, 2)
                time.sleep(0.05)
            time.sleep(2)
            #then spin
            for i in xrange(numRepeats):
                m.move.command_velocity('right', self.rd*self.speed, 4)
                time.sleep(0.05)
                m.move.command_velocity('left', -self.ld*self.speed, 4)
                time.sleep(0.05)
            time.sleep(4)

    def dock(self, actuatorVal, initial=False):
        '''
        make module re-dock to cluster 

        '''
        if not actuatorVal:
            return
        numRepeats = 3
        if initial:
            pass
        else:
            m = self.SMORESInitHandler.drivingModule
            d = self.SMORESInitHandler.dockingModule
            # tilt back down to zero, and tilt d up by 10:
            for i in xrange(numRepeats):
                m.move.command_position('tilt', 0, 1)
                d.move.command_position('tilt', 15*pi/180, 1)
                time.sleep(0.05)
            time.sleep(1)
            # turn on magnets:
            for i in xrange(numRepeats):
                m.mag.control('top', 'on')
                d.mag.control('top', 'on')
                time.sleep(0.05)
            time.sleep(0.1)
            # drive forward:
            for i in xrange(numRepeats):
                m.move.command_velocity('right', self.rd*self.speed, 2)
                time.sleep(0.05)
                m.move.command_velocity('left', self.ld*self.speed, 2)
                time.sleep(0.05)
            time.sleep(2)
            # turn on magnets:
            for i in xrange(numRepeats):
                m.mag.control('top', 'on')
                d.mag.control('top', 'on')
                time.sleep(0.05)
            time.sleep(0.1)


    def undock(self, actuatorVal, initial=False):
        '''
        make module undock from cluster 

        '''
        numRepeats = 3
        if not actuatorVal:
            return
        if initial:
            pass
        else:
            m = self.SMORESInitHandler.drivingModule
            d = self.SMORESInitHandler.dockingModule
            # turn off magnets:
            print('undocking!')
            for i in xrange(numRepeats):
                m.mag.control('top', 'off')
                d.mag.control('top', 'off')
            time.sleep(0.5)
            # tilt up:
            for i in xrange(numRepeats):
                m.move.command_position('tilt', 20*pi/180, 1)
                time.sleep(0.05)
            # drive backward:
            for i in xrange(numRepeats):
                m.move.command_velocity('right', -self.rd*self.speed, 2)
                time.sleep(0.05)
                m.move.command_velocity('left', -self.ld*self.speed, 2)
                time.sleep(0.05)
            time.sleep(2)
            