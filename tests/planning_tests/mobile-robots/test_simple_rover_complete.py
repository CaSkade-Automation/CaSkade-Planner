import os
from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.planning_result import PlanningResultType

"""
This test checks if the planner can create a plan for the simple_rover_complete.ttl ontology file. 
This ontology file contains three capabilities (driveTo, grab and drop) of a Rover that are supposed to be executed in three happenings.
"""
class TestSimpleRoverComplete:
	
	def test_create_and_solve(self):
		ontology_file = os.path.join(os.getcwd(), "tests", "planning_tests", "mobile-robots", "simple_rover_complete.ttl")
		max_happenings = 3
		planner: CaskadePlanner = CaskadePlanner("http://www.hsu-hh.de/aut/ontologies/riva/rover-complete#RequiredCap") 
		planner.with_file_query_handler(ontology_file)
		response = planner.cask_to_smt(max_happenings, "./problem.smt", "smt_solution.json", "plan.json")
		assert response.result_type == PlanningResultType.SAT
		expected_plan = response.plan
		assert expected_plan is not None
		assert expected_plan.plan_length == 3, "Plan length should be 3"

		assert expected_plan.plan_steps[0].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/ontologies/riva/rover-complete#Rover7_capDriveTo19", "First capability should be driveTo19"
		assert expected_plan.plan_steps[1].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/ontologies/riva/rover-complete#Rover7_capGrab34", "Second capability should be grab34"
		assert expected_plan.plan_steps[2].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/ontologies/riva/rover-complete#Rover7_capDrop33", "Third capability should be drop33"

		property_longitude = "http://www.hsu-hh.de/aut/ontologies/riva/rover-complete#Rover7_longitude_DE"
		property_longitude_output = False
		property_latitude = "http://www.hsu-hh.de/aut/ontologies/riva/rover-complete#Rover7_latitude_DE"
		property_latitude_output = False

		for property in expected_plan.plan_steps[0].capability_appearances[0].outputs:
			if property_longitude == property.property.iri:
				assert property.value == 10.112242266565111, "Longitude after driveTo should be 10.112242266565111"
				property_longitude_output = True
			elif property_latitude == property.property.iri:
				assert property.value == 53.567060811833365, "Latitude after driveTo should be 53.567060811833365"
				property_latitude_output = True	

		assert property_longitude_output == True, "Longitude of rover should be output"
		assert property_latitude_output == True, "Latitude of rover should be output"

		property_grabbed = "http://www.hsu-hh.de/aut/ontologies/riva/rover-complete#Rover7_capGrab34_AssuranceProdItem_grabbed162_DE"
		property_grabbed_output = False

		for property in expected_plan.plan_steps[1].capability_appearances[0].outputs:
			if property_grabbed == property.property.iri:
				assert property.value == True, "Grabbed-Property of Item should be True"
				property_grabbed_output = True
				
		assert property_grabbed_output == True, "Grabbed-Property of Item should be output"

		property_item_latitude = "http://www.hsu-hh.de/aut/ontologies/riva/rover-complete#Rover7_capDrop33_AssuranceProdItem_latitude_DE"
		property_item_latitude_output = False
		property_item_longitude = "http://www.hsu-hh.de/aut/ontologies/riva/rover-complete#Rover7_capDrop33_AssuranceProdItem_longitude_DE"
		property_item_longitude_output = False
		property_item_grabbed = "http://www.hsu-hh.de/aut/ontologies/riva/rover-complete#Rover7_capDrop33_AssuranceProdItem_grabbed158_DE"
		property_item_grabbed_output = False
		property_latitude_drop_output = False
		property_longitude_drop_output = False

		for property in expected_plan.plan_steps[2].capability_appearances[0].outputs:
			if property_longitude == property.property.iri:
				assert property.value == 10.112298130989076, "Longitude after drop should be 10.112298130989076"
				property_longitude_drop_output = True
			elif property_item_longitude == property.property.iri:
				assert property.value == 10.112298130989076, "Longitude of item after drop should be 10.112298130989076"
				property_item_longitude_output = True
			elif property_latitude == property.property.iri:
				assert property.value == 53.56687976216757, "Latitude after drop should be 53.56687976216757"
				property_latitude_drop_output = True	
			elif property_item_latitude == property.property.iri:
				assert property.value == 53.56687976216757, "Latitude of item after drop should be 53.56687976216757"
				property_item_latitude_output = True
			elif property_item_grabbed == property.property.iri:
				assert property.value == False, "Grabbed-Property of Item after drop should be False"
				property_item_grabbed_output = True
				
		assert property_longitude_drop_output == True, "Longitude of rover should be output of drop capability"
		assert property_latitude_drop_output == True, "Latitude of rover should be output of drop capability"
		assert property_item_longitude_output == True, "Longitude of item should be output of drop capability"
		assert property_item_latitude_output == True, "Latitude of item should be output of drop capability"
		assert property_item_grabbed_output == True, "Grabbed-Property of Item should be output of drop capability"

if __name__ == '__main__':
	TestSimpleRoverComplete().test_create_and_solve()
