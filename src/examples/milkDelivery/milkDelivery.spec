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
m1
m2
m3
m4
mAll
m5

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
others = 
r1 = p9
r2 = p10
r3 = p11
H2 = p3
S2 = p7
S1 = p6
H1 = p2
r8 = p16
r9 = p17
H4 = p5
B1 = p1
H3 = p4

Spec: # Specification in structured English
group house is H1,H2,H3,H4
group station is S1,S2

# Assumption of the environment goal
infinitely often not bridgeBlocked

# Use a memory proposition for each robot goals
m1 is set on (emptyBucket or H1) and reset on mAll
m2 is set on (emptyBucket or H2) and reset on mAll
m3 is set on (emptyBucket or H3) and reset on mAll
m4 is set on (emptyBucket or H4) and reset on mAll
m5 is set on (not emptyBucket or S1 or S2) and reset on mAll
# When all robot goals are satisfied
do mAll if and only if (m1 and m2 and m3 and m4 and m5)

# Robot should deliver the milk if it reaches a house and the bucket is not empty
do deliver if and only if you are not sensing emptyBucket and you are in any house
# Robot should refill the bucket at any station if the bucket is empty
do refill if and only if you are sensing emptyBucket and you are in any station
# Do not go to the bridge if it is blocked
if you are sensing bridgeBlocked then do not B1

# The modified robot goal
infinitely often mAll

