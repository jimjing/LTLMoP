# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)

CompileOptions:
neighbour_robot: False
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: True
multi_robot_mode: negotiation
cooperative_gr1: True
fastslow: True
only_realizability: False
recovery: False
include_heading: False
winning_livenesses: False
synthesizer: slugs
decompose: True
interactive: False

CurrentConfigName:
noNeighbourRobotWIthFire

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
one_line_six_regions.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
bob_r5, 0
bob_r4, 0
bob_r3, 0
bob_r6, 0
bob_r2, 0
bob_r1, 0
fire, 1


======== SPECIFICATION ========

OtherRobot: # The other robot in the same workspace
bob

RegionMapping: # Mapping between region names and their decomposed counterparts
r4 = p3
r5 = p2
r6 = p1
r1 = p6
r2 = p5
r3 = p4
others = 

Spec: # Specification in structured English
Robot starts in r1
#Env starts with bob_r3

######### system goals ##########
visit r4
infinitely often not fire and finished r3
if you are sensing fire then do not r3

######### env goals #############
#infinitely often not bob_r2 and finished r2
#infinitely often not bob_r3 and finished r3
#infinitely often not bob_r4 and finished r4
#infinitely often not bob_r5 and finished r5
#infinitely often bob_r6

####### env assumptions  #########
#if you have finished r1 then do (bob_r2 or bob_r3) and not bob_r1
#if you have finished r2 then do (bob_r3 or bob_r4 or bob_r1) and not bob_r2
#if you have finished r3 then do (bob_r4 or bob_r5 or bob_r2 or bob_r1) and not bob_r3
#if you have finished r4 then do (bob_r5 or bob_r6 or bob_r3 or bob_r2) and not bob_r4
#if you have finished r5 then do (bob_r6 or bob_r3 or bob_r4) and not bob_r5
#if you have finished r6 then do (bob_r5 or bob_r4) and not bob_r6

######## system guarantees #######
#if you are sensing bob_r1 then do not r1 and (r2 or r3)
#if you are sensing bob_r2 then do not r2 and (r1 or r3 or r4)
#if you are sensing bob_r3 then do not r3 and (r1 or r2 or r4 or r5)
#if you are sensing bob_r4 then do not r4 and (r3 or r2 or r5 or r6)
#if you are sensing bob_r5 then do not r5 and (r4 or r3 or r6)
#if you are sensing bob_r6 then do not r6 and (r5 or r4)

