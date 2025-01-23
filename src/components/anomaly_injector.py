import sys
import random
from src.exception import CustomException

class AnomalyInjector:
    """
    This class introduces anomalies into the traffic flow.
    """
    def __init__(self, network):
        """
        :param network: An instance of TrafficNetwork.
        """
        self.network = network
        # vehicle_id -> steps_remaining to remain stopped
        self.stopped_vehicles = {}

    def ignore_red_light(self, vehicle_id):
        """
        Forces the vehicle to move from its current intersection 
        even if the signal is red (bypassing normal checks).
        """
        try:
            # Find the vehicle's current intersection
            current_intersection = None
            for intersection, vehicles_list in self.network.vehicles.items():
                if vehicle_id in vehicles_list:
                    current_intersection = intersection
                    break

            if current_intersection is None:
                raise ValueError(f"Vehicle {vehicle_id} not found in network.")

            neighbors = self.network.network[current_intersection]
            if not neighbors:
                # If no neighbors, the vehicle stays put
                return

            # Remove it from current intersection
            self.network.vehicles[current_intersection].remove(vehicle_id)
            # Move to a random connected intersection
            next_intersection = random.choice(neighbors)
            self.network.vehicles[next_intersection].append(vehicle_id)
            print(f"[ANOMALY] Vehicle {vehicle_id} ignored red light at {current_intersection} and moved to {next_intersection}")

        except Exception as e:
            raise CustomException(e, sys)

    def unauthorized_entry(self, vehicle_id, intersection_id):
        """
        Inserts a vehicle into an intersection without following normal rules.
        """
        try:
            if intersection_id not in self.network.vehicles:
                raise ValueError(f"Intersection {intersection_id} does not exist.")

            # Remove vehicle from wherever it is (if at all)
            for inter, v_list in self.network.vehicles.items():
                if vehicle_id in v_list:
                    v_list.remove(vehicle_id)

            # Add to the new intersection
            self.network.vehicles[intersection_id].append(vehicle_id)
            print(f"[ANOMALY] Unauthorized vehicle {vehicle_id} appeared at intersection {intersection_id}")

        except Exception as e:
            raise CustomException(e, sys)

    def cause_unexpected_stop(self, vehicle_id, steps=1):
        """
        Mark a vehicle to remain stopped (not move) for a given number of simulation steps.
        """
        try:
            # Check if vehicle is in the network
            in_network = any(vehicle_id in v_list for v_list in self.network.vehicles.values())
            if not in_network:
                raise ValueError(f"Vehicle {vehicle_id} is not currently in the network.")

            self.stopped_vehicles[vehicle_id] = steps
            print(f"[ANOMALY] Vehicle {vehicle_id} is forced to stop for {steps} step(s).")

        except Exception as e:
            raise CustomException(e, sys)

    def apply_stops(self, snapshot):
        """
        Before vehicles move, remove 'stopped' vehicles from the snapshot 
        so they cannot move. Decrement their stop counters each step.
        """
        try:
            for vehicle_id, steps_remaining in list(self.stopped_vehicles.items()):
                if steps_remaining > 0:
                    # Find which intersection it's in and remove from the snapshot
                    for intersection, vehicles_list in snapshot.items():
                        if vehicle_id in vehicles_list:
                            vehicles_list.remove(vehicle_id)
                            break

                    # Decrement the stop duration
                    self.stopped_vehicles[vehicle_id] -= 1

                    # If we've reached zero, remove from dict so it can move next time
                    if self.stopped_vehicles[vehicle_id] <= 0:
                        del self.stopped_vehicles[vehicle_id]
                else:
                    # Clean up any zero or negative leftover
                    del self.stopped_vehicles[vehicle_id]

        except Exception as e:
            raise CustomException(e, sys)
