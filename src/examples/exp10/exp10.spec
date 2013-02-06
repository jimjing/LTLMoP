# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
resynthesize, 1
flag, 1
gotoPOI, 1

CompileOptions:
convexify: True
fastslow: False

CurrentConfigName:
Untitled configuration

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
exp10.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
tempNewRegion, 1
hazardous, 1
assignment, 1
newOffice, 1
detectPOI, 1
gotoPOIDone, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
classroom1 = p4
hall1 = p3
hall2 = p2
office1 = p1
others = 

Spec: # Specification in structured English
Environment starts with false
Robot starts with false

Always not (tempNewRegion and newOffice)
#Always not ((tempNewRegion or newOffice) and hazardous)

Group Hallways is hall1, hall2
Group Offices is office1
Group tempNewRegions is empty

#visit all tempNewRegions

gotoPOI is set on detectPOI and reset on gotoPOIDone
If you were activating gotoPOI or you are activating gotoPOI then stay there

Do flag if and only if you are sensing hazardous

If you are sensing tempNewRegion then do resynthesize and add to tempNewRegions
If you are sensing newOffice then do resynthesize and add to tempNewRegions

If you are sensing tempNewRegion or you are sensing newOffice then stay
If you are not sensing tempNewRegion and you are not sensing newOffice then do not resynthesize

If you are not sensing assignment and you are not activating resynthesize and you are not activating gotoPOI then visit all tempNewRegions
If you are not sensing assignment and you are not activating resynthesize and you are not activating gotoPOI then visit all Hallways

