# Résolution du programme linéaire avec PuLP
from typing import Dict, List
import pulp


def resoudre_avec_pulp(M, N, sensors: Dict[str, Dict[str, object]], configurations: List[List[str]]) -> Dict[int, float]:
    prob = pulp.LpProblem("OrdonnancementCapteurs", pulp.LpMaximize)

    x_vars = [pulp.LpVariable(f"x{i}", lowBound=0) for i in range(len(configurations))]
    prob += pulp.lpSum(x_vars)

    for s in sensors:
        prob += pulp.lpSum(x_vars[i] for i, cfg in enumerate(configurations) if s in cfg) <= sensors[s]['life']

    prob.solve()

    result = {}
    for i, var in enumerate(x_vars):
        if var.varValue is not None and var.varValue > 1e-6:
            result[i] = var.varValue

    return result