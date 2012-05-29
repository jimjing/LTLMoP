# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
flag, 1
explore_room, 1

CompileOptions:
convexify: False
fastslow: False

Customs: # List of custom propositions
explore
resynthesize

RegionFile: # Relative path of region description file
exp10.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
homework, 1
explore_room_done, 1
topology_changed, 1
region_blocked, 1
room_category_classroom, 1
region_added, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
r1 = p2
others = p1

Spec: # Specification in structured English
### main spec ###

robot starts with false

group classrooms is classroom1
group halls is hall1, hall2

if you are not sensing homework then visit all halls
if you are sensing homework then visit all classrooms

do flag if and only if you are sensing homework and you are in any classroom

### exploration settings ###

do explore if and only if you are not sensing homework
if you are sensing explore_room_done and room_category_classroom then add to classrooms and do resynthesize

# resynthesis will be automatic here, but we want to make sure the new spec is realizable
if you are sensing region_blocked and room_category_classroom then remove from classrooms and do resynthesize

### exploration (auto-generated) ###

# keep track of places you need to explore, at all times (TODO: BFS vs DFS?)
group unexplored_areas is empty
if you are sensing start of region_added then add to unexplored_areas
if you are sensing start of region_blocked then remove from unexplored_areas
if you are sensing start of region_added or region_blocked and you are activating explore then do resynthesize

# env fairness
if you are activating explore_room then infinitely often do explore_room_done
if you are not activating explore_room then do not explore_room_done

# actually explore the targets, if told to
if you are activating explore then visit all unexplored_areas and explore_room and explore_room_done at least once
if you were activating explore_room then stay there
if you are sensing explore_room_done then remove from unexplored_areas

# resynthesize when explore becomes true (FIXME: only do this if the regions changed)
if you are sensing start of explore then do resynthesize

