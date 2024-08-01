from typing import List, Tuple

from smt_planning.smt.StateHandler import StateHandler
from smt_planning.dicts.PropertyDictionary import PropertyDictionary, CapabilityType
from smt_planning.dicts.CapabilityDictionary import CapabilityDictionary, CapabilityPropertyInfluence, PropertyChange
from smt_planning.dicts.ResourceDictionary import ResourceDictionary

def get_all_properties(required_cap_iri: str) -> PropertyDictionary:
	
	# Names need to be a combination of the thing that has a property (ID) with the corresponding type description. 
	# Thing and type description together define a certain property in a context.
	# And we need to get properties that belong to the capabilitiy inputs / outputs themselves as well as to resources, hence the UNION.
	# 
	query_string = """
	PREFIX DINEN61360: <http://www.w3id.org/hsu-aut/DINEN61360#>
	PREFIX CSS: <http://www.w3id.org/hsu-aut/css#>
	PREFIX CaSk: <http://www.w3id.org/hsu-aut/cask#>
	PREFIX VDI3682: <http://www.w3id.org/hsu-aut/VDI3682#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	SELECT ?de (GROUP_CONCAT(?cap; SEPARATOR=",") AS ?caps) ?capType ?dataType ?relationType ?expr_goal ?log ?val WHERE {
		{
			# this part gets all the data elements of resources (that must provide a cap)
			?resource CSS:providesCapability ?cap.
			BIND(CaSk:ProvidedCapability as ?capType).
			?cap a ?capType.
			?resource DINEN61360:has_Data_Element ?de.
		}
		UNION 
		{
			# this part gets all properties that are directly connected to a process / capability
			?process ?relation ?inout.
		}
		# All caps must have a type, that can either be provided or required (but if required, filter for the one we're plannning for)
		?cap a ?capType;
			^CSS:requiresCapability ?process.
		values ?capType {
			CaSk:ProvidedCapability CaSk:RequiredCapability 
		}.
		VALUES ?relation {
				VDI3682:hasInput VDI3682:hasOutput
		}.
		BIND(STRAFTER(STR(?relation), "has") AS ?relationType)
		?inout VDI3682:isCharacterizedBy ?id.
		# Filter to get only provided caps AND the one required that we are planning for
		FILTER(?capType = CaSk:ProvidedCapability || ?cap = <{required_cap_iri}>)
		# All DE need ID with datatype, exp goal (optional), log (optional), value (optional)
		?de DINEN61360:has_Instance_Description ?id.
		?id a ?dataType.
		?dataType rdfs:subClassOf DINEN61360:Simple_Data_Type.
		FILTER(?dataType != DINEN61360:Simple_Data_Type) # Only get the real subclasses, not Simple_D_T itself
		OPTIONAL {
			?id DINEN61360:Expression_Goal ?expr_goal.
		}
		OPTIONAL {
			?id DINEN61360:Logic_Interpretation ?log .
		}
		OPTIONAL {
			?id DINEN61360:Value ?val.
		}  
	} GROUP BY ?de ?capType ?dataType ?relationType ?expr_goal ?log ?val
	"""
	query_string = query_string.replace('{required_cap_iri}', required_cap_iri)
	query_handler = StateHandler().get_query_handler()
	results = query_handler.query(query_string)
	
	properties = PropertyDictionary()

	for row in results:
		caps = set(row['caps'].split(","))
		
		if str(row['capType']) == "http://www.w3id.org/hsu-aut/cask#RequiredCapability":
			# directly with occurrence because properties of required capabilities only have one occurrence
			properties.add_required_property_occurence(str(row['de']), str(row['dataType']), str(row['relationType']), caps)  
			for cap in caps: 
				properties.add_instance_description(str(row['de']), cap, CapabilityType.RequiredCapability, str(row['expr_goal']), str(row['log']), str(row['val']))
			continue

		properties.add_provided_property(str(row['de']), str(row['dataType']), str(row['relationType']), caps)  
		for cap in caps: 
			properties.add_instance_description(str(row['de']), cap, CapabilityType.ProvidedCapability, str(row['expr_goal']), str(row['log']), str(row['val'])) 
	return properties

def get_provided_capabilities() -> Tuple[CapabilityDictionary, ResourceDictionary]:
	query_string = """
	PREFIX DINEN61360: <http://www.w3id.org/hsu-aut/DINEN61360#>
	PREFIX CSS: <http://www.w3id.org/hsu-aut/css#>
	PREFIX CaSk: <http://www.w3id.org/hsu-aut/cask#>
	PREFIX VDI3682: <http://www.w3id.org/hsu-aut/VDI3682#>
	SELECT DISTINCT ?cap ?de ?res WHERE { 
		?cap a CaSk:ProvidedCapability;
			^CSS:requiresCapability ?process.
		?process VDI3682:hasInput ?input.
		?input VDI3682:isCharacterizedBy ?id.
		?de DINEN61360:has_Instance_Description ?id.
		?res CSS:providesCapability ?cap.
	}
	"""
	query_handler = StateHandler().get_query_handler()
	results = query_handler.query(query_string)
	
	property_dictionary = StateHandler().get_property_dictionary()
	capability_dictionary = CapabilityDictionary()

	caps = set([str(row['cap']) for row in results])
	for cap in caps:
		# Input properties can be retrieved from query
		inputs = [str(row['de']) for row in results if (str(row['cap']) == cap)]
		input_properties = [property_dictionary.get_provided_property(input) for input in inputs]
		# Outputs need to have their effect attached and are more tricky
		outputs = get_output_influences_of_capability(cap)
		capability_dictionary.add_capability(cap, "http://www.w3id.org/hsu-aut/cask#ProvidedCapability", input_properties, outputs)

	resource_dictionary = ResourceDictionary()

	resources = set([str(row['res']) for row in results])
	for resource in resources:
		caps = set([str(row['cap']) for row in results if (str(row['res']) == resource)])
		resource_caps = [capability_dictionary.get_capability(cap) for cap in caps]
		resource_dictionary.add_resource(resource, resource_caps)

	return capability_dictionary, resource_dictionary

