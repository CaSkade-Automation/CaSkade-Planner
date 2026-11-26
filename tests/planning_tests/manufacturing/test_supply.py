import os
import tempfile
from tests.planning_tests.manufacturing.helper_function import combine_ontologies_to_temp_file
from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.planning_result import PlanningResultType

"""
This test checks if the planner can create a plan for supplying a product with MPS500. 
This ontology file contains one capability (supply) of the supplier module from MPS500 that is supposed to be executed in one happening.
"""
class TestSupply:

	def test_create_and_solve(self):
		ontology_files = [ 
			os.path.join(os.getcwd(), "capabilities", "manufacturing", "mps500", "RawCylinderSupply_Module", "RawCylinderSupplyModule.ttl"),
			os.path.join(os.getcwd(), "capabilities", "manufacturing", "mps500", "tests", "required-capabilities", "supplyOnly.ttl"), 
			os.path.join(os.getcwd(), "capabilities", "manufacturing", "mps500", "MPS500-PropertyTypes.ttl"),
		]
		
		with tempfile.NamedTemporaryFile(suffix='.ttl', delete=False) as temp_file:
			temp_path = temp_file.name
		
		try:
			combine_ontologies_to_temp_file(ontology_files, temp_path)

			max_happenings = 1
			planner: CaskadePlanner = CaskadePlanner("http://www.hsu-hh.de/aut/ontologies/lab/MPS500/required/SupplyOnly#SupplyOnly") 
			planner.with_file_query_handler(temp_path)
			result = planner.cask_to_smt(max_happenings, "./problem.smt", "smt_solution.json", "plan.json")
			expected_plan = result.plan
			assert (result.result_type is PlanningResultType.SAT) and (expected_plan is not None)
			assert expected_plan.plan_length == 1, "Plan length should be 1"

			assert expected_plan.plan_steps[0].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#SupplyRawCylinder", "First capability should be SupplyRawCylinder"

			property_stationId = "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#RawCylinder_StationID_DE"
			property_stationId_output = False
			property_color = "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#RawCylinderColor_DE"
			property_color_output = False
			property_outer_diameter = "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#RawCylinderOuterDiameter_DE"
			property_outer_diameter_output = False

			for property in expected_plan.plan_steps[0].capability_appearances[0].outputs:
				if property_stationId == property.property.iri:
					assert property.value == 2, "Station ID after supply should be 2"
					property_stationId_output = True
				if property_color == property.property.iri:
					assert property.value == 1, "Color after supply should be 1"
					property_color_output = True
				if property_outer_diameter == property.property.iri:
					assert property.value == 40, "Outer diameter after supply should be 40"
					property_outer_diameter_output = True

			assert property_stationId_output == True, "Station ID of product should be output"
			assert property_color_output == True, "Color of product should be output"
			assert property_outer_diameter_output == True, "Outer diameter of product should be output"
		finally:
			# Clean up the temporary file
			if os.path.exists(temp_path):
				os.remove(temp_path)

if __name__ == '__main__':
	TestSupply().test_create_and_solve()