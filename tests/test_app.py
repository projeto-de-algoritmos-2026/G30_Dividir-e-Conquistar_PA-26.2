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
    app.number_input[0].set_value(6.0)
    # Clica no botão de executar
    app.button[0].click().run()
    assert not app.exception

    # Verifica métricas exibidas
    metricas = [m.label for m in app.metric]
    assert "Distância Calculada" in metricas
    assert "Ponto 1" in metricas
    assert "Ponto 2" in metricas

    assert app.metric[0].value == "6.0000"
    # A distância igual ao limite também deve sinalizar possível duplicação.
    assert any("Possível duplicação detectada" in w.value for w in app.warning)


def test_app_alerta_quando_distancia_supera_limite():
    app = AppTest.from_file(CAMINHO_APP).run()
    # O limite padrão de 1.0 é menor que a distância de 6.0 do exemplo.
    app.button[0].click().run()
    assert not app.exception

    assert any("Nenhuma duplicação detectada" in s.value for s in app.success)
    assert not app.warning
