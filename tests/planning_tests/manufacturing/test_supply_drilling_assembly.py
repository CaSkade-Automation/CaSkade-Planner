import os
import tempfile
from tests.planning_tests.manufacturing.helper_function import combine_ontologies_to_temp_file
from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.planning_result import PlanningResultType

"""
This test checks if the planner can create a plan for assembling a product, drilling a hole into a raw cylinder and transporting between modules with MPS500. 
This ontology file contains two capabilities (supply, drilling, transport and assembly) of the supply module, drilling module, conveyor module and assembly module from MPS500 that is supposed to be executed in five happenings.
"""
class TestSupplyDrillingAssembly:

	def test_create_and_solve(self):
		ontology_files = [ 
			os.path.join(os.getcwd(), "capabilities", "manufacturing", "mps500", "Drilling_Module", "DrillingModule.ttl"),
			os.path.join(os.getcwd(), "capabilities", "manufacturing", "mps500", "Conveyor_Module", "ConveyorTransport.ttl"),
			os.path.join(os.getcwd(), "capabilities", "manufacturing", "mps500", "RawCylinderSupply_Module", "RawCylinderSupplyModule.ttl"),
			os.path.join(os.getcwd(), "capabilities", "manufacturing", "mps500", "Assembly_Module", "AssembleCylinder.ttl"),
			os.path.join(os.getcwd(), "capabilities", "manufacturing", "mps500", "tests", "required-capabilities", "Supply_Drilling_Assembly.ttl"), 
			os.path.join(os.getcwd(), "capabilities", "manufacturing", "mps500", "MPS500-PropertyTypes.ttl"),
		]
		
		with tempfile.NamedTemporaryFile(suffix='.ttl', delete=False) as temp_file:
			temp_path = temp_file.name
		
		try:
			combine_ontologies_to_temp_file(ontology_files, temp_path)

			max_happenings = 5
			planner: CaskadePlanner = CaskadePlanner("http://www.hsu-hh.de/aut/ontologies/lab/MPS500/required/SupplyDrillingAssembly#SupplyDrillingAssembly") 
			planner.with_file_query_handler(temp_path)
			result = planner.cask_to_smt(max_happenings, "./problem.smt", "smt_solution.json", "plan.json")
			expected_plan = result.plan
			assert (result.result_type is PlanningResultType.SAT) and (expected_plan is not None)
			assert expected_plan.plan_length == 5, "Plan length should be 5"

			assert expected_plan.plan_steps[0].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#SupplyRawCylinder", "First capability should be SupplyRawCylinder"
			assert expected_plan.plan_steps[1].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/Conveyor#ConveyorTransport", "Second capability should be ConveyorTransport"
			assert expected_plan.plan_steps[2].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/DrillingModule#DrillAndCheck", "Third capability should be DrillAndCheck"
			assert expected_plan.plan_steps[3].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/Conveyor#ConveyorTransport", "Fourth capability should be ConveyorTransport"
			assert expected_plan.plan_steps[4].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/AssembleCylinder#AssembleCylinder", "Fifth capability should be AssembleCylinder"

			property_color = "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#RawCylinderColor_DE"
			property_color_output = False
			property_outer_diameter = "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/RawCylinderSupplyModule#RawCylinderOuterDiameter_DE"
			property_outer_diameter_output = False

			for property in expected_plan.plan_steps[0].capability_appearances[0].outputs:
				if property_color == property.property.iri:
					assert property.value == 1, "Color after supplying should be 1"
					property_color_output = True
				elif property_outer_diameter == property.property.iri:
					assert property.value == 40, "Outer diameter after supplying should be 40"
					property_outer_diameter_output = True

			assert property_color_output == True, "Color of product should be output"
			assert property_outer_diameter_output == True, "Outer diameter of product should be output"

			property_stationId = "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/Conveyor#ProductAtTargetStation_StationID_DE"
			property_stationId_output = False

			for property in expected_plan.plan_steps[1].capability_appearances[0].outputs:
				if property_stationId == property.property.iri:
					assert property.value == 3, "Station ID of product at target station should be 3"
					property_stationId_output = True

			assert property_stationId_output == True, "Station ID of product at target station should be output"
			
			property_drilling_depth = "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/DrillingModule#DrilledProductOnCarrier_DrillingDepth_DE"
			property_drilling_depth_output = False
			property_drilling_diameter = "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/DrillingModule#DrilledProductOnCarrier_InnerDiameter_DE"
			property_drilling_diameter_output = False

			for property in expected_plan.plan_steps[2].capability_appearances[0].outputs:
				if property_drilling_depth == property.property.iri:
					assert property.value == 5, "Drilling depth after drilling should be 5"
					property_drilling_depth_output = True
				elif property_drilling_diameter == property.property.iri:
					assert property.value == 5, "Drilling diameter after drilling should be 5"
					property_drilling_diameter_output = True

			assert property_drilling_depth_output == True, "Drilling depth of product should be output"
			assert property_drilling_diameter_output == True, "Drilling diameter of product should be output"

			property_stationId = "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/Conveyor#ProductAtTargetStation_StationID_DE"
			property_stationId_output = False

			for property in expected_plan.plan_steps[3].capability_appearances[0].outputs:
				if property_stationId == property.property.iri:
					assert property.value == 4, "Station ID of product at target station should be 4"
					property_stationId_output = True

			assert property_stationId_output == True, "Station ID of product at target station should be output"

			property_is_assembled = "http://www.hsu-hh.de/aut/ontologies/lab/MPS500/AssembleCylinder#AssembledCylinderOnCarrier_isAssembled_DE"
			property_is_assembled_output = False

			for property in expected_plan.plan_steps[4].capability_appearances[0].outputs:
				if property_is_assembled == property.property.iri:
					assert property.value == True, "Assembled status after assembly should be True"
					property_is_assembled_output = True

			assert property_is_assembled_output == True, "Assembled status of product should be output"

		finally:
			# Clean up the temporary file
			if os.path.exists(temp_path):
				os.remove(temp_path)

if __name__ == '__main__':
	TestSupplyDrillingAssembly().test_create_and_solve()