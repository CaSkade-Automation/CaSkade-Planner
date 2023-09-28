from typing import List, Mapping, Dict

from rdflib import Graph, Variable
from rdflib.term import Identifier 
from z3 import BoolRef

from smt_planning.StateHandler import StateHandler
from smt_planning.dicts.PropertyDictionary import Property


class PropertyPair:
	def __init__(self, property_a: Property, property_b: Property) -> None:
		self.property_a = property_a
		self.property_b = property_b


class PropertyPairCache:
	property_pairs: List[PropertyPair] = list()

	@staticmethod
	def get_property_pairs():
		if not PropertyPairCache.property_pairs:
			PropertyPairCache.property_pairs = find_property_pairs()			

		return PropertyPairCache.property_pairs

	@staticmethod
	def reset():
		PropertyPairCache.property_pairs = None


def get_property_cross_relations(happenings: int, event_bound: int) -> List[BoolRef]:
	
	graph = StateHandler().get_graph()
	property_dictionary = StateHandler().get_property_dictionary()
	related_property_pairs = PropertyPairCache.get_property_pairs()
	
	relation_constraints = []

	# 1: Relate inits. We need to get inputs of the required capability and make sure related properties are bound to the values of these properties.
	# Both requirements and assurances need to be bound because otherwise assurance would be "floating" and could be set to goal without respecting caps
	required_input_properties = get_inputs_of_required_cap(graph)
	for required_input_prop_iri in required_input_properties:
		related_properties = get_partners(str(required_input_prop_iri), related_property_pairs)
		for related_property in related_properties:
			# related_property_relation_type = property_dictionary.get_relation_type_of_property(related_property_iri)
			# if related_property_relation_type != "Input":
			# 	continue

			required_input_prop = property_dictionary.get_required_property_occurrence(str(required_input_prop_iri)).z3_variable
			try: 
				related_property = property_dictionary.get_provided_property_occurrence(str(related_property.iri), 0, 0).z3_variable
				relation_constraint = (required_input_prop == related_property)
				relation_constraints.append(relation_constraint)
			except KeyError:
				print(f"There is no provided property with key {related_property.iri}.")

	# 2: Relate goals. We need to get all outputs of the required capability and make sure that related output properties are bound to the valu of these outputs
	# Only constrain output properties because we are only interested in the final output. The input depends on the capability and must not be "over-constrained"
	required_output_properties = get_outputs_of_required_cap(graph)
	for required_output_prop_iri in required_output_properties:
		related_properties = get_partners(str(required_output_prop_iri), related_property_pairs)
		for related_property in related_properties:
			related_property_relation_type = property_dictionary.get_property_relation_type(related_property.iri)
			if related_property_relation_type != "Output":
				continue

			required_output_prop = property_dictionary.get_required_property_occurrence(str(required_output_prop_iri)).z3_variable
			try:
				related_property = property_dictionary.get_provided_property_occurrence(str(related_property.iri), happenings-1, 1).z3_variable
				relation_constraint = (required_output_prop == related_property)
				relation_constraints.append(relation_constraint)
			except KeyError: 
				print(f"There is no provided property with key {related_property.iri}.")


	return relation_constraints

def get_inputs_of_required_cap(graph: Graph):
	query_string = """
	PREFIX DINEN61360: <http://www.hsu-ifa.de/ontologies/DINEN61360#>
	PREFIX VDI3682: <http://www.w3id.org/hsu-aut/VDI3682#>
	PREFIX CaSk: <http://www.w3id.org/hsu-aut/cask#>
	PREFIX CSS: <http://www.w3id.org/hsu-aut/css#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	SELECT ?cap ?input ?de WHERE {
		?cap a CaSk:RequiredCapability;
			^CSS:requiresCapability ?process.
		?process VDI3682:hasInput ?input.
		?de a DINEN61360:Data_Element.
		?de DINEN61360:has_Type_Description ?td;
			DINEN61360:has_Instance_Description ?id.
		?input VDI3682:isCharacterizedBy ?id.
	}
	"""
	
	result = graph.query(query_string)
	input_iris = [binding.get('de') for binding in result.bindings]
	return input_iris


def get_outputs_of_required_cap(graph: Graph):
	query_string = """
	PREFIX DINEN61360: <http://www.hsu-ifa.de/ontologies/DINEN61360#>
	PREFIX VDI3682: <http://www.w3id.org/hsu-aut/VDI3682#>
	PREFIX CaSk: <http://www.w3id.org/hsu-aut/cask#>
	PREFIX CSS: <http://www.w3id.org/hsu-aut/css#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	SELECT ?cap ?output ?de WHERE {
		?cap a CaSk:RequiredCapability;
			^CSS:requiresCapability ?process.
		?process VDI3682:hasOutput ?output.
		?de a DINEN61360:Data_Element.
		?de DINEN61360:has_Type_Description ?td;
			DINEN61360:has_Instance_Description ?id.
		?output VDI3682:isCharacterizedBy ?id.
	}
	"""
	
	result = graph.query(query_string)
	output_iris = [binding.get('de') for binding in result.bindings]
	return output_iris



