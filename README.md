# PontoAlerta

Projeto de Divisão e Conquista para identificar possíveis registros duplicados
de ocorrências urbanas de uma mesma categoria, a partir de coordenadas no plano.

O sistema utilizará o algoritmo de Par de Pontos Mais Próximos (Closest Pair of
Points), com complexidade esperada de O(n log n). A demonstração será feita com
Streamlit e gráficos em Matplotlib.

## Estado atual

Esta etapa contém a estrutura inicial, a configuração das dependências, o
modelo `Ocorrencia` com validações e o carregamento de arquivos CSV. O algoritmo
e a interface serão implementados nas próximas etapas.

## Requisitos e instalação

Python 3.10 ou superior. Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

No Windows, ative o ambiente com `.venv\Scripts\activate`.
As dependências são declaradas em `pyproject.toml`: Streamlit e Matplotlib para
a aplicação, e Pytest para desenvolvimento.

## Estrutura

```text
data/
    ocorrencias_exemplo.csv # Dados de entrada para a demonstração
src/pontoalerta/
    __init__.py
    ocorrencia.py           # Modelo e validações dos registros
    leitura_csv.py          # Carregamento e validação do CSV
tests/
    test_ocorrencia.py
    test_leitura_csv.py
pyproject.toml              # Pacote, dependências e configuração do Pytest
```

## Modelo de ocorrência

```python
from pontoalerta import Ocorrencia

ocorrencia = Ocorrencia(id="001", tipo="buraco", x=10.5, y=-3.0)
```

- `id` e `tipo` devem ser textos não vazios, contendo algum caractere que não
  seja espaço. O ID textual preserva zeros à esquerda.
- `x` e `y` devem ser números `int` ou `float` finitos. Valores negativos e zero
  são permitidos; booleanos, textos, NaN e infinito são rejeitados.
- Tipos incorretos geram `TypeError`; valores inválidos geram `ValueError`.
- As ocorrências são imutáveis após a criação, preservando as validações.

As coordenadas representam um plano cartesiano e devem usar a mesma unidade.
O CSV deve ter as colunas `ID,Tipo,X,Y`, por exemplo:

```csv
ID,Tipo,X,Y
001,buraco,10.5,-3.0
002,buraco,11.0,-3.2
003,vazamento,25.0,12.0
```

## Carregamento de CSV

Na raiz do projeto, com o pacote instalado:

```python
from pontoalerta import carregar_ocorrencias_csv

ocorrencias = carregar_ocorrencias_csv("data/ocorrencias_exemplo.csv")
print(ocorrencias[0])
```

A função aceita um caminho textual ou `pathlib.Path` e retorna uma lista de
objetos `Ocorrencia`, na ordem do arquivo. O exemplo contém nove registros em
três categorias, incluindo pares próximos para as próximas etapas.

- Use UTF-8 (com ou sem BOM), vírgula como separador e ponto decimal.
- O cabeçalho deve conter exatamente `ID`, `Tipo`, `X` e `Y`, em qualquer ordem,
  respeitando letras maiúsculas e minúsculas.
- Os IDs permanecem textuais; as coordenadas são convertidas para `float` e
  passam pelas validações do modelo.
- Linhas vazias são ignoradas. Um arquivo apenas com cabeçalho retorna `[]`;
  um arquivo totalmente vazio é rejeitado por não ter cabeçalho.
- Cabeçalhos, registros e formatação inválidos geram `ValueError`. Erros nos
  registros indicam a linha do arquivo e interrompem a carga, sem retorno parcial.
- Erros de acesso ao arquivo, como `FileNotFoundError`, são propagados.

## Testes

Com o ambiente virtual ativo e as dependências instaladas:

```bash
python -m pytest
```
