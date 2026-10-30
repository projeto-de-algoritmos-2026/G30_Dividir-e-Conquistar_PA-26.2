"""Modelo de uma ocorrência urbana no plano cartesiano."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Ocorrencia:
    """Registro com identificador textual, categoria e coordenadas finitas."""

    id: str
    tipo: str
    x: float
    y: float

    def __post_init__(self) -> None:
        for campo in ("id", "tipo"):
            valor = getattr(self, campo)
            if not isinstance(valor, str):
                raise TypeError(f"{campo} deve ser um texto.")
            if not valor.strip():
                raise ValueError(f"{campo} não pode ser vazio.")

        for campo in ("x", "y"):
            valor = getattr(self, campo)
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise TypeError(f"{campo} deve ser um número int ou float.")
            if not isfinite(valor):
                raise ValueError(f"{campo} deve ser finito.")
