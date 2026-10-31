# PontoAlerta

**Número da Lista:** 2<br>
**Conteúdo da Disciplina:** Dividir e Conquistar

## Alunos

| Matrícula | Aluno |
| -- | -- |
| 23/1011838 | Tiago Antunes Balieiro |
| 23/1026714 | Euller Júlio da Silva |

## Apresentação do trabalho
[Link para o vídeo de apresentação](https://youtu.be/)

## Sobre

Projeto de Dividir e Conquistar para identificar possíveis registros duplicados
de ocorrências urbanas de uma mesma categoria, a partir de coordenadas no plano.

O sistema utiliza o algoritmo de Par de Pontos Mais Próximos (Closest Pair of
Points), com complexidade O(n log n). A análise pode ser executada pelo terminal
ou pela interface Streamlit, com gráficos em Matplotlib.

## Estado atual

O projeto contém o modelo `Ocorrencia` com validações, o carregamento de CSV,
o algoritmo de Par de Pontos Mais Próximos, as interfaces pelo terminal e pelo
Streamlit, a visualização com Matplotlib e um benchmark comparativo com força
bruta.

## Funcionamento e estratégia de Divisão e Conquista

O fluxo da análise é carregar e validar o CSV, selecionar uma categoria,
encontrar suas duas ocorrências mais próximas e apresentar os registros e a
distância euclidiana: `d(p, q) = sqrt((q.x - p.x)² + (q.y - p.y)²)`.
No Streamlit, essa distância também é comparada com um limite configurável
para sinalizar uma possível duplicação. O resultado contém um único par mais
próximo; não é uma lista de todos os pares dentro do limite.

O algoritmo está em `src/pontoalerta/par_proximo.py` e segue estas etapas:

1. **Preparar:** ordenar os pontos uma única vez por X e por Y, obtendo `Px` e
   `Py`. Se uma categoria for informada à função `par_mais_proximo`, a filtragem
   ocorre antes da ordenação. São necessários pelo menos dois pontos.
2. **Dividir:** separar `Px` em duas metades pelo índice central. Distribuir
   `Py` entre as mesmas metades, preservando sua ordem em Y. A pertença à metade
   usa a identidade dos objetos, permitindo separar pontos com X igual.
3. **Conquistar:** resolver recursivamente cada metade. Para até três pontos,
   comparar todos os pares por força bruta. Seja `delta` a menor distância
   encontrada nas duas metades.
4. **Combinar:** verificar os pares que cruzam a divisão. Um par com distância
   menor que `delta` só pode estar na faixa `abs(p.x - x_central) < delta`.
   A faixa é extraída de `Py`, portanto já está ordenada por Y. Para cada ponto,
   comparar no máximo os sete sucessores, interrompendo quando a diferença em Y
   for maior ou igual à melhor distância atual.

O limite de sete sucessores decorre da geometria do plano: em cada metade os
pontos já estão separados por pelo menos `delta`, o que limita quantos podem
ocupar a vizinhança relevante da faixa. Assim, a combinação faz um número
constante de comparações por ponto. Se `delta` for zero, o algoritmo retorna
imediatamente, pois não existe distância menor.

### Complexidade

Para `n` ocorrências da categoria analisada:

- A ordenação inicial de `Px` e `Py` custa **O(n log n)**.
- Cada chamada divide as listas e monta a faixa em **O(n)**. As consultas ao
  conjunto de identidades têm custo médio O(1).
- Na faixa, cada ponto é comparado com no máximo sete sucessores: **O(n)**.
- As duas chamadas recursivas operam sobre metades do conjunto:
  `T(n) = 2T(n/2) + O(n)`, com caso-base constante para `n ≤ 3`.
  Portanto, a recursão e o algoritmo completo custam **O(n log n)**.

Preservar a ordenação em Y durante a divisão é essencial: reordenar a faixa
em cada chamada elevaria o custo para O(n log² n). A força bruta isolada compara
`n(n - 1)/2` pares e custa O(n²).

O espaço auxiliar do algoritmo é **O(n)** para listas e conjuntos, com pilha de
recursão de profundidade O(log n). Se o CSV contém `N` registros e a categoria
selecionada contém `n`, carregar e filtrar os dados custa O(N), e a análise
completa até obter o par custa **O(N + n log n)**, sem contar a renderização.

## Requisitos e instalação

Python 3.10 ou superior. Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

No terminal linux, crie o ambiente com `python -m venv .venv`
e ative-o com `source .venv\bin\activate` antes de instalar as dependências.
As dependências são declaradas em `pyproject.toml`: Streamlit e Matplotlib para
a aplicação, e Pytest para desenvolvimento. Para instalar apenas a aplicação,
sem o Pytest, use `python -m pip install -e .` no último passo.

## Estrutura

```text
data/
    ocorrencias_exemplo.csv # Dados de entrada para a demonstração
src/pontoalerta/
    __init__.py
    __main__.py             # Execução com python -m pontoalerta
    app.py                  # Interface web com Streamlit
    benchmark.py            # Comparação de desempenho com força bruta
    cli.py                  # Interface pelo terminal
    distancia.py            # Distância euclidiana
    ocorrencia.py           # Modelo e validações dos registros
    leitura_csv.py          # Carregamento e validação do CSV
    par_proximo.py          # Algoritmo de divisão e conquista
    visualizacao.py         # Gráfico cartesiano e destaque do par mais próximo
tests/
    test_app.py
    test_benchmark.py
    test_cli.py
    test_distancia.py
    test_integracao.py
    test_ocorrencia.py
    test_leitura_csv.py
    test_par_proximo.py
    test_visualizacao.py
pyproject.toml              # Pacote, dependências e configuração do Pytest
```

## Carregamento de CSV

Na raiz do projeto, com o pacote instalado:

```python
from pontoalerta import carregar_ocorrencias_csv

ocorrencias = carregar_ocorrencias_csv("data/ocorrencias_exemplo.csv")
print(ocorrencias[0])
```

A função aceita um caminho textual, `pathlib.Path`, buffer de texto ou arquivo
enviado pelo Streamlit e retorna uma lista de objetos `Ocorrencia`, na ordem do
arquivo. O exemplo contém 60 registros, sendo 20 por categoria, incluindo pares
próximos para demonstrar a análise.

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

## Execução pelo terminal

Com o ambiente virtual ativo e o pacote instalado:

```bash
pontoalerta data/ocorrencias_exemplo.csv --categoria "buraco"
```

Também é possível executar como módulo, usando `-c` como abreviação:

```bash
python -m pontoalerta data/ocorrencias_exemplo.csv -c "descarte irregular de lixo"
```

O caminho do CSV e a categoria são obrigatórios. A categoria deve corresponder
ao campo `Tipo`, respeitando letras maiúsculas e minúsculas. Use aspas em nomes
de categorias ou caminhos com espaços. São necessárias pelo menos duas
ocorrências da categoria selecionada.

A saída apresenta a categoria, os IDs e as coordenadas dos dois registros mais
próximos, além da distância euclidiana, na mesma unidade das coordenadas.
Por exemplo, para a categoria `buraco`:

```text
Categoria: buraco
Pontos mais próximos:
  ID=001 | X=10.5 | Y=-3.0
  ID=002 | X=16.5 | Y=-3.0
Distância: 6.0
```

Consulte `pontoalerta --help` para ver os argumentos. O programa retorna código
`0` em caso de sucesso, `1` para erros de arquivo ou dados (exibidos em stderr)
e `2` para argumentos ausentes ou incorretos. Se o pacote já estava instalado
antes da adição deste comando, execute novamente `python -m pip install -e ".[dev]"`.

## Execução com Streamlit

Na raiz do repositório, com o ambiente virtual ativo e o pacote instalado:

```bash
python -m streamlit run src/pontoalerta/app.py
```

Abra o endereço exibido no terminal, normalmente `http://localhost:8501`.
Execute o comando na raiz para que a aplicação encontre
`data/ocorrencias_exemplo.csv` ao usar os dados de exemplo.

1. Na barra lateral, mantenha **Usar dados de exemplo** marcado ou envie um CSV
   com as colunas `ID,Tipo,X,Y`. O arquivo enviado tem prioridade sobre o exemplo.
2. Ajuste o **Limite de distância para indicação de duplicação**, inicialmente
   `1.0`, na mesma unidade das coordenadas.
3. Selecione a categoria a analisar. Ela precisa conter pelo menos dois registros.
4. Clique em **Executar Análise** para exibir a distância, os IDs, as coordenadas
   e o gráfico com o par mais próximo destacado.

Se a distância for menor ou igual ao limite, a interface sinaliza uma possível
duplicação; caso contrário, informa que a distância mínima supera o limite.
Com os dados de exemplo, a categoria `buraco` retorna os IDs `001` e `002`, com
distância de `6.0`. Para demonstrar o alerta, ajuste o limite para `6.0` ou mais;
com o limite padrão de `1.0`, esse par não é sinalizado como possível duplicação.
Essa indicação depende da distância e não confirma que os registros representam
a mesma ocorrência. Para encerrar o servidor, pressione `Ctrl+C` no terminal.

## Visualização gráfica

Use `--grafico` para salvar um gráfico da categoria analisada:

```bash
pontoalerta data/ocorrencias_exemplo.csv -c "buraco" --grafico buracos.png
```

Abra a imagem gerada para visualizar as ocorrências no plano cartesiano. Os
pontos aparecem em azul; o par mais próximo é destacado com estrelas vermelhas,
IDs e uma linha tracejada. O título informa a categoria e a distância mínima.
Os eixos X e Y usam a mesma escala para preservar as proporções das distâncias.
Pontos coincidentes recebem os dois IDs em posições diferentes.

O gráfico inclui apenas a categoria selecionada. O formato do arquivo é definido
pela extensão, como `.png`, `.svg` ou `.pdf`; a pasta de destino deve existir.
A geração do arquivo funciona sem abrir uma janela gráfica.

Também é possível criar uma figura Matplotlib para uso em Python:

```python
from pontoalerta import (
    carregar_ocorrencias_csv,
    criar_grafico_ocorrencias,
    par_mais_proximo,
)

ocorrencias = carregar_ocorrencias_csv("data/ocorrencias_exemplo.csv")
selecionadas = [p for p in ocorrencias if p.tipo == "buraco"]
resultado = par_mais_proximo(selecionadas)
figura = criar_grafico_ocorrencias(selecionadas, resultado)
figura.savefig("buracos.png")
```

## Benchmark

Para comparar Divisão e Conquista com força bruta usando pontos aleatórios:

```bash
pontoalerta-benchmark --tamanhos 100 500 1000 --limite-fb 1000 --grafico benchmark.png
```

O comando imprime os tempos em segundos e salva o gráfico no caminho informado.
A força bruta é executada apenas para tamanhos menores ou iguais a `--limite-fb`.
Os tempos variam conforme o ambiente; a justificativa de O(n log n) vem da
análise do algoritmo, não das medições isoladas.

## Testes

Com o ambiente virtual ativo e as dependências instaladas:

```bash
python -m pytest
```

Para executar apenas os testes de integração:

```bash
python -m pytest tests/test_integracao.py
```

Eles percorrem o fluxo de CSV até os resultados e gráficos no terminal e no
Streamlit, incluindo entradas inválidas, casos extremos e mudanças de categoria
e limite. O terminal é executado em um processo separado; o Streamlit usa
`AppTest`, simulando apenas a entrega do arquivo pelo widget de upload.
