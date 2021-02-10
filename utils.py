import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import rdflib

def clean(uri):
    if type(uri) is str:
        r = uri.strip()[1:-1].split("/")[-1]
    else:
        r = uri.n3()[1:-1].split("/")[-1]
    if "#" in r:
        r = r.split("#")[-1]
    return r.replace("_"," ")

def plotgraph(subg, 
              filename="nx.html",
              height=900,width=1600,
              title="Example"):
    if type(subg) in [rdflib.ConjunctiveGraph, rdflib.graph]:
        subg = [(s,p,o) for s,p,o in g]

    G = nx.Graph(directed=True)
    for s,p,o in subg:
        G.add_node(clean(s),label=clean(s))
        G.add_edge(clean(s), clean(o), title=clean(p))


    # Plot Networkx instance of RDF Graph
    nt = Network(str(height)+"px", str(width)+"px",
                 directed=True,
                 heading=title )
    nt.from_nx(G)
    nt.show(filename)
