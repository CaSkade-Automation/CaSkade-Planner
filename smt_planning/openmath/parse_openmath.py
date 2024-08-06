from rdflib import Variable
from rdflib.term import Identifier
from typing import List, Dict, Mapping, Callable, MutableSequence
from rdflib import URIRef
from collections import defaultdict
from smt_planning.smt.StateHandler import StateHandler
from smt_planning.openmath.math_symbol_information import MathSymbolInformation
from smt_planning.openmath.operator_dictionary import OperatorDictionary
from smt_planning.openmath.application import Application

# Define some helper Variables to get binding values
APPLICATION = Variable("application")
ARG = Variable("arg")
ARGNAME = Variable("argName")
ARGTYPE = Variable("argType")
ARGVALUE = Variable("argValue")
CONTEXT = Variable("context")
OPERATOR = Variable("operator")
POSITION = Variable("position")

def from_open_math_in_graph( query_handler, rootApplicationIri: str, happening: int, event: int) -> str:
	# Converts OpenMath contained in a Graph into a textual, human-readable formula

	# Query to get OpenMath applications with operators and variables. Works also for nested applications. Positions stores arguments position, 
	# so that, e.g.,  "x / y" and "y / x" can be distinguished. Protect this query at all cost...
	# Note: We take the Data Element as ?argName instead of the actual arguments property OM:name. This is because we use DE IRIs as SMT variable names
	queryString = """
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
	PREFIX OM: <http://openmath.org/vocab/math#>
	PREFIX ont: <http://example.org/ontology#>
	PREFIX CSS: <http://www.w3id.org/hsu-aut/css#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	PREFIX DINEN61360: <http://www.w3id.org/hsu-aut/DINEN61360#>
	PREFIX CaSk: <http://www.w3id.org/hsu-aut/cask#>
	SELECT ?application (count(?argumentList)-1 as ?position) ?operator (COALESCE(?argDE, ?arg) AS ?argName) ?argType ?arg WHERE {
		#?application a OM:Application, CSS:CapabilityConstraint.
		?application OM:arguments/rdf:rest* ?argumentList;
										OM:operator ?operator.

		?argumentList rdf:rest*/rdf:first ?arg.
		?arg a ?argType.
		?argType rdfs:subClassOf OM:Object.
		# FILTER(STRSTARTS(STR(?argType), "http://openmath.org"))
		OPTIONAL {
			#?arg OM:name ?argName.
			?argDE DINEN61360:has_Instance_Description ?arg.
		}
	}
	GROUP BY ?application ?argDE ?operator ?argType ?arg
	"""
	
	# Fire query and get results as an array
	queryResults = QueryCache.query(query_handler, queryString)
	
	# Get root application to start the whole recursive parsing procedure
	rootApplication = get_root_application(queryResults.bindings, rootApplicationIri)
	string = get_arguments_of_application(rootApplication, queryResults.bindings, happening, event)
	
	return string


def create_expression(operator:MathSymbolInformation, argumentExpression: list[str] | str, happening: int, event: int, pad: bool):
	# Creates a string expression for a given operator and arguments. Handles unary and binary functions 
	arity = operator.arity
	operatorSymbol = f" {operator.symbol} "
	expression = ""
	if (arity == 1):
		# Unary operators are constructed like <operator>(argument), e.g., sin(x)
		expression = f"{operatorSymbol}({argumentExpression})"
	if (arity == 2):
		# Binary operators are constructed by concatenating operator and arguments, e.g. x + y + z...
		if pad:
			property_dictionary = StateHandler().get_property_dictionary()
			padded_expression = []
			for elem in argumentExpression:
				relation_type = property_dictionary.get_property_relation_type(elem)
				if relation_type == "Input":
					padded_expression.append(f"|{elem}_{happening}_0|")
				else:
					padded_expression.append(f"|{elem}_{happening}_1|")
		else: 
			padded_expression = [f"{elem}" for elem in argumentExpression]
		expression = operatorSymbol.join(padded_expression)

	return expression


def matches_Iri_and_has_no_higher_parent(bindings: MutableSequence[Mapping[Variable, Identifier]], rootApplicationIri: str):
	for binding in bindings:
		matchesRootApplicationIri = str(binding.get(APPLICATION)) == (rootApplicationIri)
		hasNoHigherParent = not any(b.get(ARG) == binding.get(APPLICATION) for b in bindings)
		if (matchesRootApplicationIri and hasNoHigherParent): 
			yield binding


def group_by(bindings: List[Mapping[Variable, Identifier]], key_fn) -> Mapping[str, List[Mapping[str, Identifier]]]:
    grouped = defaultdict(list)
    for binding in bindings:
        key = key_fn(binding)
        grouped[key].append(binding)
    return grouped


