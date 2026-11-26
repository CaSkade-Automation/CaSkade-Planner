import os
import tempfile
from tests.planning_tests.manufacturing.helper_function import combine_ontologies_to_temp_file
from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.planning_result import PlanningResultType

"""
This test checks if the planner can create a plan for drilling a hole into a product with MPS500. 
This ontology file contains one capability (drilling) of the drilling module from MPS500 that is supposed to be executed in one happening.
"""
class TestDrilling:

	def test_create_and_solve(self):
		ontology_files = [ 
			os.path.join(os.getcwd(), "capabilities", "manufacturing", "mps500", "Drilling_Module", "DrillingModule.ttl"),
			os.path.join(os.getcwd(), "capabilities", "manufacturing", "mps500", "tests", "required-capabilities", "DrillingOnly.ttl"), 
			os.path.join(os.getcwd(), "capabilities", "manufacturing", "mps500", "MPS500-PropertyTypes.ttl"),
		]
		
		with tempfile.NamedTemporaryFile(suffix='.ttl', delete=False) as temp_file:
			temp_path = temp_file.name
		
		try:
			combine_ontologies_to_temp_file(ontology_files, temp_path)

			max_happenings = 1
			planner: CaskadePlanner = CaskadePlanner("http://www.hsu-hh.de/aut/ontologies/lab/MPS500/required/Drilling#Drilling_Req") 
			planner.with_file_query_handler(temp_path)
			result = planner.cask_to_smt(max_happenings, "./problem.smt", "smt_solution.json", "plan.json")
			expected_plan = result.plan
			assert (result.result_type is PlanningResultType.SAT) and (expected_plan is not None)
			assert expected_plan.plan_length == 1, "Plan length should be 1"
			
			assert expected_plan.plan_steps[0].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/DrillingModule#DrillAndCheck", "First capability should be drillAndCheck"

			property_drilling_depth = "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/DrillingModule#DrilledProductOnCarrier_DrillingDepth_DE"
			property_drilling_depth_output = False
			property_drilling_diameter = "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/DrillingModule#DrilledProductOnCarrier_InnerDiameter_DE"
			property_drilling_diameter_output = False

			for property in expected_plan.plan_steps[0].capability_appearances[0].outputs:
				if property_drilling_depth == property.property.iri:
					assert property.value == 6, "Drilling depth after drilling should be 6"
					property_drilling_depth_output = True
				elif property_drilling_diameter == property.property.iri:
					assert property.value == 6, "Drilling diameter after drilling should be 6"
					property_drilling_diameter_output = True

			assert property_drilling_depth_output == True, "Drilling depth of product should be output"
			assert property_drilling_diameter_output == True, "Drilling diameter of product should be output"
		finally:
			# Clean up the temporary file
			if os.path.exists(temp_path):
				os.remove(temp_path)

if __name__ == '__main__':
	TestDrilling().test_create_and_solve()