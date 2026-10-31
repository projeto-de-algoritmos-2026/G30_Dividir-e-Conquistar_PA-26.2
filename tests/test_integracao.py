"""Fluxos de CSV até o resultado nas interfaces, com processamento real."""

import os
import subprocess
import sys
from io import BytesIO
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_APP = str(RAIZ / "src" / "pontoalerta" / "app.py")


def _imagens(app):
    # O nome do elemento de imagem varia entre versões do AppTest.
    return app.get("image") or app.get("imgs")


def _executar_cli(caminho, categoria, grafico):
    return subprocess.run(
        [
            sys.executable, "-m", "pontoalerta", str(caminho),
            "--categoria", categoria, "--grafico", str(grafico),
        ],
        cwd=RAIZ,
        env={**os.environ, "PYTHONPATH": str(RAIZ / "src")},
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.fixture
def csv_enviado(tmp_path, monkeypatch):
    caminho = tmp_path / "ocorrências urbanas.csv"
    upload = BytesIO()
    upload.name = caminho.name
    # Simula só a entrega do arquivo pelo widget, inclusive em versões antigas do AppTest.
    monkeypatch.setattr("streamlit.file_uploader", lambda *args, **kwargs: upload)
    return caminho, upload


@pytest.mark.parametrize(
    "coordenadas, ids, distancia",
    [
        pytest.param([(-3, -4), (0, 0)], ("001", "002"), 5.0, id="dois-pontos-negativos"),
        pytest.param(
            [(-30, -30), (-0.125, 5), (0.125, 5), (30, 30)],
            ("002", "003"), 0.25, id="par-cruza-faixa-central",
        ),
        pytest.param(
            [(2, 0), (2, 10), (2, 10.5), (2, 50)],
            ("002", "003"), 0.5, id="mesmo-x",
        ),
        pytest.param(
            [(-3, -4), (-3, -4), (10, 10), (20, 20)],
            ("001", "002"), 0.0, id="pontos-coincidentes",
        ),
    ],
)
def test_csv_ate_resultado_e_grafico_nas_duas_interfaces(
    csv_enviado, coordenadas, ids, distancia,
):
    caminho, upload = csv_enviado
    # BOM, colunas fora de ordem e registros invertidos exercitam a leitura e a ordenação.
    registros = [
        f"{y},{i:03d},descarte irregular de lixo,{x}\n"
        for i, (x, y) in enumerate(coordenadas, start=1)
    ]
    conteudo = "\ufeffY,ID,Tipo,X\n" + "".join(reversed(registros))
    conteudo += "0,901,vazamento,0\n0,902,vazamento,0\n"
    caminho.write_text(conteudo, encoding="utf-8")
    upload.write(caminho.read_bytes())
    grafico = caminho.with_suffix(".png")

    processo = _executar_cli(caminho, "descarte irregular de lixo", grafico)

    assert processo.returncode == 0, processo.stderr
    assert "Categoria: descarte irregular de lixo" in processo.stdout
    assert all(f"ID={identificador} |" in processo.stdout for identificador in ids)
    assert "ID=901" not in processo.stdout
    assert "ID=902" not in processo.stdout
    assert float(processo.stdout.split("Distância: ")[1]) == pytest.approx(distancia)
    assert grafico.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    app = AppTest.from_file(CAMINHO_APP).run()
    assert not app.exception
    app.selectbox[0].select("descarte irregular de lixo")
    app.number_input[0].set_value(distancia)
    app.button[0].click().run()

    assert not app.exception
    assert not app.error
    assert [metrica.value for metrica in app.metric] == [
        f"{distancia:.4f}", f"ID {ids[0]}", f"ID {ids[1]}",
    ]
    assert len(_imagens(app)) == 1
    assert any("Possível duplicação detectada" in aviso.value for aviso in app.warning)
    assert not app.success


@pytest.mark.parametrize(
    "conteudo, mensagem",
    [
        pytest.param(b"", "colunas ID, Tipo, X e Y", id="arquivo-vazio"),
        pytest.param(b"ID,Tipo,X\n001,buraco,0\n", "colunas ID, Tipo, X e Y", id="cabecalho"),
        pytest.param(b"ID,Tipo,X,Y\n", "", id="sem-registros"),
        pytest.param(b"ID,Tipo,X,Y\n001,buraco,0,0\n", "pelo menos 2", id="um-registro"),
        pytest.param(
            b"ID,Tipo,X,Y\n001,buraco,0,0\n002,buraco,3,4\n003,buraco,nan,0\n",
            "Linha 4:", id="invalido-apos-par-valido",
        ),
        pytest.param(b"ID,Tipo,X,Y\n001,buraco,0,inf\n", "Linha 2:", id="infinito"),
        pytest.param(b"ID,Tipo,X,Y\n001,buraco,abc,0\n", "Linha 2:", id="coordenada-textual"),
        pytest.param(b'ID,Tipo,X,Y\n001,"buraco,0,0\n', "CSV malformado", id="aspas-abertas"),
        pytest.param(b"ID,Tipo,X,Y\n001,buraco,0,\xff\n", "decode", id="utf8-invalido"),
    ],
)
def test_entradas_invalidas_nao_produzem_resultado_parcial(csv_enviado, conteudo, mensagem):
    caminho, upload = csv_enviado
    caminho.write_bytes(conteudo)
    upload.write(conteudo)
    grafico = caminho.with_suffix(".png")

    processo = _executar_cli(caminho, "buraco", grafico)

    assert processo.returncode == 1
    assert processo.stdout == ""
    assert "Erro:" in processo.stderr
    assert mensagem in processo.stderr
    assert "Traceback" not in processo.stderr
    assert not grafico.exists()

    app = AppTest.from_file(CAMINHO_APP).run()
    if app.button:
        app.button[0].click().run()

    assert not app.exception
    if conteudo == b"ID,Tipo,X,Y\n":
        assert any("Envie um arquivo CSV" in aviso.value for aviso in app.info)
    else:
        assert any(mensagem in erro.value for erro in app.error)
    assert not app.metric
    assert not _imagens(app)
    assert not app.warning
    assert not app.success


def test_streamlit_recalcula_ao_trocar_categoria_e_limite(csv_enviado):
    _, upload = csv_enviado
    upload.write(
        b"ID,Tipo,X,Y\n001,buraco,0,0\n002,buraco,3,4\n"
        b"003,vazamento,-2,-3\n004,vazamento,-2,-3\n005,isolada,0,0\n"
    )
    app = AppTest.from_file(CAMINHO_APP).run()
    app.number_input[0].set_value(5.0)
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].value == "5.0000"
    assert app.warning

    app.number_input[0].set_value(4.9).run()
    assert not app.metric
    assert not _imagens(app)
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].value == "5.0000"
    assert app.success
    assert not app.warning

    app.selectbox[0].select("vazamento").run()
    app.button[0].click().run()
    assert not app.exception
    assert [metrica.value for metrica in app.metric] == ["0.0000", "ID 003", "ID 004"]
    assert app.warning
    assert not app.success
    assert len(_imagens(app)) == 1

    app.selectbox[0].select("isolada").run()
    app.button[0].click().run()
    assert not app.exception
    assert any("pelo menos 2 ocorrências" in erro.value for erro in app.error)
    assert not app.metric
    assert not _imagens(app)
    assert not app.warning
    assert not app.success


def test_streamlit_sem_fonte_de_dados():
    app = AppTest.from_file(CAMINHO_APP).run()
    app.checkbox[0].uncheck().run()

    assert not app.exception
    assert any("Envie um arquivo CSV" in aviso.value for aviso in app.info)
    assert not app.button
    assert not app.metric
    assert not _imagens(app)
