
class Edge(object):
    def __init__(self, node, partThatWasSplit, twoPartsThatResultedFromTheSplit):
        self.node = node
        self.partThatWasSplit = partThatWasSplit
        self.twoPartsThatResultedFromTheSplit = twoPartsThatResultedFromTheSplit
