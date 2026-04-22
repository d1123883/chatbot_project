import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from backend.main import app, get_session
import uuid

# Setup an in-memory database for testing
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_create_session(client: TestClient):
    response = client.post("/sessions", params={"title": "Test Session"})
    data = response.json()
    assert response.status_code == 200
    assert data["title"] == "Test Session"
    assert "id" in data

def test_get_sessions(client: TestClient):
    client.post("/sessions", params={"title": "Session 1"})
    client.post("/sessions", params={"title": "Session 2"})
    response = client.get("/sessions")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 2

def test_chat_stream(client: TestClient):
    # First create a session
    sess_resp = client.post("/sessions", params={"title": "Chat Test"})
    session_id = sess_resp.json()["id"]
    
    # Test streaming endpoint (mocked)
    response = client.post(f"/chat/stream?session_id={session_id}&prompt=Hello")
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
