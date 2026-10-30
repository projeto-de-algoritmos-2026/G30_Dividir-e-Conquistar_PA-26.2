import math
import pytest

from pontoalerta import (
    Ocorrencia,
    ParMaisProximo,
    distancia_euclidiana,
    dividir_ordenado_y,
    dividir_pontos,
    ordenar_pontos_x_e_y,
    par_mais_proximo_forca_bruta,
)


def test_caso_base_dois_pontos_forca_bruta():
    p1 = Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=3.0, y=4.0)

    resultado = par_mais_proximo_forca_bruta([p1, p2])

    assert isinstance(resultado, ParMaisProximo)
    assert math.isclose(resultado.distancia, 5.0)
    assert set(resultado.par) == {p1, p2}
    assert resultado.contem(p1)
    assert resultado.contem(p2)


def test_caso_base_tres_pontos_forca_bruta():
    p1 = Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=10.0, y=10.0)
    p3 = Ocorrencia(id="3", tipo="buraco", x=0.5, y=0.5)

    resultado = par_mais_proximo_forca_bruta([p1, p2, p3])

    esperada = distancia_euclidiana(p1, p3)
    assert math.isclose(resultado.distancia, esperada)
    assert set(resultado.par) == {p1, p3}


def test_forca_bruta_rejeita_menos_de_dois_pontos():
    with pytest.raises(ValueError, match="pelo menos 2 ocorrências"):
        par_mais_proximo_forca_bruta([])

    p1 = Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0)
    with pytest.raises(ValueError, match="pelo menos 2 ocorrências"):
        par_mais_proximo_forca_bruta([p1])


def test_ordenacao_inicial_pontos_x_e_y():
    p1 = Ocorrencia(id="1", tipo="buraco", x=5.0, y=1.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=2.0, y=9.0)
    p3 = Ocorrencia(id="3", tipo="buraco", x=8.0, y=3.0)

    px, py = ordenar_pontos_x_e_y([p1, p2, p3])

    assert [p.id for p in px] == ["2", "1", "3"]
    assert [p.id for p in py] == ["1", "3", "2"]


def test_ordenacao_rejeita_tipo_invalido():
    p1 = Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0)
    with pytest.raises(TypeError, match="deve ser uma instância de Ocorrencia"):
        ordenar_pontos_x_e_y([p1, (1.0, 2.0)])  # type: ignore


def test_divisao_de_pontos_em_duas_metades():
    p1 = Ocorrencia(id="1", tipo="buraco", x=1.0, y=2.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=3.0, y=4.0)
    p3 = Ocorrencia(id="3", tipo="buraco", x=5.0, y=6.0)
    p4 = Ocorrencia(id="4", tipo="buraco", x=7.0, y=8.0)

    px = [p1, p2, p3, p4]
    qx, rx, mid_x = dividir_pontos(px)

    assert qx == [p1, p2]
    assert rx == [p3, p4]
    assert mid_x == 5.0


def test_divisao_preservando_ordenacao_por_y():
    p1 = Ocorrencia(id="1", tipo="buraco", x=1.0, y=10.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=2.0, y=2.0)
    p3 = Ocorrencia(id="3", tipo="buraco", x=8.0, y=8.0)
    p4 = Ocorrencia(id="4", tipo="buraco", x=9.0, y=1.0)

    px = [p1, p2, p3, p4]
    qx, rx, _ = dividir_pontos(px)

    py = sorted(px, key=lambda p: p.y)  # p4, p2, p3, p1
    qy, ry = dividir_ordenado_y(py, qx)

    assert qy == [p2, p1]
    assert ry == [p4, p3]


def test_propriedades_do_par_mais_proximo():
    p1 = Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=3.0, y=4.0)

    resultado = par_mais_proximo_forca_bruta([p1, p2])

    pt1, pt2, dist = resultado
    assert pt1 in (p1, p2)
    assert pt2 in (p1, p2)
    assert math.isclose(dist, 5.0)

    assert resultado.eh_duplicata(limite_distancia=6.0) is True
    assert resultado.eh_duplicata(limite_distancia=5.0) is True
    assert resultado.eh_duplicata(limite_distancia=4.9) is False
