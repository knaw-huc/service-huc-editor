import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_501_NOT_IMPLEMENTED

from src.public import router


# Replace 'your_module' with the actual module name

# Mocking the data and settings modules for testing purposes
class MockSettings:
    URL_DATA_PROFILES = "/mock/profiles"


mock_data = {
    "service-version": "0.1.5"
}


@pytest.fixture
def client(monkeypatch):
    from src.commons import data, settings
    monkeypatch.setattr(data, "data", mock_data)
    monkeypatch.setattr(settings, "settings", MockSettings())
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_info(client):
    response = client.get('/info')
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"name": "HuC Editor API Service", "version": "0.1.6"}


def test_get_profile_not_found(client):
    response = client.get('/profile/clarin.eu:cr1:p_1653377925727')
    assert response.status_code == HTTP_404_NOT_FOUND


def test_get_profile_xml(client, monkeypatch):
    profile_path = "/mock/profiles/p_1653377925727"
    os.makedirs(profile_path, exist_ok=True)
    with open(os.path.join(profile_path, 'p_1653377925727.xml'), 'w') as file:
        file.write('<profile>Mock XML</profile>')

    def mock_isdir(path):
        return path == profile_path

    monkeypatch.setattr(os.path, "isdir", mock_isdir)

    response = client.get('/profile/p_1653377925727', headers={"Accept": "application/xml"})
    assert response.status_code == HTTP_200_OK
    assert response.text == '<profile>Mock XML</profile>'


def test_get_profile_json(client):
    response = client.get('/profile/clarin.eu:cr1:p_1653377925727', headers={"Accept": "application/json"})
    assert response.status_code == HTTP_501_NOT_IMPLEMENTED


def test_get_profile_unsupported(client):
    response = client.get('/profile/clarin.eu:cr1:p_1653377925727', headers={"Accept": "text/html"})
    assert response.status_code == HTTP_400_BAD_REQUEST
