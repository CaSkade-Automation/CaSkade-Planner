from z3 import Not

from smt_planning.smt.StateHandler import StateHandler
from smt_planning.dicts.PropertyDictionary import PropertyDictionary

def get_init(query_handler):
	
	'''
	Get initial state properties by checking the values of all Actual_Value instances
	'''
	query_string = """
		PREFIX DINEN61360: <http://www.hsu-ifa.de/ontologies/DINEN61360#>
		PREFIX CSS: <http://www.w3id.org/hsu-aut/css#>
		PREFIX CaSk: <http://www.w3id.org/hsu-aut/cask#>
		PREFIX VDI3682: <http://www.w3id.org/hsu-aut/VDI3682#>
		SELECT DISTINCT ?de ?log ?val WHERE { 
			?de a DINEN61360:Data_Element.
			?de DINEN61360:has_Instance_Description ?id.
			?id DINEN61360:Expression_Goal "Actual_Value";
				DINEN61360:Logic_Interpretation ?log;
				DINEN61360:Value ?val. 
			?de DINEN61360:has_Instance_Description ?id2. 
			?cap a ?capType; 
				^CSS:requiresCapability ?process.
			values ?capType { CaSk:ProvidedCapability CaSk:RequiredCapability }.	
			?process ?relation ?inout.
			VALUES ?relation {VDI3682:hasInput VDI3682:hasOutput}.
			?inout VDI3682:isCharacterizedBy ?id2.
		} """

	# Inits 
	results = query_handler.query(query_string)
	property_dictionary = StateHandler().get_property_dictionary()
	inits = []
	for row in results:
		property = property_dictionary.get_property_occurence(str(row['de']), 0, 0).z3_variable					
		relation = str(row['log'])															
		value = str(row['val'])														    
		
		prop_type = property_dictionary.get_property_data_type(str(row['de'])) 
		if prop_type == "http://www.hsu-ifa.de/ontologies/DINEN61360#Real":

			match relation:
				case "<":
					init = property < value
				case "<=":
					init = property <= value
				case "=":
					init = property == value
				case "!=":
					init = property != value
				case ">=":
					init = property >= value
				case ">":
					init = property > value
				case _:
					raise RuntimeError("Incorrent logical relation")
			inits.append(init)

		elif prop_type == "http://www.hsu-ifa.de/ontologies/DINEN61360#Boolean":
			match value: 
				case 'true':
					init = property
				case 'false':
					init = Not(property)
				case _:
					raise RuntimeError("Incorrect value for Boolean")
				
			inits.append(init)
	
	return inits