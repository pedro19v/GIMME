from email.errors import NonPrintableDefect
import numpy
from GIMMECore.Edge import Edge
from GIMMECore.Node import Node
from GIMMECore.IntegerPartition import IntegerPartition


class IntegerPartitionGraph(object):
    def __init__(self, subspaces, numPlayers, largestIntegerBeingSplitInThisGraph):
        self.largestIntegerBeingSplitInThisGraph = largestIntegerBeingSplitInThisGraph

        self.nodes = [[] for _ in range(numPlayers)]
        for level in range(numPlayers):
            self.nodes[level] = numpy.empty(len(subspaces[level]), dtype=Node)
            for i in range(len(subspaces[level])):
                self.nodes[level][i] = Node(subspaces[level][i])

        for level in range(numPlayers - 1):
            for i in range(len(self.nodes[level])):

                listOfDirectlyConnectedPartitions = self.nodes[level][i].integerPartition.getListOfDirectedlyConnectedIntegerPartitions(largestIntegerBeingSplitInThisGraph, 0)
                if listOfDirectlyConnectedPartitions is None:
                    self.nodes[level][i].edgesFromThisNode = None
                
                else:
                    self.nodes[level][i].edgesFromThisNode = numpy.empty(len(listOfDirectlyConnectedPartitions), dtype=Edge)
                    index = 0
                    for j in range(len(self.nodes[level+1])):
                        integersThatResultedFromTheSplit = self.getIntegersThatResultedFromTheSplit(listOfDirectlyConnectedPartitions, self.nodes[level+1][j])
                        if integersThatResultedFromTheSplit != None:
                            sortedParts1 = self.nodes[level][i].integerPartition.partsSortedAscendingly
                            sortedParts2 = self.nodes[level+1][j].integerPartition.partsSortedAscendingly
                            partThatWasSplit = -1
                            for k in range(len(sortedParts1)-1, -1, -1):
                                if sortedParts1[k] != sortedParts2[k+1]:
                                    partThatWasSplit = sortedParts1[k]
                                    break

                            self.nodes[level][i].edgesFromThisNode[index]= Edge(self.nodes[level+1][j], partThatWasSplit, integersThatResultedFromTheSplit)
                            index += 1
                            if index == len(self.nodes[level][i].edgesFromThisNode):
                                break

    

    def getIntegersThatResultedFromTheSplit(self, listOfDirectlyConnectedIntegerPartitions, nodeOnHighLevel):
        multiplicity1 = nodeOnHighLevel.integerPartition.sortedMultiplicity
        underlyingSet1 = nodeOnHighLevel.integerPartition.sortedUnderlyingSetInBitFormat

        for i in range(len(listOfDirectlyConnectedIntegerPartitions)):
            multiplicity2 = listOfDirectlyConnectedIntegerPartitions[i].sortedMultiplicity
            underlyingSet2 = listOfDirectlyConnectedIntegerPartitions[i].sortedUnderlyingSetInBitFormat

            if underlyingSet1 != underlyingSet2:
                continue

            notEqual = False
            for j in range(len(multiplicity1)):
                if multiplicity1[j] != multiplicity2[j]:
                    notEqual = True
                    break

            if notEqual:
                continue

            return listOfDirectlyConnectedIntegerPartitions[i].tempIntegersThatResultedFromASplit
        
        return None

    def updateEdges(self, numPlayers, largestIntegerBeingSplitInThisGraph):
        prev_largestIntegerBeingSplitInThisGraph = self.largestIntegerBeingSplitInThisGraph
        if prev_largestIntegerBeingSplitInThisGraph >= largestIntegerBeingSplitInThisGraph:
            return

        for level in range(1, numPlayers - 1):
            for i in range(len(self.nodes[level])):
                listOfDirectlyConnectedIntegerPartitions = self.nodes[level][i].integerPartition.getListOfDirectedlyConnectedIntegerPartitions(largestIntegerBeingSplitInThisGraph, prev_largestIntegerBeingSplitInThisGraph)
                if listOfDirectlyConnectedIntegerPartitions != None:
                    index = 0
                    if self.nodes[level][i].edgesFromThisNode != None:
                        index = 0
                        self.nodes[level][i] = [[] for _ in range(len(listOfDirectlyConnectedIntegerPartitions))]

                    else:
                        index = len(self.nodes[level][i].edgesFromThisNode)
                        tempListOfEdges = [[] for _ in range(len(self.nodes[level][i].edgesFromThisNode) + len(listOfDirectlyConnectedIntegerPartitions))]
                        for j in range(len(self.nodes[level][i].edgesFromThisNode)):
                            tempListOfEdges[j] = self.nodes[level][i].edgesFromThisNode[j]
                        
                        self.nodes[level][i].edgesFromThisNode = tempListOfEdges

                    for j in range(len(self.nodes[level+1])):
                        integersThatResultedFromThisSplit = self.getIntegersThatResultedFromTheSplit(listOfDirectlyConnectedIntegerPartitions, self.nodes[level+1][j])
                        if integersThatResultedFromThisSplit != None:
                            sortedParts1 = self.nodes[level][i].integerPartition.partsSortedAscendingly
                            sortedParts2 = self.nodes[level+1][j].integerPartition.partsSortedAscendingly
                            partThatWasSplit = -1
                            for k in range(len(sortedParts1)-1, -1, -1):
                                if sortedParts1[k] != sortedParts2[k+1]:
                                    partThatWasSplit = sortedParts1[k]
                                    break

                            self.nodes[level][i].edgesFromThisNode[index] = Edge(self.nodes[level+1][j], partThatWasSplit, integersThatResultedFromThisSplit)
                            index += 1
                            if index == len(self.nodes[level][i].edgesFromThisNode):
                                break
                
        self.largestIntegerBeingSplitInThisGraph = largestIntegerBeingSplitInThisGraph


    def getReachableNodes(self, node):
        if node.edgesFromThisNode is None:
            return None
        
        numOfIntegersInNode = len(node.integerPartition.partsSortedAscendingly)

        node.tempIntegerRoots = None
        for level in range(numOfIntegersInNode, len(self.nodes)):
            for i in range(len(self.nodes[level])):
                self.nodes[level][i].tempFlag = False
                self.nodes[level][i].tempIntegerRoots = False

        for i in range(len(node.edgesFromThisNode)):
            node.edgesFromThisNode[i].node.tempFlag = True
            self.setIntegerRoots(node, node.edgesFromThisNode[i].node, node.edgesFromThisNode[i].twoPartsThatResultedFromTheSplit, node.edgesFromThisNode[i].partThatWasSplit)

        numOfReachableNodes = 0
        for level in range(numOfIntegersInNode, len(self.nodes) - 1):
            for i in range(len(self.nodes[level])):
                if self.nodes[level][i].tempFlag:
                    numOfReachableNodes += 1
                    if self.nodes[level][i].edgesFromThisNode != None: 
                        for j in range(len(self.nodes[level][i].edgesFromThisNode)):
                            if self.nodes[level][i].edgesFromThisNode[j].node.tempFlag == False:
                                self.nodes[level][i].edgesFromThisNode[j].node.tempFlag = True
                                self.setIntegerRoots(self.nodes[level][i], self.nodes[level][i].edgesFromThisNode[j].node, self.nodes[level][i].edgesFromThisNode[j].twoPartsThatResultedFromTheSplit, self.nodes[level][i].edgesFromThisNode[j].partThatWasSplit)

        index = 0
        listOfReachableNodes = numpy.empty(numOfReachableNodes, dtype=Node)
        for level in range(numOfIntegersInNode, len(self.nodes) - 1):
            for i in range(len(self.nodes[level])):
                if self.nodes[level][i].tempFlag:
                    listOfReachableNodes[index] = self.nodes[level][i]
                    index += 1

        return listOfReachableNodes

    def setIntegerRoots(self, lowerNode, upperNode, twoPartsThatResultedFromTheSplit, partThatWasSplit):
        upperIntegers = upperNode.integerPartition.partsSortedAscendingly
        lowerIntegers = lowerNode.integerPartition.partsSortedAscendingly

        upperNode.tempIntegerRoots = numpy.full(len(upperIntegers), -1, dtype=int)

        if lowerNode.tempIntegerRoots == None:
            for k in range(len(twoPartsThatResultedFromTheSplit)):
                for j in range(len(upperIntegers)):
                    if twoPartsThatResultedFromTheSplit[k] == upperIntegers[j] and upperNode.tempIntegerRoots[j] == -1:
                        upperNode.tempIntegerRoots[j] = partThatWasSplit
                        break

            for j in range(len(upperIntegers)):
                if upperNode.tempIntegerRoots[j] == -1:
                    upperNode.tempIntegerRoots[j] = upperIntegers[j]

        else:
            newRoot = -10
            indexOfNewRoot = -10

            for i in range(len(lowerIntegers)):
                if lowerIntegers[i] == partThatWasSplit:
                    indexOfNewRoot = i
                    newRoot = lowerNode.tempIntegerRoots[i]

            for i in range(len(lowerNode.tempIntegerRoots)):
                if i == indexOfNewRoot:
                    continue

                for j in range(len(upperIntegers)):
                    if upperIntegers[j] == lowerIntegers[i] and upperNode.tempIntegerRoots[j] == -1:
                        upperNode.tempIntegerRoots[j] = lowerNode.tempIntegerRoots[i]
                        break

            for j in range(len(upperIntegers)):
                if upperNode.tempIntegerRoots[j] == -1:
                    upperNode.tempIntegerRoots[j] = newRoot