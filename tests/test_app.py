from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_app_known_unknown_and_empty():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    assert not app.exception
    app.text_area[0].input("Payment API 500")
    next(b for b in app.button if b.label == "Find troubleshooting guidance").click().run()
    assert not app.exception
    assert any("KB-001" in m.value for m in app.markdown)
    app.text_area[0].input("My keyboard is broken")
    next(b for b in app.button if b.label == "Find troubleshooting guidance").click().run()
    assert not app.exception
    assert any("insufficient evidence" in m.value for m in app.markdown)
    assert not any("Conditional resolution" in m.value for m in app.markdown)
    app.text_area[0].input("")
    next(b for b in app.button if b.label == "Find troubleshooting guidance").click().run()
    assert not app.exception
    assert any("Describe the service" in m.value for m in app.markdown)


def test_example_button_populates_input():
    app = AppTest.from_file(str(APP)).run(timeout=30)
    next(b for b in app.button if b.label == "Cannot connect to the database").click().run()
    assert app.text_area[0].value == "Cannot connect to the database"
    assert not app.exception
