import pytest
from fastapi.testclient import TestClient
from init import init_app
from model import create_tables
from model import drop_tables
from util.sqlalchemy_util import create_session


@pytest.fixture(scope="session")
def client():
    yield TestClient(init_app())


@pytest.fixture(scope="session", autouse=True)
def reset_tables():
    create_tables()
    yield
    drop_tables()


@pytest.fixture(scope="function", autouse=True)
def session(mocker):
    # We want to create a session object for each test function, and close it after the test function is done.
    # Anything committed in the test function will be rolled back.
    with create_session() as session:
        # we mock the close method so the data created by the first API will be visible to the second API
        orig_session_close = session.close
        session.close = mocker.Mock()
        # we mock the commit method with flush so the data in the API call will not be committed
        # instead it will be visible to the session with auto-field filled
        session.commit = session.flush
        # every entrypoint should be mocked to return the same session object
        mocker.patch("util.sqlalchemy_util.create_session", return_value=session)
        mocker.patch("util.fastapi_util.create_session", return_value=session)
        yield session
        # restore the original close method so the connection will be closed and data in transaction will be cleared
        session.close = orig_session_close
