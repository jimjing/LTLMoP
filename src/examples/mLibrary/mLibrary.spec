# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
climb, 1
push, 1
takePhoto, 1
pressButton, 1
crawl, 1

CompileOptions:
convexify: True
parser: structured
symbolic: False
use_region_bit_encoding: True
synthesizer: jtlv
fastslow: False
decompose: True

Customs: # List of custom propositions
photoTaken
pushingMouse
buttonPressed

RegionFile: # Relative path of region description file
mLibrary.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
doorClosed, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
door = p10
others = p1, p2, p3
mouseTarget = p8
desk = p11
bookshelf = p13
chair = p12
stairs = p4
hall = p9

Spec: # Specification in structured English
robot starts in hall with false

# push the door if it is closed
if you are in door and you are sensing doorClosed then do push

# climb stairs
if you are in stairs then do climb

# crawl under the chair
if you are in chair then do crawl

# take a photo at the bookshelf
do takePhoto if and only if you are in bookshelf
photoTaken is set on takePhoto and reset on false

# push the mouse to the target zone and press the button
pushingMouse is set on desk and push and reset on mouseTarget
if you are in mouseTarget and you activated pushingMouse then do pressButton
buttonPressed is set on pressButton and reset on false

# goals
infinitely often buttonPressed and photoTaken

