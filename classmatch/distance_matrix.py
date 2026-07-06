from pathlib import Path

import pandas as pd


class DistanceMatrix:
    def __init__(self, distances: dict[tuple[str, str], float]):
        self._distances = distances

    def get(self, origen: str, destino: str) -> float:
        """Devuelve la distancia entre dos departamentos/zonas."""
        key = (origen, destino)

        if key not in self._distances:
            raise KeyError(f"No existe distancia cargada entre '{origen}' y '{destino}'.")

        return self._distances[key]


def cargar_distancias(path: str | Path) -> DistanceMatrix:
    """
    Lee distancias.csv con formato de matriz:

    Desde/Hasta;Ciudad;Godoy Cruz;Guaymallen;...
    Ciudad;0;5,5;12;...
    Godoy Cruz;5,5;0;21;...

    Se reemplaza coma decimal por punto decimal.
    """
    df = pd.read_csv(path, sep=";")

    origen_col = "Desde/Hasta"
    destinos = [col for col in df.columns if col != origen_col]

    distances: dict[tuple[str, str], float] = {}

    for _, row in df.iterrows():
        origen = str(row[origen_col]).strip()

        for destino in destinos:
            valor = row[destino]

            if isinstance(valor, str):
                valor = valor.replace(",", ".")

            distances[(origen, destino.strip())] = float(valor)

    return DistanceMatrix(distances)
