import re
import numpy
import sys
import regions

roi = [4,5]
roi = ["r{}".format(x) for x in roi]

def loadRegionFile(path):
    rfi = regions.RegionFileInterface()
    rfi.readFile(path)
    return rfi

def calcCostFromRegions(rfi):
    # Do same region cost first
    for r in rfi.regions:
        region2Tikz(r)
    return ""

def region2Tikz(r):
    if r.name == "building":
        color = "blue"
    elif r.name == "r1":
        color = "black"
    elif r.name in ["station1", "station2"]:
        color = "green"
    else:
        color = "{rgb:black,1;white,20}"
    coords = ["({:.3f},{:.3f})".format(pt.x/130, -pt.y/130) for pt in r.getPoints()]
    output = "\draw [thick, fill={}] plot coordinates {{ {} }} --cycle;".format(color, " ".join(coords))
    print r.name, (r.getCenter().x/130, r.getCenter().y/130)
    return output


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: python region2cost.py regionfile costfile"
    rfi = loadRegionFile(sys.argv[1])
    cost = calcCostFromRegions(rfi)
