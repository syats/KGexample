import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON

from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network

sparql_client = SPARQLWrapper("https://dbpedia.org/sparql")
cent = "<http://dbpedia.org/resource/Claude_Shannon>"


sparql_client.setReturnFormat(JSON)
sparql_client.setMethod("POST")


query = """
SELECT ?pred ?person ?place
WHERE  {
   ?person a <http://schema.org/Person> .
   """ + cent + """ ?pred ?person.
   ?person <http://dbpedia.org/ontology/birthPlace> ?place .
}

"""

sparql_client.setQuery(query)
q_results = sparql_client.query().convert()
people = set()
which_predicates = dict()
for r in q_results["results"]["bindings"]:
    people.add(rdflib.URIRef(r["person"]["value"]))
    which_predicates[rdflib.URIRef(r["person"]["value"])] = rdflib.URIRef(r["pred"]["value"])

describe_query = "DESCRIBE "
for p in people:
    describe_query += p.n3()+"\n"

sparql_client.setQuery(describe_query)
result = sparql_client.query().convert()
g = rdflib.Graph()
for b in result['results']['bindings']:
    o = rdflib.URIRef(b['o']['value']) if b['o']['type'] == "uri" else rdflib.Literal(b['o']['value'])
    g.add((rdflib.URIRef(b['s']['value']),rdflib.URIRef(b['p']['value']),o))

print(len(g),"triples in people around Claude Shannon")

predicates_of_interest = ['http://dbpedia.org/ontology/almaMater',
                          'http://dbpedia.org/ontology/academicAdvisor',
                          'http://dbpedia.org/ontology/doctoralAdvisor',
                          'http://dbpedia.org/ontology/doctoralStudent',
                          'http://dbpedia.org/ontology/employer',
                          'http://dbpedia.org/ontology/institution']
predicates_of_interest = [rdflib.URIRef(x) for x in predicates_of_interest]

subg = [triple for triple in g if triple[1] in predicates_of_interest]

def clean(uri):
    if type(uri) is str:
        r = uri.strip()[1:-1].split("/")[-1]
    else:
        r = uri.n3()[1:-1].split("/")[-1]
    if "#" in r:
        r = r.split("#")[-1]
    return r.replace("_"," ")

G = nx.Graph()
G.add_node(clean(cent))
for s,p,o in subg:
    G.add_node(clean(s),label=clean(s))
    G.add_edge(clean(s), clean(o), label=clean(p))
    if s in which_predicates.keys():
        G.add_edge(clean(s), clean(cent))

# Plot Networkx instance of RDF Graph
nt = Network("800px", "1200px")
nt.from_nx(G)
nt.show("nx.html")
