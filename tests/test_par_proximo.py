import math
import random
from itertools import combinations

import pytest

from pontoalerta import (
    Ocorrencia,
    ParMaisProximo,
    carregar_ocorrencias_csv,
    distancia_euclidiana,
    dividir_ordenado_y,
    dividir_pontos,
    ordenar_pontos_x_e_y,
    par_mais_proximo,
    par_mais_proximo_faixa,
    par_mais_proximo_forca_bruta,
)


def test_caso_base_dois_pontos():
    p1 = Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=3.0, y=4.0)

    resultado = par_mais_proximo([p1, p2])

    assert isinstance(resultado, ParMaisProximo)
    assert math.isclose(resultado.distancia, 5.0)
    assert set(resultado.par) == {p1, p2}
    assert resultado.contem(p1)
    assert resultado.contem(p2)


def test_caso_base_tres_pontos():
    p1 = Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=10.0, y=10.0)
    p3 = Ocorrencia(id="3", tipo="buraco", x=0.5, y=0.5)

    resultado = par_mais_proximo([p1, p2, p3])

    esperada = distancia_euclidiana(p1, p3)
    assert math.isclose(resultado.distancia, esperada)
    assert set(resultado.par) == {p1, p3}


def test_rejeita_menos_de_dois_pontos():
    with pytest.raises(ValueError, match="pelo menos 2 ocorrências"):
        par_mais_proximo([])

    p1 = Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0)
    with pytest.raises(ValueError, match="pelo menos 2 ocorrências"):
        par_mais_proximo([p1])


def test_rejeita_elemento_que_nao_e_ocorrencia():
    p1 = Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0)
    with pytest.raises(TypeError, match="deve ser uma instância de Ocorrencia"):
        par_mais_proximo([p1, (1.0, 2.0)])  # type: ignore


def test_pontos_duplicados_mesma_coordenada():
    p1 = Ocorrencia(id="1", tipo="buraco", x=5.0, y=5.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=5.0, y=5.0)
    p3 = Ocorrencia(id="3", tipo="buraco", x=20.0, y=20.0)
    p4 = Ocorrencia(id="4", tipo="buraco", x=30.0, y=30.0)

    resultado = par_mais_proximo([p1, p2, p3, p4])

    assert resultado.distancia == 0.0
    assert set(resultado.par) == {p1, p2}


def test_par_mais_proximo_na_metade_esquerda():
    p1 = Ocorrencia(id="1", tipo="buraco", x=1.0, y=1.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=1.1, y=1.1)
    p3 = Ocorrencia(id="3", tipo="buraco", x=50.0, y=50.0)
    p4 = Ocorrencia(id="4", tipo="buraco", x=60.0, y=60.0)

    resultado = par_mais_proximo([p1, p2, p3, p4])

    assert math.isclose(resultado.distancia, distancia_euclidiana(p1, p2))
    assert set(resultado.par) == {p1, p2}


def test_par_mais_proximo_na_metade_direita():
    p1 = Ocorrencia(id="1", tipo="buraco", x=1.0, y=1.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=10.0, y=10.0)
    p3 = Ocorrencia(id="3", tipo="buraco", x=50.0, y=50.0)
    p4 = Ocorrencia(id="4", tipo="buraco", x=50.2, y=50.1)

    resultado = par_mais_proximo([p1, p2, p3, p4])

    assert math.isclose(resultado.distancia, distancia_euclidiana(p3, p4))
    assert set(resultado.par) == {p3, p4}


def test_par_mais_proximo_cruza_faixa_central():
    p1 = Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=9.9, y=5.0)
    p3 = Ocorrencia(id="3", tipo="buraco", x=10.1, y=5.0)
    p4 = Ocorrencia(id="4", tipo="buraco", x=20.0, y=20.0)

    resultado = par_mais_proximo([p1, p2, p3, p4])

    assert math.isclose(resultado.distancia, 0.2)
    assert set(resultado.par) == {p2, p3}


