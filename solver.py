from typing import Dict, List, Union
import pulp as pl  # type: ignore

def solve(
    M: int,
    N: int,
    sensors: Dict[str, Dict[str, object]],
    configuration: List[str]
) -> float:
    """
    Computes the maximal coverage time for a single sensor configuration.
    
    Args:
        M: Number of zones (unused here but kept for consistency).
        N: Number of sensors (unused here but kept for consistency).
        sensors: Dictionary mapping sensor names to their properties ('life' and 'coverage').
        configuration: List of sensors in the current configuration.
        
    Returns:
        Maximal coverage time (minimum lifetime among active sensors in the configuration).
    """
    active_sensors = configuration
    if not active_sensors:
        return 0.0
    
    # The coverage time is limited by the sensor with the smallest lifetime in the configuration
    min_lifetime = min(sensors[s]['life'] for s in active_sensors)
    return float(min_lifetime)