import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

def test_community(client):
    rv = client.get('/community')
    assert rv.status_code == 200
