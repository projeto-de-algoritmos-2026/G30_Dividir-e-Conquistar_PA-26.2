from pathlib import Path
import pytest
from matplotlib.figure import Figure

from pontoalerta import (
    Ocorrencia,
    executar_benchmark,
    gerar_grafico_benchmark,
    gerar_pontos_aleatorios,
)
from pontoalerta.benchmark import main, medir_tempo_execucao


def test_gerar_pontos_aleatorios_quantidade_e_tipo():
    pontos = gerar_pontos_aleatorios(25, seed=123)
    assert len(pontos) == 25
    assert all(isinstance(p, Ocorrencia) for p in pontos)
    # IDs únicos e sequenciais
    ids = [p.id for p in pontos]
    assert len(set(ids)) == 25


def test_gerar_pontos_aleatorios_determinismo():
    pts1 = gerar_pontos_aleatorios(10, seed=99)
    pts2 = gerar_pontos_aleatorios(10, seed=99)
    assert pts1 == pts2


def test_gerar_pontos_rejeita_quantidade_negativa():
    with pytest.raises(ValueError, match="não-negativa"):
        gerar_pontos_aleatorios(-1)


def test_medir_tempo_execucao():
    tempo = medir_tempo_execucao(lambda: sum(range(1000)), repeticoes=2)
    assert isinstance(tempo, float)
    assert tempo >= 0.0

    with pytest.raises(ValueError, match="pelo menos 1"):
        medir_tempo_execucao(lambda: None, repeticoes=0)


def test_executar_benchmark_com_tamanhos_pequenos():
    tamanhos = [10, 20, 30]
    dados = executar_benchmark(tamanhos=tamanhos, limite_forca_bruta=20, repeticoes=1)

    assert dados["tamanhos"] == tamanhos
    assert len(dados["tempos_dc"]) == 3
    assert all(t > 0 for t in dados["tempos_dc"])

    assert dados["tamanhos_fb"] == [10, 20]
    assert len(dados["tempos_fb"]) == 2


def test_gerar_grafico_benchmark(tmp_path):
    dados = {
        "tamanhos": [10, 20, 30],
        "tempos_dc": [0.0001, 0.0002, 0.0003],
        "tamanhos_fb": [10, 20],
        "tempos_fb": [0.0001, 0.0004],
    }

    caminho = tmp_path / "grafico_benchmark.png"
    figura = gerar_grafico_benchmark(dados, salvar_caminho=caminho)

    assert isinstance(figura, Figure)
    assert caminho.exists()
    assert caminho.stat().st_size > 0


def test_cli_benchmark(tmp_path, capsys):
    caminho_grafico = tmp_path / "saida_bench.png"
    codigo = main(
        [
            "--tamanhos", "10", "20",
            "--limite-fb", "15",
            "--grafico", str(caminho_grafico),
        ]
    )

    assert codigo == 0
    saida = capsys.readouterr().out
    assert "Resultados do Benchmark" in saida
    assert caminho_grafico.exists()
