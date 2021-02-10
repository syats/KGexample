import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON, XML

from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph


from utils import *

sparql_client = SPARQLWrapper("https://dbpedia.org/sparql")
cent = "<http://dbpedia.org/resource/Claude_Shannon>"
predicates_of_interest = ['http://dbpedia.org/ontology/almaMater',
                          'http://dbpedia.org/ontology/academicAdvisor',
                          'http://dbpedia.org/ontology/doctoralAdvisor',
                          'http://dbpedia.org/ontology/doctoralStudent',
                          'http://dbpedia.org/ontology/employer',
                          'http://dbpedia.org/ontology/institution']



# 1. We get all people associated with Shannon and their birthplaces
sparql_client.setMethod("POST")
query = """
SELECT ?pred ?person ?place ?long ?lat ?placename
WHERE  {
   ?person a <http://schema.org/Person> .
   """ + cent + """ ?pred ?person.
   ?person <http://dbpedia.org/ontology/birthPlace> ?place .
   ?place <http://www.w3.org/2000/01/rdf-schema#label> ?placename .
   OPTIONAL { ?place <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?long } .
   OPTIONAL { ?place <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat }.
}

"""

sparql_client.setReturnFormat(JSON)
sparql_client.setQuery(query)
q_results = sparql_client.query().convert()



people = set()
places = dict()
for r in q_results["results"]["bindings"]:
    people.add(rdflib.URIRef(r["person"]["value"]))
    if "long" in r.keys() and "lat" in r.keys():
        lat = r["lat"]["value"]
        long = r["long"]["value"]
        places[r["placename"]["value"]] = (lat,long)


describe_query = "DESCRIBE "
for p in people:
    describe_query += p.n3()+"\n"

sparql_client.setReturnFormat(XML)
sparql_client.setQuery(describe_query)
g = sparql_client.query().convert()

print(len(g),"triples in people around Claude Shannon")
a = g.serialize(format='application/rdf+xml')
with open("test.xml","wb") as fout:
    fout.write(a)


predicates_of_interest = [rdflib.URIRef(x) for x in predicates_of_interest]

subg = [(s,p,o) for s,p,o in g
        if p in predicates_of_interest
        or s==cent ]

plotgraph(subg, filename="people_and_institutes.html")
