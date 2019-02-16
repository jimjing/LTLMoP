import subprocess
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, PathPatch
import mpl_toolkits.mplot3d.art3d as art3d

mpl.rcParams['legend.fontsize'] = 10

import time

def toCoord(data):
    print data
    # remove rank
    data  = data[:-2]
    # remove the first two and last two
    data  = data[:-2]
    data  = data[2:]

    return [i+1 for i, x in enumerate(data) if x=="1"]

def plotCube(data, color):
    size = 0.6
    xx = data[0] - size/2
    yy = data[1] - size/2
    zz = data[2] - size/2

    side = Rectangle((yy, zz), size, size, facecolor=color)
    ax.add_patch(side)
    art3d.pathpatch_2d_to_3d(side, z=xx, zdir='x')

    side = Rectangle((yy, zz), size, size, facecolor=color)
    ax.add_patch(side)
    art3d.pathpatch_2d_to_3d(side, z=xx+size, zdir='x')

    side = Rectangle((xx, zz), size, size, facecolor=color)
    ax.add_patch(side)
    art3d.pathpatch_2d_to_3d(side, z=yy, zdir='y')

    side = Rectangle((xx, zz), size, size, facecolor=color)
    ax.add_patch(side)
    art3d.pathpatch_2d_to_3d(side, z=yy+size, zdir='y')

    side = Rectangle((xx, yy), size, size, facecolor=color)
    ax.add_patch(side)
    art3d.pathpatch_2d_to_3d(side, z=zz, zdir='z')

    side = Rectangle((xx, yy), size, size, facecolor=color)
    ax.add_patch(side)
    art3d.pathpatch_2d_to_3d(side, z=zz+size, zdir='z')

t = time.time()
div_num = 5

slugs_cmd = ["./etc/slugs/src/slugs", "--sysInitRoboticsSemantics", "--twoDimensionalCost", "--interactiveStrategy", "/home/jim/Projects/LTLMoP/src/spec.slugsin".format(div_num), "/home/jim/Projects/LTLMoP/src/spec.cost".format(div_num)]

_slugs_process = subprocess.Popen(slugs_cmd, bufsize=1048000, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

_slugs_process.stdin.write("XGETINIT\n")
_slugs_process.stdin.flush()
_slugs_process.stdout.readline()
x_list = []
y_list = []
z_list = []

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_xlim3d(0, div_num+1)
ax.set_ylim3d(0, div_num+1)
ax.set_zlim3d(0, div_num+1)

env = "11"
with open("path.txt", 'w') as the_file:
    coord = toCoord(_slugs_process.stdout.readline().strip())
    x_list.append(coord[0])
    y_list.append(coord[1]-div_num)
    z_list.append(coord[2]-div_num*2)
    the_file.write("{},{},{}\n".format(coord[0], coord[1]-div_num, coord[2]-div_num*2))
    for i in xrange(50):
        if i > 20:
            env = "11"
        _slugs_process.stdin.write("XMAKETRANS\n" + env)
        _slugs_process.stdin.flush()
        _slugs_process.stdout.readline()  # Skip the prompt
        coord = toCoord(_slugs_process.stdout.readline().strip())
        x_list.append(coord[0])
        y_list.append(coord[1]-div_num)
        z_list.append(coord[2]-div_num*2)
        the_file.write("{},{},{}\n".format(coord[0], coord[1]-div_num, coord[2]-div_num*2))

        x1 = x_list[-2]
        x2 = x_list[-1]
        y1 = y_list[-2]
        y2 = y_list[-1]
        z1 = z_list[-2]
        z2 = z_list[-1]
        if abs(x1-x2) > 1 or abs(y1-y2)>1 or abs(z1-z2)>1:
            #ax.plot([x1, x2], [y1, y2], [z1, z2], 'y--', linewidth=2)
            ax.quiver([x1], [y1], [z1], [x2-x1], [y2-y1], [z2-z1], arrow_length_ratio=0.1, color='y')
        else:
            #ax.plot([x1, x2], [y1, y2], [z1, z2], 'g-', linewidth=2)
            ax.quiver([x1], [y1], [z1], [x2-x1], [y2-y1], [z2-z1], arrow_length_ratio=0.3, color='g')

print time.time() - t
# plot
obs_list = []
goal_list = []
with open("obs.txt", 'r') as the_file:
    for line in the_file.readlines():
        obs_list.append(map(int, line.strip('\n').split(',')))
        plotCube(obs_list[-1], 'r')
with open("goal.txt", 'r') as the_file:
    for line in the_file.readlines():
        goal_list.append(map(int, line.strip('\n').split(',')))
        #plotCube(goal_list[-1], 'g')

#ax.plot(x_list, y_list, z_list, label='parametric curve')
ax.scatter([x[0] for x in goal_list], [x[1] for x in goal_list], [x[2] for x in goal_list], s=80, c='k', marker='o')
ax.legend()

ax.view_init(37, -152)
plt.show()
