import os
from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.smt.planning_result import PlanningResult

"""
This test checks if the planner can create a plan for the riva_one_rover.ttl ontology file. 
This ontology file contains three capabilities (driveTo, grab and drop) of a Rover that are supposed to be executed in three happenings.
"""
class TestThreeCaps:
	
	def test_create_and_solve(self):
		ontology_file = os.getcwd() + "\\tests\\riva_one_rover.ttl"
		max_happenings = 3
		planner: CaskadePlanner = CaskadePlanner("http://www.hsu-hh.de/aut/RIVA/Logistic#required-cap-logistics") 
		planner.with_file_query_handler(ontology_file)
		expected_plan : PlanningResult = planner.cask_to_smt(max_happenings, "./problem.smt", "smt_solution.json", "plan.json") #type:ignore
		assert expected_plan.plan.plan_length == 3, "Plan length should be 3"

		assert expected_plan.plan.plan_steps[0].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/cap-driveTo19", "First capability should be driveTo19"
		assert expected_plan.plan.plan_steps[1].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/cap-grab34", "Second capability should be grab34"
		assert expected_plan.plan.plan_steps[2].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/cap-drop33", "Third capability should be drop33"
		
		property_longitude = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/longitude_de"
		property_longitude_output = False
		property_latitude = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/latitude_de"
		property_latitude_output = False

		for property in expected_plan.plan.plan_steps[0].capability_appearances[0].outputs:
			if property_longitude == property.property.iri:
				assert property.value == 10.112242266565111, "Longitude after driveTo should be 10.112242266565111"
				property_longitude_output = True
			elif property_latitude == property.property.iri:
				assert property.value == 53.567060811833365, "Latitude after driveTo should be 53.567060811833365"
				property_latitude_output = True	

		assert property_longitude_output == True, "Longitude of rover should be output"
		assert property_latitude_output == True, "Latitude of rover should be output"

		property_grabbed = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/cap-grab34/AssuranceProdItem/grabbed162_de"
		property_grabbed_output = False

		for property in expected_plan.plan.plan_steps[1].capability_appearances[0].outputs:
			if property_grabbed == property.property.iri:
				assert property.value == True, "Grabbed-Property of Item should be True"
				property_grabbed_output = True
				
		assert property_grabbed_output == True, "Grabbed-Property of Item should be output"

		property_item_latitude = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/cap-drop33/AssuranceProdItem/latitude_de"
		property_item_latitude_output = False
		property_item_longitude = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/cap-drop33/AssuranceProdItem/longitude_de"
		property_item_longitude_output = False
		property_item_grabbed = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover7/cap-drop33/AssuranceProdItem/grabbed158_de"
		property_item_grabbed_output = False
		property_latitude_drop_output = False
		property_longitude_drop_output = False

		for property in expected_plan.plan.plan_steps[2].capability_appearances[0].outputs:
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


