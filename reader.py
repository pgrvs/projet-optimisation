
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