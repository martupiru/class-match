from pathlib import Path

import pandas as pd

from classmatch.utils import normalizar_departamento


class DistanceMatrix:
    def __init__(self, distances: dict[tuple[str, str], float]):
        self._distances = distances

    def get(self, origen: str, destino: str) -> float:
        """Devuelve la distancia entre dos departamentos/zonas."""
        key = (origen, destino)

        if key not in self._distances:
            raise KeyError(f"No existe distancia cargada entre '{origen}' y '{destino}'.")

        return self._distances[key]

    def departamentos(self) -> list[str]:
        """Lista (sin duplicados) de todos los departamentos con distancias cargadas."""
        return sorted({origen for origen, _ in self._distances})


def cargar_distancias(path: str | Path) -> DistanceMatrix:
    """
    Lee distancias.csv con formato de matriz:

    Desde/Hasta;Ciudad;Godoy Cruz;Guaymallen;...
    Ciudad;0;5,5;12;...
    Godoy Cruz;5,5;0;21;...

    Se reemplaza coma decimal por punto decimal y los nombres de
    departamento se normalizan a su forma canónica (tildes, "Ciudad" ->
    "Capital"), para que coincidan con Profesor.departamento y
    Escuela.departamento
    """
    df = pd.read_csv(path, sep=";")

    origen_col = "Desde/Hasta"
    destinos = [col for col in df.columns if col != origen_col]

    distances: dict[tuple[str, str], float] = {}

    for _, row in df.iterrows():
        origen = normalizar_departamento(str(row[origen_col]).strip())

        for destino in destinos:
            valor = row[destino]

            if isinstance(valor, str):
                valor = valor.replace(",", ".")

            distances[(origen, normalizar_departamento(destino.strip()))] = float(valor)

    return DistanceMatrix(distances)