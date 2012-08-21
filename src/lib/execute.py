#!/usr/bin/env python

""" =================================================
    execute.py - Top-level hybrid controller executor
    =================================================

    This module executes a hybrid controller for a robot in a simulated or real environment.

    :Usage: ``execute.py [-hn] [-a automaton_file] [-s spec_file]``

    * The controlling automaton is imported from the specified ``automaton_file``.

    * The supporting handler modules (e.g. sensor, actuator, motion control, simulation environment initialization, etc)
      are loaded according to the settings provided in the specified ``spec_file``.

    * Unless otherwise specified with the ``-n`` or ``--no_gui`` option, a status/control window
      will also be opened for informational purposes.
"""

import sys, os, getopt, textwrap
import threading, subprocess, time
import fileMethods, regions, fsa, project
from copy import deepcopy
import functools, re
from numpy import *
from handlers.motionControl.__is_inside import is_inside
from socket import *
import specCompiler
import itertools, glob

####################
# HELPER FUNCTIONS #
####################

def usage(script_name):
    """ Print command-line usage information. """

    print textwrap.dedent("""\
                              Usage: %s [-hn] [-a automaton_file] [-s spec_file]

                              -h, --help:
                                  Display this message
                              -n, --no-gui:
                                  Do not show status/control window
                              -a FILE, --aut-file FILE:
                                  Load automaton from FILE
                              -s FILE, --spec-file FILE:
                                  Load experiment configuration from FILE """ % script_name)

