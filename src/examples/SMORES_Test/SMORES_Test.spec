# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
push, 1
spin, 1
docking, 1

CompileOptions:
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: True
synthesizer: jtlv
fastslow: True
decompose: True

CurrentConfigName:
sim

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
loc2 = p8
dock = p10
loc1 = p9
others = p11, p12, p13, p14

Spec: # Specification in structured English
Robot starts in dock

if you are sensing cup and you were in loc1 or loc2 then do spin
if you are sensing trash and you were in loc1 or loc2 then do push

if you are activating spin or push then stay there
infinitely often not (cup or trash)

loc1visited is set on loc1 and reset on false
loc2visited is set on loc2 and reset on false

do docking if and only if you were in dock and you are activating (loc1visited and loc2visited)

infinitely often do docking