def test_coordenadas_negativas():
    p1 = Ocorrencia(id="1", tipo="buraco", x=-10.0, y=-10.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=-9.8, y=-10.0)
    p3 = Ocorrencia(id="3", tipo="buraco", x=5.0, y=5.0)
    p4 = Ocorrencia(id="4", tipo="buraco", x=15.0, y=15.0)

    resultado = par_mais_proximo([p1, p2, p3, p4])

    assert math.isclose(resultado.distancia, 0.2)
    assert set(resultado.par) == {p1, p2}


def test_pontos_com_mesmo_x():
    pontos = [
        Ocorrencia(id="1", tipo="buraco", x=2.0, y=1.0),
        Ocorrencia(id="2", tipo="buraco", x=2.0, y=10.0),
        Ocorrencia(id="3", tipo="buraco", x=2.0, y=10.5),
        Ocorrencia(id="4", tipo="buraco", x=2.0, y=50.0),
    ]

    resultado = par_mais_proximo(pontos)
    assert math.isclose(resultado.distancia, 0.5)
    assert set(resultado.par) == {pontos[1], pontos[2]}


def test_filtro_por_categoria():
    pontos = [
        Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0),
        Ocorrencia(id="2", tipo="buraco", x=10.0, y=10.0),
        Ocorrencia(id="3", tipo="vazamento", x=0.0, y=0.0),
        Ocorrencia(id="4", tipo="vazamento", x=0.1, y=0.1),
    ]

    res_buracos = par_mais_proximo(pontos, categoria="buraco")
    assert set(res_buracos.par) == {pontos[0], pontos[1]}

    res_vazamentos = par_mais_proximo(pontos, categoria="vazamento")
    assert set(res_vazamentos.par) == {pontos[2], pontos[3]}


def test_filtro_categoria_invalida_ou_insuficiente():
    pontos = [
        Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0),
        Ocorrencia(id="2", tipo="buraco", x=1.0, y=1.0),
    ]

    with pytest.raises(ValueError, match="categoria deve ser uma string não vazia"):
        par_mais_proximo(pontos, categoria="")

    with pytest.raises(ValueError, match="pelo menos 2 ocorrências para a categoria 'inexistente'"):
        par_mais_proximo(pontos, categoria="inexistente")


def test_propriedades_do_par_mais_proximo():
    p1 = Ocorrencia(id="1", tipo="buraco", x=0.0, y=0.0)
    p2 = Ocorrencia(id="2", tipo="buraco", x=3.0, y=4.0)

    resultado = par_mais_proximo([p1, p2])

    pt1, pt2, dist = resultado
    assert pt1 in (p1, p2)
    assert pt2 in (p1, p2)
    assert math.isclose(dist, 5.0)

    assert resultado.eh_duplicata(limite_distancia=6.0) is True
    assert resultado.eh_duplicata(limite_distancia=5.0) is True
    assert resultado.eh_duplicata(limite_distancia=4.9) is False


def _validar_com_calculo_exaustivo(pontos):
    # A referência não usa funções do módulo, pois a recursão também usa força bruta.
    distancia_esperada = min(
        math.hypot(p2.x - p1.x, p2.y - p1.y)
        for p1, p2 in combinations(pontos, 2)
    )

    resultado = par_mais_proximo(pontos)

    assert resultado.distancia == pytest.approx(
        distancia_esperada, rel=1e-12, abs=1e-12
    )
    assert resultado.ponto1 is not resultado.ponto2
    assert any(resultado.ponto1 is ponto for ponto in pontos)
    assert any(resultado.ponto2 is ponto for ponto in pontos)
    # Em empates, qualquer par mínimo é válido, mas ele deve realizar a distância.
    distancia_do_par = math.hypot(
        resultado.ponto2.x - resultado.ponto1.x,
        resultado.ponto2.y - resultado.ponto1.y,
    )
    assert distancia_do_par == pytest.approx(
        distancia_esperada, rel=1e-12, abs=1e-12
    )


