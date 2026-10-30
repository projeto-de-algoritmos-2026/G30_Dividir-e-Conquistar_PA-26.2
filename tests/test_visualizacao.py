from io import BytesIO

import pytest
from matplotlib.figure import Figure

from pontoalerta import Ocorrencia, criar_grafico_ocorrencias, par_mais_proximo


@pytest.mark.parametrize(
    "coordenadas",
    [
        [(-4, -3), (-1, 1), (5, 4)],
        [(-2, -3), (-2, -3), (5, 4)],
        [(-3, 0), (0, 0), (1, 0)],
    ],
    ids=["coordenadas-negativas", "pontos-duplicados", "pontos-alinhados"],
)
def test_grafico_representa_pontos_e_destaca_o_par(coordenadas):
    ocorrencias = [
        Ocorrencia(id=str(i), tipo="buraco", x=x, y=y)
        for i, (x, y) in enumerate(coordenadas)
    ]
    resultado = par_mais_proximo(ocorrencias)

    figura = criar_grafico_ocorrencias(ocorrencias, resultado)

    assert isinstance(figura, Figure)
    eixo = figura.axes[0]
    assert eixo.collections[0].get_offsets().tolist() == [list(p) for p in coordenadas]
    assert eixo.collections[1].get_offsets().tolist() == [
        [p.x, p.y] for p in resultado.par
    ]
    assert list(eixo.lines[0].get_xdata()) == [p.x for p in resultado.par]
    assert list(eixo.lines[0].get_ydata()) == [p.y for p in resultado.par]
    assert {texto.get_text() for texto in eixo.texts} == {
        f"ID {p.id}" for p in resultado.par
    }
    assert eixo.get_aspect() == 1
    assert eixo.get_xlabel() == "X"
    assert eixo.get_ylabel() == "Y"
    assert "buraco" in eixo.get_title()
    assert f"Distância mínima: {resultado.distancia:.6g}" in eixo.get_title()

    imagem = BytesIO()
    figura.savefig(imagem, format="png")
    assert imagem.getvalue().startswith(b"\x89PNG\r\n\x1a\n")
