"""Visualização das ocorrências e do par mais próximo no plano cartesiano."""

from collections.abc import Sequence

from matplotlib.figure import Figure

from .ocorrencia import Ocorrencia
from .par_proximo import ParMaisProximo


def criar_grafico_ocorrencias(
    ocorrencias: Sequence[Ocorrencia], resultado: ParMaisProximo
) -> Figure:
    """Crie uma figura com as ocorrências do conjunto analisado e seu resultado.

    A figura pode ser salva com savefig ou exibida na interface. O par recebido
    deve ter sido calculado para o conjunto informado.
    """
    figura = Figure(figsize=(8, 6), layout="constrained")
    eixo = figura.subplots()
    eixo.scatter(
        [p.x for p in ocorrencias], [p.y for p in ocorrencias],
        color="#2563eb", s=45, label="Ocorrências", zorder=2,
    )

    p1, p2 = resultado.par
    eixo.plot(
        [p1.x, p2.x], [p1.y, p2.y],
        color="#dc2626", linestyle="--", zorder=3,
    )
    eixo.scatter(
        [p1.x, p2.x], [p1.y, p2.y],
        color="#dc2626", marker="*", s=180, edgecolors="black",
        label="Par mais próximo", zorder=4,
    )
    for ponto, deslocamento in zip(resultado.par, [(8, 10), (8, -16)]):
        eixo.annotate(
            f"ID {ponto.id}", (ponto.x, ponto.y),
            xytext=deslocamento, textcoords="offset points",
        )

    eixo.set_title(
        f"Ocorrências — {p1.tipo}\nDistância mínima: {resultado.distancia:.6g}"
    )
    eixo.set_xlabel("X")
    eixo.set_ylabel("Y")
    eixo.set_aspect("equal", adjustable="box")
    eixo.margins(0.15)
    eixo.grid(True, alpha=0.25)
    eixo.legend()
    return figura
