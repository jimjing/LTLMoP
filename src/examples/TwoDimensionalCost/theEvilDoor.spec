# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)

CompileOptions:
convexify: True
fastslow: False

CurrentConfigName:
Untitled configuration

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
theEvilDoor.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
BlockedB, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
r4 = p6
r5 = p5
r6 = p4
r7 = p3
r10 = p10
r2 = p9
r3 = p8
r8 = p2
others = 
r1 = p11

Spec: # Specification in structured English
go to r1
go to r2
go to r5
go to r7


# always not BlockedA or not BlockedB
infinitely often not BlockedB
# do BlockedA unless you sensed not BlockedA
# if BlockedA then do not r3
if BlockedB then do not r6

