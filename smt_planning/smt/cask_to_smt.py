import json
import time
from typing import Dict, List

from smt_planning.ontology_handling.query_handlers import FileQueryHandler, SparqlEndpointQueryHandler
from z3 import Solver, Optimize, unsat, Bool, BoolRef, BoolVal, Sum, is_expr
from smt_planning.smt.StateHandler import StateHandler
from smt_planning.openmath.parse_openmath import QueryCache
from smt_planning.ontology_handling.capability_and_property_query import get_all_properties, get_provided_capabilities
from smt_planning.ontology_handling.init_query import get_init
from smt_planning.ontology_handling.capability_constraints_query import get_capability_constraints
from smt_planning.ontology_handling.geofence_query import get_geofence_constraints
from smt_planning.smt.variable_declaration import create_property_dictionary_with_occurrences, create_capability_dictionary_with_occurrences, create_resource_ids
from smt_planning.smt.capability_preconditions import capability_preconditions_smt
from smt_planning.smt.capability_effects import capability_effects_smt
from smt_planning.smt.capability_constraints import capability_constraints_smt
from smt_planning.smt.bool_variable_support import getPropositionSupports
from smt_planning.smt.constraints_bools import get_bool_constraints
from smt_planning.smt.constraints_real_variables import get_variable_constraints
from smt_planning.smt.property_links import get_property_cross_relations
from smt_planning.smt.init import init_smt
from smt_planning.smt.goal import goal_smt
from smt_planning.smt.real_variable_contin_change import get_real_variable_continuous_changes
from smt_planning.smt.robots_same_position import robot_positions_smt
from smt_planning.smt.capability_mutexes import get_capability_mutexes
from smt_planning.smt.geofence import geofence_smt
from smt_planning.smt.planning_result import PlanningResult
from smt_planning.smt.unsat_core import find_minimal_unsat_core

