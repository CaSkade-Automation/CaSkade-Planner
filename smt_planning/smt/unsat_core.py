from typing import Dict, List

from z3 import BoolRef, Solver, unsat


def is_unsatisfiable(assertions: List[BoolRef]) -> bool:
	solver = Solver()
	solver.add(assertions)
	return solver.check() == unsat


def minimize_unsat_core(unsat_core: List[BoolRef]) -> List[BoolRef]:
	# Removes assertions one by one and keeps only those that are needed for unsatisfiability.
	# The result is minimal: Removing any of its assertions makes the remaining ones satisfiable
	minimal_core = list(unsat_core)
	index = 0
	while index < len(minimal_core):
		core_without_assertion = minimal_core[:index] + minimal_core[index + 1:]
		if is_unsatisfiable(core_without_assertion):
			minimal_core = core_without_assertion
		else:
			index += 1
	return minimal_core


def find_minimal_unsat_core(named_assertions: Dict[str, BoolRef]) -> List[BoolRef]:
	# Returns a minimal set of the given assertions that cannot be satisfied together. Returns an empty list if all assertions can be satisfied
	solver = Solver()
	solver.set(unsat_core=True)
	for name, assertion in named_assertions.items():
		solver.assert_and_track(assertion, name)

	if solver.check() != unsat:
		return []

	unsat_core = [named_assertions[str(name)] for name in solver.unsat_core()]
	return minimize_unsat_core(unsat_core)
