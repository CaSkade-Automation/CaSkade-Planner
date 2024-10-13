from typing import List

from smt_planning.smt.StateHandler import StateHandler

def get_capability_constraints():
	# Get all capability constraint IRIs and check whether its a constraint on an input or output
	# GROUP_CONCAT is used as we're only interested in the constraints and not the individual arguments as separate entries
	query_string = """
	PREFIX OM: <http://openmath.org/vocab/math#>
	PREFIX CSS: <http://www.w3id.org/hsu-aut/css#>
	PREFIX VDI3682: <http://www.w3id.org/hsu-aut/VDI3682#>
	SELECT ?cap ?constraint 
		(GROUP_CONCAT(DISTINCT ?inputArgument; SEPARATOR=",") AS ?inputArguments) 
		(GROUP_CONCAT(DISTINCT ?outputArgument; SEPARATOR=",") AS ?outputArguments)
	WHERE {
	?cap ^CSS:requiresCapability ?process;
		CSS:isRestrictedBy ?constraint.

	# Look for recursively nested arguments on any layer of an equation connected with an input
	OPTIONAL {
		?constraint (OM:arguments/rdf:rest*/rdf:first)* ?inputArgument.
		?process VDI3682:hasInput/VDI3682:isCharacterizedBy ?inputArgument.
	}

	# Look for recursively nested arguments on any layer of an equation connected with an output
	OPTIONAL {
		?constraint (OM:arguments/rdf:rest*/rdf:first)* ?outputArgument.
		?process VDI3682:hasOutput/VDI3682:isCharacterizedBy ?outputArgument.
	}
	}
	GROUP BY ?cap ?constraint
	"""
	
	stateHandler = StateHandler()
	capability_dictionary = stateHandler.get_capability_dictionary()
	query_handler = stateHandler.get_query_handler()
	results = query_handler.query(query_string)
	
	for row in results:
		# As soon as an outputArgument is present, the constraint is considered an output constraint
		if row['outputArguments']:																
			capability_dictionary.add_capability_constraint(str(row['cap']), str(row['constraint']))
		# If a row only has an inputArgument, the constraint is considered an input constraint
		if (row['inputArguments'] and not row['outputArguments']):									 
			capability_dictionary.add_capability_constraint(str(row['cap']), str(row['constraint']), True)