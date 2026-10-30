"""Estrutura de Divisão e Conquista para par de pontos mais próximos.

Implementa a ordenação inicial por coordenadas, a divisão do conjunto de pontos
em duas metades e os casos-base para subconjuntos pequenos.
"""

from collections.abc import Sequence
from typing import NamedTuple

from .distancia import distancia_euclidiana
from .ocorrencia import Ocorrencia


class ParMaisProximo(NamedTuple):
    """Representa o par de ocorrências mais próximas e a distância calculada."""

    ponto1: Ocorrencia
    ponto2: Ocorrencia
    distancia: float

    @property
    def par(self) -> tuple[Ocorrencia, Ocorrencia]:
        """Retorna os dois pontos como uma tupla."""
        return (self.ponto1, self.ponto2)

    def eh_duplicata(self, limite_distancia: float) -> bool:
        """Indica se a distância encontrada é menor ou igual ao limite configurável."""
        return self.distancia <= limite_distancia

    def contem(self, ocorrencia: Ocorrencia) -> bool:
        """Verifica se uma dada ocorrência faz parte deste par."""
        return ocorrencia in (self.ponto1, self.ponto2)


def _ordenar_par(p1: Ocorrencia, p2: Ocorrencia) -> tuple[Ocorrencia, Ocorrencia]:
    """Retorna o par ordenado deterministicamente por (x, y, id)."""
    if (p1.x, p1.y, p1.id) <= (p2.x, p2.y, p2.id):
        return p1, p2
    return p2, p1


def par_mais_proximo_forca_bruta(pontos: Sequence[Ocorrencia]) -> ParMaisProximo:
    """Encontra o par mais próximo comparando todas as combinações (força bruta).

    Utilizado como caso-base da recursão para subconjuntos com n <= 3 e como
    oráculo de validação nos testes.
    """
    total = len(pontos)
    if total < 2:
        raise ValueError(
            f"São necessárias pelo menos 2 ocorrências para calcular o par mais próximo (recebido {total})."
        )

    melhor_dist = float("inf")
    melhor_p1 = pontos[0]
    melhor_p2 = pontos[1]

    for i in range(total):
        p1 = pontos[i]
        for j in range(i + 1, total):
            p2 = pontos[j]
            dist = distancia_euclidiana(p1, p2)
            if dist < melhor_dist:
                melhor_dist = dist
                melhor_p1, melhor_p2 = p1, p2

    p1_ord, p2_ord = _ordenar_par(melhor_p1, melhor_p2)
    return ParMaisProximo(p1_ord, p2_ord, melhor_dist)


def ordenar_pontos_x_e_y(
    pontos: Sequence[Ocorrencia],
) -> tuple[list[Ocorrencia], list[Ocorrencia]]:
    """Ordena a coleção de ocorrências por X e por Y com complexidade O(n log n)."""
    for p in pontos:
        if not isinstance(p, Ocorrencia):
            raise TypeError(
                f"Elemento deve ser uma instância de Ocorrencia, recebido: {type(p).__name__}."
            )

    px = sorted(pontos, key=lambda p: (p.x, p.y, p.id))
    py = sorted(pontos, key=lambda p: (p.y, p.x, p.id))
    return px, py


def dividir_pontos(
    px: list[Ocorrencia],
) -> tuple[list[Ocorrencia], list[Ocorrencia], float]:
    """Divide a lista ordenada por X em metades esquerda e direita pelo ponto médio."""
    meio = len(px) // 2
    qx = px[:meio]
    rx = px[meio:]
    mid_x = px[meio].x
    return qx, rx, mid_x


def dividir_ordenado_y(
    py: list[Ocorrencia],
    qx: list[Ocorrencia],
) -> tuple[list[Ocorrencia], list[Ocorrencia]]:
    """Divide py em qy e ry em O(n) preservando a ordenação em Y."""
    conjunto_qx = {id(p) for p in qx}
    qy = [p for p in py if id(p) in conjunto_qx]
    ry = [p for p in py if id(p) not in conjunto_qx]
    return qy, ry
