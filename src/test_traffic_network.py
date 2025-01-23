# src/test_traffic_network.py

from src.components.traffic_network import TrafficNetwork
from src.components.anomaly_injector import AnomalyInjector
from src.components.anomaly_detector import AnomalyDetector

def run_test():
    # 1) Initialize the network
    network = TrafficNetwork()

    # 2) Add intersections
    network.add_intersection(1, green_duration=2, red_duration=2)
    network.add_intersection(2, green_duration=2, red_duration=2)
    network.add_intersection(3, green_duration=2, red_duration=2)

    # 3) Connect intersections
    network.connect_intersections(1, 2)
    network.connect_intersections(2, 3)

    # 4) Add vehicles
    network.vehicles[1] = ["Car1", "Car2"]
    network.vehicles[2] = ["Car3"]

    # 5) Create anomaly injector
    injector = AnomalyInjector(network)

    # 6) Create anomaly detector
    #    We'll assume Car1, Car2, Car3 are known. 
    #    Anything else is unauthorized.
    detector = AnomalyDetector(network, anomaly_injector=injector,
                               known_vehicles={"Car1", "Car2", "Car3"})

    print("\nAdjacency List:")
    for i, neighbors in network.network.items():
        print(f"  Intersection {i} -> {neighbors}")

    print("\nInitial Status:")
    network.display_network_status()

    # 7) Simulate steps
    for step in range(1, 6):
        print(f"\n--- Step {step} ---")

        # (A) Update signals
        network.update_signals()

        # (B) Apply movement anomalies BEFORE snapshot
        if step == 3:
            # Force Car2 to stop for 2 steps
            injector.cause_unexpected_stop("Car2", steps=2)

        if step == 4:
            # Force Car3 to ignore red light
            injector.ignore_red_light("Car3")

        # (C) Create snapshot
        snapshot = {i: list(v) for i, v in network.vehicles.items()}

        # (D) Apply stops to remove forcibly stopped vehicles from snapshot
        injector.apply_stops(snapshot)

        # (E) Simulate traffic with final snapshot
        network.simulate_traffic_flow(snapshot=snapshot)

        # (F) new positions after movement
        new_positions = {i: list(v) for i, v in network.vehicles.items()}

        # (G) Detect anomalies
        anomalies_found = detector.detect_anomalies(snapshot, new_positions)
        for anomaly_msg in anomalies_found:
            print(anomaly_msg)

        # (H) Display status
        network.display_network_status()

        # (I) Insert unauthorized vehicle at step 5
        if step == 5:
            injector.unauthorized_entry("CarX", 3)
            network.display_network_status()

            # Re-detect anomalies after CarX has been added
            new_positions = {i: list(v) for i, v in network.vehicles.items()}
            anomalies_found = detector.detect_anomalies(snapshot, new_positions)
            for anomaly_msg in anomalies_found:
                print(anomaly_msg)

if __name__ == "__main__":
    run_test()