def get_related_properties(property_iri:str) -> List[Property]:

	property_dictionary = StateHandler().get_property_dictionary()
	property_pairs = PropertyPairCache.get_property_pairs()
	result_related_properties: List[Property] = []

	# Find all related partners of the given property
	related_properties = get_partners(property_iri, property_pairs)
	
	for related_property in related_properties:
		# Get related at same happening and event, but only if Output
		# if property_dictionary.get_relation_type_of_property(related_property) != "Output": continue
		
		try: 
			related_property = property_dictionary.get_provided_property(related_property.iri)
			result_related_properties.append(related_property)
		except KeyError: 
			print(f"There is no provided property with key {related_property}.")

	return result_related_properties



def get_partners(property_iri: str, property_pairs:List[PropertyPair]) -> List[Property]:
	# Returns all partners of a property from the list of property pairs
	# Gets partnerA if partnerB is given and partnerB if partnerA is given
	related_properties = []
	for property_pair in property_pairs:
		if (str(property_iri) ==  str(property_pair.property_a.iri)):
			related_properties.append(property_pair.property_b)
		if (str(property_iri) ==  str(property_pair.property_b.iri)):
			related_properties.append(property_pair.property_a)
		
	return related_properties


def is_existing(pair: PropertyPair, other_pair: PropertyPair) -> bool:
	a_same_a = str(pair.property_a.iri) == str(other_pair.property_a.iri)
	b_same_b = str(pair.property_b.iri) == str(other_pair.property_b.iri)
	a_same_b = str(pair.property_a.iri) == str(other_pair.property_b.iri)
	b_same_a = str(pair.property_b.iri) == str(other_pair.property_a.iri)
	return (a_same_a and b_same_b) or (a_same_b and b_same_a)

def is_self_pair(pair: PropertyPair) -> bool:
	return str(pair.property_a.iri) == str(pair.property_b.iri)


def find_property_pairs() -> List[PropertyPair]: 
	# Queries the graph and finds all implicitly related property pairs

	query_string = """
	PREFIX DINEN61360: <http://www.hsu-ifa.de/ontologies/DINEN61360#>
	PREFIX VDI3682: <http://www.w3id.org/hsu-aut/VDI3682#>
	PREFIX CaSk: <http://www.w3id.org/hsu-aut/cask#>
	PREFIX CSS: <http://www.w3id.org/hsu-aut/css#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	SELECT ?cap ?inOut ?de ?td ?inOutType ?inOutSubType WHERE {
		?cap a ?capType;
			^CSS:requiresCapability ?process.
		values ?capType { CaSk:ProvidedCapability CaSk:RequiredCapability }.
		?process VDI3682:hasInput|VDI3682:hasOutput ?inOut.
		?de a DINEN61360:Data_Element.
		?de DINEN61360:has_Type_Description ?td;
			DINEN61360:has_Instance_Description ?id.
		?inOut VDI3682:isCharacterizedBy ?id.
		BIND(VDI3682:Product AS ?inOutType)
		?inOut a ?inOutType.
		OPTIONAL {
			?inOut a ?inOutSubType.
			?inOutSubType rdfs:subClassOf VDI3682:Product.
		}
	}
	"""
	graph = StateHandler().get_graph()
	result = graph.query(query_string)
	# Creates a list of pairs of related properties, i.e. a properties with a different data_element that is still implicitly connected and thus must be linked in SMT
	# Requirement for a related property:
	# Must belong to different capability, must have same type description and either both properties dont have a product subtype or both have the same subtype
	property_dictionary = StateHandler().get_property_dictionary()
	related_property_pairs: List[PropertyPair] = []
	for binding in result.bindings:
		related_bindings = list(filter(lambda x: is_related_property_binding(binding, x), result.bindings))
		for related_binding in related_bindings:
			property_a = property_dictionary.get_property(str(binding.get("de")))
			property_b = property_dictionary.get_property(str(related_binding.get("de")))
			pair = PropertyPair(property_a, property_b)
			existing_pair = next(filter(lambda x: is_existing(pair, x), related_property_pairs), None)
			self_pair = is_self_pair(pair) 
			if not existing_pair and not self_pair:
				related_property_pairs.append(pair)

	return related_property_pairs


def is_related_property_binding(binding: Mapping[Variable, Identifier], other_binding: Mapping[Variable, Identifier]) -> bool:
	# Checks whether two properties are related
	return same_type_description(binding, other_binding) and subtype_matches(binding, other_binding)


def different_capability(binding: Mapping[Variable, Identifier], other_binding: Mapping[Variable, Identifier]) -> bool:
	# Checks wheter two result bindings belong to different capabilities
	return (str(binding.get("cap")) != str(other_binding.get("cap")))


def same_type_description(binding: Mapping[Variable, Identifier], other_binding: Mapping[Variable, Identifier]) -> bool:
	# Checks whether two result bindings refer to the same type description
	return (str(binding.get("td")) == str(other_binding.get("td")))


def subtype_matches(binding: Mapping[Variable, Identifier], other_binding: Mapping[Variable, Identifier]) -> bool:
	# Checks whether the product subtype of two result bindings is identical
	return (str(binding.get("inOutSubType")) == str(other_binding.get("inOutSubType")))
