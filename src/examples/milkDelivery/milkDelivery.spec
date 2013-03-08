# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
deliver, 1
refill, 1

CompileOptions:
convexify: True
fastslow: False

CurrentConfigName:
test

Customs: # List of custom propositions
allDone
d1
d2
d3
d4
f1

RegionFile: # Relative path of region description file
milkDelivery.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
emptyBucket, 1
bridgeBlocked, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
r4 = p12
r5 = p13
r6 = p14
r7 = p15
r1 = p9
r2 = p10
r3 = p11
h2 = p5
h3 = p6
h1 = p4
r8 = p16
r9 = p17
h4 = p7
b1 = p1
others = 
c2 = p3
c1 = p2

Spec: # Specification in structured English
group house is h1,h2,h3,h4
group cow is c1,c2

infinitely often not bridgeBlocked

d1 is set on (emptyBucket or h1) and reset on allDone
d2 is set on (emptyBucket or h2) and reset on allDone
d3 is set on (emptyBucket or h3) and reset on allDone
d4 is set on (emptyBucket or h4) and reset on allDone
f1 is set on (not emptyBucket or c1 or c2) and reset on allDone


#if you are not sensing emptyBucket then visit all house
#if you are sensing emptyBucket then visit any cow

do deliver if and only if you are not sensing emptyBucket and you are in any house

do refill if and only if you are sensing emptyBucket and you are in any cow

if you are sensing bridgeBlocked then do not b1

do allDone if and only if (d1 and d2 and d3 and d4 and f1)
infinitely often allDone

