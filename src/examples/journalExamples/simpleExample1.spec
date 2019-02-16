# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)

CompileOptions:
convexify: False
parser: structured
symbolic: False
use_region_bit_encoding: False
synthesizer: slugs
fastslow: False
decompose: True

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
simpleExample1.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
jam, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
r4 = p2
r1 = p5
r2 = p4
r3 = p3
others = 

Spec: # Specification in structured English
robot starts in r1 with false
visit r3

if you are sensing jam then do not r2

