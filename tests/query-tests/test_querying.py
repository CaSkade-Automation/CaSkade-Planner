import os
import pytest

from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.openmath.parse_openmath import from_open_math_in_graph
from smt_planning.smt.StateHandler import StateHandler 
from smt_planning.ontology_handling.query_handlers import FileQueryHandler
from smt_planning.ontology_handling.capability_and_property_query import get_all_properties
from smt_planning.smt.property_links import get_related_properties, set_required_capability

class TestQuerying:

	def test_property_query(self):
		ontology_file = os.path.join(os.getcwd(), "tests", "planning_tests", "mobile-robots", "simple_rover_complete.ttl")
		required_cap_iri = "http://www.hsu-hh.de/aut/ontologies/riva/rover-complete#RequiredCap"
		s = StateHandler()
		s.set_query_handler(FileQueryHandler(ontology_file))
		property_dictionary = get_all_properties(required_cap_iri)
		
		assert len(property_dictionary.provided_properties) + len(property_dictionary.required_properties) == 24

if __name__ == '__main__':
	TestQuerying().test_property_query()