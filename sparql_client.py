# sparql_client.py
from SPARQLWrapper import SPARQLWrapper, JSON

GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/Farming"
PREFIX = "PREFIX agri: <http://www.semanticweb.org/admin/ontologies/2026/7/untitled-ontology-2#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"

def run_sparql(query: str):
    sparql = SPARQLWrapper(GRAPHDB_ENDPOINT)
    sparql.setQuery(PREFIX + query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]