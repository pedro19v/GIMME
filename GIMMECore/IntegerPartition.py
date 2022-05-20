import math
import numpy

from GIMMECore.ElementOfMultiset import ElementOfMultiset

class IntegerPartition(object):
    def __init__(self, parts):
        self.numPlayers = 0
        for i in range(len(parts)):
            self.numPlayers += parts[i]
        
        self.partsSortedAscendingly = sorted(parts)
        self.sortedUnderlyingSet = self.getUnderlyingset(self.partsSortedAscendingly)
        self.sortedMultiplicity = [[] for _ in range(len(self.sortedUnderlyingSet))]

        indexInMultiplicity = 0
        self.sortedMultiplicity[indexInMultiplicity] = 1
        for i in range(1, len(self.partsSortedAscendingly)):
            if self.partsSortedAscendingly[i] == self.partsSortedAscendingly[i-1]:
                self.sortedMultiplicity[indexInMultiplicity] += 1
            else:
                indexInMultiplicity += 1
                self.sortedMultiplicity[indexInMultiplicity] = 1

        self.sortedUnderlyingSetInBitFormat = self.convertCoalitionFromByteToBitFormat(self.sortedUnderlyingSet, len(self.sortedUnderlyingSet))

        self.sortedMultiset = [[] for _ in range(len(self.sortedMultiplicity))]
        for i in range(len(self.sortedMultiset)):
            self.sortedMultiset = ElementOfMultiset(self.sortedUnderlyingSet[i], self.sortedMultiplicity[i])

    def getIntegerPartitions(n):
        integerPartiton = IntegerPartition.allocateMemoryForIntegerPartitions(n)

        indexOfNewPartition = numpy.zeros(n, dtype=int)

        x = numpy.ones(n+1, dtype=int)
        x[1] = n
        m = 1
        h = 1
        IntegerPartition.fillXInPartitions(x, integerPartiton, m, indexOfNewPartition)

        while(x[1] != 1):
            if(x[h] == 2):
                m = m + 1
                x[h] = 1
                h -= 1
            
            else:
                r = x[h] - 1
                t = m - h + 1
                x[h] = r
                while t >= r:
                    h += 1
                    x[h] = r
                    t -= r
                
                if t == 0:
                    m = h
                else:
                    m = h + 1
                    if t > 1:
                        h += 1
                        x[h] = t

            IntegerPartition.fillXInPartitions(x, integerPartiton, m, indexOfNewPartition)

        return integerPartiton

    def getListOfDirectedlyConnectedIntegerPartitions(self, largestIntegerBeingSplit, prev_largestIntegerBeingSplit):
        counter = self.getNumOfDirectedlyConnectedIntegerPartitions(largestIntegerBeingSplit, prev_largestIntegerBeingSplit)
        if counter == 0:
            return None
        
        listOfDirectlyConnectedIntegerPartitions = numpy.empty(counter, dtype=IntegerPartition)

        if self.sortedUnderlyingSet[0] == self.numPlayers:
            index = 0
            for i in range(1, math.floor(self.numPlayers/2) + 1):
                newSortedParts = [[] for _ in range(2)]
                newSortedParts[0] = i
                newSortedParts[1] = self.numPlayers-i
                listOfDirectlyConnectedIntegerPartitions[index] = IntegerPartition(newSortedParts)
                listOfDirectlyConnectedIntegerPartitions[index].tempIntegersThatResultedFromASplit = [i, self.numPlayers-i]
                index += 1

        else:
            index = 0
            for i in range(len(self.sortedUnderlyingSet)):
                curPart = self.sortedUnderlyingSet[i]
                if curPart > largestIntegerBeingSplit or curPart <= prev_largestIntegerBeingSplit:
                    continue

                for j in range(1, math.floor(curPart/2) + 1):
                    smallHalf = j
                    largeHalf = curPart-j
                    if largeHalf > self.numPlayers - smallHalf - largeHalf:
                        continue

                    newSortedParts = [[] for _ in range(len(self.partsSortedAscendingly) + 1)]
                    i1 = 0
                    i2 = 0
                    while self.partsSortedAscendingly[i1] < smallHalf:
                        newSortedParts[i2] = self.partsSortedAscendingly[i1]
                        i1 += 1
                        i2 += 1
                    
                    newSortedParts[i2] = smallHalf
                    i2 += 1
                    while self.partsSortedAscendingly[i1] < largeHalf:
                        newSortedParts[i2] = self.partsSortedAscendingly[i1]
                        i1 += 1
                        i2 += 1

                    newSortedParts[i2] = largeHalf
                    i2 += 1
                    curPartHasBeenSeen = False
                    while i1 < len(self.partsSortedAscendingly):
                        if self.partsSortedAscendingly[i1] == curPart and curPartHasBeenSeen == False:
                            curPartHasBeenSeen = True
                            i1 += 1
                        else:
                            newSortedParts[i2] = self.partsSortedAscendingly[i1]
                            i1 += 1
                            i2 += 1
                    
                    listOfDirectlyConnectedIntegerPartitions[index] = IntegerPartition(newSortedParts)
                    listOfDirectlyConnectedIntegerPartitions[index].tempIntegersThatResultedFromASplit = [smallHalf, largeHalf]
                    index += 1

        return listOfDirectlyConnectedIntegerPartitions


    def getNumOfDirectedlyConnectedIntegerPartitions(self, largestIntegerBeingSplit, prev_largestIntegerBeingSplit):
        if self.sortedUnderlyingSet[0] == self.numPlayers:
            return math.floor(self.numPlayers / 2)

        counter = 0
        for i in range(len(self.sortedUnderlyingSet)):
            if self.sortedUnderlyingSet[i] > largestIntegerBeingSplit or self.sortedUnderlyingSet[i] <= prev_largestIntegerBeingSplit:
                continue

            for j in range(1, math.floor(self.sortedUnderlyingSet[i]/2) + 1):
                smallHalf = j
                largeHalf = self.sortedUnderlyingSet[i] - j
                if largeHalf > self.numPlayers - smallHalf - largeHalf:
                    continue
                counter += 1

        return counter


    def allocateMemoryForIntegerPartitions(n):
        numOfIntegerPartitionInLevel = numpy.empty(n, dtype=int)
        for level in range(1, n + 1):
            numOfIntegerPartitionInLevel[level-1] = IntegerPartition.getNumOfIntegerPartitionsInLevel(n, level)

        integerPartitions = [[] for _ in range(n)]
        for level in range(1, n+1):
            integerPartitions[level-1] = [[] for _ in range(numOfIntegerPartitionInLevel[level-1])]
            for i in range(numOfIntegerPartitionInLevel[level-1]):
                integerPartitions[level-1][i] = numpy.empty(level, dtype=int)

        return integerPartitions

    def fillXInPartitions(x, integerPartitions, m, indexOfNewPartition):
        for i in range(1, m+1):
            integerPartitions[m-1][indexOfNewPartition[m-1]][i-1] = x[i]
        indexOfNewPartition[m-1] += 1

    def getNumOfIntegerPartitions(n):
        numOfIntegerPartitions = 0
        for level in range(1, n+1):
            numOfIntegerPartitions += IntegerPartition.getNumOfIntegerPartitionsInLevel(n, level)

        return numOfIntegerPartitions

    def getNumOfIntegerPartitionsInLevel(n, level):
        return IntegerPartition.getNumOfIntegerPartitionsInLevel_additionalParameter(n, level, n-level+1)

    def getNumOfIntegerPartitionsInLevel_additionalParameter(n, level, M):
        if level == 1 or level == n:
            return 1
        
        sum = 0
        for M1 in range(math.ceil(n/level), min(n-level+1, M) + 1):
            sum += IntegerPartition.getNumOfIntegerPartitionsInLevel_additionalParameter(n-M1, level-1, M1)
        
        return sum

    def getUnderlyingset(self, array):
        numOfUniqueElements = 0
        uniqueElements = numpy.zeros(len(array), dtype=int)

        for i in range(len(array)):
            elementWasSeenBefore = False
            for j in range(numOfUniqueElements):
                if uniqueElements[j] == array[i]:
                    elementWasSeenBefore = True
                    break

            if elementWasSeenBefore == False:
                uniqueElements[numOfUniqueElements] = array[i]
                numOfUniqueElements += 1

        underlyingSet = [[] for _ in range(numOfUniqueElements)]
        for i in range(numOfUniqueElements):
            underlyingSet[i] = uniqueElements[i]

        return underlyingSet

    def convertCoalitionFromByteToBitFormat(self, coalitionInByteFormat, coalitionSize):
        coalitionInBitFormat = 0
        
        for i in range(coalitionSize):
            coalitionInBitFormat += 1 << (coalitionInByteFormat[i] - 1)

        return coalitionInBitFormat

    
    def contains(self, multiset):
        if len(self.sortedMultiset < len(multiset)):
            return False

        for i in range(len(multiset)):
            found = False
            for j in range(len(self.sortedMultiset)):
                if self.sortedMultiset[j].element == multiset[i].element:
                    if self.sortedMultiset[j].repetition < multiset[i].repetition:
                        return False
                    found = True
                    break

            if found == False:
                return False

        return True