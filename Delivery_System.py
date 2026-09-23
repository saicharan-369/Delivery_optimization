import argparse
import json
import math
import sys
from collections import defaultdict


def euclidean_distance(p1, p2):
    """Calculates Euclidean distance between two points: sqrt((x2 - x1)^2 + (y2 - y1)^2)"""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def clean_warehouse_key(key):
    """Removes special characters or accidental formatting artifacts."""
    clean = str(key).replace("$", "").replace('"', "").strip()
    if clean == "WI":
        return "W1"
    if clean == "N3":
        return "W3"
    return clean


def run_delivery_simulation(input_path, output_path="report.json"):
    # Load input JSON dynamically
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON from '{input_path}': {e}")
        sys.exit(1)

    # Validate top-level keys
    for key in ("warehouses", "agents", "packages"):
        if key not in data:
            print(f"Error: Missing required section '{key}' in '{input_path}'.")
            sys.exit(1)

    warehouses = data["warehouses"]
    agents = data["agents"]
    packages = data["packages"]

    # 1. Assign each package to the nearest agent based on agent start pos -> warehouse
    agent_packages = defaultdict(lambda: defaultdict(list))
    for pkg in packages:
        raw_w_id = pkg["warehouse"]
        w_id = clean_warehouse_key(raw_w_id)

        if w_id not in warehouses:
            print(f"Warning: Warehouse '{w_id}' for package '{pkg.get('id')}' not found. Skipping.")
            continue

        w_coords = warehouses[w_id]

        # Find closest agent
        best_agent = min(
            agents.keys(),
            key=lambda a_id: euclidean_distance(agents[a_id], w_coords),
        )
        agent_packages[best_agent][w_id].append(pkg["destination"])

    # 2. Simulate delivery routes for all agents
    report = {}
    best_agent_id = None
    best_efficiency = float("inf")

    for agent_id, initial_pos in agents.items():
        curr_pos = list(initial_pos)
        total_dist = 0.0
        total_delivered = 0

        # Agent visits each warehouse where they have assigned packages
        for w_id, destinations in agent_packages[agent_id].items():
            w_coords = warehouses[w_id]

            # Travel to warehouse
            total_dist += euclidean_distance(curr_pos, w_coords)
            curr_pos = w_coords

            # Deliver all picked-up packages (Greedy nearest-neighbor order)
            remaining_dests = destinations[:]
            while remaining_dests:
                next_dest = min(
                    remaining_dests,
                    key=lambda d: euclidean_distance(curr_pos, d),
                )
                total_dist += euclidean_distance(curr_pos, next_dest)
                curr_pos = next_dest
                remaining_dests.remove(next_dest)
                total_delivered += 1

        total_dist = round(total_dist, 2)
        if total_delivered > 0:
            efficiency = round(total_dist / total_delivered, 2)
            if efficiency < best_efficiency:
                best_efficiency = efficiency
                best_agent_id = agent_id
        else:
            efficiency = 0.0

        report[agent_id] = {
            "packages_delivered": total_delivered,
            "total_distance": total_dist,
            "efficiency": efficiency,
        }

    report["best_agent"] = best_agent_id

    # 3. Export to output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print(f"\nSimulation complete for: {input_path}")
    print(f"Results written to: {output_path}\n")
    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FastBox Delivery Logistics Simulator")
    parser.add_argument(
        "input_file",
        nargs="?",
        default=None,
        help="Path to any input JSON file (e.g., test1.json, data.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="report.json",
        help="Output report destination (default: report.json)",
    )

    args = parser.parse_args()

    # Prompt user interactively if no command-line argument is passed
    if args.input_file is None:
        user_input = input("Enter path to JSON input file (press Enter for 'data.json'): ").strip()
        args.input_file = user_input if user_input else "data.json"

    run_delivery_simulation(args.input_file, args.output)