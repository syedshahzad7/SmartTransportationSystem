from src.components.traffic_network import TrafficNetwork
from src.components.anomaly_injector import AnomalyInjector

# 1) Initialize the network
network = TrafficNetwork()
network.add_intersection(1, green_duration=2, red_duration=2)
network.add_intersection(2, green_duration=2, red_duration=2)
network.add_intersection(3, green_duration=2, red_duration=2)

# 2) Connect intersections
network.connect_intersections(1, 2)
network.connect_intersections(2, 3)

# 3) Add vehicles
network.vehicles[1] = ["Car1", "Car2"]
network.vehicles[2] = ["Car3"]

# 4) Create anomaly injector
anomaly_injector = AnomalyInjector(network)

print("\nAdjacency List:")
for i, neighbors in network.network.items():
    print(f"  Intersection {i} -> {neighbors}")

print("\nInitial Status:")
network.display_network_status()

# 5) Run multiple steps
for step in range(1, 6):
    print(f"\n--- Step {step} ---")
    
    # (A) Update signal counters
    network.update_signals()

    # (B) Inject anomalies that MOVE vehicles BEFORE snapshot
    if step == 3:
        # Force Car2 to stop for 2 steps (doesn't "move" Car2, just flags it)
        anomaly_injector.cause_unexpected_stop("Car2", steps=2)

    if step == 4:
        # Car3 ignores red light *before* snapshot
        anomaly_injector.ignore_red_light("Car3")

    # (C) Create snapshot (now includes the effects of ignoring red light, etc.)
    snapshot = {i: list(v) for i, v in network.vehicles.items()}

    # (D) Apply stops so that "stopped" vehicles won't move
    anomaly_injector.apply_stops(snapshot)

    # (E) Simulate traffic using the snapshot
    network.simulate_traffic_flow(snapshot=snapshot)
    
    # (F) Display current status
    network.display_network_status()

    # (G) You can do anomalies that DON’T move existing vehicles after the sim
    #     For example, unauthorized entry:
    if step == 5:
        anomaly_injector.unauthorized_entry("CarX", 3)
        network.display_network_status()
