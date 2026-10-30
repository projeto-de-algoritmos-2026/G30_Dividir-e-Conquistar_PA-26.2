"""Algoritmo de Par de Pontos Mais Próximos por Divisão e Conquista.

Implementa a estratégia clássica O(n log n) para encontrar o par de ocorrências
mais próximas no plano cartesiano, preservando a ordenação em Y durante as divisões
e inspecionando uma janela de no máximo 7 vizinhos na faixa central.
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


def par_mais_proximo_faixa(
    faixa: Sequence[Ocorrencia],
    delta: float,
    melhor_par: ParMaisProximo,
) -> ParMaisProximo:
    """Verifica os pontos na faixa central (strip) com distância horizontal < delta.

    Como os pontos na faixa estão pré-ordenados por Y, é suficiente comparar
    cada ponto com no máximo 7 sucessores cuja diferença em Y seja menor que delta.
    Garante tempo O(n) na etapa de combinação.
    """
    total = len(faixa)
    for i in range(total):
        p1 = faixa[i]
        limite_j = min(i + 8, total)
        for j in range(i + 1, limite_j):
            p2 = faixa[j]
            if p2.y - p1.y >= delta:
                break
            dist = distancia_euclidiana(p1, p2)
            if dist < delta:
                delta = dist
                p1_ord, p2_ord = _ordenar_par(p1, p2)
                melhor_par = ParMaisProximo(p1_ord, p2_ord, dist)

    return melhor_par


def _par_mais_proximo_rec(
    px: list[Ocorrencia],
    py: list[Ocorrencia],
) -> ParMaisProximo:
    """Passo recursivo da Divisão e Conquista.

    Recebe os pontos ordenados por X (px) e por Y (py).
    Divide py em qy e ry em O(n) sem reordenar, preservando O(n log n).
    """
    if len(px) <= 3:
        return par_mais_proximo_forca_bruta(px)

    qx, rx, mid_x = dividir_pontos(px)
    qy, ry = dividir_ordenado_y(py, qx)

    melhor_esq = _par_mais_proximo_rec(qx, qy)
    melhor_dir = _par_mais_proximo_rec(rx, ry)

    melhor_par = melhor_esq if melhor_esq.distancia <= melhor_dir.distancia else melhor_dir
    delta = melhor_par.distancia

    # Se a menor distância já for zero (pontos coincidentes), não há como melhorar
    if delta == 0.0:
        return melhor_par

    # Conquista na faixa central: pontos com |x - mid_x| < delta
    faixa = [p for p in py if abs(p.x - mid_x) < delta]
    return par_mais_proximo_faixa(faixa, delta, melhor_par)


def par_mais_proximo(
    pontos: Sequence[Ocorrencia],
    categoria: str | None = None,
) -> ParMaisProximo:
    """Encontra o par de ocorrências mais próximas utilizando Divisão e Conquista.

    Complexidade temporal: O(n log n).
    Complexidade espacial: O(n).

    Parâmetros:
        pontos: Sequência de objetos `Ocorrencia`.
        categoria: Se informado, filtra as ocorrências por esta categoria antes do cálculo.

    Retorna:
        Instância de `ParMaisProximo` com (ponto1, ponto2, distancia).

    Lança:
        ValueError se houver menos de 2 ocorrências (no total ou após filtragem).
        TypeError se algum elemento não for uma instância de `Ocorrencia`.
    """
    if categoria is not None:
        if not isinstance(categoria, str) or not categoria.strip():
            raise ValueError("categoria deve ser uma string não vazia.")
        pontos_candidatos = [p for p in pontos if p.tipo == categoria]
    else:
        pontos_candidatos = list(pontos)

    total = len(pontos_candidatos)
    if total < 2:
        sufixo = f" para a categoria '{categoria}'" if categoria else ""
        raise ValueError(
            f"São necessárias pelo menos 2 ocorrências{sufixo} para calcular o par mais próximo (recebido {total})."
        )

    # Pré-ordenação inicial: O(n log n)
    px, py = ordenar_pontos_x_e_y(pontos_candidatos)

    return _par_mais_proximo_rec(px, py)
