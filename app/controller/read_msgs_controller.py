from pydantic.fields import Field
from util.fastapi_util import BaseSchema
from controller.base_controller import UserControllerBase
from model.msg_model import MsgModel

class ReadMsgsRequest(BaseSchema):
    limit: int = Field(100, ge=1, le=100)

class ReadMsgsResponse(BaseSchema):
    msgs: list[str]


class ReadMsgsController(UserControllerBase):
    request_model = ReadMsgsRequest
    response_model = ReadMsgsResponse

    @classmethod
    def _module_args(cls):
        return {"response_model": cls.response_model}

    @classmethod
    def _run(cls, data: request_model):
        return {"msgs": MsgModel.read_msgs(data.limit)}