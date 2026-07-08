"""
models.py
Modelos de dominio para CLASSMATCH: Profesor, Escuela, Curso y estructuras
de apoyo (nivel de profesor, bloques de disponibilidad).

Diseño:
- Las entidades de catálogo (Profesor, Escuela, Curso) son dataclasses
  inmutables (frozen=True): no deberían cambiar durante la ejecución del
  algoritmo genético, solo se leen.
- Las relaciones entre entidades se modelan por ID (escuela_id en Curso),
  no por objetos embebidos. La resolución de esas referencias es
  responsabilidad de un repositorio central (ver data_loader.py / dataset.py
  en el próximo paso), no de estas clases.
"""

from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import List


class NivelProfesor(str, Enum):
    """Nivel del profesor. Hereda de str para que sea fácil de leer/escribir
    directamente desde/hacia CSV sin conversión manual."""
    SENIOR = "SENIOR"
    JUNIOR = "JUNIOR"


@dataclass(frozen=True)
class BloqueDisponibilidad:
    """Representa un intervalo continuo de disponibilidad de un profesor
    en un día particular.

    Ejemplo: BloqueDisponibilidad("Lunes", time(8, 0), time(13, 0))
    significa que el profesor está disponible los lunes de 8:00 a 13:00.
    """
    dia: str
    hora_inicio: time
    hora_fin: time

    def __post_init__(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValueError(
                f"Bloque inválido: hora_inicio ({self.hora_inicio}) debe ser "
                f"menor que hora_fin ({self.hora_fin})"
            )

    def cubre(self, dia: str, hora_inicio: time, hora_fin: time) -> bool:
        """Indica si este bloque cubre completamente un horario dado
        (mismo día, y el bloque contiene el intervalo solicitado)."""
        return (
            self.dia == dia
            and self.hora_inicio <= hora_inicio
            and self.hora_fin >= hora_fin
        )
    
    def contiene(self, dia, hora_inicio, hora_fin):
        return (
            self.dia == dia
            and self.hora_inicio <= hora_inicio
            and self.hora_fin >= hora_fin
        )


@dataclass(frozen=True)
class Profesor:
    """Profesor del sistema. Puede ser SENIOR o JUNIOR.

    """
    id: int
    nombre: str
    nivel: NivelProfesor
    departamento: str
    disponibilidad: List[BloqueDisponibilidad] = field(default_factory=list)

    def esta_disponible(self, dia: str, hora_inicio: time, hora_fin: time) -> bool:
        """¿Puede este profesor tomar un curso en este día y horario?"""
        return any(
            bloque.cubre(dia, hora_inicio, hora_fin)
            for bloque in self.disponibilidad
        )

    def es_senior(self) -> bool:
        return self.nivel == NivelProfesor.SENIOR

    def es_junior(self) -> bool:
        return self.nivel == NivelProfesor.JUNIOR


@dataclass(frozen=True)
class Escuela:
    """Escuela/taller donde se dictan cursos."""
    id: int
    nombre: str
    departamento: str


@dataclass(frozen=True)
class Curso:
    """Curso a cubrir. Referencia a su escuela por ID (no por objeto)."""
    id: int
    escuela_id: int
    dia: str
    hora_inicio: time
    hora_fin: time

    def se_solapa_con(self, otro: "Curso") -> bool:
        """Indica si este curso ocurre en simultáneo con otro curso
        (mismo día y los intervalos horarios se cruzan).
        """
        if self.dia != otro.dia:
            return False
        return self.hora_inicio < otro.hora_fin and otro.hora_inicio < self.hora_fin

    def es_contiguo_con(self, otro: "Curso") -> bool:
        """Indica si un curso termina exactamente cuando el otro empieza
        (mismo día, sin solapamiento, horarios pegados)."""
        if self.dia != otro.dia:
            return False
        return self.hora_fin == otro.hora_inicio or otro.hora_fin == self.hora_inicio

    def conflictua_con(self, otro: "Curso") -> bool:
        """Indica si un mismo profesor NO puede dictar ambos cursos.

        Reglas de negocio:
        - Si se solapan en el tiempo -> conflicto siempre.
        - Si son contiguos (sin solapar) pero en escuelas distintas ->
          conflicto, porque no hay margen de traslado entre escuelas.
        - Si son contiguos en la MISMA escuela -> sin conflicto (permitido).

        Se usará en fitness.py para validar la restricción de
        "un profesor no puede estar en dos cursos simultáneos/incompatibles".
        """
        if self.se_solapa_con(otro):
            return True
        if self.es_contiguo_con(otro) and self.escuela_id != otro.escuela_id:
            return True
        return False
