from .IntegerPartition import IntegerPartition

class Node(object):
    def __init__(self, subspace):
        self.subspace = subspace
        self.integerPartition = IntegerPartition(subspace.integers)
        
        self.edgesFromThisNode = None
        self.tempFlag = False
        self.tempIntegerRoots = []