"""Interface web do PontoAlerta construída com Streamlit."""

from pathlib import Path
import streamlit as st

from pontoalerta.leitura_csv import carregar_ocorrencias_csv
from pontoalerta.par_proximo import par_mais_proximo
from pontoalerta.visualizacao import criar_grafico_ocorrencias


def carregar_dados(arquivo_upload, usar_exemplo: bool):
    """Carrega as ocorrências a partir do arquivo enviado ou do arquivo de exemplo."""
    if arquivo_upload is not None:
        try:
            return carregar_ocorrencias_csv(arquivo_upload), arquivo_upload.name
        except ValueError as erro:
            st.error(f"Erro ao ler CSV: {erro}")
            return [], ""
    if usar_exemplo:
        caminho_exemplo = Path("data/ocorrencias_exemplo.csv")
        if caminho_exemplo.exists():
            return carregar_ocorrencias_csv(caminho_exemplo), "data/ocorrencias_exemplo.csv"
        st.error("Arquivo de exemplo 'data/ocorrencias_exemplo.csv' não encontrado.")
        return [], ""
    return [], ""


def main() -> None:
    """Renderiza a aplicação Streamlit do PontoAlerta."""
    st.set_page_config(
        page_title="PontoAlerta — Identificação de Ocorrências",
        page_icon="📍",
        layout="wide",
    )

    st.title("📍 PontoAlerta")
    st.subheader("Identificação de ocorrências urbanas próximas por Divisão e Conquista")
    st.markdown(
        """
        O **PontoAlerta** identifica registros urbanos duplicados ou muito próximos
        dentro de uma mesma categoria utilizando o algoritmo de
        **Par de Pontos Mais Próximos** com complexidade $O(n \\log n)$.
        """
    )

    with st.sidebar:
        st.header("📂 Dados de Entrada")
        arquivo_upload = st.file_uploader(
            "Carregar arquivo CSV com ocorrências",
            type=["csv"],
            help="O arquivo deve conter as colunas ID, Tipo, X e Y.",
        )
        usar_exemplo = st.checkbox(
            "Usar dados de exemplo (data/ocorrencias_exemplo.csv)",
            value=arquivo_upload is None,
        )

        st.header("⚙️ Configurações")
        limite_duplicacao = st.number_input(
            "Limite de distância para indicação de duplicação:",
            min_value=0.0,
            value=1.0,
            step=0.1,
            format="%.2f",
            help="Pares com distância menor ou igual a este limite serão sinalizados como possíveis duplicações.",
        )

    ocorrencias, origem = carregar_dados(arquivo_upload, usar_exemplo)

    if not ocorrencias:
        st.info("Envie um arquivo CSV pela barra lateral ou selecione os dados de exemplo para iniciar.")
        return

    categorias = sorted(list({o.tipo for o in ocorrencias}))

    col_config, col_acao = st.columns([2, 1])
    with col_config:
        categoria_selecionada = st.selectbox(
            "Selecione a categoria a ser analisada:",
            options=categorias,
            index=0,
            help="Serão analisadas apenas ocorrências com o Tipo selecionado.",
        )

    with col_acao:
        st.write("")
        st.write("")
        executar = st.button("🔍 Executar Análise", type="primary", use_container_width=True)

    ocorrencias_filtradas = [o for o in ocorrencias if o.tipo == categoria_selecionada]
    st.markdown(
        f"**Origem:** `{origem}` | **Total de ocorrências:** {len(ocorrencias)} | "
        f"**Ocorrências na categoria '{categoria_selecionada}':** {len(ocorrencias_filtradas)}"
    )

    if not executar:
        st.info("Clique em **Executar Análise** para calcular o par de pontos mais próximos.")
        return

    if len(ocorrencias_filtradas) < 2:
        st.error(
            f"A categoria '{categoria_selecionada}' possui apenas {len(ocorrencias_filtradas)} ocorrência(s). "
            "São necessárias pelo menos 2 ocorrências para calcular o par mais próximo."
        )
        return

    with st.spinner("Executando algoritmo de Divisão e Conquista..."):
        resultado = par_mais_proximo(ocorrencias_filtradas)

    p1, p2 = resultado.par

    st.subheader("📊 Resultados da Análise")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Distância Calculada", f"{resultado.distancia:.4f}")
    with col_m2:
        st.metric("Ponto 1", f"ID {p1.id}", f"({p1.x}, {p1.y})")
    with col_m3:
        st.metric("Ponto 2", f"ID {p2.id}", f"({p2.x}, {p2.y})")

    if resultado.eh_duplicata(limite_duplicacao):
        st.warning(
            f"⚠️ **Possível duplicação detectada!** A distância mínima ({resultado.distancia:.4f}) "
            f"é menor ou igual ao limite configurado ({limite_duplicacao:.4f})."
        )
    else:
        st.success(
            f"✅ **Nenhuma duplicação detectada.** A distância mínima ({resultado.distancia:.4f}) "
            f"está acima do limite de duplicação ({limite_duplicacao:.4f})."
        )

    st.subheader("📈 Visualização no Plano Cartesiano")
    figura = criar_grafico_ocorrencias(ocorrencias_filtradas, resultado)
    st.pyplot(figura)


if __name__ == "__main__":
    main()
