import os

from z3 import Solver, sat

from smt_planning.ontology_handling.capability_and_property_query import get_all_properties, get_provided_capabilities
from smt_planning.ontology_handling.query_handlers import FileQueryHandler
from smt_planning.ontology_handling.related_inits import find_all_related_inits
from smt_planning.openmath.parse_openmath import QueryCache
from smt_planning.smt.StateHandler import StateHandler
from smt_planning.smt.constraints_real_variables import get_variable_constraints
from smt_planning.smt.property_links import reset_property_pairs, set_required_capability
from smt_planning.smt.real_variable_contin_change import get_real_variable_continuous_changes
from smt_planning.smt.variable_declaration import create_capability_dictionary_with_occurrences, create_property_dictionary_with_occurrences

"""
These tests check if free parameters of capabilities, e.g. the target position of driveTo, are handled correctly.
A free parameter is an input without a value. Its expression goal is either "Variable" or it has no expression goal at all.
"""

NAMESPACE = "http://www.hsu-hh.de/aut/RIVA/Logistic#"
REQUIRED_CAPABILITY = NAMESPACE + "required-cap-logistics"
HAPPENINGS = 2
EVENT_BOUND = 2


class TestFreeParameters:

	"""
	A robot has to be able to drive to different targets in different happenings. Thus, frame and continuity constraints must not fix the target to one value for the whole plan.
	"""
	def test_free_parameter_can_change_between_happenings(self):
		state_handler = StateHandler()
		state_handler.set_query_handler(FileQueryHandler(os.path.join(os.getcwd(), "tests", "riva_one_rover_with_gf.ttl")))
		reset_property_pairs()
		set_required_capability(REQUIRED_CAPABILITY)
		QueryCache.reset()
		property_dictionary = get_all_properties(REQUIRED_CAPABILITY)
		state_handler.set_property_dictionary(property_dictionary)
		find_all_related_inits()
		capability_dictionary, resource_dictionary = get_provided_capabilities(REQUIRED_CAPABILITY)
		state_handler.set_capability_dictionary(capability_dictionary)
		state_handler.set_resource_dictionary(resource_dictionary)
		create_property_dictionary_with_occurrences(HAPPENINGS, EVENT_BOUND)
		create_capability_dictionary_with_occurrences(HAPPENINGS)

		solver = Solver()
		solver.add(get_variable_constraints(HAPPENINGS, EVENT_BOUND))
		solver.add(get_real_variable_continuous_changes(HAPPENINGS, EVENT_BOUND))

		target_latitude = NAMESPACE + "Rover7/cap-driveTo19/RequiredInflat/latitude71_de"
		target_in_first_happening = property_dictionary.get_provided_property_occurrence(target_latitude, 0, 0).z3_variable
		target_in_second_happening = property_dictionary.get_provided_property_occurrence(target_latitude, 1, 0).z3_variable
		solver.add(target_in_first_happening != target_in_second_happening)

		assert solver.check() == sat, "Target of driveTo should be able to differ between two happenings"
