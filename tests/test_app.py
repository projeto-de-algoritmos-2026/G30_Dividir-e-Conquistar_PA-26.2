from pathlib import Path
from streamlit.testing.v1 import AppTest

CAMINHO_APP = str(Path(__file__).parent.parent / "src" / "pontoalerta" / "app.py")


def test_app_inicializa_sem_erros():
    app = AppTest.from_file(CAMINHO_APP).run()
    assert not app.exception
    assert len(app.title) > 0
    assert "PontoAlerta" in app.title[0].value


def test_app_carrega_dados_de_exemplo_e_mostra_categorias():
    app = AppTest.from_file(CAMINHO_APP).run()
    assert not app.exception
    assert len(app.selectbox) > 0
    selectbox = app.selectbox[0]
    assert "buraco" in selectbox.options
    assert "vazamento" in selectbox.options
    assert len(app.button) > 0


def test_app_executa_analise_com_sucesso():
    app = AppTest.from_file(CAMINHO_APP).run()
    # Clica no botão de executar
    app.button[0].click().run()
    assert not app.exception

    # Verifica métricas exibidas
    metricas = [m.label for m in app.metric]
    assert "Distância Calculada" in metricas
    assert "Ponto 1" in metricas
    assert "Ponto 2" in metricas

    # Distância para buraco é ~0.5385, com limite padrão 1.0 deve alertar duplicação
    assert any("Possível duplicação detectada" in w.value for w in app.warning)


def test_app_alerta_quando_distancia_supera_limite():
    app = AppTest.from_file(CAMINHO_APP).run()
    # Altera limite para 0.1 (menor que a distância 0.5385)
    app.number_input[0].set_value(0.1).run()
    app.button[0].click().run()
    assert not app.exception

    assert any("Nenhuma duplicação detectada" in s.value for s in app.success)
