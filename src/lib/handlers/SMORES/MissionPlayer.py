import sys
#sys.path.insert(0, '..')
# Add SMORES libraries to path:
sys.path.insert(0, '/home/tarik/Embedded/ecosystem/smores_build/smores_reconfig/python')
from SmoresModule import SmoresCluster 
#
import xml.etree.ElementTree as ET
from numpy import pi
import time
import pdb
#


class MissionPlayer():
    '''
        MissionPlayer.py:
        This class can load multiple low-level behaviors, and execute them on
        the modules.
    '''
    configurations_dir = '/home/tarik/Embedded/ecosystem/smores_build/smores_reconfig/python/configurations'
    jointNameMap = { # simulator uses different DoF names than hardware
        'Body': 'tilt',
        'LeftWheel': 'left',
        'RightWheel': 'right',
        'FrontWheel': 'pan'
    }
    signMap = {   # Simulator uses different sign convention than hardware
        'tilt': -1,
        'left': 1,
        'right': -1,
        'pan': -1
    }
    numRepeats = 4 
    sendInterval = 0.005

    #speed_scale = 0.5   

    def __init__(self, dirname, debugMode=False):
        ''' constructor '''
        # If we're running in debug mode, we don't send commands to any modules.
        self.debugMode = debugMode
        # Import the config file:

        sys.path.insert(0, self.configurations_dir+'/'+dirname)
        import config
        MissionPlayer.config = config
        self.speed_scale = self.config.speed_scale
        # ModuleMap maps module names from the simulator to actual hardware module numbers.
        self.ModuleMap = self.config.ModuleMap 
        self.NeutralPositions = self.config.NeutralPositions
        self.disabledDof = self.config.disabledDof #These DoF will not move
        self.behaviorFiles = self.config.behaviorFiles

        # Parse all behaviors and store in a dict:
        self.parsed_behaviors = {}
        for name in self.behaviorFiles.keys():
            #try:
            filepath = self.configurations_dir+'/'+dirname+'/'+self.behaviorFiles[name]
            self.parsed_behaviors[name] = self.parseSimulatorXML(filepath)
            #    print 'Parsed behavior ' + str(name) + ' from file ' + str(self.behaviorFiles[name])
            #except:
            #    raise Exception('Could not parse behavior file ' + str(self.behaviorFiles[name]))
        
        # Create a cluster with all of the hardware modules specified in config file.
        if not self.debugMode:
            self.c = SmoresCluster.SmoresCluster(self.ModuleMap.values())
            # verify cluster is on by requesting battery states:
            print('Battery voltages:')
            moduleList = self.c.mods.keys()
            repeat=True
            while repeat:
                repeat=False
                for n in self.c.mods.keys():
                    m = self.c.mods[n]
                    if n is 20:
                        continue # hack
                    try:
                        voltage = m.req.requestBatteryCondition(True)
                        print( str(n) + ': ' + str(voltage) )
                        moduleList.remove(n)
                    except:
                        print( 'Module '+str(n) + ' did not respond!')
                        #repeat=True

    ###### Functions for cluster management:
    def allMagnets(self, state):
        ''' Fires all magnets on all faces'''
        if self.debugMode:
            return
        for m in self.c.mods.values():
            for face in ['top', 'bottom']:
                m.mag.control(face, state)

    def reset(self):
        ''' Sends all modules to neutral positions '''
        for moduleName in self.ModuleMap.keys():
            moduleNumber = self.ModuleMap[moduleName]
            m = self.c.mods[moduleNumber]
            # send each DoF in the neutral positions dict to neutral position:
            for dofName in self.NeutralPositions[moduleName].keys():
                p = self.NeutralPositions[moduleName][dofName]
                m.move.command_position(dofName, p, 3)

    def motorsOff(self):
        ''' Sends zero torque to all modules. '''
        for moduleName in self.ModuleMap.keys():
            moduleNumber = self.ModuleMap[moduleName]
            m = self.c.mods[moduleNumber]
            # send each DoF in the neutral positions dict to neutral position:
            for dofName in self.NeutralPositions[moduleName].keys():
                m.move.send_torque(dofName, 0)

    ###### Functions for playing behaviors:
    def parseSimulatorXML(self, fileName=None):
        ''' Parses an XML behavior from the simulator '''
        tree = ET.parse(fileName)
        root = tree.getroot() # root is everything in the <behavior> tag
        xRobotStates = root[0]
        behaviorList = []
        # xml things start with x.
        for xRobotState in xRobotStates:
            newState = {} # a new state. Keys will be module names.
            xModuleStates = xRobotState.find('ModuleStates')
            for xModuleState in xModuleStates:
                # ModuleState is the state of a single module in the cluster.
                moduleName = xModuleState.get('name')
                newState[moduleName] = {} # New entry for a module. Keys will be DoF names. 
                xJointCommands = xModuleState.find('JointCommands')
                for xJointCommand in xJointCommands:
                    xJointName = xJointCommand.get('name') # simulator uses different joint naming convention than hardware.
                    dofName = self.jointNameMap[xJointName]
                    commandType = xJointCommand[0].text
                    targetValue = self.signMap[dofName]*float(xJointCommand[1].text)
                    period      = float(xJointCommand[2].text)
                    newState[moduleName][dofName] = {'commandType': commandType,
                                                       'targetValue': targetValue,
                                                       'period'     : period }
            behaviorList.append(newState)                                           
        return behaviorList

    def playBehavior(self, behaviorName, repeats = 1):
        ''' Plays the behavior. '''
        assert self.parsed_behaviors.has_key(behaviorName), 'No behavior named ' + behaviorName
        behaviorList = self.parsed_behaviors[behaviorName]
        for repeat in xrange(repeats):
            for i,robotState in enumerate(behaviorList):
                #raw_input('enter for next state...')
                self.allMagnets('on')
                print('State ' + str(i))
                maxDuration = 0.0 # duration of command in this state
                for (moduleName, moduleNumber) in self.ModuleMap.iteritems():
                    moduleState = robotState[moduleName]
                    for (dofName, command) in moduleState.iteritems():
                        maxDuration = max(maxDuration, float(command['period']))
                        self.sendModuleCommand(moduleNumber, dofName, command)
                print('waiting ' + str(maxDuration)+ ' seconds...')
                print
                time.sleep(maxDuration) 

    def sendModuleCommand(self, moduleNumber, dofName, command):
        ''' Sends commands to a module based on moduleState dict passed in. '''
        if dofName in self.disabledDof:
            return # don't move the disabled DoF.
        commandType   = command['commandType']
        periodSeconds = command['period']
        targetValue   = command['targetValue']
        if commandType == 'Position':
            # for position commands, targetValue is the desired position
            # in degrees.  Convert to radians before sending:
            positionRadians = targetValue * (pi/180.0)
            print(str(moduleNumber)+ ', ' + dofName + ', pos: ' + str(positionRadians) + ', ' + str(periodSeconds) )
            if not (dofName == 'right' or dofName== 'left'): # skip for left and right:
                for i in xrange(self.numRepeats):
                    if not self.debugMode:
                        self.c.mods[moduleNumber].move.command_position(dofName, positionRadians, periodSeconds)
                    time.sleep(self.sendInterval)
        if commandType == 'Velocity':
            # for velocity commands, targetValue is desired velocity in 
            # degrees/sec.  Convert to PWM:
            velocityPWM = int((targetValue/90.0)*100) * self.speed_scale
            print(str(moduleNumber)+ ', ' + dofName + ', vel: ' + str(velocityPWM) + ', ' + str(periodSeconds))
            for i in xrange(self.numRepeats):
                if not self.debugMode:
                    self.c.mods[moduleNumber].move.command_velocity(dofName, velocityPWM, periodSeconds)
                time.sleep(self.sendInterval)
if __name__ == '__main__':
    if len(sys.argv) > 1:
        dirname = sys.argv.pop()
    #sys.path.insert(0, dirname)
    #import config
    #MissionPlayer.config = config
    p = MissionPlayer(dirname)
    # raw_input('Enter for LowDrive...')
    # p.playBehavior('LowDrive')
    # raw_input('enter for standup...')
    # p.playBehavior('StandUp.xml')
    # raw_input('Enter for StandDrive...')
    # p.playBehavior('StandDrive.xml')
    # raw_input('Enter for sitdown...')
    # p.playBehavior('SitDown.xml')
    # #s.playBehavior()







