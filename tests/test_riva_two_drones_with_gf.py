import os
from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.smt.planning_result import PlanningResult

"""
This test checks if the planner can create a plan for the riva_two_drone_with_gf_and_current_holder.ttl ontology file. 
This ontology file contains three capabilities (flyTo, grab and drop) of two Drones that are supposed to be executed in five happenings. Additionally, drones have geofences, which restrict the drones range of movement.
"""
class TestTwoDronesWithGF:
	
	def test_create_and_solve(self):
		ontology_file = os.getcwd() + "/tests/riva_two_drones.ttl"
		max_happenings = 6
		planner: CaskadePlanner = CaskadePlanner("http://www.hsu-hh.de/aut/RIVA/Logistic#required-cap-logistics") 
		planner.with_file_query_handler(ontology_file)
		expected_plan : PlanningResult = planner.cask_to_smt(max_happenings, "./problem.smt", "smt_solution.json", "plan.json") #type:ignore
		assert expected_plan.plan.plan_length == 6, "Plan length should be 6"

		assert expected_plan.plan.plan_steps[0].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone59/cap-flyTo2", "First capability should be flyTo2 from Drone 59"
		assert expected_plan.plan.plan_steps[1].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone59/cap-grab31", "Second capability should be grab31 from Drone 59"
		assert expected_plan.plan.plan_steps[2].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone59/cap-drop32", "Third capability should be drop32 from Drone 59"
		assert expected_plan.plan.plan_steps[3].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone52/cap-flyTo2", "Fourth capability should be flyTo2 from Drone 52"
		assert expected_plan.plan.plan_steps[4].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone52/cap-grab31", "Fifth capability should be grab31 from Drone 52"
		assert expected_plan.plan.plan_steps[5].capability_appearances[0].capability_iri == "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone52/cap-drop32", "Sixth capability should be drop32 from Drone 52"
		
		## Step 0 ##
		property_longitude_Drone59 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone59/longitude_de"
		property_longitude_Drone59_output = False
		property_latitude_Drone59 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone59/latitude_de"
		property_latitude_Drone59_output = False

		for property in expected_plan.plan.plan_steps[0].capability_appearances[0].outputs:
			if property_longitude_Drone59 == property.property.iri:
				assert property.value == 10.110400526940438, "Longitude after flyTo from Drone 59 should be 10.110400526940438"
				property_longitude_Drone59_output = True
			elif property_latitude_Drone59 == property.property.iri:
				assert property.value == 53.56699992113897, "Latitude after flyTo from Drone 59 should be 53.56699992113897"
				property_latitude_Drone59_output = True	

		assert property_longitude_Drone59_output == True, "Longitude of Drone 59 should be output"
		assert property_latitude_Drone59_output == True, "Latitude of Drone 59 should be output"

		## Step 1 ##

		property_grabbed_Drone59 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone59/cap-grab31/AssuranceProdItem/grabbed147_de"
		property_grabbed_Drone59_output = False
		property_current_holder_Drone59 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone59/cap-grab31/AssuranceProdItem/currentHolder_de"
		property_current_holder_Drone59_output = False

		for property in expected_plan.plan.plan_steps[1].capability_appearances[0].outputs:
			if property_grabbed_Drone59 == property.property.iri:
				assert property.value == True, "Grabbed-Property of Item should be True"
				property_grabbed_Drone59_output = True
			elif property_current_holder_Drone59 == property.property.iri:
				assert property.value != 0, "Current holder of Item should not be 0, but an ID for Drone 59"
				property_current_holder_Drone59_output = True
				
		assert property_grabbed_Drone59_output == True, "Grabbed-Property of Item should be output"
		assert property_current_holder_Drone59_output == True, "Current holder of Item should be output"

		## Step 2 ##

		property_item_latitude_Drone59 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone59/cap-drop32/AssuranceProdItem/latitude_de"
		property_item_latitude_value = 0
		property_item_latitude_Drone59_output = False
		property_item_longitude_Drone59 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone59/cap-drop32/AssuranceProdItem/longitude_de"
		property_item_longitude_value = 0
		property_item_longitude_Drone59_output = False
		property_item_grabbed_Drone59 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone59/cap-drop32/AssuranceProdItem/grabbed151_de"
		property_item_current_holder_Drone59 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone59/cap-drop32/AssuranceProdItem/currentHolder_de"
		property_item_grabbed_Drone59_output = False
		property_item_current_holder_Drone59_output = False
		property_latitude_drop_Drone59_output = False
		property_longitude_drop_Drone59_output = False

		for property in expected_plan.plan.plan_steps[2].capability_appearances[0].outputs:
			if property_longitude_Drone59 == property.property.iri:
				assert property.value != 10.110400526940438, "Longitude after drop should be not equal to position of item and somewhere near Drone 52"
				property_longitude_drop_Drone59_output = True
			elif property_item_longitude_Drone59 == property.property.iri:
				assert property.value != 10.110400526940438, "Longitude of item after drop should be not equal to position of item and somewhere near Drone 52"
				property_item_longitude_value = property.value
				property_item_longitude_Drone59_output = True
			elif property_latitude_Drone59 == property.property.iri:
				assert property.value != 53.56699992113897, "Latitude after drop should be not equal to position of item and somewhere near Drone 52"
				property_latitude_drop_Drone59_output = True	
			elif property_item_latitude_Drone59 == property.property.iri:
				assert property.value != 53.56699992113897, "Latitude of item after drop should be not equal to position of item and somewhere near Drone 52"
				property_item_latitude_value = property.value
				property_item_latitude_Drone59_output = True
			elif property_item_grabbed_Drone59 == property.property.iri:
				assert property.value == False, "Grabbed-Property of Item after drop should be False"
				property_item_grabbed_Drone59_output = True
			elif property_item_current_holder_Drone59 == property.property.iri:
				assert property.value == 0, "Current holder of Item after drop should be 0, which stands for no holder"
				property_item_current_holder_Drone59_output = True
				
		assert property_longitude_drop_Drone59_output == True, "Longitude of Drone should be output of drop capability"
		assert property_latitude_drop_Drone59_output == True, "Latitude of Drone should be output of drop capability"
		assert property_item_longitude_Drone59_output == True, "Longitude of item should be output of drop capability"
		assert property_item_latitude_Drone59_output == True, "Latitude of item should be output of drop capability"
		assert property_item_grabbed_Drone59_output == True, "Grabbed-Property of Item should be output of drop capability"
		assert property_item_current_holder_Drone59_output == True, "Current holder of Item should be output of drop capability"

		## Step 3 ##

		property_longitude_Drone52 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone52/longitude_de"
		property_longitude_Drone52_output = False
		property_latitude_Drone52 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone52/latitude_de"
		property_latitude_Drone52_output = False

		for property in expected_plan.plan.plan_steps[3].capability_appearances[0].outputs:
			if property_longitude_Drone52 == property.property.iri:
				assert property.value == property_item_longitude_value, "Longitude after flyTo from Drone 52 should be last item position"
				property_longitude_Drone52_output = True
			elif property_latitude_Drone52 == property.property.iri:
				assert property.value == property_item_latitude_value, "Latitude after flyTo from Drone 52 should be last item position"
				property_latitude_Drone52_output = True	

		assert property_longitude_Drone52_output == True, "Longitude of Drone 52 should be output"
		assert property_latitude_Drone52_output == True, "Latitude of Drone 52 should be output"

		## Step 4 ##

		property_grabbed_Drone52 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone52/cap-grab31/AssuranceProdItem/grabbed147_de"
		property_grabbed_Drone52_output = False
		property_current_holder_Drone52 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone52/cap-grab31/AssuranceProdItem/currentHolder_de"
		property_current_holder_Drone52_output = False

		for property in expected_plan.plan.plan_steps[4].capability_appearances[0].outputs:
			if property_grabbed_Drone52 == property.property.iri:
				assert property.value == True, "Grabbed-Property of Item should be True"
				property_grabbed_Drone52_output = True
			elif property_current_holder_Drone52 == property.property.iri:
				assert property.value != 0, "Current holder of Item should not be 0, but an ID for Drone 52"
				property_current_holder_Drone52_output = True
				
		assert property_grabbed_Drone52_output == True, "Grabbed-Property of Item should be output"
		assert property_current_holder_Drone52_output == True, "Current holder of Item should be output"

		## Step 5 ##

		property_item_latitude_Drone52 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone52/cap-drop32/AssuranceProdItem/latitude_de"
		property_item_latitude_Drone52_output = False
		property_item_longitude_Drone52 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone52/cap-drop32/AssuranceProdItem/longitude_de"
		property_item_longitude_Drone52_output = False
		property_item_grabbed_Drone52 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone52/cap-drop32/AssuranceProdItem/grabbed151_de"
		property_item_current_holder_Drone52 = "http://www.hsu-hh.de/aut/RIVA/Logistic#Drone52/cap-drop32/AssuranceProdItem/currentHolder_de"
		property_item_grabbed_Drone52_output = False
		property_item_current_holder_Drone52_output = False
		property_latitude_drop_Drone52_output = False
		property_longitude_drop_Drone52_output = False

		for property in expected_plan.plan.plan_steps[5].capability_appearances[0].outputs:
			if property_longitude_Drone52 == property.property.iri:
				assert property.value == 10.109503269195558, "Longitude after drop should be 10.109503269195558"
				property_longitude_drop_Drone52_output = True
			elif property_item_longitude_Drone52 == property.property.iri:
				assert property.value == 10.109503269195558, "Longitude of item after drop should be 10.109503269195558"
				property_item_longitude_Drone52_output = True
			elif property_latitude_Drone52 == property.property.iri:
				assert property.value == 53.56712941566084, "Latitude after drop should be 53.56712941566084"
				property_latitude_drop_Drone52_output = True	
			elif property_item_latitude_Drone52 == property.property.iri:
				assert property.value == 53.56712941566084, "Latitude of item after drop should be 53.56712941566084"
				property_item_latitude_Drone52_output = True
			elif property_item_grabbed_Drone52 == property.property.iri:
				assert property.value == False, "Grabbed-Property of Item after drop should be False"
				property_item_grabbed_Drone52_output = True
			elif property_item_current_holder_Drone52 == property.property.iri:
				assert property.value == 0, "Current holder of Item after drop should be 0, which stands for no holder"
				property_item_current_holder_Drone52_output = True
				
		assert property_longitude_drop_Drone52_output == True, "Longitude of Drone should be output of drop capability"
		assert property_latitude_drop_Drone52_output == True, "Latitude of Drone should be output of drop capability"
		assert property_item_longitude_Drone52_output == True, "Longitude of item should be output of drop capability"
		assert property_item_latitude_Drone52_output == True, "Latitude of item should be output of drop capability"
		assert property_item_grabbed_Drone52_output == True, "Grabbed-Property of Item should be output of drop capability"
		assert property_item_current_holder_Drone52_output == True, "Current holder of Item should be output of drop capability"

