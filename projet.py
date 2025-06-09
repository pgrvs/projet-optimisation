import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from typing import Dict, List, Tuple
import random
import time
import pulp

# Lecture des données depuis un fichier texte
def read_data_file(filepath: str) -> Tuple[int, int, Dict[str, Dict[str, object]]]:
    sensors: Dict[str, Dict[str, object]] = {}
    with open(filepath, 'r') as f:
        N = int(f.readline().strip())
        M = int(f.readline().strip())
        durabilities = list(map(float, f.readline().strip().split()))
        if len(durabilities) != N:
            raise ValueError(f"{len(durabilities)} durées trouvées, attendu : {N}")
        for i in range(N):
            line = f.readline().strip()
            if not line:
                raise ValueError(f"Données manquantes pour capteur #{i+1}")
            zones = line.split()
            coverage = [f"z{int(z)}" for z in zones]
            sensors[f"s{i+1}"] = {"coverage": coverage, "life": durabilities[i]}
    return M, N, sensors

# Construction d'une configuration élémentaire (une seule)
def construire_configuration_elementaire(M: int, sensors: Dict[str, Dict[str, object]], k: int = 2) -> List[str]:
    zones_couvertes = set()
    toutes_les_zones = {f"z{i+1}" for i in range(M)}
    capteurs_restants = set(sensors.keys())
    configuration = []

    while zones_couvertes != toutes_les_zones and capteurs_restants:
        candidats = []
        for capteur in capteurs_restants:
            nouvelles_zones = set(sensors[capteur]['coverage']) - zones_couvertes
            if nouvelles_zones:
                candidats.append((capteur, len(nouvelles_zones)))

        if not candidats:
            break

        candidats.sort(key=lambda x: x[1], reverse=True)
        limite = min(k, len(candidats))
        choisi = random.choice(candidats[:limite])[0]

        configuration.append(choisi)
        zones_couvertes.update(sensors[choisi]['coverage'])
        capteurs_restants.remove(choisi)

    if zones_couvertes == toutes_les_zones:
        return configuration
    else:
        return []  # échec

# Génération de plusieurs configurations distinctes avec limite de temps/essais
def generer_configurations_elementaires(M: int, N: int, sensors: Dict[str, Dict[str, object]], k: int = 2) -> List[List[str]]:
    configurations = []
    deja_vues = set()
    nb_attendu = min(5 + (M + N) // 4, 50)
    limite_temps = min(3 + (M + N) * 0.05, 20)

    debut = time.time()
    while len(configurations) < nb_attendu and (time.time() - debut) < limite_temps:
        config = construire_configuration_elementaire(M, sensors, k)
        config_tri = tuple(sorted(config))
        if config and config_tri not in deja_vues:
            configurations.append(config)
            deja_vues.add(config_tri)

    return configurations

# Résolution du programme linéaire avec PuLP
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

# Interface graphique pour sélectionner un fichier
def select_file():
    filepath = filedialog.askopenfilename(
        title="Choisir un fichier de données",
        filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
    )
    if not filepath:
        return
    try:
        M, N, sensors = read_data_file(filepath)
        display_output(filepath, M, N, sensors)
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

# Affichage des données dans l'interface
def display_output(filepath: str, M: int, N: int, sensors: Dict[str, Dict[str, object]]):
    output_text.config(state='normal')
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"Fichier : {filepath}\n")
    output_text.insert(tk.END, f"Nombre de zones (M) : {M}\n")
    output_text.insert(tk.END, f"Nombre de capteurs (N) : {N}\n\n")
    for sid, info in sensors.items():
        zones = ", ".join(info['coverage'])
        output_text.insert(tk.END, f"{sid} → Zones : [{zones}], Durée : {info['life']}\n")

    # Génération des configurations élémentaires
    configs = generer_configurations_elementaires(M, N, sensors, k=3)
    output_text.insert(tk.END, "\nConfigurations élémentaires générées :\n")
    for i, cfg in enumerate(configs, 1):
        output_text.insert(tk.END, f"  {i}. {cfg}\n")

    solution = resoudre_avec_pulp(M, N, sensors, configs)
    output_text.insert(tk.END, "\nSolution optimale (durée d’activation des configurations) :\n")
    total = 0
    for i, val in solution.items():
        output_text.insert(tk.END, f"  Configuration {i+1} : {val:.2f}\n")
        total += val
    output_text.insert(tk.END, f"\nDurée totale de couverture : {total:.2f} unités\n")

    output_text.config(state='disabled')

# Interface utilisateur principale
root = tk.Tk()
root.title("Interface - Données Capteurs")
root.geometry("500x400")

btn = tk.Button(root, text="Sélectionner un fichier", command=select_file)
btn.pack(pady=10)

output_text = scrolledtext.ScrolledText(root, wrap='word', state='disabled')
output_text.pack(fill='both', expand=True, padx=10, pady=10)

root.mainloop()