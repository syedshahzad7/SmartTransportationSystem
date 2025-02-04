import sys
import random
from collections import defaultdict
from src.exception import CustomException

class TrafficNetwork:
    def __init__(self):
        """
        Manages intersections, vehicles, and signal states.
        """
        self.network = {}   
        self.vehicles = {}  
        self.signals = {}

    def add_intersection(self, intersection_id, green_duration=2, red_duration=2):
        """
        Adds an intersection with default durations for green and red signals.
        """
        try:
            if intersection_id in self.network:
                raise ValueError(f"Intersection {intersection_id} already exists.")

            self.network[intersection_id] = []
            self.vehicles[intersection_id] = []
            
            # Initialize signal config
            self.signals[intersection_id] = {
                "state": "red",
                "green_duration": green_duration,
                "red_duration": red_duration,
                "counter": red_duration  # start in red
            }

        except Exception as e:
            raise CustomException(e, sys)

    def connect_intersections(self, from_id, to_id):
        """
        Connects two intersections in both directions (undirected).
        """
        try:
            if from_id not in self.network or to_id not in self.network:
                raise ValueError("Both intersections must exist in the network.")
            self.network[from_id].append(to_id)
            self.network[to_id].append(from_id)
        except Exception as e:
            raise CustomException(e, sys)

    def update_signals(self):
        """
        Decrement counter for each intersection. 
        Toggle red/green when counter hits 0, then reset to new duration.
        """
        try:
            for intersection_id, signal_data in self.signals.items():
                if signal_data["counter"] > 0:
                    signal_data["counter"] -= 1
                else:
                    # Toggle
                    if signal_data["state"] == "red":
                        signal_data["state"] = "green"
                        signal_data["counter"] = signal_data["green_duration"]
                    else:
                        signal_data["state"] = "red"
                        signal_data["counter"] = signal_data["red_duration"]
        except Exception as e:
            raise CustomException(e, sys)

    def simulate_traffic_flow(self, snapshot=None):
        """
        Move each vehicle at most once, based on the snapshot of the network 
        at the start of the step (if provided). 
        Vehicles only move from green intersections.
        """
        print("Simulating Traffic Flow:")
        try:
            # If no external snapshot is given, create one now
            if snapshot is None:
                snapshot = {i: list(v) for i, v in self.vehicles.items()}

            # Prepare new_positions from the current self.vehicles
            new_positions = {i: list(v) for i, v in self.vehicles.items()}

            # Go through each intersection in the snapshot
            for intersection, vehicles_list in snapshot.items():
                current_state = self.signals[intersection]["state"]
                
                if current_state == "green" and vehicles_list:
                    # All vehicles at a green intersection move exactly once
                    for vehicle in vehicles_list:
                        # Remove from old location
                        new_positions[intersection].remove(vehicle)

                        neighbors = self.network[intersection]
                        if neighbors:
                            # Move to a random connected intersection
                            next_intersection = random.choice(neighbors)
                            new_positions[next_intersection].append(vehicle)
                            print(f"Vehicle {vehicle} moved from {intersection} to {next_intersection}")
                        else:
                            # No neighbors -> vehicle stays put
                            new_positions[intersection].append(vehicle)
                else:
                    if current_state == "red" and vehicles_list:
                        print(f"Intersection {intersection} is red; vehicles do not move.")

            self.vehicles = new_positions

        except Exception as e:
            raise CustomException(e, sys)

    def display_network_status(self):
        """
        Show current signal states and vehicles in each intersection.
        """
        print("Network Status:")
        for intersection_id in self.network:
            signal_data = self.signals[intersection_id]
            vehicles_list = self.vehicles[intersection_id]
            print(
                f"  Intersection {intersection_id} "
                f"(Signal: {signal_data['state']}, Counter: {signal_data['counter']}): "
                f"{vehicles_list}"
            )
