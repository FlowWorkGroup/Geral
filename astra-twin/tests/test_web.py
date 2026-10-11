from pathlib import Path

import pytest

from astra_twin.web import create_app


class FakeMemory:
    def __init__(self):
        self.cleared = []

    def clear_session(self, session_id):
        self.cleared.append(session_id)
        return 2


class FakeAgent:
    def __init__(self):
        self.memory = FakeMemory()
        self.calls = []

    def ask(self, prompt, session_id):
        self.calls.append((prompt, session_id))
        return "Resposta de teste local"


@pytest.fixture
def client(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("ASTRA_TWIN_PROVIDER", "ollama")
    monkeypatch.setenv("ASTRA_TWIN_MODEL", "qwen3:4b")
    monkeypatch.setenv("ASTRA_TWIN_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("ASTRA_TWIN_DB", str(tmp_path / "memory.sqlite3"))
    monkeypatch.setenv("ASTRA_TWIN_WEB_SECRET", "s" * 48)
    agent = FakeAgent()
    app = create_app(agent=agent, password="p" * 24)
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client, agent


def csrf_from_login_page(client):
    response = client.get("/")
    assert response.status_code == 200
    import re
    return re.search(rb'name="csrf_token" value="([^"]+)"', response.data).group(1).decode()


def login(client):
    token = csrf_from_login_page(client)
    return client.post("/login", data={"password": "p" * 24, "csrf_token": token})


def test_requires_long_password_and_secret(monkeypatch):
    monkeypatch.setenv("ASTRA_TWIN_WEB_SECRET", "short")
    with pytest.raises(RuntimeError, match="ASTRA_TWIN_WEB_SECRET"):
        create_app(password="p" * 24)


def test_api_requires_authentication(client):
    test_client, _ = client
    response = test_client.post("/api/chat", json={"prompt": "Olá"})
    assert response.status_code == 401


def test_login_chat_and_security_headers(client):
    test_client, agent = client
    response = login(test_client)
    assert response.status_code == 303
    page = test_client.get("/")
    assert b"Laborat" in page.data
    import re
    token = re.search(rb'id="csrf" value="([^"]+)"', page.data).group(1).decode()
    response = test_client.post("/api/chat", json={"prompt": "Olá"}, headers={"X-CSRF-Token": token})
    assert response.status_code == 200
    assert response.json["answer"] == "Resposta de teste local"
    assert agent.calls[0][0] == "Olá"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Cache-Control"] == "no-store"


def test_csrf_is_required_for_chat(client):
    test_client, _ = client
    login(test_client)
    response = test_client.post("/api/chat", json={"prompt": "Olá"})
    assert response.status_code == 403


def test_wrong_password_rejected(client):
    test_client, _ = client
    token = csrf_from_login_page(test_client)
    response = test_client.post("/login", data={"password": "incorrect", "csrf_token": token})
    assert response.status_code == 401


def test_clear_only_clears_current_web_session(client):
    test_client, agent = client
    login(test_client)
    import re
    page = test_client.get("/")
    token = re.search(rb'id="csrf" value="([^"]+)"', page.data).group(1).decode()
    response = test_client.post("/api/clear", headers={"X-CSRF-Token": token})
    assert response.status_code == 200
    assert len(agent.memory.cleared) == 1
    assert agent.memory.cleared[0].startswith("web-")
