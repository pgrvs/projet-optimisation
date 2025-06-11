import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, END
from tkinter import ttk
from typing import Dict, List, Tuple
import random
import time
from configsGeneratorRandom import generateConfigsRandom
from configsGeneratorTabou import generateConfigsTabou

from reader import read_data_file
from pulpSolver import solve as solvePulp
from GLPKSolver import solve as solveGLPK
from util import coversAll, isElementary



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



# Interface graphique pour sélectionner un fichier
def select_file():
    filepath = filedialog.askopenfilename(
        title="Choisir un fichier de données",
        filetypes=[("Fichiers texte", "*"), ("Tous les fichiers", "*")]
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
    # configs = generer_configurations_elementaires(M, N, sensors, k=3) #méthode de Paul

    nb_rounds = int(rounds_input.get())
    tabu_size = int(tabu_input.get())

    if generator_CB.get() == "random" :
        configs = generateConfigsRandom(M,N,sensors,nb_rounds)
    else :
        configs = generateConfigsTabou(M,N,sensors,nb_rounds,tabu_size)

    for c in configs :
        if not coversAll(M,N,sensors,c):
            raise f"config : {c} does not cover all"

        if not isElementary(M,N,sensors,c):
            raise f"config : {c} is not elementary"

    output_text.insert(tk.END, "\nConfigurations élémentaires générées :\n")
    for i, cfg in enumerate(configs, 1):
        output_text.insert(tk.END, f"  {i}. {cfg}\n")

    solver = solver_CB.get()
    if solver == "pulp":
        print("solving with pulp !")
        result = solvePulp(M,N,sensors,configs)
    else :
        print("solving with GLPK !")
        result = solveGLPK(M,N,sensors,configs)

    output_text.insert(tk.END,f"resultat : {result}")

# Interface utilisateur principale
root = tk.Tk()
root.title("Interface - Données Capteurs")
root.geometry("500x400")

btn = tk.Button(root, text="Sélectionner un fichier", command=select_file)
btn.pack(pady=10)

generator_label = tk.StringVar()
generator_label.set("Configs generation algorithm : ")
tk.Label(root,textvariable=generator_label).pack(pady=5)
generator_CB = ttk.Combobox(root)
generator_CB["values"] = ["random","tabou"]
generator_CB.pack(pady=10)

tabu_label = tk.StringVar()
tabu_label.set("Tabu size : ")
tk.Label(root,textvariable=tabu_label).pack(pady=5)
tabu_input = tk.Entry(root)
tabu_input.insert(END,"100")
tabu_input.pack(pady=10)

rounds_label = tk.StringVar()
rounds_label.set("Nb rounds : ")
tk.Label(root,textvariable=rounds_label).pack(pady=5)
rounds_input = tk.Entry(root)
rounds_input.insert(END,"100")
rounds_input.pack(pady=10)

generator_label = tk.StringVar()
generator_label.set("Solver implementation : ")
tk.Label(root,textvariable=generator_label).pack(pady=5)
solver_CB = ttk.Combobox(root)
solver_CB["values"] = ["pulp","GLPK"]
solver_CB.pack(pady=10)

output_text = scrolledtext.ScrolledText(root, wrap='word', state='disabled')
output_text.pack(fill='both', expand=True, padx=10, pady=10)

root.mainloop()