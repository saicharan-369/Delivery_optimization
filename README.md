# FastBox Delivery Logistics Simulator

A small Python command-line simulator for assigning packages to delivery agents and estimating route efficiency.

## Requirements

- Python 3.8 or newer
- No third-party packages

## Usage

Run the simulator with an input JSON file:

```powershell
python Delivery_System.py data.json
```

By default, results are written to `report.json`. Use `-o` or `--output` to select another destination:

```powershell
python Delivery_System.py test_case_2.json --output results.json
```

When no input file is provided, the program prompts for a path and uses `data.json` when the response is empty:

```powershell
python Delivery_System.py
```

The completed report is printed to the terminal and saved as formatted JSON.

## Input Format

The input file must contain `warehouses`, `agents`, and `packages` sections:

```json
{
    "warehouses": {
        "W1": [0, 0],
        "W2": [50, 75]
    },
    "agents": {
        "A1": [5, 5],
        "A2": [60, 60]
    },
    "packages": [
        {
            "id": "P1",
            "warehouse": "W1",
            "destination": [30, 40]
        }
    ]
}
```

- Warehouse and agent positions are two-number `[x, y]` coordinates.
- Each package references a warehouse and provides a two-number destination.
- Package IDs are used in warning messages and do not need to be unique for the calculation.

## Simulation Rules

1. Each package is assigned to the agent closest to its warehouse, based on Euclidean distance from the agent's starting position.
2. Each agent travels to assigned warehouses in the order they appear in the input packages.
3. At each warehouse, the agent delivers packages using a greedy nearest-neighbor route.
4. `efficiency` is calculated as `total_distance / packages_delivered`, rounded to two decimal places.
5. `best_agent` is the agent with the lowest non-zero efficiency. Agents with no deliveries receive zero values and are not selected as the best agent.

Warehouse keys with accidental `$` or quote characters are cleaned. The aliases `WI` and `N3` are interpreted as `W1` and `W3`. Packages that reference an unknown warehouse are skipped with a warning.

## Output Format

The report contains one entry for each agent:

```json
{
    "A1": {
        "packages_delivered": 1,
        "total_distance": 43.17,
        "efficiency": 43.17
    },
    "best_agent": "A1"
}
```

- `packages_delivered`: number of packages delivered by the agent.
- `total_distance`: calculated route distance, rounded to two decimal places.
- `efficiency`: average distance per delivered package, rounded to two decimal places.
- `best_agent`: ID of the most efficient agent, or `null` when no packages are delivered.

## Included Files

- `Delivery_System.py`: simulator and command-line entry point.
- `data.json`: sample input.
- `test_case_1.json` through `test_case_10.json`: additional input cases.
- `report.json`: sample generated output.

## Error Handling

The program exits with an error when the input file is missing, contains invalid JSON, or lacks a required top-level section. Unknown warehouse references are reported and skipped.
