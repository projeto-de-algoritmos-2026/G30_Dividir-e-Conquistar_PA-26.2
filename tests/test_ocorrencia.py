from dataclasses import FrozenInstanceError

import pytest

from pontoalerta import Ocorrencia


def test_cria_ocorrencia_preservando_id_e_coordenadas():
    ocorrencia = Ocorrencia(id="001", tipo="buraco", x=0, y=-3.5)

    assert ocorrencia.id == "001"
    assert ocorrencia.tipo == "buraco"
    assert ocorrencia.x == 0
    assert ocorrencia.y == -3.5


@pytest.mark.parametrize("campo", ["id", "tipo"])
@pytest.mark.parametrize("valor", ["", " ", "\t\n"])
def test_rejeita_texto_vazio(campo, valor):
    dados = dict(id="001", tipo="buraco", x=1, y=2)
    dados[campo] = valor

    with pytest.raises(ValueError, match=campo):
        Ocorrencia(**dados)


@pytest.mark.parametrize("campo", ["id", "tipo"])
@pytest.mark.parametrize("valor", [None, 1])
def test_rejeita_campo_textual_com_tipo_incorreto(campo, valor):
    dados = dict(id="001", tipo="buraco", x=1, y=2)
    dados[campo] = valor

    with pytest.raises(TypeError, match=campo):
        Ocorrencia(**dados)


@pytest.mark.parametrize("campo", ["x", "y"])
@pytest.mark.parametrize("valor", [None, "1.5", True, False])
def test_rejeita_coordenada_com_tipo_incorreto(campo, valor):
    dados = dict(id="001", tipo="buraco", x=1, y=2)
    dados[campo] = valor

    with pytest.raises(TypeError, match=campo):
        Ocorrencia(**dados)


@pytest.mark.parametrize("campo", ["x", "y"])
@pytest.mark.parametrize("valor", [float("nan"), float("inf"), -float("inf")])
def test_rejeita_coordenada_nao_finita(campo, valor):
    dados = dict(id="001", tipo="buraco", x=1, y=2)
    dados[campo] = valor

    with pytest.raises(ValueError, match=campo):
        Ocorrencia(**dados)


def test_impede_alteracao_de_ocorrencia_validada():
    ocorrencia = Ocorrencia(id="001", tipo="buraco", x=1, y=2)

    with pytest.raises(FrozenInstanceError):
        ocorrencia.x = float("nan")
