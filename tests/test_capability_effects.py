import os

from smt_planning.dicts.CapabilityDictionary import PropertyChange
from smt_planning.ontology_handling.capability_and_property_query import get_all_properties, get_output_influences_of_capability
from smt_planning.ontology_handling.query_handlers import FileQueryHandler
from smt_planning.smt.StateHandler import StateHandler

"""
These tests check if the effects of a capability on its output properties are detected correctly.
"""

NAMESPACE = "http://www.hsu-hh.de/aut/RIVA/Logistic#"


def get_effects(ontology_file: str, capability: str):
	state_handler = StateHandler()
	state_handler.set_query_handler(FileQueryHandler(os.path.join(os.getcwd(), "tests", ontology_file)))
	state_handler.set_property_dictionary(get_all_properties())
	influences = get_output_influences_of_capability(NAMESPACE + capability)
	return {(influence.property.iri.removeprefix(NAMESPACE), influence.effect) for influence in influences}


class TestCapabilityEffects:

	"""
	Grab sets the current holder of the item to the rover by a constraint (current holder = Rover7). There is no constraint between input and output and the output has no value.
	"""
	def test_output_set_to_resource_is_a_change(self):
		effects = get_effects("riva_one_rover_with_gf_and_current_holder.ttl", "Rover7/cap-grab34")
		current_holder = "Rover7/cap-grab34/AssuranceProdItem/currentHolder_de"
		assert (current_holder, PropertyChange.ChangeByExpression) in effects, "Grab should change the current holder of the item"
		assert all(effect is PropertyChange.ChangeByExpression for property_iri, effect in effects if property_iri == current_holder), "Current holder should have no other effect"

	"""
	Grab does not move the item: Position of the item after grab is equal to its position before.
	"""
	def test_output_equal_to_input_is_no_change(self):
		effects = get_effects("riva_one_rover_with_gf_and_current_holder.ttl", "Rover7/cap-grab34")
		assert ("Rover7/cap-grab34/AssuranceProdItem/latitude_de", PropertyChange.NoChange) in effects, "Grab should not change the latitude of the item"
		assert ("Rover7/cap-grab34/AssuranceProdItem/longitude_de", PropertyChange.NoChange) in effects, "Grab should not change the longitude of the item"

	def test_output_with_different_value_is_a_change(self):
		effects = get_effects("riva_one_rover_with_gf_and_current_holder.ttl", "Rover7/cap-grab34")
		assert ("Rover7/cap-grab34/AssuranceProdItem/grabbed162_de", PropertyChange.SetTrue) in effects, "Grab should set the item to grabbed"
