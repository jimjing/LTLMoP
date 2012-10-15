# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
flashlight, 1

CompileOptions:
convexify: False
fastslow: False

CurrentConfigName:
Basic Simulation

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
ICRA2013.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
daytime, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
Hall4 = p4
Tunnel6 = p16
Tunnel1 = p11
Room4 = p9
Room5 = p10
Room2 = p7
Room3 = p8
Room1 = p6
Tunnel2 = p12
others = 
Tunnel5 = p15
Tunnel4 = p14
Tunnel7 = p17
Hall5 = p5
Hall2 = p2
Hall3 = p3
Tunnel3 = p13
Hall1 = p1

Spec: # Specification in structured English
Robot starts in Room2

#group office is Room2,Tunnel2,Room5,Tunnel2
#group office is Room2,Room5
#group classroom is Room1,Tunnel2,Room3,Room4
group classroom is Room3,Room1,Room4
group office is Room2,Room5


if you are not sensing daytime then visit Room2
if you are not sensing daytime then visit Room1
if you are not sensing daytime then visit Room5
if you are not sensing daytime then visit Room3
if you are not sensing daytime then visit Room4
if you are sensing daytime then visit all office

#if you are not sensing daytime then visit Room1

#if you are not sensing daytime then visit any office
#if you are not sensing daytime then visit Room4
#if you are not sensing daytime then visit Room3
#if you are not sensing daytime then visit Tunnel2
#if you are sensing daytime then visit all office
do flashlight if and only if you are sensing daytime

