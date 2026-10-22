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


def test_gemini_mode_without_key_falls_back(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    app = AppTest.from_file(str(APP)).run(timeout=30)
    app.selectbox[0].select("Gemini + sources").run()
    app.text_area[0].input("Payment API 500")
    next(b for b in app.button if b.label == "Find troubleshooting guidance").click().run()
    assert not app.exception
    assert any("not configured" in c.value for c in app.caption)
    assert any("KB-001" in m.value for m in app.markdown)


def test_successful_gemini_is_saved_not_recalled_and_cooled_down(monkeypatch):
    import gemini
    from unittest.mock import Mock
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-test-key")
    generate = Mock(return_value=gemini.GeneratedAnswer("gemini", "Tentative runbook match."))
    monkeypatch.setattr(gemini, "generate_answer", generate)
    app = AppTest.from_file(str(APP)).run(timeout=30)
    app.selectbox[0].select("Gemini + sources").run()
    app.text_area[0].input("Payment API 500")
    next(b for b in app.button if b.label == "Find troubleshooting guidance").click().run()
    assert not app.exception
    assert any("Tentative runbook match." in t.value for t in app.text)
    assert generate.call_count == 1
    app.run()
    assert generate.call_count == 1
    next(b for b in app.button if b.label == "Find troubleshooting guidance").click().run()
    assert generate.call_count == 1
    assert any("Wait 20 seconds" in c.value for c in app.caption)
