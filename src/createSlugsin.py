from itertools import *
from random import random, seed
seed(304932)

def zip(*iterables):
    # izip('ABCD', 'xy') --> Ax By
    iterators = map(iter, iterables)
    while iterators:
        yield tuple(map(next, iterators))

div_num = 5
min_obs = 1
max_obs = div_num - min_obs + 2
min_fly = 2
max_fly = div_num - min_fly + 1

x_dim = ["xdim"+str(i) for i in xrange(1, 1+div_num)]
y_dim = ["ydim"+str(i) for i in xrange(1, 1+div_num)]
z_dim = ["zdim"+str(i) for i in xrange(1, 1+div_num)]
t_dim = ["tdim"+str(i) for i in xrange(1, 1+div_num)]

#print x_dim
#print y_dim
#print z_dim
#print t_dim
#print

mutual_x_list = []
for data in combinations(x_dim, 2):
    mutual_x_list.append("! & {} {}".format(data[0], data[1]))
mutual_y_list = []
for data in combinations(y_dim, 2):
    mutual_y_list.append("! & {} {}".format(data[0], data[1]))
mutual_z_list = []
for data in combinations(z_dim, 2):
    mutual_z_list.append("! & {} {}".format(data[0], data[1]))
mutual_t_list = []
for data in combinations(t_dim, 2):
    mutual_t_list.append("! & {} {}".format(data[0], data[1]))

#print mutual_x_list
#print mutual_y_list
#print mutual_z_list
#print mutual_t_list
#print

mutual_str = ""
mutual_str += "& " * (len(mutual_x_list) - 1) + " ".join(mutual_x_list) + "\n"
mutual_str += "& " * (len(mutual_y_list) - 1) + " ".join(mutual_y_list) + "\n"
mutual_str += "& " * (len(mutual_z_list) - 1) + " ".join(mutual_z_list) + "\n"
#mutual_str += "& " * (len(mutual_t_list) - 1) + " ".join(mutual_t_list) + "\n"

#print mutual_str
#print

must_one_x_list = []
for i, data in enumerate(x_dim):
    temp_str = ""
    temp_str += "& " * (len(x_dim) - 1)
    temp_str += data + " "
    temp_str += " ".join(["! " + d for d in x_dim if d!=data])
    must_one_x_list.append(temp_str)
must_one_y_list = []
for i, data in enumerate(y_dim):
    temp_str = ""
    temp_str += "& " * (len(y_dim) - 1)
    temp_str += data + " "
    temp_str += " ".join(["! " + d for d in y_dim if d!=data])
    must_one_y_list.append(temp_str)
must_one_z_list = []
for i, data in enumerate(z_dim):
    temp_str = ""
    temp_str += "& " * (len(z_dim) - 1)
    temp_str += data + " "
    temp_str += " ".join(["! " + d for d in z_dim if d!=data])
    must_one_z_list.append(temp_str)
must_one_t_list = []
for i, data in enumerate(t_dim):
    temp_str = ""
    temp_str += "& " * (len(t_dim) - 1)
    temp_str += data + " "
    temp_str += " ".join(["! " + d for d in t_dim if d!=data])
    must_one_t_list.append(temp_str)

#print must_one_x_list
#print must_one_y_list
#print must_one_z_list
#print must_one_t_list
#print

must_one_str = ""
must_one_str += "| " * (len(must_one_x_list) - 1) + " ".join(must_one_x_list) + "\n"
must_one_str += "| " * (len(must_one_y_list) - 1) + " ".join(must_one_y_list) + "\n"
must_one_str += "| " * (len(must_one_z_list) - 1) + " ".join(must_one_z_list) + "\n"
#must_one_str += "| " * (len(must_one_t_list) - 1) + " ".join(must_one_t_list) + "\n"

#print must_one_str
#print

