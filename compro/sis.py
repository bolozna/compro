"""Example, SIS model.
"""

from compro import *
import networkx as nx
from matplotlib import pyplot as plt

nsize=10000
k=5
g=nx.fast_gnp_random_graph(nsize,k/float(nsize))


s=CompartmentSimulation({ "I":("S",1.)},{("I","S"):("I",1.)},"S",g)
s.reset(comps={"S":0.9,"I":0.1})
t,c=s.record(maxiter=100000,trim=100)

plt.plot(t,c["S"],t,c["I"])
plt.show()  


