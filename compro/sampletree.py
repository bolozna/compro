
import random

class TreeNode(object):
    """
    - leafs are static: leafs don't become branches or the elements in them changed
    """
    def __init__(self,element=None,weight=0,parent=None):
        self.r=None
        self.l=None
        self.element=element
        self.weight=weight
        self.parent=parent

    def _update_child(self,oldchild,newchild):
        if self.l==oldchild:
            self.l=newchild
        elif self.r==oldchild:
            self.r=newchild
        else:
            raise Exception("The old child is not mine!")

    def add(self,element,weight):
        if self.l==None and self.r==None and self.element==None:
            #This is an empty node of an empty tree, becomes a leaf
            self.element=element
            self.weight=weight
            return self
        elif self.l==None and self.r==None:
            #This is a leaf, becomes a branch, old leaf to right, new to left
            #Make a new branch: this leaf to right, new to left
            newBranch=TreeNode(weight=self.weight+weight,parent=self.parent)
            self.parent._update_child(self,newBranch)
            self.parent=newBranch
            newBranch.r=self

            newLeaf=TreeNode(element,weight,parent=newBranch)
            newBranch.l=newLeaf

            return newLeaf
        elif self.l==None or self.r==None:
            #This should not happen
            raise Exception("Invalid tree structure.")
        elif self.r.weight>self.l.weight:
            #This is a branch, and left branch lighter, put the new element there
            self.weight+=weight
            return self.l.add(element,weight)
        else:
            #This is a branch, and right branch lighter, put the new element there
            self.weight+=weight
            return self.r.add(element,weight)

    def sample(self):
        if self.element!=None:
            return self.element
        pleft=self.l.weight/float(self.l.weight + self.r.weight)
        if random.random()<pleft:
            return self.l.sample()
        else:
            return self.r.sample()

    def update(self,wdiff):
        self.weight=self.weight+wdiff
        if self.parent!=None:
            self.parent.update(wdiff)

    def remove(self):
        assert self.element!=None, "You can only remove leaves."
        # When this leaf is removed: 
        # (1) we replace its parent with the sibling, and
        # (2) update the weight of the grandparent
        # Special cases:
        # (a) this is a root
        # (b) the parent is a root

        #If this is a root, it is simple.
        if not isinstance(self.parent,TreeNode): 
            self.element=None
            self.weight=0
            return None
                
        #find the sibling
        if self.parent.l==self:
            sibling=self.parent.r
        else:
            assert self.parent.r==self
            sibling=self.parent.l

        sibling.parent=self.parent.parent
        self.parent.parent._update_child(self.parent,sibling)
        self.parent.parent.update(-self.weight)

        #for memory leaks, remove refs from parent to reduce the ref counts to 0
        self.parent.l=None
        self.parent.r=None

    def __str__(self):
        if self.element!=None:
            return "("+str(self.element)+":"+str(self.weight)+")"
        return "["+str(self.l) +","+str(self.r)+":"+str(self.weight)+"]"

    def _assert_weights(self):
        """Check that the weights in the tree are consistent.
        """
        pass

    def _assert_parents(self):
        """Check that the parents in the tree are consistent.
        """
        pass

class SampleTree(object):
    """Balanced sum tree.
    """
    def __init__(self):
        self._t=TreeNode(parent=self) 
        self._leafs={}

    def update(self,dummy):
        """Does nothing.
        """
        pass

    def _update_child(self,oldchild,newchild):
        self._t=newchild

    def add(self,element,weight):
        assert element not in self._leafs, "element already added"
        self._leafs[element]=self._t.add(element,weight)

    def sample(self):
        return self._t.sample()

    def remove(self,element):
        self._leafs[element].remove()
        del self._leafs[element]
    
    def update_weight(self,element,wdiff):
        self._leafs[element].update(wdiff)


if __name__=="__main__":
    #test addition
    tree=SampleTree()
    rlist=[(i,random.random()) for i in range(50)]
    target={}; s=sum(map(lambda x:x[1],rlist))
    for i,w in rlist:
        tree.add(i,w)
        target[i]=w/s

    samples={}
    for _ in range(10**2):
        sample=tree.sample()
        samples[sample]=samples.get(sample,0)+1

    #test addition, deletion, addition
    tree=SampleTree()
    rlist=[(i,random.random()) for i in range(50)]
    for i,w in rlist[:30]+rlist[40:]:
        tree.add(i,w)
    for i,w in rlist[40:]:
        tree.remove(i)
    for i,w in rlist[30:40]:
        tree.add(i,w)

    target={}; s=sum(map(lambda x:x[1],rlist[:40]))
    for i,w in rlist[:40]:
        target[i]=w/s


    samples={}
    for _ in range(10**6):
        sample=tree.sample()
        samples[sample]=samples.get(sample,0)+1
    print(target)
    print(samples)