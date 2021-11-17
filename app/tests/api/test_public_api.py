import believe as B
import json
import logging
import pytest
from util.auth_util import JWTAuthenticator
from util.config_util import Config

logger = logging.getLogger(__name__)


class TestLogin:
    path = '/api/public/login'

    @pytest.fixture(autouse=True)
    def __setup__(self, client):
        self.client = client

    def trigger_run(self, payload):
        return self.client.post(url=self.path, data=json.dumps(payload))

    def test_login_fail(self):
        resp = self.trigger_run({"name": "xxx", "password": "ooo"})
        assert resp.status_code == 400
        assert resp.json() == {'code': 'INVALID_PARAM', 'msg': 'User or password mismatch'}

        resp = self.trigger_run({"name": "user1", "password": "ooo"})
        assert resp.status_code == 400
        assert resp.json() == {'code': 'INVALID_PARAM', 'msg': 'User or password mismatch'}

        resp = self.trigger_run({"name": "admin1", "password": "ooo"})
        assert resp.status_code == 400
        assert resp.json() == {'code': 'INVALID_PARAM', 'msg': 'User or password mismatch'}

    def test_login_success__user(self):
        resp = self.trigger_run({"name": "user1", "password": "user_password1"})
        assert resp.status_code == 200
        assert resp.json() == {'access_token': B.AnyStr()}

        user = JWTAuthenticator.load_access_token(Config.auth_secret_key, resp.json()["access_token"])
        assert user.is_user()

    def test_login_success__admin(self):
        resp = self.trigger_run({"name": "admin1", "password": "admin_password1"})
        assert resp.status_code == 200
        assert resp.json() == {'access_token': B.AnyStr()}

        user = JWTAuthenticator.load_access_token(Config.auth_secret_key, resp.json()["access_token"])
        assert user.is_admin()

