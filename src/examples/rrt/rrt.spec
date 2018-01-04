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
rrt.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
rrtComplete, 1


======== SPECIFICATION ========

GlobalSensors: # Sensors accessible by all robots

OtherRobot: # The other robot in the same workspace

RegionMapping: # Mapping between region names and their decomposed counterparts
building = p6
r5 = p3
station1 = p2
station2 = p1
O2 = p9
others = 
O4 = p7
O3 = p8
r4 = p4
O1 = p10

Spec: # Specification in structured English
robot starts in station1

visit station2
visit station1

if you are not sensing rrtComplete then do not building
infinitely often rrtComplete

