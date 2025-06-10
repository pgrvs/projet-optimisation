from typing import Dict, List, TypedDict
import pulp as pl

class SolutionResult(TypedDict):
    max_time: float
    config_activation_times: List[Dict[str, float]]

def solve(
    M: int,
    N: int,
    sensors: Dict[str, Dict[str, object]],
    configurations: List[List[str]]
) -> SolutionResult:
    """
    Solves the sensor scheduling problem and returns detailed activation information.
    
    Args:
        M: Number of zones (unused but kept for interface)
        N: Number of sensors (unused but kept for interface)
        sensors: Dictionary mapping sensor IDs to their properties (must include 'lifetime')
        configurations: List of valid configurations (each configuration is a list of sensor IDs)
    
    Returns:
        Dictionary containing:
        - max_time: float - The maximum total surveillance time
        - config_activation_times: List[Dict] - Activation details for each configuration
          Each entry contains:
            - 'config': List[str] - The sensor IDs in this configuration
            - 'time': float - The activation duration for this configuration
    """
    # Create the LP problem
    prob = pl.LpProblem("OptimalSensorScheduling", pl.LpMaximize)
    
    # Create activation time variables for each configuration
    config_vars = [
        pl.LpVariable(f"t_{i}", lowBound=0)
        for i in range(len(configurations))
    ]
    
    # Objective: Maximize total surveillance time
    prob += pl.lpSum(config_vars), "TotalSurveillanceTime"
    
    # Add constraints for each sensor's lifetime
    for sensor_id, sensor_data in sensors.items():
        relevant_configs = [
            config_vars[i]
            for i, config in enumerate(configurations)
            if sensor_id in config
        ]
        if relevant_configs:
            prob += (
                pl.lpSum(relevant_configs) <= sensor_data['life'],
                f"LifetimeConstraint_{sensor_id}"
            )
    
    # Solve the problem
    status = prob.solve(pl.PULP_CBC_CMD(msg=False))
    
    if status != pl.LpStatusOptimal:
        raise RuntimeError(f"Optimization failed with status: {pl.LpStatus[status]}")
    
    # Prepare the detailed results
    activation_times = []
    for i, config in enumerate(configurations):
        time = pl.value(config_vars[i])
        if time > 1e-6:  # Only include configurations with non-negligible activation
            activation_times.append({
                'config': config,
                'time': float(time)
            })
    
    return {
        'max_time': float(pl.value(prob.objective)),
        'config_activation_times': activation_times
    }