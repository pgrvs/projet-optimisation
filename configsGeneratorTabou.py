import random
from typing import Set, List
from util import coversAll, isElementary

def generateConfigsTabou(M, N, sensors, rounds=100, tabu_size=10):
    configs = []
    tabu_sensors = set()

    # Initial config
    current_config = generateElementaryAvoidingTabu(M, N, sensors, tabu_sensors)
    configs.append(current_config)

    for _ in range(rounds):
        # Add some used sensors to tabu list
        used_sensors = random.sample(current_config, min(len(current_config), 2))
        tabu_sensors.update(used_sensors)

        # Cap tabu list size
        if len(tabu_sensors) > tabu_size:
            tabu_sensors = set(list(tabu_sensors)[-tabu_size:])

        # Try to generate new config avoiding tabu sensors
        new_config = generateElementaryAvoidingTabu(M, N, sensors, tabu_sensors)

        # If no new valid config, break
        if not new_config or sorted(new_config) in [sorted(c) for c in configs]:
            break

        configs.append(new_config)
        current_config = new_config

    # Display results
    for config in configs:
        print("---------------------------------------------------")
        print(config)
        print("covers all ? :", coversAll(M, N, sensors, config))
        print("elementary ? :", isElementary(M, N, sensors, config))
        print("total life :", sum(sensors[s]['life'] for s in config))
        print("---------------------------------------------------")

    return configs


def generateElementaryAvoidingTabu(M, N, sensors, tabu_sensors: Set[str]):
    """Generates an elementary config while avoiding sensors in the tabu list."""

    available = sorted(
        [f"s{i}" for i in range(1, N+1) if f"s{i}" not in tabu_sensors],
        key=lambda s: -sensors[s]['life']
    )

    if not available:
        return set()

    chosen: Set[str] = set()
    for sensor in available:
        chosen.add(sensor)
        if coversAll(M, N, sensors, chosen):
            break

    # Try to reduce the config to make it elementary
    while not isElementary(M, N, sensors, chosen):
        removable = sorted(chosen, key=lambda s: sensors[s]['life'])  # Prefer removing low-life
        for s in removable:
            temp = set(chosen)
            temp.remove(s)
            if coversAll(M, N, sensors, temp):
                chosen = temp
                break
        else:
            break

    return chosen
