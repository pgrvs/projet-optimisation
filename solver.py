from typing import Dict, List
import pulp as pl

def solve(
    M: int,
    N: int,
    sensors: Dict[str, Dict[str, object]],
    configurations: List[List[str]]
) -> float:
    """
    Solves the sensor scheduling problem to maximize total surveillance time by optimally
    alternating between configurations while respecting sensor lifetime constraints.
    
    Args:
        M: Number of zones (unused in this implementation but kept for interface consistency)
        N: Number of sensors (unused in this implementation but kept for interface consistency)
        sensors: Dictionary mapping sensor IDs to their properties (must include 'lifetime')
        configurations: List of valid configurations (each configuration is a list of sensor IDs)
    
    Returns:
        float: The maximum total surveillance time achievable
    """
    # Create the LP problem
    prob = pl.LpProblem("OptimalSensorScheduling", pl.LpMaximize)
    
    # Create activation time variables for each configuration
    config_vars = [
        pl.LpVariable(f"t_{i}", lowBound=0) 
        for i in range(len(configurations))
    ]
    
    # Objective: Maximize total surveillance time (sum of all configuration times)
    prob += pl.lpSum(config_vars), "TotalSurveillanceTime"
    
    # Add constraints for each sensor's lifetime
    for sensor_id, sensor_data in sensors.items():
        # Find all configurations that use this sensor
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
    
    return float(pl.value(prob.objective))