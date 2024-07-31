import os
from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.smt.planning_result import PlanningResult

"""
This test checks if the planner can create a plan for the ex_two_caps.ttl ontology file. 
This ontology file contains two capabilities (driveTo and grab) of a Rover that are supposed to be executed in two happenings.
"""
class TestTwoCaps:
	
	def test_create_and_solve(self):
		ontology_file = os.getcwd() + "\\tests\\ex_two_caps.ttl"
		max_happenings = 2
		planner: CaskadePlanner = CaskadePlanner("http://www.hsu-hh.de/aut/RIVA/Logistic#Required-cap-Transport") 
		planner.with_file_query_handler(ontology_file)
		expected_plan : PlanningResult = planner.cask_to_smt(max_happenings, "./problem.smt", "smt_solution.json", "plan.json") #type:ignore
		assert expected_plan.plan.plan_length == 2, "Plan length should be 2"
		
		assert expected_plan.plan.plan_steps[0].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/cap-driveTo19", "First capability should be driveTo19"
		assert expected_plan.plan.plan_steps[1].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/cap-grab34", "Second capability should be grab34"
		
		property_longitude = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/longitude_de"
		property_longitude_output = False
		property_latitude = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/latitude_de"
		property_latitude_output = False

		for property in expected_plan.plan.plan_steps[0].capability_appearances[0].outputs:
			if property_longitude == property.property.iri:
				assert property.value == 10.11041, "Longitude after driveTo should be 10.11041"
				property_longitude_output = True
			elif property_latitude == property.property.iri:
				assert property.value == 53.56687, "Latitude after driveTo should be 53.56687"
				property_latitude_output = True	

		assert property_longitude_output == True, "Longitude of rover should be output"
		assert property_latitude_output == True, "Latitude of rover should be output"

		property_grabbed = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/cap-grab34/AssuranceProdItem/grabbed162_de"
		property_grabbed_output = False

		for property in expected_plan.plan.plan_steps[1].capability_appearances[0].outputs:
			if property_grabbed == property.property.iri:
				assert property.value == True
				property_grabbed_output = True
				
		assert property_grabbed_output == True, "Grabbed-Property of Item should be output"

if __name__ == '__main__':
	TestTwoCaps().test_create_and_solve()