# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.
# Note that all values are separated by *tabs*.


======== EXPERIMENT CONFIG 0 ========

Calibration: # Coordinate transformation between map and experiment: XScale, XOffset, YScale, YOffset
0.0161324195365,-5.18045013709,-0.0146557950745,4.12082218245

InitialRegion: # Initial region number
2

InitialTruths: # List of initially true propositions

Lab: # Lab configuration file
pioneer_shahar.lab

Name: # Name of the experiment
Default

RobotFile: # Relative path of robot description file
pioneer_shahar.robot


======== SETTINGS ========

Actions: # List of actions and their state (enabled = 1, disabled = 0)
resynthesize,1
flag,1
gotoPOI,1

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
step1.regions

Sensors: # List of sensors and their state (enabled = 1, disabled = 0)
tempNewRegion,1
hazardous,1
assignment,1
newOffice,1
detectPOI,1
gotoPOIDone,1

currentExperimentName:
Default


======== SPECIFICATION ========

RegionMapping:

classroom1=p5
office1=p2
others=
tempNew1=p1
hall2=p3
hall1=p4

Spec: # Specification in simple English
Environment starts with false
Robot starts with

Always not (tempNewRegion and newOffice)
#Always not ((tempNewRegion or newOffice) and hazardous)

Group Hallways is hall1, hall2
Group Offices is office1
Group tempNewRegions is tempNew1, empty

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

