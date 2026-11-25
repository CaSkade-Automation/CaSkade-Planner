import os

from z3 import Real

from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.smt.planning_result import PlanningResultType
from smt_planning.smt.unsat_core import find_minimal_unsat_core

"""
These tests check if the planner explains why no plan can be found by returning a minimal unsat core.
"""
class TestUnsatCore:

	"""
	Three of the five assertions cannot be satisfied together (x > 5, y > x and y < 3). The other two are not part of the conflict.
	"""
	def test_minimal_unsat_core_only_contains_conflicting_assertions(self):
		x, y, z = Real("x"), Real("y"), Real("z")
		named_assertions = {
			"unrelated_1": z == 1,
			"lower_bound": x > 5,
			"order": y > x,
			"unrelated_2": z < 10,
			"upper_bound": y < 3,
		}
		unsat_core = find_minimal_unsat_core(named_assertions)
		assert set(str(assertion) for assertion in unsat_core) == {"x > 5", "y > x", "y < 3"}, "Unsat core should consist of the three conflicting assertions"

	def test_satisfiable_assertions_have_no_unsat_core(self):
		x = Real("x")
		assert find_minimal_unsat_core({"lower_bound": x > 5, "upper_bound": x < 10}) == [], "There should be no unsat core"

	"""
	The gozone of the rover is split into separate areas, so that the mission cannot be solved. Without the restriction by the gozone the mission can be solved.
	Thus, the gozone has to be part of the explanation.
	"""
	def test_unsolvable_mission_returns_unsat_core_with_gozone(self):
		ontology_file = os.path.join(os.getcwd(), "tests", "gozone_ontologies", "riva_one_rover_with_gz_split_fail.ttl")
		planner: CaskadePlanner = CaskadePlanner("http://www.hsu-hh.de/aut/RIVA/Logistic#required-cap-logistics")
		planner.with_file_query_handler(ontology_file)
		result = planner.cask_to_smt(3)
		assert result.result_type is PlanningResultType.UNSAT, "No plan should be found"
		assert result.plan is None, "There should be no plan"
		assert result.unsat_core, "An unsat core should be returned"
		assert any("crossed_edge" in assertion for assertion in result.unsat_core), "The gozone should be part of the unsat core"
