# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
push, 1
spin, 1
docking, 1
undock, 1
climbup, 1
climbdown, 1

CompileOptions:
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: True
synthesizer: jtlv
fastslow: True
decompose: True

CurrentConfigName:
SMORES

Customs: # List of custom propositions
loc1visited
loc2visited

RegionFile: # Relative path of region description file
SMORES_Test.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
cup, 1
trash, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
loc2 = p15, p16
dock = p7
loc1 = p5
others = p8, p9, p10, p11, p12
ground = p13, p14

Spec: # Specification in structured English
Robot starts false

if you are sensing cup  then do spin
if you are sensing trash then do push

loc1visited is set on loc1 and reset on false
loc2visited is set on loc2 and reset on false

do docking if and only if you were in dock and you are activating (loc1visited and loc2visited)

do undock if and only if you were in dock and you are not activating (loc1visited or loc2visited)

do climbdown if and only if you were in dock and you activated  (loc1visited and loc2visited)

do climbup if and only if you were in ground and you are not activating (loc1visited or loc2visited)

infinitely often do docking

