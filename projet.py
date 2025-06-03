import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from typing import Dict, Tuple

def read_data_file(filepath: str) -> Tuple[int, int, Dict[str, Dict[str, object]]]:
    """
    Lit les données depuis un fichier texte structuré comme suit :
    - Ligne 1 : nombre de capteurs (N)
    - Ligne 2 : nombre de zones (M)
    - Ligne 3 : durées de vie des N capteurs
    - Lignes suivantes : pour chaque capteur, les zones qu’il couvre

    Retourne :
    - M : nombre de zones
    - N : nombre de capteurs
    - sensors : dictionnaire {id capteur: {coverage, life}}
    """
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

def display_output(filepath: str, M: int, N: int, sensors: Dict[str, Dict[str, object]]):
    output_text.config(state='normal')
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"Fichier : {filepath}\n")
    output_text.insert(tk.END, f"Nombre de zones (M) : {M}\n")
    output_text.insert(tk.END, f"Nombre de capteurs (N) : {N}\n\n")
    for sid, info in sensors.items():
        zones = ", ".join(info['coverage'])
        output_text.insert(tk.END, f"{sid} → Zones : [{zones}], Durée : {info['life']}\n")
    output_text.config(state='disabled')

# Interface graphique
root = tk.Tk()
root.title("Interface - Données Capteurs")
root.geometry("500x400")

btn = tk.Button(root, text="Sélectionner un fichier", command=select_file)
btn.pack(pady=10)

output_text = scrolledtext.ScrolledText(root, wrap='word', state='disabled')
output_text.pack(fill='both', expand=True, padx=10, pady=10)

root.mainloop()