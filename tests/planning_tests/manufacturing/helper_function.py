import os
from typing import List
from rdflib import Graph, URIRef, OWL, RDF

def combine_ontologies_to_temp_file(paths: list[str], out_path: str):
		os.makedirs(os.path.dirname(out_path), exist_ok=True)
		graphs: List[Graph] = [] 
		merged_graph = Graph()
		
		for path in paths:
			graphs.append(Graph())
			graphs[-1].parse(path)

		for graph in graphs:
			merged_graph += graph
		
		# Remove owl:imports for ontologies that are already merged
		# Get all ontology URIs that are declared as owl:Ontology in the merged graph
		merged_ontology_uris = set()
		for subj, pred, obj in merged_graph.triples((None, RDF.type, OWL.Ontology)):
			merged_ontology_uris.add(subj)
		
		# Find and remove owl:imports statements for any ontology already in the merged graph
		import_triples_to_remove = []
		for subj, pred, obj in merged_graph.triples((None, OWL.imports, None)):
			if obj in merged_ontology_uris:
				import_triples_to_remove.append((subj, pred, obj))
		
		for triple in import_triples_to_remove:
			merged_graph.remove(triple)
		
		merged_graph.serialize(destination=out_path, format="turtle")