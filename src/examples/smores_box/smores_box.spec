# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
pickup, 1
drop, 1
dock, 1

CompileOptions:
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: True
synthesizer: jtlv
fastslow: True
decompose: True

CurrentConfigName:
sim_smore

Customs: # List of custom propositions
carry
dropped

RegionFile: # Relative path of region description file
smores_box.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
box, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
r3 = p1
r1 = p3
r2 = p2
others = 

Spec: # Specification in structured English
carry is set on pickup and reset on false
dropped is set on drop and reset on false

do pickup if and only if you were sensing box and you are not activating carry
do dock if and only if you are activating dropped
do drop if and only if you were activating carry and you are not activating dropped

