import random,math,itertools

class IndexedSet(object):
    """A set where each element also has an index from 0 to n-1. Indices are updated if
    the an element is removed from the set.
    """
    def __init__(self):
        self._list=[]
        self._element_to_index={}

    def remove_element(self,element,assertion=True):
        if element not in self._element_to_index:
            if assertion:
                raise KeyError("No such element: "+str(element))
            return False

        element_index=self._element_to_index[element]

        #Remove from the list
        last_element=self._list[-1]
        self._list[-1],self._list[element_index]=self._list[element_index],self._list[-1] #Swap in list
        self._element_to_index[last_element]=element_index #Update index
        self._list.pop()

        #Remove from the dict
        del self._element_to_index[element]
        
        return True

    def add_element(self,element):
        assert element not in self._element_to_index, "Element already in the set: "+str(element) 
        self._element_to_index[element]=len(self._list)
        self._list.append(element)

    def get_element(self,index):
        return self._list[index]

    def pop_index(self,index):
        element=self.get_element(index)
        self.remove_element(element)
        return element

    def pop_random(self):
        index=random.randint(0,len(self)-1)
        return self.pop_index(index)

    def __len__(self):
        return len(self._list)
    
def choice_weighted(emap):
    elements=list(emap)
    return random.choices(elements,weights=list(map(lambda e:emap[e],elements)))[0]
    

class EventRandomizer(object):
    """Event stack for multiple events taking place via Poisson process. 

    Implemented with a Gillespie algorithm.
    """
    def __init__(self):
        self.rtoe={}
        self.size=0

    def add(self,event,rate):
        if rate not in self.rtoe:
            self.rtoe[rate]=IndexedSet()
        self.rtoe[rate].add_element(event)
        self.size+=1

    def remove(self,event,rate):
        if rate in self.rtoe and self.rtoe[rate].remove_element(event,assertion=False):
            self.size-=1
        
            #flush empty ones
            if len(self.rtoe[rate])==0:
                del self.rtoe[rate]

    def next(self):
        events_weighted=dict((  (e,r*len(e)) for r,e in self.rtoe.items()))
        totrate=sum( (r for e,r in events_weighted.items()  ) ) 
        events=choice_weighted(events_weighted)
        event=events.pop_random()
        dt=-math.log(random.uniform(0.0, 1.0)) / totrate
        self.size-=1
        return event, dt



class CompartmentProcess(object):
    """State of the compartment process.
    """
    def __init__(self,noderates,edgerates,ncompartment,net):
        self.noderates=noderates
        self.edgerates=edgerates
        self.net=net
        self.ncompartment=ncompartment
        self.reset()

    def reset(self):
        self.events=EventRandomizer()
        self.node_events={}
        self.time=0        
        self.node_compartment=dict(map(lambda n:(n,self.ncompartment),self.net))

        self.counts=dict( ((c,0) for c in  self.get_compartments() ))
        self.counts[self.ncompartment]=len(self.net)

        for node in self.net:
            self.node_events[node]=[]


    def get_compartments(self):
        """Parse compartments from rules
        """
        nkeys=set(self.noderates)
        ekeys=set(itertools.chain.from_iterable(self.edgerates))
        nvals=set(c for c,r in self.noderates.values())
        evals=set(c for c,r in self.edgerates.values())
        return nkeys | ekeys | nvals | evals

    def change_node_compartment(self,node,compartment):

        #remove all events where this node is involved in
        while len(self.node_events[node])>0:
            event=self.node_events[node].pop()
            rate=event[3]
            self.events.remove(event,rate)

        #change the compartment of this node
        self.counts[self.node_compartment[node]]-=1
        self.counts[compartment]+=1
        self.node_compartment[node]=compartment

        #add events as dictated by the new compartment
        if compartment in self.noderates:
            target,rate = self.noderates[compartment]
            event=(node,node,target,rate)
            self.events.add(event,rate)
            self.node_events[node].append(event)

        #add events with all neighbors
        for neighbor in self.neighbors(node):
            ncompartment=self.node_compartment[neighbor]
            if (compartment,ncompartment) in self.edgerates:
                target,rate=self.edgerates[(compartment,ncompartment)]
                if callable(rate):
                    rate=rate(self.net[node][neighbor]['weight'])
                event=(node,neighbor,target,rate)
                self.events.add(event,rate)
                self.node_events[node].append(event)
                self.node_events[neighbor].append(event)
            if (ncompartment,compartment) in self.edgerates:
                target,rate=self.edgerates[(ncompartment,compartment)]
                if callable(rate):
                    rate=rate(self.net[node][neighbor]['weight'])
                event=(neighbor,node,target,rate)
                self.events.add(event,rate)
                self.node_events[neighbor].append(event)
                self.node_events[node].append(event)


    def next(self):
        event,dt=self.events.next()
        self.change_node_compartment(event[1],event[2])
        self.time+=dt
        return event,dt


    def neighbors(self,node):
        """Iterate over neighbors of a node in the network.

        This method works with networkx. Overrride if you want to use some other
        container for your network.
        """
        for neighbor in self.net.neighbors(node):
            yield neighbor

    def unfinished(self):
        return self.events.size>0


class CompartmentSimulation(object):
    """Helper object for keeping track of simulations of compartment process.
    Useful for setup and keeping the history.
    """
    def __init__(self,noderates,edgerates,ncompartment,net):
        self.cp=CompartmentProcess(noderates,edgerates,ncompartment,net)
        
    def reset(self,nodecomps={},comps={},defcomp=None):
        if defcomp==None:
            defcomp=self.cp.ncompartment
        self.cp.reset()
        self.n=len(self.cp.net)
        for node in self.cp.net:
            if node in nodecomps:
                self.set_node(node,nodecomps[node])
            elif len(comps)>0:
                comp=choice_weighted(comps)
                self.set_node(node,comp)
            else:
                self.set_node(node,defcomp)

        self.maxvals={}
        for comp in self.cp.get_compartments():
            self.maxvals[comp]=-1

    def set_node(self,node,compartment):
        if self.cp.node_compartment[node]!=compartment:
            self.cp.change_node_compartment(node,compartment)


    def next(self):
        event,dt=self.cp.next()
        return event,dt

    def record(self,trim=1,maxtime=None,maxiter=None,rmax=True,rcustom=None,rcustom_start=None):
        self.times=[]
        i=0
        self.comps=dict((c,[]) for c in self.cp.get_compartments())
        self.custom=rcustom_start
        while(self.cp.unfinished() and (maxtime==None or self.cp.time<maxtime) and (maxiter==None or i<maxiter) ):
            self.next()
            i+=1
            if i%trim==0:
                self.times.append(self.cp.time)
                for comp, l in self.comps.items():
                    l.append(self.cp.counts[comp])
            if rmax:
                for comp, l in self.comps.items():
                    self.maxvals[comp]=max(self.cp.counts[comp],self.maxvals[comp])
            if rcustom!=None:
                self.custom=rcustom(self.custom,self.cp.counts)
        return self.times,self.comps
            

    def nsteps(self,n):
        for i in range(n):
            self.next()

    def __iter__(self):
        while len(self.cp.events)!=0:
            yield self.next()


