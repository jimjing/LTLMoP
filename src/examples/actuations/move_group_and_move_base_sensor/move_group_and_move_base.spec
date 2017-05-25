# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
pickup, 1
drop, 1

CompileOptions:
neighbour_robot: False
convexify: False
parser: structured
symbolic: False
use_region_bit_encoding: False
multi_robot_mode: negotiation
cooperative_gr1: True
fastslow: True
only_realizability: False
recovery: False
include_heading: False
winning_livenesses: False
synthesizer: slugs
decompose: False
interactive: True

CurrentConfigName:
Untitled configuration

Customs: # List of custom propositions
sawObject
holdingObject
stop

RegionFile: # Relative path of region description file
../../../../../../../../home/catherine/LTLMoP/src/examples/_RegionFiles/one_line_two_regions.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
object, 1


======== SPECIFICATION ========

GlobalSensors: # Sensors accessible by all robots

OtherRobot: # The other robot in the same workspace

Spec: # Specification in structured English
Robot starts in r1

infinitely often drop and finished drop
# sense an object then pick it up
#if you are sensing object or sawObject and you are not activating holdingObject then do pickup

do pickup if and only if you are sensing object or sawObject and you are not activating holdingObject
sawObject is set on object and reset on finished pickup
holdingObject is set on finished pickup and reset on finished drop

# drop object to right ground
if you are activating holdingObject then visit r2
#if you are activating holdingObject and you have finished rightGround then do drop
do drop and stop if and only if you are activating holdingObject and you have finished r2

# patrol normally
if you are not activating holdingObject then visit r1

#if you are activating sawObject then visit pickup

# extra added
always not (pickup and drop)
#always ((pickup and not stop and not topLane and not rightLane and not bottomLane and not leftLane and not leftGround and not rightGround) or (not pickup and stop and not topLane and not rightLane and not bottomLane and not leftLane and not leftGround and not rightGround) or (not pickup and not stop and topLane and not rightLane and not bottomLane and not leftLane and not leftGround and not rightGround) or (not pickup and not stop and not topLane and rightLane and not bottomLane and not leftLane and not leftGround and not rightGround) or (not pickup and not stop and not topLane and not rightLane and bottomLane and not leftLane and not leftGround and not rightGround) or (not pickup and not stop and not topLane and not rightLane and not bottomLane and leftLane and not leftGround and not rightGround) or (not pickup and not stop and not topLane and not rightLane and not bottomLane and not leftLane and leftGround and not rightGround) or (not pickup and not stop and not topLane and not rightLane and not bottomLane and not leftLane and not leftGround and rightGround))

