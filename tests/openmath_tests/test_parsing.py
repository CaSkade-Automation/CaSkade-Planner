# import os
# import pytest

# from smt_planning.smt.cask_to_smt import CaskadePlanner
# from smt_planning.openmath.parse_openmath import from_open_math_in_graph
# from smt_planning.ontology_handling.query_handlers import FileQueryHandler
# from smt_planning.smt.capability_constraints import infix_to_prefix


# @pytest.fixture(scope="function", autouse=True)
# def setup():
# 	# Super hacky, we need to instantiate a CaskadePlanner even though we dont use it here
# 	# It's just done to reset the singletons
# 	cpl = CaskadePlanner("asd")
# 	print("setup")
	

# """
# asd
# """
# # @pytest.mark.usefixtures("setup")
# class TestParsing:

# 	def test_simple_equation(self):
# 		ontology_file = os.path.join(os.getcwd(), "tests", "openmath-tests", "simple_equation.ttl")
# 		query_handler = FileQueryHandler(ontology_file)
# 		equation = from_open_math_in_graph(query_handler, "http://example.org/ontology#myApplication_equals", 1, 1)
# 		expected_equation = "|http://example.org/ontology#x_1_1| = |http://example.org/ontology#y_1_1|"
# 		assert expected_equation == equation
# 		return equation
	
# 	def test_conversion_to_infix(self):
# 		infix_expression = self.test_simple_equation()
# 		prefix_expression = infix_to_prefix(infix_expression)
# 		expected_expression = ' = |http://example.org/ontology#x_1_1| |http://example.org/ontology#y_1_1|'
# 		assert prefix_expression == expected_expression


# 	def test_transport(self):
# 		ontology_file = os.path.join(os.getcwd(), "tests", "openmath-tests", "transport.ttl")
# 		query_handler = FileQueryHandler(ontology_file)
# 		equation = from_open_math_in_graph(query_handler, "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/Transport#TargetStationConstraint", 1, 1)
# 		expected_equation = "|http://www.hsu-hh.de/aut/ontologies/lab/MPS500/Transport#ProductAtTargetStation_StationID_DE_1_1| = |http://www.hsu-hh.de/aut/ontologies/lab/MPS500/Transport#TargetStation_DE_1_1|"
# 		assert expected_equation == equation


# 	def test_cylinder_supply(self):
# 		ontology_file = os.path.join(os.getcwd(), "tests", "openmath-tests", "cylinder-supply.ttl")
# 		query_handler = FileQueryHandler(ontology_file)
# 		equation = from_open_math_in_graph(query_handler, "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#ColorStackConstraint", 1, 1)
# 		expected_equation = "|http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#ProductStack1CurrentColor_DE_1_1| = |http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#RawCylinderColor_DE_1_1| or |http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#ProductStack2CurrentColor_DE_1_1| = |http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#RawCylinderColor_DE_1_1| or |http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#ProductStack3CurrentColor_DE_1_1| = |http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#RawCylinderColor_DE_1_1|"
# 		assert expected_equation == equation