@pytest.mark.parametrize("tamanho", [2, 3, 4, 5, 16, 31, 64, 257, 1024, 2048])
@pytest.mark.parametrize("semente", [0, 42, 2026])
def test_equivalencia_com_calculo_exaustivo_conjuntos_aleatorios(tamanho, semente):
    rng = random.Random(semente)
    pontos = [
        Ocorrencia(
            id=f"pt_{i}",
            tipo="teste",
            x=rng.uniform(-1000.0, 1000.0),
            y=rng.uniform(-1000.0, 1000.0),
        )
        for i in range(tamanho)
    ]

    _validar_com_calculo_exaustivo(pontos)


@pytest.mark.parametrize(
    "coordenadas",
    [
        pytest.param(
            [(-50, -80), (-20, -30), (-19.9, -30.2), (-8, -2), (-1, -100)],
            id="apenas-coordenadas-negativas",
        ),
        pytest.param(
            [(-10, -10), (-0.1, -0.1), (0.1, 0.1), (10, 10), (-10, 10), (10, -10)],
            id="par-cruza-a-origem",
        ),
        pytest.param([(i * i - 128, -10) for i in range(17)], id="horizontal"),
        pytest.param([(-10, i * i - 128) for i in range(17)], id="vertical"),
        pytest.param([(i, 2 * i) for i in range(-16, 17)], id="colineares"),
        pytest.param(
            [(x, y) for x in range(-4, 4) for y in range(-4, 4)],
            id="grade-com-empates",
        ),
        pytest.param(
            [(-20, -20), (-10, -10), (0, -5), (0, -5), (10, 10), (20, 20)],
            id="duplicados-em-metades-distintas",
        ),
        pytest.param([(2, -3)] * 16, id="todos-coincidentes"),
        pytest.param(
            [(-10, -10), (-10, -10), (0, 0), (5, 5), (5, 5), (20, 20)],
            id="multiplos-pares-duplicados",
        ),
        pytest.param(
            [
                (-10, -40), (-9, -10), (-0.001, 0), (-0.0005, 15),
                (0.0005, 15.0001), (0.001, 0.01), (9, 10), (10, 40),
            ],
            id="par-minimo-na-faixa-central",
        ),
    ],
)
def test_equivalencia_com_calculo_exaustivo_casos_especiais(coordenadas):
    pontos = [
        Ocorrencia(id=str(i), tipo="teste", x=x, y=y)
        for i, (x, y) in enumerate(coordenadas)
    ]
    random.Random(42).shuffle(pontos)

    _validar_com_calculo_exaustivo(pontos)


def test_par_mais_proximo_arquivo_exemplo_csv():
    """Testa a identificação de ocorrências próximas nas categorias do arquivo de exemplo."""
    ocorrencias = carregar_ocorrencias_csv("data/ocorrencias_exemplo.csv")

    res_buraco = par_mais_proximo(ocorrencias, categoria="buraco")
    assert {res_buraco.ponto1.id, res_buraco.ponto2.id} == {"001", "002"}
    assert math.isclose(
        res_buraco.distancia,
        distancia_euclidiana((10.5, -3.0), (16.5, -3.0)),
    )

    res_vazamento = par_mais_proximo(ocorrencias, categoria="vazamento")
    assert {res_vazamento.ponto1.id, res_vazamento.ponto2.id} == {"004", "005"}

    res_lixo = par_mais_proximo(ocorrencias, categoria="descarte irregular de lixo")
    assert {res_lixo.ponto1.id, res_lixo.ponto2.id} == {"007", "008"}


def test_forca_bruta_rejeita_menos_de_dois_pontos():
    with pytest.raises(ValueError, match="pelo menos 2 ocorrências"):
        par_mais_proximo_forca_bruta([])
    with pytest.raises(ValueError, match="pelo menos 2 ocorrências"):
        par_mais_proximo_forca_bruta([Ocorrencia(id="1", tipo="t", x=0, y=0)])
