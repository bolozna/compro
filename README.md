
Compartmental model processes on networks


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

![SIR example](https://raw.githubusercontent.com/bolozna/compro/master/examples/sir_example.png "A SIR model run.")
