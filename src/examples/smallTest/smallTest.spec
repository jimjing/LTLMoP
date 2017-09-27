# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)

CompileOptions:
neighbour_robot: False
convexify: False
parser: structured
symbolic: False
use_region_bit_encoding: False
multi_robot_mode: negotiation
cooperative_gr1: False
fastslow: False
only_realizability: False
recovery: False
include_heading: False
winning_livenesses: False
synthesizer: slugs
decompose: False
interactive: False

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
smallTest.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
stop, 1


======== SPECIFICATION ========

GlobalSensors: # Sensors accessible by all robots

OtherRobot: # The other robot in the same workspace

Spec: # Specification in structured English
robot starts in r1
visit r3
visit r1
if you are sensing stop then do not r5
infinitely often not stop

