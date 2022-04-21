import pytest
from fastapi.testclient import TestClient

from init import init_app
from model.msg_model import MsgModel


@pytest.fixture(scope="session")
def client():
    yield TestClient(init_app())


@pytest.fixture(autouse=True)
def reset_model():
    MsgModel.clear()
