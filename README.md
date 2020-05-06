
A simulator for compartmental model processes on networks. 

"Because what the world needs right now is yet another epidemic model simulator."

Each node is in one of the states specified by the user. The transitions of nodes from states to other take place with Poisson processes. The user can define the rates of spontaneous transitions or transitions due to the compartment of a neighboring node. 


# Examples

Example of running an SIR process on an ER network and plotting the results.
```
>>> from compro import *
>>> import networkx as nx
>>> from matplotlib import pyplot as plt

>>> nsize=10000
>>> k=5
>>> g=nx.fast_gnp_random_graph(nsize,k/float(nsize))

>>> s=CompartmentSimulation({ "I":("R",0.5)},{("I","S"):("I",1.0)},"S",g)
>>> s.reset(comps={"S":0.99,"I":0.01})
>>> t,c=s.record()

>>> plt.plot(t,c["S"],t,c["I"],t,c["R"]) 
>>> plt.show()
```

![SIR example](https://github.com/bolozna/compro/blob/master/examples/sir_example.png "A SIR model run.")
