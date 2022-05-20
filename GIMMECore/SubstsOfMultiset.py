
from xml.etree.ElementTree import ElementTree
from numpy import size
import numpy

from GIMMECore.ElementOfMultiset import ElementOfMultiset


class SubsetsOfMultiset(object):
    def __init__(self, multiset, sizeOfSubsets, keepTrackOfNumOfInstancesOutsideSubset):
        self.multiset = multiset
        self.sizeOfSubsets = sizeOfSubsets
        self.keepTrackOfNumOfInstancesOutsideSubset = keepTrackOfNumOfInstancesOutsideSubset
        self.resetParameters()
        
    
    def resetParameters(self):
        self.currentSubsetIsFirstSubset = True
        self.multisetWithIncrementalElements = numpy.empty(len(self.multiset))

        for i in range(len(self.multiset)):
            self.multisetWithIncrementalElements[i] = ElementOfMultiset(i+1, self.multiset[i].repetition)

        self.setLastSubset()
        self.currentSubset = numpy.empty(len(self.multiset), dtype=ElementOfMultiset)

        self.totalNumOfElementsInMultiset = 0
        for i in range(len(self.multiset)):
            self.totalNumOfElementsInMultiset += self.multiset[i].repetition

    def getNextSubset(self):
        if self.currentSubsetIsFirstSubset:
            self.setCurrentSubsetToFirstSubset()
            self.currentSubsetIsFirstSubset = False
            return self.prepareResult()

        else:
            totalNumberOfElementsSeenSoFar = 0
            indexInLastSubset = len(self.lastSubset) - 1
            for indexInCurrentSubset in range(self.numOfUniqueElementsInCurrentSubset-1, - 1, -1):

                if self.currentSubset[indexInCurrentSubset].element != self.lastSubset[indexInLastSubset].element:

                    if self.currentSubset[indexInCurrentSubset].repetition > 1:

                        self.currentSubset[indexInCurrentSubset].repetition -= 1
                        self.currentSubset[indexInCurrentSubset + 1].element = self.currentSubset[indexInCurrentSubset].element + 1
                        self.currentSubset[indexInCurrentSubset + 1].repetition = 1
                        self.numOfUniqueElementsInCurrentSubset += 1

                        self.fillRemainingAgents(totalNumberOfElementsSeenSoFar, indexInCurrentSubset + 1)

                    else:
                        self.currentSubset[indexInCurrentSubset].element += 1
                        self.fillRemainingAgents(totalNumberOfElementsSeenSoFar, indexInCurrentSubset)

                    return self.prepareResult()

                else:
                    if self.currentSubset[indexInCurrentSubset].repetition < self.lastSubset[indexInLastSubset].repetition:
                        totalNumberOfElementsSeenSoFar += self.currentSubset[indexInCurrentSubset].repetition
                        self.numOfUniqueElementsInCurrentSubset -= 1
                        indexInCurrentSubset -= 1

                        if self.currentSubset[indexInCurrentSubset].repetition > 1:
                            self.currentSubset[indexInCurrentSubset].repetition -= 1
                            self.currentSubset[indexInCurrentSubset + 1].element = self.currentSubset[indexInCurrentSubset].element + 1
                            self.currentSubset[indexInCurrentSubset + 1].repetition = 1
                            self.numOfUniqueElementsInCurrentSubset += 1

                            self.fillRemainingAgents(totalNumberOfElementsSeenSoFar, indexInCurrentSubset + 1)

                        else:
                            self.currentSubset[indexInCurrentSubset].element += 1
                            self.fillRemainingAgents(totalNumberOfElementsSeenSoFar, indexInCurrentSubset)

                        return self.prepareResult()

                    else:
                        totalNumberOfElementsSeenSoFar += self.currentSubset[indexInCurrentSubset].repetition
                        indexInLastSubset -= 1
                        self.numOfUniqueElementsInCurrentSubset -= 1

        return None


    def setCurrentSubsetToFirstSubset(self):
        self.currentSubset = numpy.full(ElementOfMultiset(0,0), len(self.multisetWithIncrementalElements))

        totalNumOfAgentsToBeAdded = self.sizeOfSubsets
        i = 0
        for j in range(len(self.multisetWithIncrementalElements)):
            if totalNumOfAgentsToBeAdded <= self.multisetWithIncrementalElements[j].repetition:
                self.currentSubset[i] = ElementOfMultiset(self.multisetWithIncrementalElements[j].element, totalNumOfAgentsToBeAdded)
                break

            else:
                self.currentSubset[i] = ElementOfMultiset(self.multisetWithIncrementalElements[j].element, self.multisetWithIncrementalElements[j].repetition)
                totalNumOfAgentsToBeAdded -= self.multisetWithIncrementalElements[j].repetition
                i += 1
                if self.keepTrackOfNumOfInstancesOutsideSubset:
                    self.numOfInstancesOutsideSubset[i] = 0

        self.numOfUniqueElementsInCurrentSubset = i+1


    def setLastSubset(self):
        temp = numpy.full(len(self.multisetWithIncrementalElements), ElementOfMultiset(0,0), dtype=ElementOfMultiset)

        totalNumOfAgentsToBeAdded = self.sizeOfSubsets
        i = len(temp) - 1
        for j in range(len(self.multisetWithIncrementalElements)-1, -1, -1):
            if totalNumOfAgentsToBeAdded <= self.multisetWithIncrementalElements[j].repetition:
                temp[i] = ElementOfMultiset(self.multisetWithIncrementalElements[j].element, totalNumOfAgentsToBeAdded)
                break

            else:
                temp[i] = ElementOfMultiset(self.multisetWithIncrementalElements[j].element, self.multisetWithIncrementalElements[j].repetition) 
                totalNumOfAgentsToBeAdded -= self.multisetWithIncrementalElements[j].repetition
                i -= 1

        self.lastSubset = numpy.empty(len(self.multisetWithIncrementalElements) - i)
        for j in range(len(self.lastSubset) - 1, -1, -1):
            self.lastSubset[j] = temp[len(temp) - len(self.lastSubset) + j]


    def fillRemainingAgents(self, totalNumOfAgentsToBeAdded, indexAtWhichToStartFilling):
        if totalNumOfAgentsToBeAdded == 0:
            return

        firstUniqueAgentToBeAdded = self.currentSubset[indexAtWhichToStartFilling].element

        max = self.multisetWithIncrementalElements[firstUniqueAgentToBeAdded-1].repetition - self.currentSubset[indexAtWhichToStartFilling].repetition
        if max > 0:
            if totalNumOfAgentsToBeAdded <= max:
                self.currentSubset[indexAtWhichToStartFilling].repetition += totalNumOfAgentsToBeAdded
                return
            else:
                self.currentSubset[indexAtWhichToStartFilling].repetition += max
                totalNumOfAgentsToBeAdded -= max

        k = 1
        while True:
            self.numOfUniqueElementsInCurrentSubset += 1
            if totalNumOfAgentsToBeAdded <= self.multisetWithIncrementalElements[firstUniqueAgentToBeAdded + k - 1].repetition:
                self.currentSubset[k + indexAtWhichToStartFilling] = ElementOfMultiset(firstUniqueAgentToBeAdded + k, totalNumOfAgentsToBeAdded)
                break
                
            else:
                self.currentSubset[k + indexAtWhichToStartFilling] = ElementOfMultiset(firstUniqueAgentToBeAdded + k, self.multisetWithIncrementalElements[firstUniqueAgentToBeAdded + k - 1].repetition)
                totalNumOfAgentsToBeAdded -= self.multisetWithIncrementalElements[firstUniqueAgentToBeAdded + k - 1].repetition
                k += 1


    def prepareResult(self):
        subsetWithOriginalElements = numpy.empty(self.numOfUniqueElementsInCurrentSubset)

        for i in range(self.numOfUniqueElementsInCurrentSubset):
            originalElement = self.multiset[self.currentSubset[i].element - 1]
            subsetWithOriginalElements[i] = ElementOfMultiset(originalElement.element, self.currentSubset[i].repetition)

        return subsetWithOriginalElements

