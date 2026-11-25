import os
from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.smt.planning_result import PlanningResult

"""
This test checks if the planner can create a plan for the riva_two_rover_with_gf_and_current_holder.ttl ontology file. 
This ontology file contains three capabilities (driveTo, grab and drop) of two Rover that are supposed to be executed in five happenings. Additionally, rovers have geofences, which restrict the rovers range of movement.
"""
class TestTwoRoverWithGF:
	
	def test_create_and_solve(self):
		ontology_file = os.getcwd() + "/tests/riva_two_rover_with_gf_and_current_holder.ttl"
		max_happenings = 6
		planner: CaskadePlanner = CaskadePlanner("http://www.hsu-hh.de/aut/RIVA/Logistic#required-cap-logistics") 
		planner.with_file_query_handler(ontology_file)
		expected_plan : PlanningResult = planner.cask_to_smt(max_happenings, "./problem.smt", "smt_solution.json", "plan.json") #type:ignore
		assert expected_plan.plan.plan_length == 6, "Plan length should be 6"

		assert expected_plan.plan.plan_steps[0].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover50/cap-driveTo19", "First capability should be driveTo19 from Rover 50"
		assert expected_plan.plan.plan_steps[1].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover50/cap-grab34", "Second capability should be grab34 from Rover 50"
		assert expected_plan.plan.plan_steps[2].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover50/cap-drop33", "Third capability should be drop33 from Rover 50"
		assert expected_plan.plan.plan_steps[3].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover49/cap-driveTo19", "Fourth capability should be driveTo19 from Rover 49"
		assert expected_plan.plan.plan_steps[4].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover49/cap-grab34", "Fifth capability should be grab34 from Rover 49"
		assert expected_plan.plan.plan_steps[5].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover49/cap-drop33", "Sixth capability should be drop33 from Rover 49"
		
		## Step 0 ##
		property_longitude_rover50 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover50/longitude_de"
		property_longitude_rover50_output = False
		property_latitude_rover50 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover50/latitude_de"
		property_latitude_rover50_output = False

		for property in expected_plan.plan.plan_steps[0].capability_appearances[0].outputs:
			if property_longitude_rover50 == property.property.iri:
				assert property.value == 10.110400526940438, "Longitude after driveTo from Rover 50 should be 10.110400526940438"
				property_longitude_rover50_output = True
			elif property_latitude_rover50 == property.property.iri:
				assert property.value == 53.56699992113897, "Latitude after driveTo from Rover 50 should be 53.56699992113897"
				property_latitude_rover50_output = True	

		assert property_longitude_rover50_output == True, "Longitude of rover 50 should be output"
		assert property_latitude_rover50_output == True, "Latitude of rover 50 should be output"

		## Step 1 ##

		property_grabbed_rover50 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover50/cap-grab34/AssuranceProdItem/grabbed162_de"
		property_grabbed_rover50_output = False
		property_current_holder_rover50 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover50/cap-grab34/AssuranceProdItem/currentHolder_de"
		property_current_holder_rover50_output = False

		for property in expected_plan.plan.plan_steps[1].capability_appearances[0].outputs:
			if property_grabbed_rover50 == property.property.iri:
				assert property.value == True, "Grabbed-Property of Item should be True"
				property_grabbed_rover50_output = True
			elif property_current_holder_rover50 == property.property.iri:
				assert property.value != 0, "Current holder of Item should not be 0, but an ID for Rover 50"
				property_current_holder_rover50_output = True
				
		assert property_grabbed_rover50_output == True, "Grabbed-Property of Item should be output"
		assert property_current_holder_rover50_output == True, "Current holder of Item should be output"

		## Step 2 ##

		property_item_latitude_rover50 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover50/cap-drop33/AssuranceProdItem/latitude_de"
		property_item_latitude_value = 0
		property_item_latitude_rover50_output = False
		property_item_longitude_rover50 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover50/cap-drop33/AssuranceProdItem/longitude_de"
		property_item_longitude_value = 0
		property_item_longitude_rover50_output = False
		property_item_grabbed_rover50 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover50/cap-drop33/AssuranceProdItem/grabbed158_de"
		property_item_current_holder_rover50 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover50/cap-drop33/AssuranceProdItem/currentHolder_de"
		property_item_grabbed_rover50_output = False
		property_item_current_holder_rover50_output = False
		property_latitude_drop_rover50_output = False
		property_longitude_drop_rover50_output = False

		for property in expected_plan.plan.plan_steps[2].capability_appearances[0].outputs:
			if property_longitude_rover50 == property.property.iri:
				assert property.value != 10.110400526940438, "Longitude after drop should be not equal to position of item and somewhere near Rover 49"
				property_longitude_drop_rover50_output = True
			elif property_item_longitude_rover50 == property.property.iri:
				assert property.value != 10.110400526940438, "Longitude of item after drop should be not equal to position of item and somewhere near Rover 49"
				property_item_longitude_value = property.value
				property_item_longitude_rover50_output = True
			elif property_latitude_rover50 == property.property.iri:
				assert property.value != 53.56699992113897, "Latitude after drop should be not equal to position of item and somewhere near Rover 49"
				property_latitude_drop_rover50_output = True	
			elif property_item_latitude_rover50 == property.property.iri:
				assert property.value != 53.56699992113897, "Latitude of item after drop should be not equal to position of item and somewhere near Rover 49"
				property_item_latitude_value = property.value
				property_item_latitude_rover50_output = True
			elif property_item_grabbed_rover50 == property.property.iri:
				assert property.value == False, "Grabbed-Property of Item after drop should be False"
				property_item_grabbed_rover50_output = True
			elif property_item_current_holder_rover50 == property.property.iri:
				assert property.value == 0, "Current holder of Item after drop should be 0, which stands for no holder"
				property_item_current_holder_rover50_output = True
				
		assert property_longitude_drop_rover50_output == True, "Longitude of rover should be output of drop capability"
		assert property_latitude_drop_rover50_output == True, "Latitude of rover should be output of drop capability"
		assert property_item_longitude_rover50_output == True, "Longitude of item should be output of drop capability"
		assert property_item_latitude_rover50_output == True, "Latitude of item should be output of drop capability"
		assert property_item_grabbed_rover50_output == True, "Grabbed-Property of Item should be output of drop capability"
		assert property_item_current_holder_rover50_output == True, "Current holder of Item should be output of drop capability"

		## Step 3 ##

		property_longitude_rover49 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover49/longitude_de"
		property_longitude_rover49_output = False
		property_latitude_rover49 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover49/latitude_de"
		property_latitude_rover49_output = False

		for property in expected_plan.plan.plan_steps[3].capability_appearances[0].outputs:
			if property_longitude_rover49 == property.property.iri:
				assert property.value == property_item_longitude_value, "Longitude after driveTo from Rover 49 should be last item position"
				property_longitude_rover49_output = True
			elif property_latitude_rover49 == property.property.iri:
				assert property.value == property_item_latitude_value, "Latitude after driveTo from Rover 49 should be last item position"
				property_latitude_rover49_output = True	

		assert property_longitude_rover49_output == True, "Longitude of rover 49 should be output"
		assert property_latitude_rover49_output == True, "Latitude of rover 49 should be output"

		## Step 4 ##

		property_grabbed_rover49 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover49/cap-grab34/AssuranceProdItem/grabbed162_de"
		property_grabbed_rover49_output = False
		property_current_holder_rover49 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover49/cap-grab34/AssuranceProdItem/currentHolder_de"
		property_current_holder_rover49_output = False

		for property in expected_plan.plan.plan_steps[4].capability_appearances[0].outputs:
			if property_grabbed_rover49 == property.property.iri:
				assert property.value == True, "Grabbed-Property of Item should be True"
				property_grabbed_rover49_output = True
			elif property_current_holder_rover49 == property.property.iri:
				assert property.value != 0, "Current holder of Item should not be 0, but an ID for Rover 49"
				property_current_holder_rover49_output = True
				
		assert property_grabbed_rover49_output == True, "Grabbed-Property of Item should be output"
		assert property_current_holder_rover49_output == True, "Current holder of Item should be output"

		## Step 5 ##

		property_item_latitude_rover49 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover49/cap-drop33/AssuranceProdItem/latitude_de"
		property_item_latitude_rover49_output = False
		property_item_longitude_rover49 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover49/cap-drop33/AssuranceProdItem/longitude_de"
		property_item_longitude_rover49_output = False
		property_item_grabbed_rover49 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover49/cap-drop33/AssuranceProdItem/grabbed158_de"
		property_item_current_holder_rover49 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Rover49/cap-drop33/AssuranceProdItem/currentHolder_de"
		property_item_grabbed_rover49_output = False
		property_item_current_holder_rover49_output = False
		property_latitude_drop_rover49_output = False
		property_longitude_drop_rover49_output = False

		for property in expected_plan.plan.plan_steps[5].capability_appearances[0].outputs:
			if property_longitude_rover49 == property.property.iri:
				assert property.value == 10.11109918355942, "Longitude after drop should be 10.11109918355942"
				property_longitude_drop_rover49_output = True
			elif property_item_longitude_rover49 == property.property.iri:
				assert property.value == 10.11109918355942, "Longitude of item after drop should be 10.11109918355942"
				property_item_longitude_rover49_output = True
			elif property_latitude_rover49 == property.property.iri:
				assert property.value == 53.56678943083351, "Latitude after drop should be 53.56678943083351"
				property_latitude_drop_rover49_output = True	
			elif property_item_latitude_rover49 == property.property.iri:
				assert property.value == 53.56678943083351, "Latitude of item after drop should be 53.56678943083351"
				property_item_latitude_rover49_output = True
			elif property_item_grabbed_rover49 == property.property.iri:
				assert property.value == False, "Grabbed-Property of Item after drop should be False"
				property_item_grabbed_rover49_output = True
			elif property_item_current_holder_rover49 == property.property.iri:
				assert property.value == 0, "Current holder of Item after drop should be 0, which stands for no holder"
				property_item_current_holder_rover49_output = True
				
		assert property_longitude_drop_rover49_output == True, "Longitude of rover should be output of drop capability"
		assert property_latitude_drop_rover49_output == True, "Latitude of rover should be output of drop capability"
		assert property_item_longitude_rover49_output == True, "Longitude of item should be output of drop capability"
		assert property_item_latitude_rover49_output == True, "Latitude of item should be output of drop capability"
		assert property_item_grabbed_rover49_output == True, "Grabbed-Property of Item should be output of drop capability"
		assert property_item_current_holder_rover49_output == True, "Current holder of Item should be output of drop capability"

