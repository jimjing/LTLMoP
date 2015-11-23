# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
climb, 1
takePhoto, 1
pressButton, 1
crawl, 1
pushMouse, 1
pushDoor, 1

CompileOptions:
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: True
synthesizer: jtlv
fastslow: False
decompose: True

CurrentConfigName:
Untitled configuration

Customs: # List of custom propositions
photoTaken
buttonPressed

RegionFile: # Relative path of region description file
mLibrary.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
doorClosed, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
r4 = p8
r5 = p7
door = p14
vent = p4
mouseTarget = p12
desk = p15
bookshelf = p17
chair = p16
stairs = p5
hall = p13
others = p1, p2, p3

Spec: # Specification in structured English
robot starts in hall with false

# push the door if it is closed
if you are in door and you are sensing doorClosed then do pushDoor

# crawl under the vent
if you are in vent then do crawl

# climb stairs
if you are in stairs then do climb

# crawl under the chair
if you are in chair then do crawl

# take a photo at the bookshelf
do takePhoto if and only if you are in bookshelf
photoTaken is set on takePhoto and reset on false

# push the mouse to the target zone and press the button
if you are in desk and you are not activating buttonPressed then do pushMouse
do pressButton if and only if you are in mouseTarget
buttonPressed is set on pressButton and reset on false

# goals
infinitely often photoTaken and buttonPressed

