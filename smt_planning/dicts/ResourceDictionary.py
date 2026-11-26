from typing import Dict, List
from smt_planning.dicts.name_util import convert_iri_to_z3_variable
from z3 import Int
from smt_planning.dicts.CapabilityDictionary import Capability

#TODO: needs to leave but openmath parser needs occurernces. After fixing openmath parser, remove this class
class ResourceOccurence:
	def __init__(self, iri: str, happening: int, event: int):
		self.iri = iri
		self.happening = happening
		self.event = event
		z3_variable_name = convert_iri_to_z3_variable(iri, happening, event)
		self.z3_variable = Int(z3_variable_name)

class Resource: 
	id: int = 0
	def __init__(self, iri: str, capabilities: List[Capability]) -> None:
		self.iri = iri
		#self.z3_variable = Int(iri)
		Resource.id += 1
		self.id = Resource.id
		self.occurrences: Dict[int, Dict[int, ResourceOccurence]] = {}
		self.capabilities = capabilities

	def __eq__(self, other) -> bool:
		if not isinstance(other, Resource):
			return False
		return self.iri == other.iri
	
	def __hash__(self) -> int:
		return hash(self.iri)
	
	def __repr__(self) -> str:
		return f"Resource(iri={self.iri}"

	def add_occurence(self, occurence: ResourceOccurence):
		happening = occurence.happening
		event = occurence.event
		self.occurrences.setdefault(happening, {}).setdefault(event, occurence)
		
class ResourceDictionary: 
	def __init__(self):
		self.resources: Dict[str, Resource] = {}

	def add_resource(self, iri: str, capabilities: List[Capability]) -> None:
		resource = Resource(iri, capabilities)
		self.resources.setdefault(iri, resource)
	
	def get_resource(self, iri: str) -> Resource:
		if (not iri in self.resources):
			raise KeyError(f"There is no resource with key {iri}.")
		return self.resources[iri]

	def add_resource_occurences(self, happenings: int, event_bound: int) -> None:
		for resource in self.resources.values():
			for happening in range(happenings):
				for event in range(event_bound):
					resource_occurrence = ResourceOccurence(resource.iri, happening, event)
					resource.add_occurence(resource_occurrence)