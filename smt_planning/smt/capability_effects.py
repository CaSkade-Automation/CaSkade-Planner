from rdflib import Graph
from typing import List
from z3 import Implies, Not, BoolRef, ArithRef

from smt_planning.smt.StateHandler import StateHandler
from smt_planning.smt.property_links import get_related_properties


def getCapabilityEffects(happenings: int, event_bound: int) -> List:
	
	# Effect 1. Fall Assurance mit statischem Value

	# Get all capability outputs  
	query_string = """
	PREFIX cask: <http://www.w3id.org/hsu-aut/cask#>
	PREFIX VDI3682: <http://www.w3id.org/hsu-aut/VDI3682#>
	PREFIX DINEN61360: <http://www.hsu-ifa.de/ontologies/DINEN61360#>
	PREFIX CSS: <http://www.w3id.org/hsu-aut/css#>

	select ?cap ?de ?log ?val where {  
		?cap a cask:ProvidedCapability;
			^CSS:requiresCapability ?process.
		?process VDI3682:hasOutput ?output.
		?output VDI3682:isCharacterizedBy ?id.
		?id DINEN61360:Expression_Goal "Assurance";
			DINEN61360:Logic_Interpretation ?log.
		?de DINEN61360:has_Instance_Description ?id.
		OPTIONAL { ?id DINEN61360:Value ?val. }
	} """

	query_handler = StateHandler().get_query_handler()
	results = query_handler.query(query_string)
	property_dictionary = StateHandler().get_property_dictionary()
	capability_dictionary = StateHandler().get_capability_dictionary()
	effects = []
	for happening in range(happenings):
		for row in results:
			current_capability = capability_dictionary.get_capability_occurrence(str(row['cap']), happening).z3_variable
			effect_property = property_dictionary.get_provided_property_occurrence(str(row['de']), happening, 1).z3_variable
			relation = str(row['log'])																						
			# Case 1: Constant effect 																					
			if row['val']: 																								
				value = str(row['val'])																							
				prop_type = property_dictionary.get_property_data_type(str(row['de'])) 												
				effect = generate_effect_constraint(current_capability, effect_property, prop_type, relation, value)	
				effects.append(effect)
			else: 
				# TODO: Constraint effect currently in capability_constraints. Needs to be changed  
				pass
			related_properties = get_related_properties(str(row['de']))
			for related_property in related_properties:
				# effect = generate_effect_constraint(current_capability, related_property, prop_type, relation, value)
				property = property_dictionary.get_property_occurence(related_property.iri, happening, 1)
				effect = Implies(current_capability, effect_property == property.z3_variable)
				effects.append(effect)
				
	return effects

def generate_effect_constraint(capability: BoolRef, property: BoolRef | ArithRef, prop_type: str, relation: str, value: str) -> BoolRef :	
	
	if prop_type == "http://www.hsu-ifa.de/ontologies/DINEN61360#Real":
		match relation:
			case "<":
				effect = Implies(capability, property < value)									
			case "<=":
				effect = Implies(capability, property <= value)									
			case "=":
				effect = Implies(capability, property == value)									
			case "!=":
				effect = Implies(capability, property != value)									
			case ">=":
				effect = Implies(capability, property >= value)									
			case ">":
				effect = Implies(capability, property > value)									
			case _:
				raise RuntimeError("Incorrect logical relation")
		return effect
	
	elif prop_type == "http://www.hsu-ifa.de/ontologies/DINEN61360#Boolean":
		match value: 
			case 'true':
				effect = Implies(capability, property)
			case 'false':
				effect = Implies(capability, Not(property))
			case _:
				raise RuntimeError("Incorrect value for Boolean")
		return effect