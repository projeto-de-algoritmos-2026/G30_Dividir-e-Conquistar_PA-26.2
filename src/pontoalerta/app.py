"""Interface web do PontoAlerta construída com Streamlit."""

from pathlib import Path
import streamlit as st

from pontoalerta.leitura_csv import carregar_ocorrencias_csv


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

    # Organização dos componentes em barra lateral e área principal
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


if __name__ == "__main__":
    main()