# TODO one query for both ... 
def get_output_influences_of_capability(capability_iri: str) -> List[CapabilityPropertyInfluence] :
	query_string = """
	PREFIX DINEN61360: <http://www.w3id.org/hsu-aut/DINEN61360#>
	PREFIX CSS: <http://www.w3id.org/hsu-aut/css#>
	PREFIX CaSk: <http://www.w3id.org/hsu-aut/cask#>
	PREFIX VDI3682: <http://www.w3id.org/hsu-aut/VDI3682#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
	PREFIX OM: <http://openmath.org/vocab/math#>
	PREFIX OM-Relation1: <http://www.openmath.org/cd/relation1#>
	SELECT ?cap ?input_de ?inputStateClass ?inputExpressionGoal ?inputValue ?output_de ?outputStateClass ?outputValue ?equalConstraint ?resourceConstraint WHERE {
		BIND(<{capability_iri}> AS ?cap)
		?cap a CaSk:ProvidedCapability;
			^CSS:requiresCapability ?process.	
		?process VDI3682:hasInput ?input.
		?input a ?inputStateClass. 
		?inputStateClass rdfs:subClassOf* VDI3682:State.
		?input VDI3682:isCharacterizedBy ?input_id.
		?input_de DINEN61360:has_Instance_Description ?input_id;
			DINEN61360:has_Type_Description ?td.
		?input_id a ?dataType.
		?dataType rdfs:subClassOf DINEN61360:Simple_Data_Type.
		OPTIONAL {
			?input_id DINEN61360:Expression_Goal ?inputExpressionGoal.
		}
		OPTIONAL {
			?input_id DINEN61360:Value ?inputValue.
		}
		
		?process VDI3682:hasOutput ?output.
		?output a ?outputStateClass. 
		?outputStateClass rdfs:subClassOf* VDI3682:State.
		?output VDI3682:isCharacterizedBy ?output_id.
		?output_de DINEN61360:has_Instance_Description ?output_id;
			DINEN61360:has_Type_Description ?td.
		?output_id a ?dataType.
		OPTIONAL {
			?output_id DINEN61360:Value ?outputValue.
		}
		OPTIONAL {
			?capability CSS:isRestrictedBy ?equalConstraint.
			?equalConstraint OM:arguments/rdf:rest/rdf:first|OM:arguments/rdf:first ?input_id;
				OM:arguments/rdf:rest/rdf:first|OM:arguments/rdf:first ?output_id;
									OM:operator OM-Relation1:eq.
		}
		OPTIONAL {
			# Output is set to a resource, e.g. the holder of an item is set to the robot that grabs it
			?cap CSS:isRestrictedBy ?resourceConstraint.
			?resourceConstraint OM:arguments/rdf:rest/rdf:first|OM:arguments/rdf:first ?output_id;
				OM:arguments/rdf:rest/rdf:first|OM:arguments/rdf:first ?resource;
				OM:operator OM-Relation1:eq.
			?resource CSS:providesCapability ?anyCapability.
		}
	} """
	query_string = query_string.replace('{capability_iri}', capability_iri)
	query_handler = StateHandler().get_query_handler()
	results = query_handler.query(query_string)
	property_dictionary = StateHandler().get_property_dictionary()
	influences: List[CapabilityPropertyInfluence] = []
	for row in results: 
		# for happening in range(happenings): 
		# capDict.add_CapabilityOccurrence(str(row['cap']), "http://www.w3id.org/hsu-aut/cask#ProvidedCapability", happening, [], [])
		property_iri = str(row['output_de'])
		prop = property_dictionary.get_property(property_iri)
		if(not row.get('equalConstraint') and not row.get('outputValue') and not row.get('resourceConstraint')):
			continue
		if(row.get('resourceConstraint')):
			# Output is set to a resource by a constraint. This is a property change even if there is no constraint between input and output
			effect = PropertyChange.ChangeByExpression
		elif(row.get('equalConstraint')):
			if(not row.get('inputStateClass').eq(row.get('outputStateClass'))):
				# equalConstraint but with different product type / information in output it is a property change
				effect = PropertyChange.ChangeByExpression
			elif(row.get('inputExpressionGoal')):
				# Case of requirements or actual values. In this case, prop has a constant value and output is set to equal
				effect = PropertyChange.NoChange
			else:
				# Case of no expression goal, i.e., free parameter. In this case, prop is changed to the free parameter
				effect = PropertyChange.ChangeByExpression
		else:
			if (row.get('outputValue') and row.get('outputValue') == (row.get('inputValue'))):
				# Simple case: both input and output have the same static value
				effect = PropertyChange.NoChange
			elif (row.get('outputValue') and not row.get('outputValue') == (row.get('inputValue'))):
				if str(row.get('outputValue')).lower() == "false":
					effect = PropertyChange.SetFalse
				elif str(row.get('outputValue')).lower() == "true":
					effect = PropertyChange.SetTrue
				else:
					# Numeric change
					effect = PropertyChange.NumericConstant

		influence = CapabilityPropertyInfluence(prop, effect)
		influences.append(influence)

	return influences