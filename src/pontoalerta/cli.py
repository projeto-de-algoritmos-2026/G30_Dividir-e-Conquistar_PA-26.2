"""Interface de execução do PontoAlerta pelo terminal."""

import argparse
import sys

from .leitura_csv import carregar_ocorrencias_csv
from .par_proximo import par_mais_proximo


def main(argv: list[str] | None = None) -> int:
    """Execute a análise de um CSV e retorne o código de saída."""
    parser = argparse.ArgumentParser(
        prog="pontoalerta",
        description="Encontra as duas ocorrências mais próximas de uma categoria.",
    )
    parser.add_argument("arquivo", help="Caminho do CSV com as colunas ID, Tipo, X e Y.")
    parser.add_argument(
        "-c", "--categoria", required=True, help="Categoria a analisar, conforme o campo Tipo."
    )
    args = parser.parse_args(argv)

    try:
        ocorrencias = carregar_ocorrencias_csv(args.arquivo)
        resultado = par_mais_proximo(ocorrencias, categoria=args.categoria)
    except (OSError, ValueError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1

    print(f"Categoria: {args.categoria}")
    print("Pontos mais próximos:")
    for ponto in resultado.par:
        print(f"  ID={ponto.id} | X={ponto.x} | Y={ponto.y}")
    print(f"Distância: {resultado.distancia}")
    return 0
