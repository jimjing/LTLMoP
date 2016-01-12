# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)

CompileOptions:
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: True
synthesizer: jtlv
fastslow: False
decompose: True

CurrentConfigName:
SMORES

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
SMORES_Test.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
r3 = p2
r1 = p4
r2 = p3
others = p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16

Spec: # Specification in structured English
visit r1
visit r2
visit r3

