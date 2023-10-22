from controller.base_controller import RbacControllerBase
from fastapi_example.crud import list_messages
from pydantic.fields import Field
from sqlalchemy.orm import Session
from util.auth_util import Identity
from util.auth_util import Perm
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
    def run(
        cls, session: Session, identity: Identity, data: request_model
    ) -> response_model:
        messages = list_messages(session, data.limit)
        return cls.response_model(**{"msgs": [i.content for i in messages]})
