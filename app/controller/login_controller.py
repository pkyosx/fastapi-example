from controller.base_controller import ControllerBase
from util.http_error_util import HttpErrors
from util.fastapi_util import BaseSchema
from util.config_util import Config
from util.auth_util import JWTAuthenticator
from util.auth_util import Identity
from util.auth_util import Role
from pydantic import Field


class LoginRequest(BaseSchema):
    name: str = Field(...)
    password: str = Field(...)


class LoginResponse(BaseSchema):
    access_token: str = Field(..., description="JWT token that could be used on Authorization header")


class LoginController(ControllerBase):
    request_model = LoginRequest
    response_model = LoginResponse

    class Errors(ControllerBase.Errors):
        INVALID_PARAM = HttpErrors.INVALID_PARAM

    @classmethod
    def run(cls, payload: request_model) -> response_model:
        if payload.name in Config.auth_admins and payload.password == Config.auth_admins[payload.name]:
            return cls.response_model(**{
                "access_token": JWTAuthenticator.dump_access_token(Config.auth_secret_key,
                                                                   Identity(payload.name, Role.ADMIN),
                                                                   Config.auth_token_exp)
            })
        if payload.name in Config.auth_users and payload.password == Config.auth_users[payload.name]:
            return cls.response_model(**{
                "access_token": JWTAuthenticator.dump_access_token(Config.auth_secret_key,
                                                                   Identity(payload.name, Role.USER),
                                                                   Config.auth_token_exp)
            })
        raise cls.Errors.INVALID_PARAM("User or password mismatch")

