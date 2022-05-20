

import math

import numpy


class Subspace(object):
    def __init__(self, integers, avgValueForEachSize = None, maxValueForEachSize = None, numPlayers = None):
        self.integers = integers
        self.integersSortedAscendingly = sorted(integers)
        self.sizeOfSubspace = self.computeNumOfCSInSubspace(self.integers)
        sizeOfIntegers = len(self.integers)

        self.priority = 0.0
        self.isReachableFromBottomNode = False
        self.relevantNodes = []

        if avgValueForEachSize is not None:
            self.enabled = True

            self.totalNumOfExpansionsInSubspace = self.computeTotalNumOfExpansionsInSubspace(self.integers)

            if sizeOfIntegers == 2:
                size1 = self.integers[0]
                size2 = self.integers[1]
                numOfCombinationsOfSize1 = math.comb(numPlayers, size1)
                temp = 0
                if size1 != size2:
                    temp = numOfCombinationsOfSize1
                else:
                    temp = numOfCombinationsOfSize1/2

                self.numOfSearchedCoalitionsInThisSubspace = 2*temp
            
            else:
                if sizeOfIntegers == 1 or sizeOfIntegers == numPlayers:
                    self.numOfSearchedCoalitionsInThisSubspace = sizeOfIntegers
                else:
                    self.numOfSearchedCoalitionsInThisSubspace = 0

            # Calculating UB
            j = 0
            self.UB = 0
            for k in range(sizeOfIntegers):
                if k > 0 and self.integers[k] == self.integers[k-1]:
                    j += 1
                else:
                    j = 0
                self.UB += maxValueForEachSize[self.integers[k]-1][j]

            # Calculating Avg
            self.Avg = 0
            print(avgValueForEachSize)
            for k in range(sizeOfIntegers):
                self.Avg += avgValueForEachSize[self.integers[k] - 1]

            # Calculating LB
            self.LB = self.Avg
        
        else:
            self.enabled = False
            self.totalNumOfExpansionsInSubspace = -1
            self.numOfSearchedCoalitionsInThisSubspace = -1
            self.UB = 0
            self.Avg = 0
            self.LB = 0
            

    def search(self, odpip, odpHasFinished, acceptableValue, sumOfMax, numOfIntegersToSplit):
        if odpHasFinished:
            self.enabled = False
            return 1

        self.search_useBranchAndBound(odpip, acceptableValue, sumOfMax, numOfIntegersToSplit)

        if odpHasFinished == False:
            CS = odpip.getOptimalSplit(odpip.ipBestCSFound)
            odpip.updateIPSolution(CS, odpip.getCoalitionStructureInByteFormatValue(CS))

        self.enabled = False
        numOfSearchedSubspaces = 1

        if self.relevantNodes != None:
            for i in range(len(self.relevantNodes)):
                if self.relevantNodes[i].subspace.enabled:
                    self.relevantNodes[i].subspace.enabled = False
                    numOfSearchedSubspaces += 1

        return numOfSearchedSubspaces

    
    def search_useBranchAndBound(self, odpip, acceptableValue, sumOfMax, numOfIntegersToSplit):
        if len(self.integers) == 1 or len(self.integers) == odpip.numPlayers:
            self.searchFirstOrLastLevel(odpip, self.integers)
            return
        
        numOfIntegers = len(self.integers)
        ipNumOfSearchedCoalitions_beforeSearchingThisSubspace = odpip.ipNumOfExpansions
        numPlayers = odpip.numPlayers
        numOfIntsToSplit = numOfIntegersToSplit
        constraintsExist = True
        this_CS_is_useless = False
        valueOfCS = 0
        if odpip.feasibleCoalitions == None:
            constraintsExist = False

        bit                         =   self.initBit(numPlayers)
        lengthOfA                   =   self.initLengthOfA(numPlayers, self.integers)
        maxFirstMemberOfM           =   self.initMaxFirstMemberOfM(self.integers, lengthOfA, False)
        numOfCombinations           =   self.initNumOfCombinations(self.integers, lengthOfA, maxFirstMemberOfM)
        sumOfNumOfCombinations      =   self.initSumOfNumOfCombinations(numOfCombinations, self.integers, lengthOfA, maxFirstMemberOfM)
        numOfRemovedCombinations    =   self.initNumOfRemovedCombinations(self.integers, lengthOfA, maxFirstMemberOfM)
        increment                   =   self.initIncrement(self.integers, numOfCombinations, sumOfNumOfCombinations, maxFirstMemberOfM, False)
        indexToStartAt              =   self.initIndexToStartAt(numOfIntegers, numOfRemovedCombinations, sumOfNumOfCombinations)
        indexToStopAt               =   self.initIndexToStopAt(numOfIntegers, numOfRemovedCombinations)
        indexOfM                    =   self.initIndexOfM(1, self.integers, increment, maxFirstMemberOfM, numOfCombinations, numOfRemovedCombinations, sumOfNumOfCombinations)
        M                           =   self.initM(odpip, indexOfM, self.integers, lengthOfA, numPlayers)
        A                           =   self.initA(numPlayers, self.integers, M, lengthOfA)
        CS                          =   self.initCS(M, A, lengthOfA, bit, numOfIntegers)
        sumOfAgents                 =   self.initSumOfAgents(numOfIntegers, CS)
        sumOfValues                 =   self.initSumOfValues(numOfIntegers, CS, odpip)
        odpip.ipNumOfExpansions += len(self.integers) - 2
        s1 = 0

        def search_useBranchAndBoundSubLoop():
            s1 = numOfIntegers - 3
            while s1 >= 0:
                if indexOfM[s1] > indexToStopAt[s1]:
                    if s1 == 0:
                        if odpip.odpHasFinished:
                            self.numOfSearchedCoalitionsInThisSubspace = odpip.ipNumOfExpansions - ipNumOfSearchedCoalitions_beforeSearchingThisSubspace
                            return 0

                    for s2 in range(s1, numOfIntegers - 2):
                        firstTime = True
                        while True:
                            odpip.ipNumOfExpansions += 1
                            if firstTime and s2 > s1:
                                self.setMAndIndexOfM(M, indexOfM, lengthOfA, indexToStartAt, s2)
                                firstTime = False
                            
                            else:
                                odpip.getPreviousCombination(lengthOfA[s2], indexToStartAt, s2)
                                indexOfM[s2] -= 1

                            temp3 = 0
                            for j1 in range(self.integers[s2] - 1, -1, -1):
                                temp3 |= bit[A[s2][M[s2][j1]-1]]
                            
                            CS[s2] = temp3

                            this_CS_is_useless = False
                            if constraintsExist:
                                if CS[s2] not in odpip.feasibleCoalitions:
                                    this_CS_is_useless = True

                            if this_CS_is_useless != False:
                                newCoalition = CS[s2]
                                valueOfNewCoalition = 0.0
                                if s2 >= numOfIntegers - numOfIntsToSplit:
                                    valueOfNewCoalition = odpip.f[CS[s2]]
                                else:
                                    valueOfNewCoalition = odpip.getCoalitionInBitFormatValue(CS[s2])

                                sumOfValues[s2 + 1] = sumOfValues[s2] + valueOfNewCoalition
                                sumOfValues[s2 + 1] = sumOfAgents[s2] + CS[s2]

                                upperBoundForRemainingAgents = sumOfMax[s2 + 2]
                                if sumOfValues[s2 + 1] + upperBoundForRemainingAgents - odpip.ipValueOfBestCSFound < - 0.0000000005 \
                                    or self.useLocalBranchAndBound(odpip, sumOfValues, sumOfAgents, s2, newCoalition, valueOfNewCoalition):
                                    this_CS_is_useless = True

                            if this_CS_is_useless == False:
                                break

                            if indexOfM[s2] <= indexToStopAt[s2]:
                                break
                        
                        if this_CS_is_useless:
                            s1 = s2-1
                            continue

                        self.update_A(A[s2 + 1], A[s2], lengthOfA[s2], M[s2], self.integers[s2])

                        s2 = numOfIntegers - 2
                        self.setMAndIndexOfM(M, indexOfM, lengthOfA, indexToStartAt, s2)

                        return 1

                s -= 1


        while True:
            if odpip.odpHasFinished:
                self.numOfSearchedCoalitionsInThisSubspace = odpip.ipNumOfExpansions - ipNumOfSearchedCoalitions_beforeSearchingThisSubspace
                return

            while True:
                self.setTheLastTwoCoalitionsInCS(CS, M[numOfIntegers-2], A, numOfIntegers, bit)

                this_CS_is_useless = False
                if constraintsExist and self.checkIfLasTwoCoalitionsSatisfyConstraints(CS, odpip.feasibleCoalitions) == False:
                    this_CS_is_useless = True

                if this_CS_is_useless == False:
                    if numOfIntsToSplit == 0:
                        valueOfCS = sumOfValues[numOfIntegers-2] + odpip.getCoalitionInByteFormatValue(CS[numOfIntegers - 2]) + odpip.getCoalitionInByteFormatValue(CS[numOfIntegers-1])
                    elif numOfIntsToSplit == 1:
                        valueOfCS = sumOfValues[numOfIntegers-2] + odpip.getCoalitionInByteFormatValue(CS[numOfIntegers - 2]) + odpip.f[CS[numOfIntegers-1]]
                    else:
                        valueOfCS = sumOfValues[numOfIntegers-2] + odpip.f[CS[numOfIntegers-2]] + odpip.f[CS[numOfIntegers-1]]

                    if odpip.ipValueOfBestCSFound < valueOfCS:
                        CSInByteFormat = odpip.convertSetOfCombinationsFromBitFormatWithSizes(CS, self.integers)
                        odpip.updateIPSolution(CSInByteFormat, valueOfCS)

                        if odpip.ipValueOfBestSolutionFound >= acceptableValue:
                            self.numOfSearchedCoalitionsInThisSubspace = odpip.ipNumOfExpansions - ipNumOfSearchedCoalitions_beforeSearchingThisSubspace
                            return

                indexOfM[numOfIntegers - 2] -= 1
                odpip.getPreviousCombination(lengthOfA[numOfIntegers-2], self.integers[numOfIntegers-2], M[numOfIntegers-2])

                if indexOfM[numOfIntegers - 2] < indexToStopAt[numOfIntegers - 2]:
                    break
            
            result = search_useBranchAndBoundSubLoop()
            if result == 0:
                return
            
            elif result == 1:
                continue
            
            break

        self.numOfSearchedCoalitionsInThisSubspace = odpip.ipNumOfExpansions - ipNumOfSearchedCoalitions_beforeSearchingThisSubspace


    def searchFirstOrLastLevel(self, odpip, integers):
        numPlayers = odpip.numPlayers
        curCS = []

        if len(integers) == 1:
            curCS[0] = [i + 1 for i in range(numPlayers)]

        else:
            curCS = [[i+1] for i in range(numPlayers)]

        valueOfCurCS = odpip.getCoalitionStructureInByteFormatValue(curCS)

        odpip.updateIPSolution(curCS, valueOfCurCS)


    def computeNumOfCSInSubspace(self, integers):
        numPlayers = 0
        for i in range(len(integers)):
            numPlayers += integers[i]

        if len(integers) == 1 or len(integers) == numPlayers:
            return 1

        lengthOfA = self.initLengthOfA(numPlayers, integers)
        maxFirstMemberOfM = self.initMaxFirstMemberOfM(integers, lengthOfA, False)
        numOfCombinations = self.initNumOfCombinations(integers, lengthOfA, maxFirstMemberOfM)
        sumOfNumOfCombinations = self.initSumOfNumOfCombinations(numOfCombinations, integers, lengthOfA, maxFirstMemberOfM)
        numOfRemovedCombinations = self.initNumOfRemovedCombinations(integers, lengthOfA, maxFirstMemberOfM)
        increment = self.initIncrement(integers, numOfCombinations, sumOfNumOfCombinations, maxFirstMemberOfM, False)

        sizeOfSubspace = 0
        if numOfRemovedCombinations[0] == 0:
            sizeOfSubspace = increment[0][0] * sumOfNumOfCombinations[0]

        else:
            for i in range(maxFirstMemberOfM[0]):
                sizeOfSubspace += increment[0][i] * numOfCombinations[0][i]

        return sizeOfSubspace

    def computeTotalNumOfExpansionsInSubspace(self, integers):
        numPlayers = 0
        lenIntegers = len(integers)
        for i in range(lenIntegers):
            numPlayers += integers[i]

        sortedIntegers = sorted(integers)
        alpha = [[] for _ in range(lenIntegers)]
        gamma = [[] for _ in range(lenIntegers)]

        for j in range(lenIntegers):
            maxIndex = 0
            for k in range(lenIntegers):
                if sortedIntegers[k] == sortedIntegers[j]:
                    maxIndex = k
            
            alpha[j] = numPlayers + 1
            for k in range(maxIndex):
                alpha[j] -= sortedIntegers[k]
            
            gamma[j] = [[] for _ in range(alpha[j])]
            for beta in range(alpha[j]):
                sumOfPreviousIntegers = 0
                for k in range(j):
                    sumOfPreviousIntegers += sortedIntegers[k]

                if j == 0:
                    gamma[j][beta] = math.comb(numPlayers-sumOfPreviousIntegers-beta+1, sortedIntegers[j] - 1)
                else:
                    omega = alpha[j-1] - 1
                    if sortedIntegers[j] == sortedIntegers[j-1]:
                        omega = beta

                    sum = 0
                    for k in range(omega+1):
                        sum += gamma[j-1][k]
                    
                    gamma[j][beta] = sum * math.comb(numPlayers-sumOfPreviousIntegers-beta+1, sortedIntegers[j] - 1)

        numOfExpansionsInSubspace = 0
        for j in range(len(sortedIntegers)):
            for beta in range(alpha[j]):
                numOfExpansionsInSubspace += gamma[j][beta]

        return numOfExpansionsInSubspace
                    
    
    def checkIfLasTwoCoalitionsSatisfyConstraints(CS, feasibleCoalitions):
        if CS[-1] not in feasibleCoalitions:
            return False
        if CS[-2] not in feasibleCoalitions:
            return False
        return True




    def initBit(self, numPlayers):
        bit = numpy.empty(numPlayers + 1, dtype=int)
        for i in range(numPlayers):
            bit[i+1] = 1 << i
        
        return bit

    def initIndexToStartAt(self, numOfIntegers, numOfRemovedCombinations, sumOfNumOfCombinations):
        indexToStartAt = numpy.empty(numOfIntegers, dtype=numpy.int64)

        for i in range(numOfIntegers):
            indexToStartAt[i] = sumOfNumOfCombinations[i] + numOfRemovedCombinations[i]

        return indexToStartAt

    def initIndexToStopAt(self, numOfIntegers, numOfRemovedCombinations):
        indexToStopAt = numpy.empty(numOfIntegers, dtype=numpy.int64)

        for i in range(numOfIntegers):
            indexToStopAt[i] = numOfRemovedCombinations[i] + 1

        return indexToStopAt

    def initLengthOfA(self, numPlayers, integers):
        lengthOfA = [[] for _ in range(len(integers))]

        lengthOfA[0] = numPlayers
        if len(integers) > 1:
            for s in range(1, len(integers)):
                lengthOfA[s] = int(lengthOfA[s-1] - integers[s-1])

        return lengthOfA

    def initMaxFirstMemberOfM(self, integers, lengthOfA, ipUsesLocalBranchAndBound):
        maxFirstMemberOfM = [[] for _ in range(len(integers))]
        i = len(integers) - 1

        if ipUsesLocalBranchAndBound and self.relevantNodes != None and len(integers) > 2:
            maxFirstMemberOfM[i] = int(lengthOfA[i] - integers[i] + 1)
            i -= 1

        while i >= 0:
            maxFirstMemberOfM[i] = int(lengthOfA[i] - integers[i] + 1)
            i -= 1
            while i >= 0 and integers[i] == integers[i+1]:
                maxFirstMemberOfM[i] = maxFirstMemberOfM[i+1]
                i -= 1

        return maxFirstMemberOfM

    def initNumOfCombinations(self, integers, lengthOfA, maxFirstMemberOfM):
        numOfCombinations = [[] for _ in range(len(integers))]
        for i in range(len(integers)):
            if lengthOfA[i] == integers[i]:
                numOfCombinations[i] = [1,]

            else:
                numOfCombinations[i] = [[] for _ in range(maxFirstMemberOfM[i])]
                for j in range(maxFirstMemberOfM[i]):
                    numOfCombinations[i][j] = math.comb(lengthOfA[i] - j+1, integers[i] - 1)

        return numOfCombinations

    def initSumOfNumOfCombinations(self, numOfCombinations, integers, lengthOfA, maxFirstMemberOfM):
        sumOfNumOfCombinations = [[] for _ in range(len(integers))]

        for i in range(len(integers)):
            if lengthOfA[i] == integers[i]:
                sumOfNumOfCombinations[i] = 1

            else:
                sumOfNumOfCombinations[i] = 0
                for j in range(maxFirstMemberOfM[i]):
                    sumOfNumOfCombinations[i] = sumOfNumOfCombinations[i] + numOfCombinations[i][j]

        return sumOfNumOfCombinations

    def initNumOfRemovedCombinations(self, integers, lengthOfA, maxFirstMemberOfM):
        numOfRemovedCombinations = [[] for _ in range(len(integers))]

        for i in range(len(integers)):
            if lengthOfA[i] == integers[i]:
                numOfRemovedCombinations[i] = 0

            else:
                numOfRemovedCombinations[i] = 0
                for j in range(maxFirstMemberOfM[i], lengthOfA[i] - integers[i] + 1):
                    numOfRemovedCombinations[i] = numOfRemovedCombinations[i] + math.comb(lengthOfA[i] - j+1, integers[i] - 1)

        return numOfRemovedCombinations

    def initIncrement(self, integers, numOfCombinations, sumOfNumOfCombinations, maxFirstMemberOfM, ipUsesLocalBranchAndBound):
        increment = [[] for _ in range(len(integers))]
        increment[-1] = [1,]

        s = len(integers) - 2
        while s >= 0:
            if integers[s] != integers[s+1] or (ipUsesLocalBranchAndBound and s == len(integers) - 2 and len(integers) > 2):
                increment[s] = [sumOfNumOfCombinations[s+1] * increment[s+1][0]]
                s -= 1

            else:
                increment[s] = [[] for _ in range(maxFirstMemberOfM[s])]
                for i in range(maxFirstMemberOfM[s]):
                    increment[s][i] = 0
                    for j in range(i, maxFirstMemberOfM[s]):
                        increment[s][i] += numOfCombinations[s+1][j] * increment[s+1][0]

                s -= 1

                while s >= 0 and integers[s] == integers[s+1]:
                    increment[s] = [[] for _ in range(maxFirstMemberOfM[s])]
                    for i in range(maxFirstMemberOfM[s]):
                        increment[s][i] = 0
                        for j in range(i, maxFirstMemberOfM[s]):
                            increment[s][i] += numOfCombinations[s+1][j] * increment[s+1][j]
                    
                    s -= 1

                if s >= 0:
                    increment[s] = [0,]
                    for j in range(maxFirstMemberOfM[s+1]):
                        increment[s][0] += numOfCombinations[s+1][j] * increment[s+1][j]
                    s -= 1

        return increment

    
    def initIndexOfM(self, index, integers, increment, maxFirstMemberOfM, numOfCombinations, numOfRemovedCombinations, sumOfNumOfCombinations):
        counter1 = 0
        counter2 = 1
        indexOfM = numpy.empty(len(integers), dtype=numpy.int64)

        indexOfM[-1] = 1

        minFirstMemberOfM = 0
        for i in range(len(integers) - 1):
            if sumOfNumOfCombinations[i] == 1:
                indexOfM[i] = 1
            
            else:
                if len(increment[i]) == 1:
                    counter1 = 0
                    counter2 = 1
                    if minFirstMemberOfM > 0:
                        for j in range(minFirstMemberOfM):
                            counter2 += numOfCombinations[i][j]

                    steps = math.ceil( index / increment[i][0]) - 1
                    counter1 += steps * increment[i][0]
                    counter2 += steps

                    indexOfM[i] = counter2
                    index -= counter1

                    if i >= len(integers) - 1 or integers[i] != integers[i+1]:
                        minFirstMemberOfM = 0

                else:
                    counter1 = 0
                    counter2 = 1
                    if minFirstMemberOfM > 0:
                        for j in range(minFirstMemberOfM):
                            counter2 += numOfCombinations[i][j]

                    for j in range(minFirstMemberOfM, maxFirstMemberOfM[i]):
                        if index <= counter1 + (numOfCombinations[i][j] * increment[i][j]):
                            steps = math.ceil(index-counter1 / increment[i][j]) - 1
                            counter1 += steps * increment[i][j]
                            counter2 += steps

                            indexOfM[i] = counter2
                            index -= counter1

                            if i < len(integers) - 1 and integers[i] == integers[i+1]:
                                minFirstMemberOfM = j
                            else:
                                minFirstMemberOfM = 0

                            break
                        else:
                            steps = numOfCombinations[i][j]
                            counter1 += steps * increment[i][j]
                            counter2 += steps

        for i in range(len(indexOfM)):
            indexOfM[i] = sumOfNumOfCombinations[i] + numOfRemovedCombinations[i] - indexOfM[i] + 1

        return indexOfM

    
    def initM(self, odpip, indexOfM, integers, lengthOfA, numPlayers):
        pascalMatrix = odpip.initPascalMatrix(numPlayers + 1, numPlayers + 1)

        M = [[] for _ in range(len(integers))]
        for s in range(len(integers)):
            M[s] = numpy.empty(integers[s], dtype=int)

        for i in range(len(integers)):
            j = 1
            index = indexOfM[i]
            s1 = integers[i]

            done = False
            while True:
                x = 1
                while(pascalMatrix[s1-1][x-1] < index):
                    x += 1

                M[i][j-1] = int(lengthOfA[i] - s1 + 1 - x + 1)
                if pascalMatrix[s1-1][x-1] == index:
                    for k in range(j, integers[i]):
                        M[i][k] = int(M[i][k-1]+1)
                    done = True
                
                else:
                    j = j+1
                    index = index-pascalMatrix[s1-1][x-2]
                    s1 = s1 - 1
                
                if done:
                    break
        
        breakpoint()
        print(pascalMatrix)
        return M

    
    def initA(self, numPlayers, integers, M, lengthOfA):
        A = [[] for _ in range(len(integers) - 1)]
        for s in range(len(integers)-1):
            A[s] = numpy.empty(lengthOfA[s])
            if s == 0:
                for j1 in range(numPlayers):
                    A[s][j1] = j1 + 1
            
            else:
                j1 = 0
                j2 = 0
                for j3 in range(lengthOfA[s-1]):
                    if j1 >= len(M[s-1]) or j3 + 1 != M[s-1][j1]:
                        A[s][j2] = A[s-1][j3]
                        j2 += 1
                    
                    else:
                        j1 += 1

        return A

    
    def initCS(self, M, A, lengthOfA, bit, numOfIntegers):
        CS = numpy.empty(len(self.integers))

        for s in range(len(self.integers) - 1):
            CS[s] = 0
            for j1 in range(len(M[s])):
                CS[s] |= bit[A[s][M[s][j1] - 1]]

        self.setTheLastTwoCoalitionsInCS(CS, M[numOfIntegers - 2], A, numOfIntegers, bit)
        return CS

    def initSumOfAgents(self, numOfIntegers, CS):
        sumOfAgents = numpy.empty(numOfIntegers + 1)
        sumOfAgents[0] = 0
        for i in range(1, numOfIntegers + 1):
            sumOfAgents[i] = sumOfAgents[i-1] + CS[i-1]

        return sumOfAgents

    def initSumOfValues(self, numOfIntegers, CS, odpip):
        sumOfValues = numpy.empty(numOfIntegers + 1)

        sumOfValues[0] = 0
        for i in range(1, numOfIntegers + 1):
            sumOfValues[i] = sumOfValues[i-1] + odpip.getCoalitionInByteFormatValue(CS[i-1])

        return sumOfValues


    def updateA(self, A1, A2, M, lengthOfM):
        j1 = 0
        j2 = 0
        for j3 in range(len(A2)):
            if j1 >= lengthOfM or j3 + 1 != M[j1]:
                A1[j2] = A2[j3]
                j2 += 1
            
            else:
                j1 += 1

    def setMAndIndexOfM(self, M, indexOfM, lengthOfA, indexToStartAt, s2):
        indexOfM[s2] = indexToStartAt[s2]

        if self.integers[s2] == self.integers[s2-1]:
            if M[s2-1][0] > 1:
                for j in range(1, M[s2-1][0]):
                    indexOfM[s2] -= math.comb(lengthOfA[s2] - j, self.integers[s2] - 1)

            for j1 in range(self.integers[s2]):
                M[s2][j1] = M[s2-1][0] + j1

        else:
            for j1 in range(self.integers[s2]):
                M[s2][j1] = 1 + j1
    
    def setTheLastTwoCoalitionsInCS(self, CS, M, A, numOfIntegers, bit):
        result1 = 0
        result2 = 0
        m = self.integers[numOfIntegers - 2] - 1
        a = len(A[numOfIntegers - 2]) - 1

        while True:
            if a == M[m] - 1:
                result += bit[A[numOfIntegers - 2][a]]
                if m== 0:
                    a -= 1 
                    break
                m -= 1
            
            else:
                result2 += bit[A[numOfIntegers - 2][a]]

            a -= 1
            if a < 0:
                break
        
        while a >= 0:
            result2 += bit[A[numOfIntegers - 2][a]]
            a -= 1

        CS[numOfIntegers - 2] = result1
        CS[numOfIntegers - 1] = result2

    
    def useLocalBranchAndBound(self, odpip, sumOfValues, sumOfAgents, s2, newCoalition, valueOfNewCoalition):
        result = False

        if odpip.f[sumOfAgents[s2+1]] - sumOfValues[s2+1] > 0.000000000005 \
            or odpip.f[newCoalition] - valueOfNewCoalition > 0.000000000005:
            result = True

        if odpip.f[sumOfAgents[s2+1]] - sumOfValues[s2+1] < -0.000000000005:
            odpip.updateValueOfBestPartitionFound(sumOfAgents[s2+1], sumOfValues[s2+1])

        if odpip.f[newCoalition] - valueOfNewCoalition < -0.000000000005:
            odpip.updateValueOfBestPartitionFound(newCoalition, valueOfNewCoalition)

        return result