class LTLMoPExecutor(object):
    def __init__(self, spec_file, aut_file, show_gui=True):
        self.proj = None

        # Choose a timer func with maximum accuracy for given platform
        if sys.platform in ['win32', 'cygwin']:
            self.timer_func = time.clock
        else:
            self.timer_func = time.time

        self.show_gui = show_gui

        self.runFSA = threading.Event()  # Start out paused

        self.proj = project.Project()

        self.initialize(spec_file, aut_file, firstRun=True)

    def loadSpecFile(self, filename):
        if filename is not None:
            # Load configuration files

            new_proj = project.Project()
            new_proj.loadProject(filename)

            # Update with this new project
            self.proj = new_proj
            self.next_proj = new_proj

        if self.show_gui:
            # Tell GUI to load the spec file
            print "SPEC:" + self.proj.getFilenamePrefix() + ".spec"

    def loadAutFile(self, filename):
        print "Loading automaton..."

        aut = fsa.Automaton(self.proj)

        success = aut.loadFile(filename, self.proj.enabled_sensors, self.proj.enabled_actuators, self.proj.all_customs + self.proj.internal_props)

        return aut if success else None

    def _getCurrentRegionFromPose(self, rfi=None):
        if rfi is None:
            rfi = self.proj.rfi

        pose = self.proj.h_instance['pose'].getPose()

        region = None

        for i, r in enumerate(rfi.regions):
            if r.name.lower() == "boundary":
                continue

            pointArray = [self.proj.coordmap_map2lab(x) for x in r.getPoints()]
            vertices = mat(pointArray).T


            if r.objectContainsPoint(*self.proj.coordmap_lab2map(pose)):
                region = i
                break

        if region is None:
            print "Pose of ", pose, "not inside any region!"

        return region

    def doResynthesis(self):
        print "Starting resynthesis..."
        
        c = specCompiler.SpecCompiler()
        c.proj = self.next_proj

        # make sure rfi is non-decomposed here
        # NOTE: only matters if this is a proj that has been initialized
        if c.proj == self.proj:
            print "Resynthesis not necessary! (Specification has not changed)"
            return True

        #c.proj.loadRegionFile(decomposed=False)

        (realizable, realizableFS, output) = c.compile()
        print output

        if not (realizable or realizableFS):
            print "!!!!!!!!!!!!!!!!!!!!!!"
            print "ERROR: UNSYNTHESIZABLE"
            print "!!!!!!!!!!!!!!!!!!!!!!"
            self.runFSA.clear()
            print "PAUSED."
            return False

        print "New automaton has been created."

        self.proj = self.next_proj

        print "Reinitializing execution..."

        aut_file = self.proj.getFilenamePrefix() + ".aut"
        self.initialize(None, aut_file, firstRun=False)

        return True

    def rewriteSpec(self, group_name, operator, operand, n=itertools.count(1)):
        # reload from file instead of deepcopy because hsub stuff can include uncopyable thread locks, etc
        new_proj = project.Project()
        new_proj.setSilent(True)
        new_proj.loadProject(self.next_proj.getFilenamePrefix() + ".spec")

        # copy hsub references manually
        new_proj.hsub = self.proj.hsub
        new_proj.h_instance = self.proj.h_instance
        new_proj.sensor_handler = self.proj.sensor_handler
        new_proj.actuator_handler = self.proj.actuator_handler

        base_name = self.next_proj.getFilenamePrefix().rsplit('.',1)[0] # without the modifier
        newSpecName = "%s.step%d.spec" % (base_name, n.next())

        # Find the most recent region file
        newest_regions = max([self.proj.rfiold.filename] + glob.glob("%s.update*.regions" % base_name), key=lambda f: os.stat(f).st_mtime)

        print "Using newest region file: " + newest_regions
        new_proj.rfi.readFile(newest_regions)

        # Update region grouping with changed regions
        RegionGroupingRE = re.compile('^group\s+%s\s+(is|are)\s+(?P<regions>.+)\n' % group_name, re.IGNORECASE|re.MULTILINE)
        def gen_replacement_text(group_name, operand, m):
            regions = set(re.split(r"\s*,\s*", m.group('regions')))

            regions -= set(["empty"])

            if operator == "add":
                regions = regions | operand
            else:
                regions = regions - operand

            if not regions:
                regions = ['empty']
            
            return "group %s is %s\n" % (group_name, ", ".join(regions))

        new_proj.specText = RegionGroupingRE.sub(functools.partial(gen_replacement_text, group_name, operand), new_proj.specText)

        # TODO: Order goals properly!!!!!!!!!!!!!!!!

        # Constrain initial condition to current state
        # FIXME: We probably ought to constrain to the decomposed region, not the larger one
        current_region = new_proj.rfi.regions[self._getCurrentRegionFromPose(rfi=new_proj.rfi)].name
        current_sys_state = " and ".join([k if v else "not " + k for k,v in self.aut.current_outputs.iteritems() if not k.startswith("_")])
        sys_init_formula = "robot starts in {0} with {1}\n".format(current_region, current_sys_state)

        # delete old ones
        r = re.compile("^robot\s+starts\s+(in|with).*\n", flags=re.IGNORECASE|re.MULTILINE)
        new_proj.specText = r.sub("", new_proj.specText)
        # TODO: can we constrain the environment more?
        r = re.compile("^env(ironment)?\s+starts\s+with.*\n", flags=re.IGNORECASE|re.MULTILINE)
        new_proj.specText = r.sub("", new_proj.specText)

        # prepend to beginning
        new_proj.specText = sys_init_formula + new_proj.specText

        new_proj.writeSpecFile(newSpecName)

        print "Wrote new spec file: %s" % newSpecName

        self.next_proj = new_proj
        
    def checkForInternalFlags(self):
        for k in sorted(self.aut.current_outputs.keys()): # sort ensures group updates happen before resynthesis when triggered in same state
            # Only trigger on rising edges
            if not (int(self.prev_outputs[k]) == 0 and int(self.aut.current_outputs[k]) == 1):
                continue

            m = re.match("_(?P<action>add_to|remove_from)_(?P<groupName>\w+)", k)
            if m is not None:
                # Decide referent by currently-true sensor values (we assume these are mutually exclusive)
                # HACK/FIXME: don't hardcode sensor prop names
                if int(self.aut.next_state.inputs['region_added']) == 1:
                    referent = self.proj.h_instance['sensor'][self.proj.currentConfig.main_robot].addedRegions
                elif int(self.aut.next_state.inputs['region_removed']) == 1:
                    referent = self.proj.h_instance['sensor'][self.proj.currentConfig.main_robot].removedRegions
                # TODO: add finalization referent case
                else:
                    print "ERROR: missing group update referent"
                
                if m.group('action') == "add_to":
                    print "Added region(s) %s to group %s." % (", ".join(referent), m.group('groupName'))
                    self.rewriteSpec(m.group('groupName'), 'add', referent)
                elif m.group('action') == "remove_from":
                    print "Removed region(s) %s from group %s." % (", ".join(referent), m.group('groupName'))
                    self.rewriteSpec(m.group('groupName'), 'remove', referent)
            elif k == "resynthesize":
                # TODO: maybe requires a stay-there for non-F/S?
                # TODO: maybe this should be a shared actuator handler function instead of a hardcoded keyword?
                self.doResynthesis()

    def _guiListen(self):
        """
        Processes messages from the GUI window, and reacts accordingly
        """

        # Set up socket for communication from simGUI
        addrFrom = ('localhost', 9562)
        UDPSockFrom = socket(AF_INET, SOCK_DGRAM)
        UDPSockFrom.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        UDPSockFrom.bind(addrFrom)

        while 1:
            # Wait for and receive a message from the subwindow
            data_in, addrFrom = UDPSockFrom.recvfrom(1024)

            if data_in == '':  # EOF indicates that the connection has been destroyed
                print "GUI listen thread is shutting down!"
                break

            data_in = data_in.strip()

            # Check for the initialization signal, if necessary
            if not self.guiListenInitialized.isSet() and data_in == "Hello!":
                self.guiListenInitialized.set()
                continue

            # Do what the GUI tells us, lest we anger it
            if data_in == "START":
                self.runFSA.set()
            elif data_in == "PAUSE":
                self.runFSA.clear()
                print "PAUSED."
            else:
                print "WARNING: Unknown command received from GUI: " + data_in

    def startGUI(self):
        self.guiListenInitialized = threading.Event()

        # Create a subprocess
        print "Starting GUI window and listen thread..."
        p_gui = subprocess.Popen(["python", "-u", os.path.join(self.proj.ltlmop_root, "lib", "simGUI.py")])

        # Create new thread to communicate with subwindow
        guiListenThread = threading.Thread(target = self._guiListen)
        guiListenThread.start()

        # Set up socket for communication to simGUI
        addrTo = ('localhost', 9563)
        UDPSockTo = socket(AF_INET, SOCK_DGRAM)

        # Block until the GUI listener gets the go-ahead from the subwindow
        self.guiListenInitialized.wait()

        # Redirect all output to the log
        redir = RedirectText(UDPSockTo, addrTo)

        sys.stdout = redir
        sys.stderr = redir

    def initialize(self, spec_file, aut_file, firstRun=True):
        # Start status/control GUI
        if firstRun and self.show_gui:
            self.startGUI()

        # load project only first time; otherwise self.proj is modified in-place
        self.loadSpecFile(spec_file)

        self.proj.rfiold = self.proj.rfi  # Save the undecomposed regions
        self.proj.rfi = self.proj.loadRegionFile(decomposed=True)
        self.proj.hsub.proj = self.proj  # FIXME: this is kind of ridiculous...

        # Import the relevant handlers
        if firstRun:
            print "Importing handler functions..."
            self.proj.importHandlers()
        else:
            print "Reloading motion control handler..."
            self.proj.importHandlers(['motionControl'])

        # Load automaton file
        new_aut = self.loadAutFile(aut_file)

        if firstRun:
            ### Wait for the initial start command
            if show_gui:
                self.runFSA.wait()
            else:
                raw_input('Press enter to begin...')
                self.runFSA.set()

        ### Figure out where we should start from

        init_region = self._getCurrentRegionFromPose()
        if init_region is None:
            print "Initial pose not inside any region!"
            sys.exit(-1)

        print "Starting from initial region: " + self.proj.rfi.regions[init_region].name

        ### Have the FSA find a valid initial state

        if firstRun:
            # Figure out our initially true outputs
            init_outputs = []
            for prop in self.proj.currentConfig.initial_truths:
                if prop not in self.proj.enabled_sensors:
                    init_outputs.append(prop)

            init_state = new_aut.chooseInitialState(init_region, init_outputs)
        else:
            # Figure out our initially true outputs
            init_outputs = [k for k,v in self.aut.current_outputs.iteritems() if int(v) == 1]

            init_state = new_aut.chooseInitialState(init_region, init_outputs)#, goal=prev_z)

        if init_state is None:
            print "No suitable initial state found; unable to execute. Quitting..."
            sys.exit(-1)
        else:
            print "Starting from state %s." % init_state.name

        self.aut = new_aut

    def run(self):
        avg_freq = 0
        last_gui_update_time = 0

        while True:
            # Idle if we're not running
            if not self.runFSA.isSet():
                self.proj.h_instance['drive'].setVelocity(0,0)
                self.runFSA.wait()

            self.prev_outputs = deepcopy(self.aut.current_outputs)
            self.prev_z = self.aut.current_state.rank

            tic = self.timer_func()
            self.aut.runIteration()
            toc = self.timer_func()

            self.checkForInternalFlags()

            # Update GUI, no faster than 20Hz
            if show_gui and (time.time() - last_gui_update_time > 0.05):
                avg_freq = 0.9*avg_freq + 0.1*1/(toc-tic) # IIR filter
                print "Running at approximately %dHz..." % int(avg_freq)
                pose = self.proj.h_instance['pose'].getPose(cached=True)[0:2]
                print "POSE:%d,%d" % tuple(map(int, self.proj.coordmap_lab2map(pose)))

                last_gui_update_time = time.time()

