from controller.base_controller import RbacControllerBase
from model.msg_model import MsgModel
from pydantic.fields import Field
from util.auth_util import Identity, Perm
from util.fastapi_util import BaseSchema


class ReadMsgsRequest(BaseSchema):
    limit: int = Field(100, ge=1, le=100)


class ReadMsgsResponse(BaseSchema):
    msgs: list[str]


class ReadMsgsController(RbacControllerBase):
    request_model = ReadMsgsRequest
    response_model = ReadMsgsResponse
    perm = Perm.READ_MSG

    @classmethod
    def run(cls, identity: Identity, data: request_model) -> response_model:
        return cls.response_model(**{"msgs": MsgModel.read_msgs(data.limit)})
