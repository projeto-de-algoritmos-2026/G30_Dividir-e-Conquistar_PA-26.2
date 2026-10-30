"""Benchmark e análise de desempenho do algoritmo de Divisão e Conquista."""

import argparse
import random
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from matplotlib.figure import Figure

from .ocorrencia import Ocorrencia
from .par_proximo import par_mais_proximo, par_mais_proximo_forca_bruta


def gerar_pontos_aleatorios(quantidade: int, seed: int = 42) -> list[Ocorrencia]:
    """Gera uma lista com a quantidade indicada de ocorrências aleatórias no plano."""
    if quantidade < 0:
        raise ValueError("A quantidade de pontos deve ser não-negativa.")

    rng = random.Random(seed)
    return [
        Ocorrencia(
            id=f"{i:05d}",
            tipo="gerada",
            x=round(rng.uniform(-1000.0, 1000.0), 3),
            y=round(rng.uniform(-1000.0, 1000.0), 3),
        )
        for i in range(quantidade)
    ]


def medir_tempo_execucao(funcao: Callable[[], Any], repeticoes: int = 3) -> float:
    """Mede e retorna o menor tempo de execução da função em segundos."""
    if repeticoes < 1:
        raise ValueError("O número de repetições deve ser pelo menos 1.")

    tempos = []
    for _ in range(repeticoes):
        inicio = time.perf_counter()
        funcao()
        fim = time.perf_counter()
        tempos.append(fim - inicio)
    return min(tempos)


def executar_benchmark(
    tamanhos: list[int] | None = None,
    limite_forca_bruta: int = 2000,
    seed: int = 42,
    repeticoes: int = 2,
) -> dict[str, Any]:
    """Executa o benchmark comparativo entre Divisão e Conquista e Força Bruta.

    Retorna um dicionário contendo os tamanhos testados e os respectivos tempos.
    """
    if tamanhos is None:
        tamanhos = [100, 250, 500, 1000, 2000, 4000, 8000]

    tempos_dc = []
    tempos_fb = []
    tamanhos_fb = []

    for n in tamanhos:
        pontos = gerar_pontos_aleatorios(n, seed=seed + n)

        # Divisão e Conquista O(n log n)
        tempo_dc = medir_tempo_execucao(
            lambda: par_mais_proximo(pontos), repeticoes=repeticoes
        )
        tempos_dc.append(tempo_dc)

        # Força Bruta O(n^2), limitada para evitar tempos excessivos
        if n <= limite_forca_bruta:
            tempo_fb = medir_tempo_execucao(
                lambda: par_mais_proximo_forca_bruta(pontos), repeticoes=repeticoes
            )
            tempos_fb.append(tempo_fb)
            tamanhos_fb.append(n)

    return {
        "tamanhos": tamanhos,
        "tempos_dc": tempos_dc,
        "tamanhos_fb": tamanhos_fb,
        "tempos_fb": tempos_fb,
    }


def gerar_grafico_benchmark(
    dados: dict[str, Any], salvar_caminho: str | Path | None = None
) -> Figure:
    """Gera um gráfico comparativo de desempenho e opcionalmente salva em disco."""
    figura = Figure(figsize=(9, 5.5), layout="constrained")
    eixo = figura.subplots()

    eixo.plot(
        dados["tamanhos"],
        dados["tempos_dc"],
        marker="o",
        color="#2563eb",
        linewidth=2,
        label="Divisão e Conquista — O(n log n)",
    )

    if dados.get("tempos_fb"):
        eixo.plot(
            dados["tamanhos_fb"],
            dados["tempos_fb"],
            marker="s",
            color="#dc2626",
            linestyle="--",
            linewidth=2,
            label="Força Bruta — O(n²)",
        )

    eixo.set_title("Desempenho do Algoritmo de Par Mais Próximo", fontsize=13)
    eixo.set_xlabel("Quantidade de Pontos (n)", fontsize=11)
    eixo.set_ylabel("Tempo de Execução (segundos)", fontsize=11)
    eixo.grid(True, alpha=0.3)
    eixo.legend(fontsize=10)

    if salvar_caminho:
        caminho = Path(salvar_caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        figura.savefig(caminho)

    return figura


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada de linha de comando para o benchmark."""
    parser = argparse.ArgumentParser(
        prog="pontoalerta-benchmark",
        description="Executa o benchmark de desempenho do algoritmo de Par Mais Próximo.",
    )
    parser.add_argument(
        "--tamanhos",
        nargs="+",
        type=int,
        default=[100, 250, 500, 1000, 2000, 4000],
        help="Lista de quantidades de pontos para teste (ex.: 100 500 1000).",
    )
    parser.add_argument(
        "--limite-fb",
        type=int,
        default=2000,
        help="Tamanho máximo de pontos para executar o algoritmo de Força Bruta O(n²).",
    )
    parser.add_argument(
        "--grafico",
        metavar="ARQUIVO.png",
        help="Caminho para salvar o gráfico gerado (ex.: benchmark.png).",
    )
    args = parser.parse_args(argv)

    print("Executando benchmark...")
    dados = executar_benchmark(
        tamanhos=args.tamanhos, limite_forca_bruta=args.limite_fb
    )

    print("\nResultados do Benchmark:")
    print(f"{'n':>8} | {'D&C (s)':>12} | {'Força Bruta (s)':>16}")
    print("-" * 42)

    fb_map = dict(zip(dados["tamanhos_fb"], dados["tempos_fb"]))
    for n, t_dc in zip(dados["tamanhos"], dados["tempos_dc"]):
        t_fb_str = f"{fb_map[n]:.6f}" if n in fb_map else "N/A"
        print(f"{n:>8} | {t_dc:>12.6f} | {t_fb_str:>16}")

    if args.grafico:
        gerar_grafico_benchmark(dados, salvar_caminho=args.grafico)
        print(f"\nGráfico salvo em: {args.grafico}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