class RedirectText:
    """
    A class that lets the output of a stream be directed into a socket.

    http://mail.python.org/pipermail/python-list/2007-June/445795.html
    """

    def __init__(self,s,addrTo):
        self.s = s
        self.addrTo = addrTo

    def write(self,string):
        self.s.sendto(string, self.addrTo)

####################################################
# Main function, run when called from command-line #
####################################################

if __name__ == "__main__":
    ### Check command-line arguments

    aut_file = None
    spec_file = None
    show_gui = True

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hna:s:", ["help", "no-gui", "aut-file=", "spec-file="])
    except getopt.GetoptError, err:
        print str(err)
        usage(sys.argv[0])
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(sys.argv[0])
            sys.exit()
        elif opt in ("-n", "--no-gui"):
            show_gui = False
        elif opt in ("-a", "--aut-file"):
            aut_file = arg
        elif opt in ("-s", "--spec-file"):
            spec_file = arg

    if aut_file is None:
        print "ERROR: Automaton file needs to be specified."
        usage(sys.argv[0])
        sys.exit(2)

    if spec_file is None:
        print "ERROR: Specification file needs to be specified."
        usage(sys.argv[0])
        sys.exit(2)

    print "\n[ LTLMOP HYBRID CONTROLLER EXECUTION MODULE ]\n"
    print "Hello. Let's do this!\n"

    e = LTLMoPExecutor(spec_file, aut_file, show_gui)
    e.run()


