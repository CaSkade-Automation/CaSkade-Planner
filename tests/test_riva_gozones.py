import os
from typing import List

import pytest

from smt_planning.smt.cask_to_smt import CaskadePlanner
from smt_planning.smt.planning_result import PlanningResultType

"""
These tests check if the planner correctly plans missions for robots that are restricted by a gozone.
A gozone is the area a robot is allowed to move in. It can have holes and it can be split into separate areas.
"""

ONTOLOGY_FOLDER = os.path.join(os.getcwd(), "tests", "gozone_ontologies")
CAPABILITY_NAMESPACE = "http://www.hsu-hh.de/aut/RIVA/Logistic#"
MAX_HAPPENINGS = 6

ROVER_PLAN = [["Rover49/cap-driveTo19"], ["Rover49/cap-grab34"], ["Rover49/cap-drop33"]]
DRONE_PLAN = [["Drone52/cap-flyTo2"], ["Drone52/cap-grab31"], ["Drone52/cap-drop32"]]
# The rover delivers first. It then has to leave its position, because two robots are not allowed to be at the same position
ROVER_AND_DRONE_PLAN = [
	["Rover49/cap-driveTo19"],
	["Rover49/cap-grab34"],
	["Rover49/cap-drop33"],
	["Drone52/cap-flyTo2", "Rover49/cap-driveTo19"],
	["Drone52/cap-grab31"],
	["Drone52/cap-drop32"],
]


def plan(ontology_file: str):
	planner: CaskadePlanner = CaskadePlanner("http://www.hsu-hh.de/aut/RIVA/Logistic#required-cap-logistics")
	planner.with_file_query_handler(os.path.join(ONTOLOGY_FOLDER, ontology_file))
	return planner.cask_to_smt(MAX_HAPPENINGS)


class TestGozones:

	"""
	Every ontology file contains a mission that can be solved inside the gozone(s) of the robot(s).
	The file riva_one_drone_with_gz_and_two_holes.ttl contains a rover and not a drone.
	"""
	@pytest.mark.parametrize("ontology_file, expected_steps", [
		("riva_one_rover_just_gf.ttl", ROVER_PLAN),
		("riva_one_rover_with_gz_hole.ttl", ROVER_PLAN),
		("riva_one_drone_just_gf.ttl", DRONE_PLAN),
		("riva_one_drone_with_gz_and_two_holes.ttl", ROVER_PLAN),
		("riva_one_rover_one_drone_just_gf.ttl", ROVER_AND_DRONE_PLAN),
		("riva_one_rover_one_drone_with_gz_holes.ttl", ROVER_AND_DRONE_PLAN),
	])
	def test_mission_inside_gozone_is_solved(self, ontology_file: str, expected_steps: List[List[str]]):
		result = plan(ontology_file)
		assert result.result_type is PlanningResultType.SAT, "A plan should be found"
		assert result.plan.plan_length == len(expected_steps), f"Plan length should be {len(expected_steps)}"

		for step_number, expected_capabilities in enumerate(expected_steps):
			capabilities = sorted(appearance.capability_iri for appearance in result.plan.plan_steps[step_number].capability_appearances)
			expected_iris = sorted(CAPABILITY_NAMESPACE + capability for capability in expected_capabilities)
			assert capabilities == expected_iris, f"Step {step_number} should consist of {expected_capabilities}"

	"""
	The gozone is split into separate areas and the mission cannot be solved inside the area the robot is in. No plan can be found.
	"""
	@pytest.mark.parametrize("ontology_file", [
		"riva_one_rover_with_gz_split_fail.ttl",
		"riva_one_drone_with_gz_split_fail.ttl",
	])
	def test_mission_across_split_gozone_is_not_solved(self, ontology_file: str):
		result = plan(ontology_file)
		assert result.result_type is PlanningResultType.UNSAT, "No plan should be found"
		assert result.plan is None, "There should be no plan"
