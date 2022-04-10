import believe as B
import json
import logging
import pytest
from util.auth_util import Identity
from util.auth_util import JWTAuthenticator
from util.auth_util import Role
from util.config_util import Config
from model.msg_model import MsgModel
logger = logging.getLogger(__name__)


class TestReadMsgs:
    path = '/api/user/read_msgs'

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
        # prepare fixture
        MsgModel.leave_msg("hello")
        MsgModel.leave_msg("world")

        # user read two messages
        resp = self.trigger_run(Role.USER, {})
        assert resp.status_code == 200
        assert resp.json() == {'msgs': ["hello", "world"]}

        # admin also has permission to read
        resp = self.trigger_run(Role.ADMIN, {"limit": 1})
        assert resp.status_code == 200
        assert resp.json() == {'msgs': ["hello"]}

    def test__authentication_error(self):
        resp = self.trigger_run(None, {"msg": "hello"})
        assert resp.status_code == 401
        assert resp.json() == {'code': 'UNAUTHENTICATED', 'msg': 'JWT is missing'}

    def test__limit_error(self):
        resp = self.trigger_run(Role.USER, {"limit": 101})
        assert resp.status_code == 400
        assert resp.json() == {'code': 'INVALID_PARAM', 'msg': 'Invalid body param: limit'}

