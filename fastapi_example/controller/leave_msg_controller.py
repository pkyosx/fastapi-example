from controller.base_controller import RbacControllerBase
from crud import create_message
from pydantic.fields import Field
from sqlalchemy.orm import Session
from util.auth_util import Identity
from util.auth_util import Perm
from util.fastapi_util import BaseSchema


class LeaveMsgRequest(BaseSchema):
    msg: str = Field(...)


class LeaveMsgResponse(BaseSchema):
    result: str


class LeaveMsgController(RbacControllerBase):
    request_model = LeaveMsgRequest
    response_model = LeaveMsgResponse
    perm = Perm.WRITE_MSG

    @classmethod
    def run(
        cls, session: Session, identity: Identity, payload: request_model
    ) -> response_model:
        create_message(session, payload.msg)
        return cls.response_model(**{"result": "ok"})
