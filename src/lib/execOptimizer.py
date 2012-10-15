#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import math, re, sys, random, os, subprocess, time, copy
import itertools
import random
import numpy as np
from regions import *
import fsa
from shortestPath import shortestpath



class Optimizer():

    def __init__(self):
        self.weightedAut = None
        self.proj = None
        self.FSA = None
        self.weight = {}
        self.goalStates = {}
        self.weightedGraph = None
        
        # For heuristic search
        self.maxIter = 2000
        self.maxSwap = 10
    def constructWeightedAutomaton(self, envState=None):
        """
        envState is a dict
        """

        print "Calculating Transition Weights"
        # copy the full FSA
        self.weightedAut = copy.deepcopy(self.FSA)
        if envState != None:

            # find state initially has no incoming transition
            stateHasIncoming = []
            for state in self.weightedAut.states:
                for traState in state.transitions:
                    if traState not in stateHasIncoming:
                        stateHasIncoming.append(traState)
            self.stateWithNoIncoming = [s for s in self.weightedAut.states if s not in stateHasIncoming]

            # remove the states with mismatch input
            stateToRemove = [s for s in self.weightedAut.states if s.inputs!=envState]
            map(self.weightedAut.states.remove,stateToRemove)

            # remove the transitions with mismatch input
            for state in self.weightedAut.states:
                stateToRemove = [s for s in state.transitions if s.inputs!=envState]
                map(state.transitions.remove,stateToRemove)

            needRemove = True
            while needRemove:
                # remove the states with no outgoing transitions
                stateToRemove = [s for s in self.weightedAut.states if len(s.transitions)==0]
                if len(stateToRemove) == 0:
                    needRemove = False
                else:
                    #print 'out',len(stateToRemove)
                    map(self.weightedAut.states.remove,stateToRemove)

                    for state in self.weightedAut.states:
                        stateToRemove = [s for s in state.transitions if s not in self.weightedAut.states]
                        map(state.transitions.remove,stateToRemove)

                
            needRemove = True
            while needRemove:
                # remove the states with no incoming transitions
                stateHasIncoming = []
                for state in self.weightedAut.states:
                    for traState in state.transitions:
                        if traState not in stateHasIncoming:
                            stateHasIncoming.append(traState)

                stateToRemove = [s for s in self.weightedAut.states if ((s not in stateHasIncoming) and (s not in self.stateWithNoIncoming))]
                if len(stateToRemove) == 0:
                    needRemove = False
                else:
                    #print 'in',len(stateToRemove)
                    map(self.weightedAut.states.remove,stateToRemove)


        for state in self.weightedAut.states:
            self.weight[state] = {}
            for traState in state.transitions:
                self.weight[state][traState]=self.calcWeight(state,traState)

        self.weightedAut.writeDot('test.dot')
        
    def calcWeight(self,state1,state2):
        region1 = self.proj.rfi.regions[self.FSA.regionFromState(state1)]
        region2 = self.proj.rfi.regions[self.FSA.regionFromState(state2)]
        return self.proj.rfi.calcTransitionCost(region1,region2)

    def calcShortestPath(self,state1,state2):

        return shortestpath(self.weight,state1,state2,visited=[],distances={},predecessors={})

        """
        result = {}
        for state in self.weightedAut.states:
            result[state] = {}
            for traState in self.weightedAut.states:
                if (state is not traState) and (traState not in state.transitions):
                    result[state][traState]=shortestpath(self.weight,state,traState)
        print "DONE"
        
        for state in self.weightedAut.states:
            for traState in self.weightedAut.states:
                if (state is not traState) and (traState not in state.transitions):
                    print result[state][traState]
        raw_input()
        """
    def findGoalStates(self,envState=None):
        for state in self.weightedAut.states:
            for traState in state.transitions:
                if (traState.rank != state.rank) and state not in self.stateWithNoIncoming:
                    if state.rank not in self.goalStates.keys():
                        self.goalStates[state.rank]=[]
                    self.goalStates[state.rank].append(state)
                    break
                    
    def constructWeightedGraph(self):
        self.weightedGraph = {}
        for rank,goalStates in self.goalStates.iteritems():
            for state in goalStates:
                if state not in self.weightedGraph.keys():
                    self.weightedGraph[state]={}
        for state in self.weightedGraph.keys():
            for traState in self.weightedGraph.keys():
                if state != traState:
                    (self.weightedGraph[state][traState],path)=self.calcShortestPath(state,traState)
        
                    print "DONE"
        """
        for state in self.weightedGraph: 
            for traState in self.weightedGraph[state]:
                print self.weightedGraph[state][traState]
        raw_input()
        """
       
    def findOrder(self):
        initialSolution = [] 
        for rank,goalStates in self.goalStates.iteritems():
            initialSolution.append([rank,goalStates[0]])
    
        tabuResult =  self.TabuSearch(initialSolution)
        for item in tabuResult:
            print item[0],self.FSA.getAnnotatedRegionName(self.FSA.regionFromState(item[1]))

    def TabuSearch(self,initialSolution = None):
        bestSolution = []
        bestCost = float("inf")
        if initialSolution == None:
            print 'Please provide initial solution'
            return
        currentSolution = initialSolution

        numOfGoals = len(currentSolution)
        maxStateOfGoal = 0 # max number of states of any goal

        for states in self.goalStates.values():
            if len(states)>maxStateOfGoal:
                maxStateOfGoal = len(states)

        tabuListSwap = np.zeros([numOfGoals,numOfGoals])
        tabuListChange = np.zeros([1,numOfGoals])
        # value for tabu list
        swap_K = numOfGoals*(numOfGoals-1)/2-1
        change_K = numOfGoals-1
        
        AL = self.tabuCost([currentSolution]) # for aspriation criterion
        iterNum = 1
        while iterNum<self.maxIter:
            print iterNum
            print 'CurrentSolution'
            for item in currentSolution:
                print item[0],self.FSA.getAnnotatedRegionName(self.FSA.regionFromState(item[1]))
            print 'CurrentCost'
            print self.tabuCost([currentSolution])[0]
            print
            print

            (neighborList,pertMode,pertIndex) = self.tabuNeighbors(currentSolution)
            neighborCostList = self.tabuCost(neighborList)
        
            bestNeighborCost = np.min(neighborCostList)
            bestNeighborIndex = neighborCostList.index(bestNeighborCost) 

            if pertMode[bestNeighborIndex] == 'swap':
                if tabuListSwap[pertIndex[bestNeighborIndex][0],pertIndex[bestNeighborIndex][1]] < 1:
                    # This solution is not tabu
                    currentSolution = neighborList[bestNeighborIndex]
                    # update tabu list
                    tabuListSwap[pertIndex[bestNeighborIndex][0],pertIndex[bestNeighborIndex][1]] = swap_K
                    tabuListSwap[pertIndex[bestNeighborIndex][1],pertIndex[bestNeighborIndex][0]] = swap_K
                    # update best cost
                    if bestNeighborCost < bestCost:
                        bestCost = bestNeighborCost
                        bestSolution = currentSolution
                else:
                    # this solution is tabu
                    if bestNeighborCost < bestCost:
                        # Best solution aspiration criterion
                        currentSolution = neighborList[bestNeighborIndex]
                        # update tabu list
                        tabuListSwap[pertIndex[bestNeighborIndex][0],pertIndex[bestNeighborIndex][1]] = swap_K
                        tabuListSwap[pertIndex[bestNeighborIndex][1],pertIndex[bestNeighborIndex][0]] = swap_K
                        # update best cost
                        bestCost = bestNeighborCost
                        bestSolution = currentSolution
                    else:
                        # find next best neighbor not tabu
                        isTabu = True
                        while isTabu:
                            neighborList.pop(bestNeighborIndex)
                            pertMode.pop(bestNeighborIndex)
                            pertIndex.pop(bestNeighborIndex)
                            neighborCostList.pop(bestNeighborIndex)

                            bestNeighborCost = np.min(neighborCostList)
                            bestNeighborIndex = neighborCostList.index(bestNeighborCost) 

                            if pertMode[bestNeighborIndex] == 'swap':
                                if tabuListSwap[pertIndex[bestNeighborIndex][0],pertIndex[bestNeighborIndex][1]] < 1:
                                    isTabu = False
                                    # update tabu list
                                    tabuListSwap[pertIndex[bestNeighborIndex][0],pertIndex[bestNeighborIndex][1]] = swap_K
                                    tabuListSwap[pertIndex[bestNeighborIndex][1],pertIndex[bestNeighborIndex][0]] = swap_K
                            else:
                                if tabuListChange[0,pertIndex[bestNeighborIndex][0]] < 1:
                                    isTabu = False
                                    # update tabu list
                                    tabuListChange[0,pertIndex[bestNeighborIndex][0]] = change_K
                            currentSolution = neighborList[bestNeighborIndex]
                            # update best cost
                            if bestNeighborCost < bestCost:
                                bestCost = bestNeighborCost
                                bestSolution = currentSolution
                        
            else:
                if tabuListChange[0,pertIndex[bestNeighborIndex][0]] < 1:
                    # This solution is not tabu
                    currentSolution = neighborList[bestNeighborIndex]
                    # update tabu list
                    tabuListChange[0,pertIndex[bestNeighborIndex][0]] = change_K
                    # update best cost
                    if bestNeighborCost < bestCost:
                        bestCost = bestNeighborCost
                        bestSolution = currentSolution
                else:
                    # this solution is tabu
                    if bestNeighborCost < bestCost:
                        # Best solution aspiration criterion
                        currentSolution = neighborList[bestNeighborIndex]
                        # update tabu list
                        tabuListChange[0,pertIndex[bestNeighborIndex][0]] = change_K
                        # update best cost
                        bestCost = bestNeighborCost
                        bestSolution = currentSolution
                    else:
                        # find next best neighbor not tabu
                        isTabu = True
                        while isTabu:
                            neighborList.pop(bestNeighborIndex)
                            pertMode.pop(bestNeighborIndex)
                            pertIndex.pop(bestNeighborIndex)
                            neighborCostList.pop(bestNeighborIndex)


                            bestNeighborCost = np.min(neighborCostList)
                            bestNeighborIndex = neighborCostList.index(bestNeighborCost) 

                            if pertMode[bestNeighborIndex] == 'swap':
                                if tabuListSwap[pertIndex[bestNeighborIndex][0],pertIndex[bestNeighborIndex][1]] < 1:
                                    isTabu = False
                                    # update tabu list
                                    tabuListSwap[pertIndex[bestNeighborIndex][0],pertIndex[bestNeighborIndex][1]] = swap_K
                                    tabuListSwap[pertIndex[bestNeighborIndex][1],pertIndex[bestNeighborIndex][0]] = swap_K
                            else:
                                if tabuListChange[0,pertIndex[bestNeighborIndex][0]] < 1:
                                    isTabu = False
                                    # update tabu list
                                    tabuListChange[0,pertIndex[bestNeighborIndex][0]] = change_K
                            currentSolution = neighborList[bestNeighborIndex]
                            # update best cost
                            if bestNeighborCost < bestCost:
                                bestCost = bestNeighborCost
                                bestSolution = currentSolution
            iterNum = iterNum + 1
            # update tabu list
            tabuListChange -= 1
            tabuListChange[tabuListChange<0]=0
            tabuListSwap -= 1
            tabuListSwap[tabuListSwap<0]=0

        return bestSolution

    def tabuCost(self,solutionList):
        costList = [[] for x in range(len(solutionList))]

        for i,solution in enumerate(solutionList):
            cost = 0
            transPair = self.pairwise(solution)
            for tran in transPair:
                cost += self.weightedGraph[tran[0][1]][tran[1][1]]

            cost += self.weightedGraph[solution[-1][1]][solution[1][1]]
            costList[i] = cost

        return costList
        
    def pairwise(self,iterable):
        a, b = itertools.tee(iterable)
        next(b, None)
        return itertools.izip(a, b)

    def tabuNeighbors(self,solution):
        
        neighborList = []
        pertMode = []
        pertIndex = []
        
        numOfGoals = len(solution)

        # neighbor by swap
        swapListIndex = [x for x in itertools.combinations(range(numOfGoals),2)]
        
        numOfSwap = np.min([self.maxSwap, len(swapListIndex)])
        swapIndex = [swapListIndex[x] for x in random.sample(range(len(swapListIndex)),numOfSwap)]
        
        for index in swapIndex:
            newSolution = [x for x in solution]
            newSolution[index[0]]=solution[index[1]]
            newSolution[index[1]]=solution[index[0]]

            neighborList.append(newSolution)
            pertMode.append('swap')
            pertIndex.append(index)

        # neighbor by change state
        for i,item in enumerate(solution):
            if len(self.goalStates[item[0]])>1:
                newSolution = [x for x in solution]
                
                candidates = range(len(self.goalStates[item[0]]))
                candidates.remove(self.goalStates[item[0]].index(item[1]))
                newSolution[i] = [item[0], self.goalStates[item[0]][[x for x in random.sample(candidates,1)][0]]]

                neighborList.append(newSolution)
                pertMode.append('change')
                pertIndex.append([i,i])
            

        return (neighborList,pertMode,pertIndex)









