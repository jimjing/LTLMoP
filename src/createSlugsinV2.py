from itertools import *
import random
from pprint import pprint
random.seed(304932)

region_template = "& & x{} y{} z{}"
mutual_exclusion_template = "! & {} {}" # They will be connected by &

def regionIDToSLUGSString(region_id_):
    """ (1,2,3) -> "& & x1 y2 z3" """
    return region_template.format(region_id_[0], region_id_[1], region_id_[2])

def envDecisionIDToString(int_id_, id_list_):
    format_str_ = "{" + "0:{}b".format(len(id_list_)) + "}"
    out_str_ = "& " * (len(id_list_) - 1)
    for i, c in enumerate(format_str_.format(int_id_)):
        out_str_ += "! " if c == "0" else ""
        out_str_ += id_list_[i] + " "

    out_str_.rstrip(" ")
    return out_str_

# The number of divisions on each dimension
div_num = 5

# Environment fly decision id
env_fly_dec_id_list = ["EFD_0", "EFD_1"] # We will use them as binary so we have four decisions

# Environment goal decision id
env_goal_dec_id_list = ["EGD_0", "EGD_1"] # We will use them as binary so we have four decisions

# Dimension name
dim_name_list = ["x", "y", "z"]

# The id (coord) of each dimension, they are the same in this case
dim_id_list = range(div_num)

# Goals / Start position
temp_g = div_num-1
goal_list = ((0,0,0), (temp_g, temp_g, temp_g), (0, temp_g, 0), (temp_g, 0, temp_g))
start_pos = goal_list[0]

# Fly station
temp_f = div_num-2
fly_station_list = ((1,1,1), (temp_f, temp_f, temp_f), (0, temp_f, 0),(temp_f, 0, temp_f))

# Region list
region_id_list = list(product(dim_id_list, repeat = 3))
# Region without goal pr fly stations
region_clean_id_list = []
for region_id in region_id_list:
    if region_id not in goal_list and region_id not in fly_station_list:
        region_clean_id_list.append(region_id)

obs_num = int(round(div_num * 3 / 10)) # 10% regions are obstacles

# Construct robot safties

###############################################################################

# Cannot be in two coord positions in the same dimension at the same time
mutual_exclusion_coord_list = []
for dim_name in dim_name_list:
    for data in combinations(dim_id_list, 2):
        s0 = dim_name+str(data[0])
        s1 = dim_name+str(data[1])
        mutual_exclusion_coord_list.append(mutual_exclusion_template.format(s0, s1))

#pprint(mutual_exclusion_coord_list)

mutual_exclusion_coord_str = ""
mutual_exclusion_coord_str += "& " * (len(mutual_exclusion_coord_list) - 1) + " ".join(mutual_exclusion_coord_list) + "\n"

#pprint(mutual_exclusion_coord_str)

###############################################################################

# Must be at one coord position in every dimension
must_one_coord_list = []
for dim_name in dim_name_list:
    temp_list = [] # For this dimension

    for data in dim_id_list:
        temp_str = ""
        temp_str += "& " * (div_num - 1)
        temp_str += dim_name+ str(data) + " "
        temp_str += " ".join(["! " + dim_name + str(d) for d in dim_id_list if d!=data])
        temp_list.append(temp_str)

    must_one_coord_list.append(temp_list)

#pprint(must_one_coord_list)

must_one_coord_str = ""
for data in must_one_coord_list:
    must_one_coord_str += "| " * (len(data) - 1) + " ".join(data) + "\n"

#print(must_one_coord_str)

###############################################################################

# Create obstacles based on the environment goal decision numbers
num_of_obs_groups = 2 ** len(env_goal_dec_id_list)

obs_group_list = []
obs_str = ""
for i in xrange(num_of_obs_groups):
    temp_obs_list = random.sample(region_clean_id_list, obs_num)

    temp_goal_str = envDecisionIDToString(i, env_goal_dec_id_list)
    print(temp_goal_str)

    for region_id in temp_obs_list:

        temp_region_str = regionIDToSLUGSString(region_id)

        obs_str += "! & {} {}\n".format(temp_goal_str, temp_region_str)


































