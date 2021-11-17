from pydantic.fields import Field
from util.fastapi_util import BaseSchema
from controller.base_controller import AdminControllerBase
from model.msg_model import MsgModel

class LeaveMsgRequest(BaseSchema):
    msg: str = Field(...)

class LeaveMsgResponse(BaseSchema):
    result: str


class LeaveMsgController(AdminControllerBase):
    request_model = LeaveMsgRequest
    response_model = LeaveMsgResponse

    @classmethod
    def _module_args(cls):
        return {"response_model": cls.response_model}

    @classmethod
    def _run(cls, data: request_model):
        MsgModel.leave_msg(data.msg)
        return {"result": "ok"}