obs_rate = 0.1
goal_rate = 0.05
obs_list = []
goal_list = []
with open("obs.txt", 'w') as the_file:
    with open("goal.txt", 'w') as the_file2:
        for i in xrange(min_obs,max_obs):
            for j in xrange(min_obs,max_obs):
                for k in xrange(min_obs,max_obs):
                    if i+j+k == 3: continue
                    if i+j+k == div_num*3: continue
                    if random() < obs_rate:
                        current_pos = "! & & xdim{} ydim{} zdim{}".format(i, j, k)
                        obs_list.append(current_pos)
                        the_file.write("{},{},{}\n".format(i,j,k))
                    elif random() < goal_rate:
                        goal_list.append("& & xdim{}' ydim{}' zdim{}'".format(i, j, k))
                        the_file2.write("{},{},{}\n".format(i,j,k))

obs_str = "\n".join(obs_list)
#print obs_str
#print

tran_list = []
fly_list = []
cost_list = []

for i in xrange(1,div_num+1):
    for j in xrange(1,div_num+1):
        for k in xrange(1,div_num+1):
            current_pos = "! & & xdim{} ydim{} zdim{}".format(i, j, k)

            if current_pos in obs_list: continue

            current_pos_str = "& & xdim{} ydim{} zdim{}".format(i, j, k)
            current_pos_str_full = "& " * (div_num * 3 - 1)
            for name in ["xdim", "ydim", "zdim"]:
                for x in xrange(1, div_num+1):
                    if (name == "xdim" and x == i) or (name == "ydim" and x == j) or (name == "zdim" and x == k):
                        current_pos_str_full += (name + str(x) + " ")
                    else:
                        current_pos_str_full += ("! " + name + str(x) + " ")

            # Fly
            x_v_list_ext = []
            y_v_list_ext = []
            z_v_list_ext = []
            if i in [min_fly, max_fly] and j in [min_fly, max_fly] and k in [min_fly, max_fly]:
                for ii, jj, kk in product([min_fly, max_fly], repeat = 3):
                    if ii > i: continue
                    if jj > j: continue
                    if kk > k: continue
                    x_v_list_ext.append(ii)
                    y_v_list_ext.append(jj)
                    z_v_list_ext.append(kk)

            next_str_list = []
            next_str_list_ext = []
            next_str_list_full = []
            next_str_list_ext_full = []

            x_v_list = [i, i-1, i+1, i, i, i, i]
            y_v_list = [j, j, j, j-1, j+1, j, j]
            z_v_list = [k, k, k, k, k, k-1, k+1]

            for data in izip(x_v_list_ext, y_v_list_ext, z_v_list_ext):
                x_v = "xdim"+str(data[0])
                y_v = "ydim"+str(data[1])
                z_v = "zdim"+str(data[2])

                if x_v in x_dim and y_v in y_dim and z_v in z_dim:
                    if "{},{},{}".format(x_v, y_v, z_v) in obs_list:
                        continue
                    else:
                        next_str_list_ext.append("& & {}' {}' {}'".format(x_v, y_v, z_v))

                        temp = "& " * (div_num * 3 - 1)
                        for name in ["xdim", "ydim", "zdim"]:
                            for x in xrange(1, div_num+1):
                                if (name == "xdim" and x == data[0]) or (name == "ydim" and x == data[1]) or (name == "zdim" and x == data[2]):
                                    temp += (name + str(x) + "' ")
                                else:
                                    temp += ("! " + name + str(x) + "' ")
                        next_str_list_ext_full.append(temp)

            for data in izip(x_v_list, y_v_list, z_v_list):
                x_v = "xdim"+str(data[0])
                y_v = "ydim"+str(data[1])
                z_v = "zdim"+str(data[2])
                if x_v in x_dim and y_v in y_dim and z_v in z_dim:
                    if "{},{},{}".format(x_v, y_v, z_v) in obs_list:
                        continue
                    else:
                        next_str_list.append("& & {}' {}' {}'".format(x_v, y_v, z_v))

                        temp = "& " * (div_num * 3 - 1)
                        for name in ["xdim", "ydim", "zdim"]:
                            for x in xrange(1, div_num+1):
                                if (name == "xdim" and x == data[0]) or (name == "ydim" and x == data[1]) or (name == "zdim" and x == data[2]):
                                    temp += (name + str(x) + "' ")
                                else:
                                    temp += ("! " + name + str(x) + "' ")
                        next_str_list_full.append(temp)

            full_list = next_str_list + next_str_list_ext
            next_str = "| " * (len(full_list) - 1) + " ".join(full_list)
            one_tran_str = "| ! {} {}".format(current_pos_str, next_str)
            tran_list.append(one_tran_str)

            for data in next_str_list_full:
                if data.replace("'", "") == current_pos_str_full:
                    cost_str = "{} & {} {}".format(0, current_pos_str_full, data)
                else:
                    cost_str = "{} & {} {}".format(15, current_pos_str_full, data)
                cost_list.append(cost_str)
            for data in next_str_list_ext_full:
                if data.replace("'", "") == current_pos_str_full:
                    cost_str = "{} & {} {}".format(0, current_pos_str_full, data)
                else:
                    cost_str = "{} & {} {}".format(30, current_pos_str_full, data)
                cost_list.append(cost_str)

            for data in next_str_list_ext:
                if data.replace("'", "") == current_pos_str:
                    pass
                else:
                    fly_list.append([current_pos_str, data])


