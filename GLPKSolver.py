import subprocess
from tempfile import NamedTemporaryFile
from typing import Dict, List, TypedDict
import os
import re
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
    Solves the sensor scheduling problem using GLPK via CPLEX LP file format.
    
    Args:
        M: Number of zones (unused)
        N: Number of sensors (unused)
        sensors: Dictionary mapping sensor IDs to their properties (must include 'life')
        configurations: List of valid configurations (each configuration is a list of sensor IDs)
    
    Returns:
        Dictionary containing:
        - max_time: Total maximum surveillance time
        - config_activation_times: List of configurations with their activation times
    """
    # Generate CPLEX LP file content
    lp_content = _generate_lp_file(sensors, configurations)
    print("file generated !")
    # Create temporary files
    with NamedTemporaryFile(mode='w', suffix='.lp', delete=False) as lp_file, \
         NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as sol_file:
        
        lp_file.write(lp_content)
        lp_file_path = lp_file.name
        sol_file_path = sol_file.name
    
    try:
        # Run GLPK solver
        cmd = [
            'glpsol',
            '--cpxlp', lp_file_path,
            '--output', sol_file_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        # Parse the solution
        result = _parse_glpk_solution(sol_file_path, configurations)
        
    finally:
        # Clean up temporary files
        os.unlink(lp_file_path)
        os.unlink(sol_file_path)
    
    return result

def _generate_lp_file(sensors: Dict[str, Dict[str, object]], 
                     configurations: List[List[str]]) -> str:
    """Generates CPLEX LP format string for the problem."""
    lines = ["Maximize"]
    
    # Objective function
    obj_terms = [f"t{i}" for i in range(len(configurations))]
    lines.append("    " + " + ".join(obj_terms))
    
    # Constraints
    lines.append("Subject To")
    for sensor_id, sensor_data in sensors.items():
        terms = []
        for i, config in enumerate(configurations):
            if sensor_id in config:
                terms.append(f"t{i}")
        if terms:
            lines.append(f"    {' + '.join(terms)} <= {sensor_data['life']}")
    
    # Variable bounds
    lines.append("Bounds")
    for i in range(len(configurations)):
        lines.append(f"    t{i} >= 0")
    
    lines.append("End")
    return "\n".join(lines)

def _parse_glpk_solution(sol_file_path: str, 
                         configurations: List[List[str]]) -> SolutionResult:
    """Parses GLPK solution file."""
    with open(sol_file_path, 'r') as f:
        content = f.read()

    # Extract objective value
    obj_match = re.search(r'Objective:\s+obj\s+=\s+([-\d.]+)', content)
    max_time = float(obj_match.group(1)) if obj_match else 0.0

    # Extract activation times
    config_times = []
    for i, config in enumerate(configurations):
        var_name = f"t{i}"
        # Match line with variable name and extract activity value (3rd column)
        match = re.search(rf"\s+\d+\s+{var_name}\s+\w+\s+([-\d.]+)", content)
        if match:
            time = float(match.group(1))
            if time > 1e-6:
                config_times.append({
                    'config': config,
                    'time': time
                })

    return {
        'max_time': max_time,
        'config_activation_times': config_times
    }