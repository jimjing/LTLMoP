import re
import numpy
import sys
import regions

def loadRegionFile(path):
    rfi = regions.RegionFileInterface()
    rfi.readFile(path)
    return rfi

def calcCostFromRegions(rfi):
    cost_map = []
    for r_id_1, data in enumerate(rfi.transitions):
        r1 = rfi.regions[r_id_1]
        if r1.name == "boundary":
            continue
        for r_id_2, faces in enumerate(data):
            r2 = rfi.regions[r_id_2]
            if r2.name == "boundary":
                continue
            if faces:
                cost = costFromTransition(r1, r2)
                saftyLTL = safetyLTLFromRegion(rfi, r1, r2)
                cost_map.append([round(cost,3), saftyLTL])
    return cost_map

def costFromTransition(r1, r2):
    return numpy.linalg.norm(r1.getCenter()-r2.getCenter())

def writeCostFile(costs, path):
    with open(path, "w") as f:
        f.write("1 0 <\n")
        f.write("# The first line must always represent the cost factors for waiting and delay cost.\n\n")
        f.write("# Some cost assignments.\n")

        for cost in costs:
            f.write("{0} {1}\n".format(cost[0], cost[1]))

def safetyLTLFromRegion(rfi, r_from, r_to):
    text_list = []
    for r in rfi.regions:
        if r.name == "boundary": continue
        if r.isObstacle:
            continue
        if r == r_from:
            text_list.append(r.name)
            text_list.append("! " + r.name + "'")
        elif r == r_to:
            text_list.append("! " + r.name)
            text_list.append(r.name + "'")
        else:
            text_list.append("! " + r.name)
            text_list.append("! " + r.name + "'")

    return "& " * (len(text_list) - 1) + " ".join(text_list)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: python region2cost.py regionfile costfile"
    rfi = loadRegionFile(sys.argv[1])
    cost = calcCostFromRegions(rfi)
    writeCostFile(cost, sys.argv[2])
