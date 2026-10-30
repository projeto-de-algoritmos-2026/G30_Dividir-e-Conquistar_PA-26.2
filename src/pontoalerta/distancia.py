"""Cálculo de distância euclidiana entre pontos no plano cartesiano."""

import math
from typing import Any

from .ocorrencia import Ocorrencia


def _extrair_coordenadas(ponto: Any) -> tuple[float, float]:
    """Extrai e valida coordenadas (x, y) de uma Ocorrencia ou tupla/lista numérica."""
    if hasattr(ponto, "x") and hasattr(ponto, "y"):
        x, y = ponto.x, ponto.y
    elif isinstance(ponto, (tuple, list)) and len(ponto) == 2:
        x, y = ponto[0], ponto[1]
    else:
        raise TypeError(
            f"Ponto inválido: {ponto!r}. Esperado objeto Ocorrencia ou tupla/lista (x, y)."
        )

    for nome, val in (("x", x), ("y", y)):
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            raise TypeError(
                f"Coordenada {nome} deve ser int ou float, recebido: {type(val).__name__}."
            )
        if not math.isfinite(val):
            raise ValueError(f"Coordenada {nome} deve ser finita, recebido: {val}.")

    return float(x), float(y)


def distancia_euclidiana(
    p1: Ocorrencia | tuple[float, float] | list[float],
    p2: Ocorrencia | tuple[float, float] | list[float],
) -> float:
    """Calcula a distância euclidiana entre dois pontos no plano cartesiano.

    Aceita instâncias de `Ocorrencia` ou tuplas/listas de duas coordenadas `(x, y)`.
    Utiliza a fórmula euclidiana d = sqrt((x2 - x1)^2 + (y2 - y1)^2).

    Retorna um float não-negativo.
    Lança TypeError para tipos inválidos e ValueError para valores não-finitos.
    """
    x1, y1 = _extrair_coordenadas(p1)
    x2, y2 = _extrair_coordenadas(p2)
    return math.hypot(x2 - x1, y2 - y1)
