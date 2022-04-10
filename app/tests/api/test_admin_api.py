import believe as B
import json
import logging
import pytest
from util.auth_util import Identity
from util.auth_util import JWTAuthenticator
from util.auth_util import Role
from util.config_util import Config

logger = logging.getLogger(__name__)


class TestLeaveMsg:
    path = '/api/admin/leave_msg'

    @pytest.fixture(autouse=True)
    def __setup__(self, client):
        self.client = client

    def trigger_run(self, role, payload):
        headers = {}
        if role:
            auth_token = JWTAuthenticator.dump_access_token(Config.auth_secret_key, Identity(user="xxx", role=role), exp=86400)
            headers = {"Authorization": f"bearer {auth_token}"}
        return self.client.post(url=self.path, data=json.dumps(payload), headers=headers)

    def test__ok(self):
        resp = self.trigger_run(Role.ADMIN, {"msg": "hello"})
        assert resp.status_code == 200
        assert resp.json() == {'result': 'ok'}

    def test__authentication_error(self):
        resp = self.trigger_run(None, {"msg": "hello"})
        assert resp.status_code == 401
        assert resp.json() == {'code': 'UNAUTHENTICATED', 'msg': 'JWT is missing'}

    def test__authorization_error(self):
        resp = self.trigger_run(Role.USER, {"msg": "hello"})
        assert resp.status_code == 403
        assert resp.json() == {'code': 'UNAUTHORIZED', 'msg': 'USER does not have WRITE_MSG'}

