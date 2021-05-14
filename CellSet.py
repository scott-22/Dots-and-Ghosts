from configs import *

# Disjoint Set implementation to store grid cells
class CellSet:
    def __init__(self):
        # Disjoint set
        self.dset = [i for i in range(COL*ROW)]
        self.drank = [0 for i in range(COL*ROW)]
    
    # Hash each row/col pair to an index
    def dhash(self, x):
        return x[0]*ROW + x[1]
    
    def dfind(self, i): # i is hashed index
        if self.dset[i] != i:
            self.dset[i] = self.dfind(self.dset[i]) # Path compression
        return self.dset[i]
    
    def dhashfind(self, x): # x is tuple
        return self.dfind(self.dhash(x))
    
    def dmerge(self, x, y): # x, y are tuples
        i = self.dhashfind(x)
        j = self.dhashfind(y)
        if self.drank[i] > self.drank[j]:
            self.dset[j] = i
        elif self.drank[j] > self.drank[i]:
            self.dset[i] = j
        else:
            self.dset[j] = i
            self.drank[i] += 1