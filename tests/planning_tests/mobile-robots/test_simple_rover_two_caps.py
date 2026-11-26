import os
from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.planning_result import PlanningResultType

"""
This test checks if the planner can create a plan for the simple_rover_with_two_caps.ttl ontology file. 
This ontology file contains two capabilities (driveTo and grab) of a Rover that are supposed to be executed in two happenings.
"""
class TestSimpleRoverTwoCaps:
	
	def test_create_and_solve(self):
		ontology_file = os.path.join(os.getcwd(), "tests", "planning_tests", "mobile-robots", "simple_rover_with_two_caps.ttl")
		max_happenings = 2
		planner: CaskadePlanner = CaskadePlanner("http://www.hsu-hh.de/aut/ontologies/riva/rover-two-caps#RequiredCap") 
		planner.with_file_query_handler(ontology_file)
		result = planner.cask_to_smt(max_happenings, "./problem.smt", "smt_solution.json", "plan.json")
		expected_plan = result.plan
		assert (result.result_type is PlanningResultType.SAT) and (expected_plan is not None)
		assert expected_plan.plan_length == 2, "Plan length should be 2"
		
		assert expected_plan.plan_steps[0].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/ontologies/riva/rover-two-caps#Rover7_capDriveTo19", "First capability should be driveTo19"
		assert expected_plan.plan_steps[1].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/ontologies/riva/rover-two-caps#Rover7_capGrab34", "Second capability should be grab34"

		property_longitude = "http://www.hsu-hh.de/aut/ontologies/riva/rover-two-caps#Rover7_longitude_DE"
		property_longitude_output = False
		property_latitude = "http://www.hsu-hh.de/aut/ontologies/riva/rover-two-caps#Rover7_latitude_DE"
		property_latitude_output = False

		for property in expected_plan.plan_steps[0].capability_appearances[0].outputs:
			if property_longitude == property.property.iri:
				assert property.value == 10.11041, "Longitude after driveTo should be 10.11041"
				property_longitude_output = True
			elif property_latitude == property.property.iri:
				assert property.value == 53.56687, "Latitude after driveTo should be 53.56687"
				property_latitude_output = True	

		assert property_longitude_output == True, "Longitude of rover should be output"
		assert property_latitude_output == True, "Latitude of rover should be output"

		property_grabbed = "http://www.hsu-hh.de/aut/ontologies/riva/rover-two-caps#Rover7_capGrab34_AssuranceProdItem_grabbed162_DE"
		property_grabbed_output = False

		for property in expected_plan.plan_steps[1].capability_appearances[0].outputs:
			if property_grabbed == property.property.iri:
				assert property.value == True
				property_grabbed_output = True
				
		assert property_grabbed_output == True, "Grabbed-Property of Item should be output"

if __name__ == '__main__':
	TestSimpleRoverTwoCaps().test_create_and_solve()