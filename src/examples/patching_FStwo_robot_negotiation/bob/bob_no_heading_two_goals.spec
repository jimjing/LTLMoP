# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)

CompileOptions:
neighbour_robot: True
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: True
multi_robot_mode: patching
fastslow: True
recovery: False
include_heading: False
synthesizer: slugs
decompose: True

CurrentConfigName:
bobWithAliceSensorR5

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
../two_robot_negotiation.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
alice_r1, 1
alice_r2, 1
alice_r3, 1
alice_r4, 1
alice_r5, 1


======== SPECIFICATION ========

OtherRobot: # The other robot in the same workspace
alice

RegionMapping: # Mapping between region names and their decomposed counterparts
r4 = p2
r5 = p1
r1 = p5
r2 = p4
r3 = p3
others = 

Spec: # Specification in structured English
####### initial conditions ##########
Robot starts in r1
Environment starts with alice_r5

###### environment assumptions ######
if you have finished r1 then do not (alice_r2 or alice_r1)
if you have finished r2 then do not (alice_r2 or alice_r4 or alice_r1)
if you have finished r4 then do not (alice_r4 or alice_r5 or alice_r2)
#if you have finished r3 then do not (alice_r3)
if you have finished r5 then do not (alice_r5 or alice_r4)

######### system guarantees ##########
# not allowing both robots to be at the same place
if you are sensing alice_r1 then do not r1
if you are sensing alice_r2 then do not r2
if you are sensing alice_r3 then do not r3
if you are sensing alice_r4 then do not r4
if you are sensing alice_r5 then do not r5

######## system goals ###########
visit r5
visit r1