tran_str = "\n".join(tran_list)
#print tran_str
#print

stay_var = "calculating"
stay_str_list = []
for data in fly_list:
    stay_str_list.append("| ! & {} {} ! {}".format(data[0], stay_var, data[1]))
stay_str = "\n".join(stay_str_list)

#print stay_str
goal_var = "switch"

sys_goal = ""
sys_goal += "| ! {} & & xdim{}' ydim{}' zdim{}'\n".format(goal_var, 1,1,1)
sys_goal += "| ! {} & & xdim{}' ydim{}' zdim{}'\n".format(goal_var, div_num, div_num, div_num)
for data in goal_list:
    sys_goal += "| {} {}\n".format(goal_var, data)

#print sys_goal

with open("spec.cost".format(div_num), 'w') as the_file:
    the_file.write("1 1 <\n")
    the_file.write("# The first line must always represent the cost factors for waiting and delay cost.\n")
    for data in cost_list:
        the_file.write("{}\n".format(data))

with open("spec.slugsin".format(div_num), 'w') as the_file:
    the_file.write("[INPUT]\n")
    the_file.write("{}\n".format(stay_var))
    the_file.write("{}\n".format(goal_var))
    the_file.write("\n")

    the_file.write("[OUTPUT]\n")
    the_file.write("{}\n".format("\n".join(x_dim)))
    the_file.write("{}\n".format("\n".join(y_dim)))
    the_file.write("{}\n".format("\n".join(z_dim)))
    the_file.write("\n")

    the_file.write("[ENV_TRANS]\n")
    the_file.write("1\n")
    the_file.write("\n")

    the_file.write("[ENV_LIVENESS]\n")
    the_file.write("! {}\n".format(stay_var))
    the_file.write("\n")

    the_file.write("[ENV_INIT]\n")
    the_file.write("1\n")
    the_file.write("\n")

    the_file.write("[SYS_TRANS]\n")
    the_file.write("# Cannot be in two regions at the same time\n")
    the_file.write("{}\n".format(mutual_str))

    the_file.write("# Must be in one region\n")
    the_file.write("{}\n".format(must_one_str))

    the_file.write("# Stay away from obstacles\n")
    the_file.write("{}\n".format(obs_str))
    the_file.write("\n")

    the_file.write("# How to move between regions\n")
    the_file.write("{}\n".format(tran_str))
    the_file.write("\n")

    the_file.write("# The env controls when the system arrives\n")
    the_file.write("{}\n".format(stay_str))
    the_file.write("\n")

    the_file.write("[SYS_LIVENESS]\n")
    the_file.write("{}\n".format(sys_goal))

    the_file.write("[SYS_INIT]\n")
    the_file.write("& & xdim{} ydim{} zdim{}\n".format(1,1,1))
    the_file.write("{}\n".format(mutual_str))
    the_file.write("{}\n".format(must_one_str))
    the_file.write("{}\n".format(obs_str))
    the_file.write("\n")
























