def convert_bindings_to_applications(bindings: List[Mapping[Variable, Identifier]]) -> List[Application]:
    if len(bindings) == 0:
        return []

    # Gruppiere die Bindungen nach der 'application'-Variable
    grouped_bindings = group_by(bindings, lambda binding: str(binding.get(APPLICATION)))

    # Erzeuge Application-Objekte aus den Gruppierungen
    applications = []
    for group_key, group in grouped_bindings.items():
        first_entry = group[0]
        args = [entry.get(ARG) for entry in group]

        application = Application(
            first_entry.get(CONTEXT),
            first_entry.get(APPLICATION),
            first_entry.get(POSITION),
            first_entry.get(OPERATOR),
            first_entry.get(ARGNAME),
            first_entry.get(ARGVALUE)
        )
        application.args = args
        applications.append(application)

    return applications

def get_root_application(bindings: MutableSequence[Mapping[Variable, Identifier]], root_application_iri: str)-> Application:
	# Finds the root application element by searching for rootApplicationIri and making sure it is in fact a root application element.

	# In all bindings, filter for those that don't have superordinate parents and match the given root_application_iri
	rootCandidates = list(matches_Iri_and_has_no_higher_parent(bindings, root_application_iri))

	# We can then still have multiple rows within the bindings if the root application is a binary relation (e.g. for "y=x+z" and x=y).
	# If there are no sub applications, any line can be returend. If there is a sub application, this one must be returned
	# ARGTYPE = Variable("argType")
	# isApplication: Callable[[Mapping[Variable, Identifier]], bool] = lambda binding: str(binding.get(ARGTYPE)) == "http://openmath.org/vocab/math#Application"
	# rootBindings = list(filter(isApplication, rootCandidates))

	rootApplications = convert_bindings_to_applications(rootCandidates)

	if len(rootApplications) == 0:
		raise Exception("No root application found. This usually points to an error in the way capability constraints are modeled")

	return rootApplications[0]

def get_arguments_of_application(parent_application: Application, bindings: MutableSequence[Mapping[Variable, Identifier]], happening: int, event: int)-> str:
	# Check if there are more entries with arguments under the current element's application. This is the case for non-nested terms like x+y+z...
	filterSameApplications: Callable[[Mapping[Variable, Identifier]], bool] = lambda binding :binding.get(APPLICATION) == parent_application.application
	argumentEntries = list(filter(filterSameApplications, bindings))
	
	# Check if the entry has children. If it has, we need to recursively go deeper
	child_bindings = []
    
    # Durchlaufe alle Argumente des Parent Application
	for parent_arg in parent_application.args:
		# Finde alle Bindungen, die auf das aktuelle Parent Argument verweisen
		child_binding = list(filter(lambda binding: binding.get(APPLICATION) == parent_arg, bindings))
		child_bindings.extend(child_binding)
	
	child_applications = convert_bindings_to_applications(child_bindings)

	if (len(child_applications) > 0):
		openMathOperator = str(argumentEntries[0].get(OPERATOR))
		operator = OperatorDictionary.getSmtSymbol(openMathOperator)
		argumentNames = list()
		for entry in argumentEntries:
			argType = str(entry.get(ARGTYPE))
			if argType == 'http://openmath.org/vocab/math#Variable':
				argumentNames.append(str(entry.get(ARGNAME)))
			elif argType == 'http://openmath.org/vocab/math#Literal':
				argumentNames.append(str(entry.get(ARGVALUE)))
		
		argumentsOfChildApplications = list()
		for childApp in child_applications:
			argumentsFormula = get_arguments_of_application(childApp, bindings, happening, event)
			argumentsOfChildApplications.append(argumentsFormula)
		
		string = create_expression(operator, [*argumentNames, *argumentsOfChildApplications], happening, event, False)
	else:
		allSameOperator = all(entry.get(OPERATOR) == argumentEntries[0].get(OPERATOR) for entry in argumentEntries)
		
		if (not allSameOperator):
			getOperatorNames = lambda binding: str(binding.get(OPERATOR))
			operators = list(map(getOperatorNames, argumentEntries))
			raise Exception(f"Error trying to obtain the operator of application. Multiple operators found: {str(operators)}")

		openMathOperator = str(argumentEntries[0].get(OPERATOR))
		operator = OperatorDictionary.getSmtSymbol(openMathOperator)
		
		getArgNames: Callable[[Mapping[Variable, Identifier]], str] = lambda binding: str(binding.get(ARGNAME))
		argumentNames = list(map(getArgNames, argumentEntries))
		
		string = create_expression(operator, argumentNames, happening, event, True)
	
	return string




class QueryCache:
	query_result = None

	@staticmethod
	def query(query_handler, query_string: str):
		if(QueryCache.query_result is None):
			QueryCache.query_result = query_handler.query(query_string)		

		return QueryCache.query_result
	
	@staticmethod
	def reset():
		QueryCache.query_result = None