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
