from pathlib import Path

import pytest

from pontoalerta.cli import main


@pytest.fixture
def caminho_csv(tmp_path):
    caminho = tmp_path / "ocorrencias urbanas.csv"
    caminho.write_text(
        "ID,Tipo,X,Y\n001,buraco,0,0\n002,buraco,3,4\n003,vazamento,0,0\n",
        encoding="utf-8",
    )
    return caminho


def test_exibe_par_e_distancia_apenas_da_categoria_selecionada(caminho_csv, capsys):
    codigo = main([str(caminho_csv), "--categoria", "buraco"])

    saida = capsys.readouterr()
    assert codigo == 0
    assert "Categoria: buraco" in saida.out
    assert "ID=001 | X=0.0 | Y=0.0" in saida.out
    assert "ID=002 | X=3.0 | Y=4.0" in saida.out
    assert "ID=003" not in saida.out
    assert "Distância: 5.0" in saida.out
    assert saida.err == ""


@pytest.mark.parametrize(
    "categoria, ids, distancia",
    [
        ("buraco", ("001", "002"), 0.5385164807134504),
        ("vazamento", ("004", "005"), 0.3605551275463989),
        ("descarte irregular de lixo", ("007", "008"), 0.223606797749979),
    ],
)
def test_analisa_categorias_do_csv_de_exemplo(categoria, ids, distancia, capsys):
    caminho = Path(__file__).resolve().parents[1] / "data" / "ocorrencias_exemplo.csv"

    assert main([str(caminho), "-c", categoria]) == 0

    saida = capsys.readouterr()
    assert f"Categoria: {categoria}" in saida.out
    assert all(f"ID={identificador}" in saida.out for identificador in ids)
    assert float(saida.out.split("Distância: ")[1]) == pytest.approx(distancia)
    assert saida.err == ""


@pytest.mark.parametrize("categoria", ["inexistente", "vazamento", ""])
def test_informa_erro_para_categoria_invalida_ou_insuficiente(caminho_csv, categoria, capsys):
    assert main([str(caminho_csv), "--categoria", categoria]) == 1

    saida = capsys.readouterr()
    assert saida.out == ""
    assert "Erro:" in saida.err
    assert "Traceback" not in saida.err


def test_informa_erro_para_arquivo_inexistente(tmp_path, capsys):
    caminho = tmp_path / "inexistente.csv"

    assert main([str(caminho), "-c", "buraco"]) == 1

    saida = capsys.readouterr()
    assert saida.out == ""
    assert "Erro:" in saida.err
    assert "inexistente.csv" in saida.err


@pytest.mark.parametrize(
    "conteudo",
    [
        b"",
        b"ID,Tipo,X,Y\n",
        b"ID,Tipo,X\n001,buraco,1\n",
        b"ID,Tipo,X,Y\n001,buraco,nan,0\n",
        b'ID,Tipo,X,Y\n001,"buraco,1,2\n',
        b"ID,Tipo,X,Y\n001,buraco,1,\xff\n",
    ],
)
def test_informa_erro_para_csv_invalido_ou_sem_ocorrencias(tmp_path, conteudo, capsys):
    caminho = tmp_path / "invalido.csv"
    caminho.write_bytes(conteudo)

    assert main([str(caminho), "-c", "buraco"]) == 1

    saida = capsys.readouterr()
    assert saida.out == ""
    assert "Erro:" in saida.err
    assert "Traceback" not in saida.err


@pytest.mark.parametrize("argumentos", [[], ["arquivo.csv"], ["-c", "buraco"]])
def test_exige_arquivo_e_categoria(argumentos, capsys):
    with pytest.raises(SystemExit) as erro:
        main(argumentos)

    assert erro.value.code == 2
    assert capsys.readouterr().err


def test_exibe_ajuda(capsys):
    with pytest.raises(SystemExit) as erro:
        main(["--help"])

    assert erro.value.code == 0
    saida = capsys.readouterr()
    assert "--categoria" in saida.out
    assert "arquivo" in saida.out
    assert saida.err == ""


def test_salva_grafico_da_categoria_selecionada(caminho_csv, tmp_path, capsys, monkeypatch):
    from pontoalerta import cli

    criar_grafico = cli.criar_grafico_ocorrencias
    pontos_plotados = []

    def capturar_ocorrencias(ocorrencias, resultado):
        pontos_plotados.extend(ocorrencias)
        return criar_grafico(ocorrencias, resultado)

    monkeypatch.setattr(cli, "criar_grafico_ocorrencias", capturar_ocorrencias)
    destino = tmp_path / "grafico de buracos.png"

    assert main([str(caminho_csv), "-c", "buraco", "--grafico", str(destino)]) == 0

    assert [p.id for p in pontos_plotados] == ["001", "002"]
    assert destino.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert "Distância: 5.0" in capsys.readouterr().out


def test_informa_erro_quando_nao_consegue_salvar_grafico(caminho_csv, tmp_path, capsys):
    destino = tmp_path / "pasta_inexistente" / "grafico.png"

    assert main([str(caminho_csv), "-c", "buraco", "--grafico", str(destino)]) == 1

    saida = capsys.readouterr()
    assert saida.out == ""
    assert "Erro:" in saida.err
    assert "Traceback" not in saida.err
