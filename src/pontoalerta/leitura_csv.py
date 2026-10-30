"""Carregamento de ocorrências a partir de arquivos CSV."""

import csv
import io
from contextlib import nullcontext
from pathlib import Path
from typing import Any

from .ocorrencia import Ocorrencia


def carregar_ocorrencias_csv(
    origem: str | Path | io.StringIO | io.TextIOBase | Any,
) -> list[Ocorrencia]:
    """Leia um CSV UTF-8 com as colunas ID, Tipo, X e Y, em qualquer ordem.

    Aceita caminho textual, pathlib.Path, buffer de texto ou UploadedFile do Streamlit.
    Dados inválidos geram ValueError, sem retornar uma lista parcial.
    Erros de acesso ao arquivo são propagados ao chamador.
    """
    if isinstance(origem, (str, Path)):
        contexto = Path(origem).open(encoding="utf-8-sig", newline="")
    elif isinstance(origem, (io.StringIO, io.TextIOBase)):
        contexto = nullcontext(origem)
    elif hasattr(origem, "getvalue"):
        valor = origem.getvalue()
        if isinstance(valor, bytes):
            texto = valor.decode("utf-8-sig")
        else:
            texto = str(valor)
        contexto = nullcontext(io.StringIO(texto))
    else:
        raise TypeError(f"Origem inválida para leitura de CSV: {type(origem).__name__}")

    with contexto as arquivo:
        leitor = csv.DictReader(arquivo, strict=True)
        try:
            cabecalho = leitor.fieldnames
            if (
                cabecalho is None
                or len(cabecalho) != 4
                or set(cabecalho) != {"ID", "Tipo", "X", "Y"}
            ):
                raise ValueError("O CSV deve conter exatamente as colunas ID, Tipo, X e Y.")

            ocorrencias = []
            for linha in leitor:
                if None in linha or any(valor is None for valor in linha.values()):
                    raise ValueError(
                        f"Linha {leitor.line_num}: quantidade de campos inválida."
                    )
                try:
                    ocorrencia = Ocorrencia(
                        id=linha["ID"],
                        tipo=linha["Tipo"],
                        x=float(linha["X"]),
                        y=float(linha["Y"]),
                    )
                except ValueError as erro:
                    raise ValueError(f"Linha {leitor.line_num}: {erro}") from erro
                ocorrencias.append(ocorrencia)
        except csv.Error as erro:
            raise ValueError(
                f"CSV malformado na linha {leitor.line_num}: {erro}"
            ) from erro

    return ocorrencias
