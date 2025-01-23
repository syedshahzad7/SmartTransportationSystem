# src/components/anomaly_detector.py

import sys
from src.exception import CustomException
from src.logger import logging

class AnomalyDetector:
    def __init__(self, network, anomaly_injector=None, known_vehicles=None):
        """
        :param network: Instance of your TrafficNetwork class
        :param anomaly_injector: (Optional) reference to AnomalyInjector 
                                 so we can see which vehicles are intentionally stopped.
        :param known_vehicles: A set of vehicle IDs that are valid in the system
        """
        self.network = network
        self.anomaly_injector = anomaly_injector

        # If no known vehicles set is given, assume all vehicles we start with are known
        self.known_vehicles = known_vehicles if known_vehicles else set()

    def update_known_vehicles(self, additional_vehicles):
        """
        Dynamically add new vehicles to the list of known/authorized vehicles,
        if you want to grant them access.
        """
        self.known_vehicles.update(additional_vehicles)

    def detect_anomalies(self, snapshot, new_positions):
        """
        Main method to detect anomalies based on:
          - the snapshot (vehicles + signals before movement)
          - new_positions (vehicles after movement).
        """
        try:
            detected_anomalies = []

            # 1) Red-Light Violations
            detected_anomalies.extend(
                self._detect_red_light_violations(snapshot)
            )

            # 2) Unauthorized Vehicles
            detected_anomalies.extend(
                self._detect_unauthorized_vehicles(new_positions)
            )

            # 3) Unexpected Stops
            detected_anomalies.extend(
                self._detect_unexpected_stops(snapshot, new_positions)
            )

            # Log each anomaly
            for anomaly in detected_anomalies:
                logging.warning(anomaly)

            return detected_anomalies

        except Exception as e:
            raise CustomException(e, sys)

    def _detect_red_light_violations(self, snapshot):
        """
        A vehicle is considered a red-light violator if it moved
        from an intersection that was red in the snapshot.
        """
        anomalies = []
        for intersection_id, vehicles_list in snapshot.items():
            signal_state = self.network.signals[intersection_id]['state']
            if signal_state == 'red' and vehicles_list:
                # Vehicles that have left a red intersection
                old_vehicles = set(vehicles_list)
                new_vehicles = set(self.network.vehicles[intersection_id])  # after movement
                moved_vehicles = old_vehicles - new_vehicles

                for mv in moved_vehicles:
                    msg = (f"[DETECTED] Red-Light Violation: Vehicle {mv} "
                           f"moved from intersection {intersection_id} while red.")
                    anomalies.append(msg)
        return anomalies

    def _detect_unauthorized_vehicles(self, new_positions):
        """
        Any vehicle not in self.known_vehicles is considered unauthorized.
        """
        anomalies = []
        for intersection_id, vehicles_list in new_positions.items():
            for vehicle_id in vehicles_list:
                if vehicle_id not in self.known_vehicles:
                    msg = (f"[DETECTED] Unauthorized Vehicle: {vehicle_id} "
                           f"found at intersection {intersection_id}.")
                    anomalies.append(msg)
        return anomalies

    def _detect_unexpected_stops(self, snapshot, new_positions):
        """
        Detect if a vehicle remained in place even though:
          1) Its intersection was green.
          2) The vehicle was not intentionally stopped by anomaly_injector.
          3) The intersection had at least one road to move to (i.e., not isolated).
        
        NOTE: This logic is basic. Real logic might also check
              if a vehicle 'wanted' or 'needed' to move.
        """
        anomalies = []
        for intersection_id, old_vehicles in snapshot.items():
            # Check if intersection was green in the snapshot
            if self.network.signals[intersection_id]['state'] == "green" and old_vehicles:
                # Some or all vehicles here might have stayed put
                stayed_vehicles = self._vehicles_that_stayed(
                    intersection_id, old_vehicles, new_positions
                )

                # For each vehicle that stayed, check if it is intentionally stopped
                for vehicle in stayed_vehicles:
                    # If the anomaly_injector is known, check if it's forcibly stopped
                    if self.anomaly_injector:
                        if vehicle not in self.anomaly_injector.stopped_vehicles:
                            # The intersection has neighbors, so they could move
                            if self.network.network[intersection_id]:
                                msg = (f"[DETECTED] Unexpected Stop: Vehicle {vehicle} "
                                       f"did not move from intersection {intersection_id} "
                                       f"despite green light.")
                                anomalies.append(msg)
                    else:
                        # If we have no anomaly_injector reference, we can't check. 
                        # We'll assume any vehicle that stayed is unexpected:
                        if self.network.network[intersection_id]:
                            msg = (f"[DETECTED] Unexpected Stop: Vehicle {vehicle} "
                                   f"did not move from intersection {intersection_id} "
                                   f"despite green light.")
                            anomalies.append(msg)
        return anomalies

    def _vehicles_that_stayed(self, intersection_id, old_vehicles, new_positions):
        """
        Helper method: find which vehicles are in the same intersection 
        before and after the movement.
        """
        old_set = set(old_vehicles)
        new_set = set(new_positions[intersection_id])
        stayed_vehicles = old_set & new_set  # intersection of both sets
        return stayed_vehicles
