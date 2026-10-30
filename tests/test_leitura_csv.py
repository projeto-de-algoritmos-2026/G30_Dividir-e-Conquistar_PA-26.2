from pathlib import Path

import pytest

from pontoalerta import Ocorrencia, carregar_ocorrencias_csv


@pytest.mark.parametrize(
    "conteudo",
    [
        "ID,Tipo,X,Y\n001,buraco,0,-3.5\n\n002,vazamento,10.5,2\n",
        '\ufeffY,ID,X,Tipo\r\n-3.5,001,0,buraco\r\n2,002,10.5,vazamento\r\n',
    ],
)
def test_carrega_ocorrencias_preservando_ids_e_ordem(tmp_path, conteudo):
    caminho = tmp_path / "ocorrencias.csv"
    caminho.write_text(conteudo, encoding="utf-8")

    assert carregar_ocorrencias_csv(caminho) == [
        Ocorrencia(id="001", tipo="buraco", x=0.0, y=-3.5),
        Ocorrencia(id="002", tipo="vazamento", x=10.5, y=2.0),
    ]


def test_aceita_caminho_textual_e_categoria_entre_aspas(tmp_path):
    caminho = tmp_path / "ocorrencias.csv"
    caminho.write_text('ID,Tipo,X,Y\n001,"lixo, construção",1,2\n', encoding="utf-8")

    ocorrencias = carregar_ocorrencias_csv(str(caminho))

    assert ocorrencias == [Ocorrencia("001", "lixo, construção", 1.0, 2.0)]


def test_csv_apenas_com_cabecalho_retorna_lista_vazia(tmp_path):
    caminho = tmp_path / "ocorrencias.csv"
    caminho.write_text("ID,Tipo,X,Y\n", encoding="utf-8")

    assert carregar_ocorrencias_csv(caminho) == []


@pytest.mark.parametrize(
    "conteudo",
    ["", "ID,Tipo,X\n", "ID,Tipo,X,X\n", "ID,Tipo,X,Y,Extra\n", "id,tipo,x,y\n"],
)
def test_rejeita_cabecalho_invalido(tmp_path, conteudo):
    caminho = tmp_path / "ocorrencias.csv"
    caminho.write_text(conteudo, encoding="utf-8")

    with pytest.raises(ValueError, match="colunas ID, Tipo, X e Y"):
        carregar_ocorrencias_csv(caminho)


@pytest.mark.parametrize(
    "registro",
    [
        ",buraco,1,2",
        "002, ,1,2",
        "002,buraco,abc,2",
        "002,buraco,1,",
        "002,buraco,nan,2",
        "002,buraco,1,inf",
        "002,buraco,-inf,2",
        "002,buraco,1",
        "002,buraco,1,2,extra",
    ],
)
def test_rejeita_registro_invalido_informando_linha(tmp_path, registro):
    caminho = tmp_path / "ocorrencias.csv"
    caminho.write_text(
        f"ID,Tipo,X,Y\n001,buraco,0,0\n{registro}\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Linha 3:"):
        carregar_ocorrencias_csv(caminho)


def test_rejeita_csv_com_aspas_nao_fechadas(tmp_path):
    caminho = tmp_path / "ocorrencias.csv"
    caminho.write_text('ID,Tipo,X,Y\n001,"buraco,1,2\n', encoding="utf-8")

    with pytest.raises(ValueError, match="CSV malformado na linha"):
        carregar_ocorrencias_csv(caminho)


def test_propaga_erro_de_arquivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        carregar_ocorrencias_csv(tmp_path / "inexistente.csv")


def test_carrega_arquivo_de_exemplo_do_projeto():
    caminho = Path(__file__).resolve().parents[1] / "data" / "ocorrencias_exemplo.csv"

    ocorrencias = carregar_ocorrencias_csv(caminho)

    assert ocorrencias
    assert all(isinstance(ocorrencia, Ocorrencia) for ocorrencia in ocorrencias)
    assert len({ocorrencia.tipo for ocorrencia in ocorrencias}) == 3