class CaskadePlanner:

	def with_file_query_handler(self, filename: str):
		self.query_handler = FileQueryHandler(filename)

	def with_endpoint_query_handler(self, endpoint_url):
		self.query_handler = SparqlEndpointQueryHandler(endpoint_url)

	def add_comment(self, solver: Solver, comment_text: str):
		# Adds a comment to the smt output in a pretty hackish way: 
		# Z3 doesn't allow adding comments, so we create a variable with the comment as its name and add it to the solver

		comment = Bool(f"## {comment_text} ##")
		solver.add(comment)

	def add_assertions(self, solver: Solver, named_assertions: Dict[str, BoolRef], group: str, assertions: List[BoolRef]) -> None:
		# Adds assertions to the solver and stores them under a unique name, which is needed to find an unsat core if no plan can be found
		for number, assertion in enumerate(assertions):
			# Some assertions are plain Python booleans, e.g. a comparison of two constants
			named_assertions[f"{group}_{number}"] = assertion if is_expr(assertion) else BoolVal(assertion)
			solver.add(assertion)

	def cask_to_smt(self, max_happenings: int = 5, problem_location = None, model_location = None, plan_location = None) -> PlanningResult:

		start_time = time.time()
		state_handler = StateHandler()
		state_handler.set_query_handler(self.query_handler)

		happenings = 0
		# Fixed upper bound for number of events in one happening. Currently no events, so we just have the start and end of a happening
		event_bound = 2
		solver_result = unsat

		# needs to be reset for new planning request, otherwise it will keep the old data annd not be able to solve the problem at all or solve the problem incorrectly
		QueryCache.reset()
			
		# Get all properties connected to provided capabilities as inputs or outputs as well as all instance descriptions 
		property_dictionary = get_all_properties()
		state_handler.set_property_dictionary(property_dictionary)

		# Get provided capabilities and their influence on output objects as well as resources that provide capabilities
		cap_and_res_dictionary = get_provided_capabilities()
		capability_dictionary = cap_and_res_dictionary[0]
		resource_dictionary = cap_and_res_dictionary[1]
		state_handler.set_capability_dictionary(capability_dictionary)
		state_handler.set_resource_dictionary(resource_dictionary)

		# Capability Constraints
		get_capability_constraints()

		# Get all inits and goals of planning problem based on the instance descriptions
		get_init()

		# Get geofence constraints
		geofence_dictionary = get_geofence_constraints()
		state_handler.set_geofence_dictionary(geofence_dictionary)

		# All assertions of the current number of happenings with a unique name
		named_assertions: Dict[str, BoolRef] = {}

		while (happenings <= max_happenings and solver_result == unsat):
			# SMT Solver
			solver = Solver()
			solver.reset()
			named_assertions = {}
			state_handler.reset_caches()
			solver_result = unsat
			happenings += 1

			# ------------------------------Variable Declaration------------------------------------------ 	
			# Get all properties connected to provided capabilities as inputs or outputs
			create_property_dictionary_with_occurrences(happenings, event_bound)

			# Get provided capabilities and transform to boolean SMT variables
			create_capability_dictionary_with_occurrences(happenings)

			# ------------------------------Ressource IDs---------------------------------------------------
			self.add_comment(solver, "Start of resource ids")
			resource_ids = create_resource_ids(happenings, event_bound)
			self.add_assertions(solver, named_assertions, "resource_ids", resource_ids)

			# ------------------------Constraint Proposition (H1 + H2) --> bool properties------------------
			self.add_comment(solver, "Start of constraints proposition")
			bool_constraints = get_bool_constraints(happenings, event_bound)
			self.add_assertions(solver, named_assertions, "bool_constraints", bool_constraints)

			# ---------------------Constraint Real Variable (H5) --> real properties-----------------------------
			self.add_comment(solver, "Start of constraints real variables")
			variable_constraints = get_variable_constraints(happenings, event_bound)
			self.add_assertions(solver, named_assertions, "variable_constraints", variable_constraints)

			# ----------------- Capability Precondition ------------------------------------------------------
			self.add_comment(solver, "Start of preconditions")
			preconditions = capability_preconditions_smt(happenings, event_bound)
			self.add_assertions(solver, named_assertions, "preconditions", preconditions)

			# --------------------------------------- Capability Effect ---------------------------------------
			self.add_comment(solver, "Start of effects")
			effects = capability_effects_smt(happenings, event_bound)
			self.add_assertions(solver, named_assertions, "effects", effects)

			# Capability constraints are expressions in smt2 form that cannot be added programmatically. Thus, we take the current solver in string form
			# We create a new solver object. Then we take the current solver string and add the constraint strings. We then re-import everything back into the fresh solver object
			# It has to be a fresh object because just re-importing doesn't clear everything
			self.add_comment(solver, "Start of capability constraints")
			current_solver_string = solver.to_smt2()
			number_of_assertions = len(solver.assertions())
			solver = Solver()
			constraints = capability_constraints_smt(happenings, event_bound)
			for constraint in constraints:
				current_solver_string += f"\n{constraint}"

			solver.from_string(current_solver_string)

			# The re-imported solver contains the previous assertions followed by the capability constraints
			capability_constraints = solver.assertions()[number_of_assertions:]
			if len(capability_constraints) != len(constraints):
				raise RuntimeError(f"Expected {len(constraints)} capability constraints after re-import of the solver, but found {len(capability_constraints)}.")
			for number, capability_constraint in enumerate(capability_constraints):
				named_assertions[f"capability_constraints_{number}"] = capability_constraint

			# ---------------- Constraints Capability mutexes (H14) -----------------------------------------
			self.add_comment(solver, "Start of capability mutexes")
			capability_mutexes = get_capability_mutexes(happenings)
			self.add_assertions(solver, named_assertions, "capability_mutexes", capability_mutexes)

			# ---------------- Init  --------------------------------------------------------
			self.add_comment(solver, "Start of init")
			inits = init_smt()
			self.add_assertions(solver, named_assertions, "inits", inits)

			# ---------------------- Goal ------------------------------------------------- 
			self.add_comment(solver, "Start of goal")
			goals = goal_smt()
			self.add_assertions(solver, named_assertions, "goals", goals)

			# ------------------- Proposition support (P5 + P6) ----------------------------
			self.add_comment(solver, "Start of proposition support")
			proposition_supports = getPropositionSupports(happenings, event_bound)
			self.add_assertions(solver, named_assertions, "proposition_supports", proposition_supports)

			# ----------------- Continuous change on real variables (P11) ------------------
			self.add_comment(solver, "Start of real variable continuous change")
			real_variable_cont_changes = get_real_variable_continuous_changes(happenings, event_bound)
			self.add_assertions(solver, named_assertions, "real_variable_cont_changes", real_variable_cont_changes)

			# ----------------- Cross-connection of related properties (new) -----------------
			self.add_comment(solver, "Start of related properties")
			property_cross_relations = get_property_cross_relations(happenings, event_bound)
			self.add_assertions(solver, named_assertions, "property_cross_relations", property_cross_relations)

			# ----------------- Geofence constraints (new) -----------------
			self.add_comment(solver, "Start of geofence constraints")
			geofence_constraints = geofence_smt(happenings, event_bound)
			self.add_assertions(solver, named_assertions, "geofence_constraints", geofence_constraints)

			# ----------------- Robots are not allowed to be at same position (new) -----------------
			self.add_comment(solver, "Start of robots not at same position constraints")
			robots_not_same_position_constraints = robot_positions_smt(happenings, event_bound)
			self.add_assertions(solver, named_assertions, "robots_not_same_position_constraints", robots_not_same_position_constraints)

			# Optimize by minimizing number of used capabilities to prevent unnecessary use of capabilities
			constraints = solver.assertions()
			opt = Optimize()
			opt.add(constraints)

			capabilities = [occurrence.z3_variable for capability in capability_dictionary.capabilities.values() for occurrence in capability.occurrences.values()]
			opt.minimize(Sum(capabilities))

			end_time = time.time()
			print(f"Time for generating SMT: {end_time - start_time}")	

			# Check satisfiability and get the model
			solver_result = opt.check()
			end_time_solver = time.time()
			print(f"Time for solving SMT: {end_time_solver - end_time}")

			if solver_result == unsat:
				print(f"No solution with {happenings} happening(s) found.")
			else:
				model = opt.model()
				plan = PlanningResult.from_model(model)

				if problem_location:
					# if problem_location is passed, store problem
					with open(problem_location, 'w') as file:
						file.write(solver.to_smt2())

				if model_location:
					# if model_location is passed, store model untransformed
					model_dict = {}
					for var in model:
						model_dict[str(var)] = str(model[var])
					with open(model_location, 'w') as file:
						json.dump(model_dict, file, indent=4)

				if plan_location:
					# if plan_location is passed, store model after transformation to better JSON
					with open(plan_location, 'w') as json_file:
						json.dump(plan, json_file, default=lambda o: o.as_dict(), indent=4)


				return plan

		# No plan was found. Explain why by a minimal unsat core of the problem with the highest number of happenings
		start_time_unsat_core = time.time()
		unsat_core = find_minimal_unsat_core(named_assertions)
		print(f"Time for finding minimal unsat core: {time.time() - start_time_unsat_core}")
		return PlanningResult.from_unsat_core([str(assertion) for assertion in unsat_core])
