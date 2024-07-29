from typing import List, Mapping

from rdflib import Graph, Variable
from rdflib.term import Identifier 

from smt_planning.smt.StateHandler import StateHandler
from smt_planning.dicts.PropertyDictionary import Property
from smt_planning.dicts.CapabilityDictionary import Capability
from smt_planning.smt.property_links import different_capability, same_type_description, subtype_matches

class CapabilityPair:
	def __init__(self, capability_a: Capability, capability_b: Capability, property: Property) -> None:
		self.capability_a = capability_a
		self.capability_b = capability_b
		self.property = property


class CapabilityPairCache:
	capability_pairs: List[CapabilityPair] = list()

	@staticmethod
	def get_capability_pairs():
		if not CapabilityPairCache.capability_pairs:
			CapabilityPairCache.capability_pairs = find_capability_pairs()			

		return CapabilityPairCache.capability_pairs
	
	@staticmethod
	def reset():
		CapabilityPairCache.capability_pairs = None


def get_capability_partners(capability_iri: str, property_iri: str, capability_pairs:List[CapabilityPair]) -> List[Capability]:
	# Returns all partners of a property from the list of property pairs
	# Gets partnerA if partnerB is given and partnerB if partnerA is given
	related_capabilities = []
	for capability_pair in capability_pairs:
		if (str(capability_iri) == str(capability_pair.capability_a.iri)) and (str(property_iri) == str(capability_pair.property.iri)):
			related_capabilities.append(capability_pair.capability_b)
		if (str(capability_iri) == str(capability_pair.capability_b.iri)) and (str(property_iri) == str(capability_pair.property.iri)):
			related_capabilities.append(capability_pair.capability_a)
		
	return related_capabilities

def is_existing_cap(pair: CapabilityPair, other_pair: CapabilityPair) -> bool:
	a_same_a = str(pair.capability_a.iri) == str(other_pair.capability_a.iri) and str(pair.property.iri) == str(other_pair.property.iri)
	b_same_b = str(pair.capability_b.iri) == str(other_pair.capability_b.iri) and str(pair.property.iri) == str(other_pair.property.iri)
	a_same_b = str(pair.capability_a.iri) == str(other_pair.capability_b.iri) and str(pair.property.iri) == str(other_pair.property.iri)
	b_same_a = str(pair.capability_b.iri) == str(other_pair.capability_a.iri) and str(pair.property.iri) == str(other_pair.property.iri)
	return (a_same_a and b_same_b) or (a_same_b and b_same_a)


def find_capability_pairs() -> List[CapabilityPair]:
	query_string = """
	PREFIX DINEN61360: <http://www.w3id.org/hsu-aut/DINEN61360#>
	PREFIX VDI3682: <http://www.w3id.org/hsu-aut/VDI3682#>
	PREFIX CaSk: <http://www.w3id.org/hsu-aut/cask#>
	PREFIX CSS: <http://www.w3id.org/hsu-aut/css#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	SELECT ?cap ?de ?td ?inOutSubType WHERE {
		?cap a CaSk:ProvidedCapability;
			^CSS:requiresCapability ?process.
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
	} """

	query_handler = StateHandler().get_query_handler()
	result = query_handler.query(query_string)
	# Creates a list of pairs of related capabilites, i.e. a capability with a different data_element that is still implicitly connected and thus must be linked in SMT
	# Requirement for a related capability:
	# Property of Output must have same type description and either both properties dont have a product subtype or both have the same subtype
	property_dictionary = StateHandler().get_property_dictionary()
	capability_dictionary = StateHandler().get_capability_dictionary()
	related_capability_pairs: List[CapabilityPair] = []
	for binding in result.bindings:
		related_bindings = list(filter(lambda x: is_related_capability_binding(binding, x), result.bindings))
		for related_binding in related_bindings:
			capability_a = capability_dictionary.get_capability(str(binding.get(Variable("cap"))))
			capability_b = capability_dictionary.get_capability(str(related_binding.get(Variable("cap"))))
			property = property_dictionary.get_property(str(binding.get(Variable("de"))))
			pair = CapabilityPair(capability_a, capability_b, property)
			existing_pair = next(filter(lambda x: is_existing_cap(pair, x), related_capability_pairs), None)
			# TODO: do we need to check for same pair here as well?
			if not existing_pair:
				related_capability_pairs.append(pair)

	return related_capability_pairs


def is_related_capability_binding(binding: Mapping[Variable, Identifier], other_binding: Mapping[Variable, Identifier]) -> bool:
	# Checks whether two properties are related
	return different_capability(binding, other_binding) and same_type_description(binding, other_binding) and subtype_matches(binding, other_binding)


def get_related_capabilities(capability_iri:str, property_iri:str) -> List[Capability]:

	capability_pairs = CapabilityPairCache.get_capability_pairs()

	# Find all related partners of the given capability
	related_capabilities = get_capability_partners(capability_iri, property_iri, capability_pairs)
	return related_capabilities
	
