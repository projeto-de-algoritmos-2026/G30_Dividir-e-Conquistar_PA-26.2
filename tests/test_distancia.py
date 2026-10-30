import math
import pytest

from pontoalerta import Ocorrencia
from pontoalerta.distancia import distancia_euclidiana


def test_distancia_entre_mesmo_ponto_e_zero():
    p1 = Ocorrencia(id="001", tipo="buraco", x=10.0, y=20.0)
    assert distancia_euclidiana(p1, p1) == 0.0
    assert distancia_euclidiana((5.0, 5.0), (5.0, 5.0)) == 0.0


def test_distancia_triangulo_pitagorico():
    # Triângulo 3-4-5
    p1 = Ocorrencia(id="001", tipo="buraco", x=0.0, y=0.0)
    p2 = Ocorrencia(id="002", tipo="buraco", x=3.0, y=4.0)
    assert math.isclose(distancia_euclidiana(p1, p2), 5.0)


def test_distancia_com_tuplas_e_listas():
    assert math.isclose(distancia_euclidiana((0, 0), (6, 8)), 10.0)
    assert math.isclose(distancia_euclidiana([1.0, 2.0], [4.0, 6.0]), 5.0)


def test_distancia_mista_ocorrencia_e_tupla():
    p1 = Ocorrencia(id="001", tipo="buraco", x=1.0, y=1.0)
    p2 = (4.0, 5.0)
    assert math.isclose(distancia_euclidiana(p1, p2), 5.0)
    assert math.isclose(distancia_euclidiana(p2, p1), 5.0)


def test_simetria_da_distancia():
    p1 = Ocorrencia(id="001", tipo="buraco", x=-12.5, y=34.2)
    p2 = Ocorrencia(id="002", tipo="vazamento", x=7.8, y=-15.3)
    assert distancia_euclidiana(p1, p2) == distancia_euclidiana(p2, p1)


def test_distancia_coordenadas_negativas():
    p1 = (-2.0, -3.0)
    p2 = (1.0, 1.0)
    assert math.isclose(distancia_euclidiana(p1, p2), 5.0)


def test_distancia_eixos_horizontal_e_vertical():
    # Apenas variação em X
    assert math.isclose(distancia_euclidiana((2.0, 5.0), (7.0, 5.0)), 5.0)
    # Apenas variação em Y
    assert math.isclose(distancia_euclidiana((3.0, -2.0), (3.0, 8.0)), 10.0)


@pytest.mark.parametrize(
    "ponto_invalido",
    [
        None,
        "coordenada",
        123,
        (1.0,),
        (1.0, 2.0, 3.0),
        [],
        [1.0],
    ],
)
def test_rejeita_ponto_com_formato_ou_tipo_invalido(ponto_invalido):
    p_valido = (0.0, 0.0)
    with pytest.raises(TypeError, match="Ponto inválido"):
        distancia_euclidiana(ponto_invalido, p_valido)
    with pytest.raises(TypeError, match="Ponto inválido"):
        distancia_euclidiana(p_valido, ponto_invalido)


@pytest.mark.parametrize(
    "coordenada_booleana",
    [(True, 1.0), (0.0, False), [True, False]],
)
def test_rejeita_coordenadas_booleanas(coordenada_booleana):
    with pytest.raises(TypeError, match="deve ser int ou float"):
        distancia_euclidiana(coordenada_booleana, (0.0, 0.0))


@pytest.mark.parametrize(
    "coordenada_nao_finita",
    [
        (float("nan"), 1.0),
        (0.0, float("inf")),
        (-float("inf"), 2.0),
    ],
)
def test_rejeita_coordenadas_nao_finitas(coordenada_nao_finita):
    with pytest.raises(ValueError, match="deve ser finita"):
        distancia_euclidiana(coordenada_nao_finita, (0.0, 0.0))
