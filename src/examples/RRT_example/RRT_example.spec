# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)

CompileOptions:
convexify: False
fastslow: False

CurrentConfigName:
basicsim

Customs: # List of custom propositions
vr1
vr3
g1
g3
vr4
g4

RegionFile: # Relative path of region description file
RRT_example.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
test, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
r4 = p4
others = 
r1 = p1
r2 = p2
r3 = p3

Spec: # Specification in structured English
Robot starts in r2 with false
Env starts with false

vr1 is set on r1 and reset on false
vr3 is set on r3 and reset on false
vr4 is set on r4 and reset on false

g1 is set on vr1 and reset on (vr1 and (not test or vr3) and vr4)
g3 is set on (not test or vr3) and reset on (vr1 and (not test or vr3) and vr4)
g4 is set on vr4 and reset on (vr1 and (not test or vr3) and vr4)

if not g3 then do not g4
if not g4 then do not g1

if you are not sensing test then do not r3
infinitely often test

#if you were in r1 then do r1


infinitely often vr1
infinitely often vr4
if you are sensing test then infinitely often vr3

