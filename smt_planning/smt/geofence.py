from typing import List, Tuple, Dict
from z3 import Bool, And, Or, Sum, If, BoolRef

from smt_planning.smt.StateHandler import StateHandler

def geofence_smt(happenings: int, event_bound: int) -> List[BoolRef]:

    stateHandler = StateHandler()
    gf_dict = stateHandler.get_geofence_dictionary()

    geofence_constraints = []
    robot_id = 1

    for robot in gf_dict.robots.values():
        # Define a list of vertices representing the polygon. A robot without a gozone is restricted by its geofence
        allowed_area = robot.gozone if robot.gozone.points else robot.geofence
        gozone_polygon = allowed_area.generate_polygon()
        #TODO: What to do with gozone split in multiple polygons? A vehicle can enter its other gozone only if another robot moves this robot to other gozone 
        nogozone_polygons: Dict[int, List[Tuple[float, float]]] = {}
        hole_number = 0
        for hole in robot.gozone.holes.values():
            hole_number += 1
            nogozone_polygons[hole_number] = hole.generate_polygon()


        # get z3 variables for longitude and latitude
        for happening in range(happenings):
            for layer in range(event_bound):
                z3_variable_latitude = robot.latitude.occurrences[happening][layer].z3_variable
                z3_variable_longitude = robot.longitude.occurrences[happening][layer].z3_variable

                # Create symbolic boolean variables for the edges crossed by the ray
                crossed_edges = [Bool(f'crossed_edge_{robot_id}_{i}_{happening}_{layer}') for i in range(len(gozone_polygon))]

                # Holes in gozone are not allowed 
                crossed_hole_edges = [Bool(f'crossed_edge_{robot_id}_{j}_{i}_{happening}_{layer}') for j in nogozone_polygons for i in range(len(nogozone_polygons[j]))]

                # Add constraints to check if the point is inside the polygon
                for i in range(len(gozone_polygon)):
                    p1x, p1y = gozone_polygon[i]
                    p2x, p2y = gozone_polygon[(i + 1) % len(gozone_polygon)]
                    
                    # Check if the ray crosses this edge
                    cross_condition = And(
                        z3_variable_latitude > min(p1y, p2y),                                                          # type: ignore
                        z3_variable_latitude <= max(p1y, p2y),                                                         # type: ignore
                        z3_variable_longitude <= max(p1x, p2x),                                                          # type: ignore
                        p1y != p2y,
                        Or(
                            p1x == p2x,
                            z3_variable_longitude <= (z3_variable_latitude - p1y) * (p2x - p1x) / (p2y - p1y) + p1x     # type: ignore
                        )
                    )

                    # Add constraint 
                    constraint = crossed_edges[i] == cross_condition
                    geofence_constraints.append(constraint) 

                # Check if an odd number of edges are crossed
                num_crossed_edges = Sum([If(ce, 1, 0) for ce in crossed_edges])
                inside = num_crossed_edges % 2 == 1
                geofence_constraints.append(inside)

                for j in nogozone_polygons:
                    z = 0
                    for i in range(len(nogozone_polygons[j])):
                        p1x, p1y = nogozone_polygons[j][i]
                        p2x, p2y = nogozone_polygons[j][(i + 1) % len(nogozone_polygons[j])]
                        
                        # Check if the ray crosses this edge
                        cross_condition = And(
                            z3_variable_latitude > min(p1y, p2y),                                                          # type: ignore
                            z3_variable_latitude <= max(p1y, p2y),                                                         # type: ignore
                            z3_variable_longitude <= max(p1x, p2x),                                                          # type: ignore
                            p1y != p2y,
                            Or(
                                p1x == p2x,
                                z3_variable_longitude <= (z3_variable_latitude - p1y) * (p2x - p1x) / (p2y - p1y) + p1x     # type: ignore
                            )
                        )

                        # Add constraint 
                        constraint = crossed_hole_edges[z] == cross_condition
                        geofence_constraints.append(constraint)
                        z+=1
                        
                # Check if an even number of edges are crossed --> outside the hole 
                num_crossed_hole_edges = Sum([If(ce, 1, 0) for ce in crossed_hole_edges])
                outside = num_crossed_hole_edges % 2 == 0
                geofence_constraints.append(outside)
        robot_id += 1
    return geofence_constraints
