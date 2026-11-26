from typing import Set, Dict, List

from smt_planning.types.PropertyOccurrence import PropertyOccurrence
from smt_planning.types.InstanceDescription import InstanceDescription


'''
iri is the IRI of the data element
data_type is some instance of http://www.w3id.org/hsu-aut/DINEN61360#Simple_Data_Type
relation_types are the relation types of the property ("Input" and / or "Output") for every capability it belongs to. 
A property can be input of one capability and output of another one, e.g. the position of a robot.
'''
class Property:
	def __init__(self, iri: str, data_type: str, relation_type: str, capability_iris: Set[str]):
		self.iri = iri
		self.data_type = data_type
		self.capability_iris: Set[str] = set()
		self.relation_types: Dict[str, Set[str]] = {}
		self.add_relation(relation_type, capability_iris)
		self.occurrences: Dict[int, Dict[int, PropertyOccurrence]] = {}
		self.instances: List[InstanceDescription] = []

	def add_relation(self, relation_type: str, capability_iris: Set[str]) -> None:
		# A property is found once for every relation type, so that the capabilities and relation types of all findings have to be collected
		self.capability_iris.update(capability_iris)
		for capability_iri in capability_iris:
			self.relation_types.setdefault(capability_iri, set()).add(relation_type)

	def is_input_of(self, capability_iri: str) -> bool:
		return "Input" in self.relation_types.get(capability_iri, set())

	def is_output_of(self, capability_iri: str) -> bool:
		return "Output" in self.relation_types.get(capability_iri, set())

	def is_output(self) -> bool:
		# Checks whether the property is an output of at least one capability
		return any("Output" in relation_types for relation_types in self.relation_types.values())

	def add_occurrence(self, occurrence: PropertyOccurrence):
		happening = occurrence.happening
		event = occurrence.event
		self.occurrences.setdefault(happening, {}).setdefault(event, occurrence)

	def get_all_occurrences(self) -> List[PropertyOccurrence]:
		# Double list comprehension to flatten the double dict-structure of self.occurrences
		occurrences = [value for inner_dict in self.occurrences.values() for value in inner_dict.values()]
		return occurrences

	def get_occurrence_by_z3_variable(self, z3_variable_name: str) -> PropertyOccurrence | None:
		# Filters occurrences for the given z3_variable. There should only be one result
		happening_occurrences = [occ for occ in self.occurrences.values()]
		all_occurrences_2d = [list(occ.values()) for occ in happening_occurrences]
		all_occurrences: List[PropertyOccurrence] = []
		[all_occurrences.extend(occ) for occ in all_occurrences_2d]
		try:
			occurrence = [occurrence for occurrence in all_occurrences if str(occurrence.z3_variable) == z3_variable_name][0]
			return occurrence
		except:
			return None
		
	def add_instance(self, instance: InstanceDescription):
		self.instances.append(instance)
	

	def __lt__(self, other):
		return self.iri < other.iri  # Comparison / Sorting by IRI string 

	def __repr__(self):
		return f"Property(iri={self.iri})"
    
	def __eq__(self, other):
		return self.iri == other.iri
    
	def __hash__(self):
		return hash(self.iri)
