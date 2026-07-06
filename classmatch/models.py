from dataclasses import dataclass
from datetime import time
from enum import Enum
from typing import Dict, List, Optional


class NivelProfesor(Enum):
    SENIOR = "SENIOR"
    JUNIOR = "JUNIOR"


@dataclass(frozen=True)
class BloqueDisponibilidad:
    dia: str
    hora_inicio: time
    hora_fin: time

    def contiene(self, dia: str, hora_inicio: time, hora_fin: time) -> bool:
        """Devuelve True si el bloque contiene completamente el horario indicado"""
        return (
            self.dia == dia
            and self.hora_inicio <= hora_inicio
            and self.hora_fin >= hora_fin
        )


@dataclass(frozen=True)
class Escuela:
    id: str
    nombre: str
    departamento: str


@dataclass(frozen=True)
class Curso:
    id: str
    escuela_id: str
    dia: str
    hora_inicio: time
    hora_fin: time

    def se_solapa_con(self, otro: "Curso") -> bool:
        """Devuelve True si dos cursos se pisan en el mismo día"""
        if self.dia != otro.dia:
            return False

        # Cursos contiguos no se consideran solapados
        # Ej: 09:00-10:00 y 10:00-11:00 pueden ser dados por la misma persona
        return self.hora_inicio < otro.hora_fin and otro.hora_inicio < self.hora_fin


@dataclass(frozen=True)
class Profesor:
    id: str
    nombre: str
    nivel: NivelProfesor
    departamento: str
    disponibilidad: List[BloqueDisponibilidad]
    anos_experiencia: int = 0
    max_escuelas: Optional[int] = None
    distancia_max_km: Optional[float] = None

    def esta_disponible_para(self, curso: Curso) -> bool:
        """Devuelve True si algún bloque disponible cubre el curso completo"""
        return any(
            bloque.contiene(curso.dia, curso.hora_inicio, curso.hora_fin)
            for bloque in self.disponibilidad
        )


@dataclass(frozen=True)
class ClassMatchData:
    profesores: Dict[str, Profesor]
    escuelas: Dict[str, Escuela]
    cursos: Dict[str, Curso]
