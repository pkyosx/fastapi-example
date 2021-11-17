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
    def _module_args(cls):
        return {"response_model": cls.response_model}

    @classmethod
    async def _run(cls, data: request_model):
        if data.name in Config.auth_admins and data.password == Config.auth_admins[data.name]:
            return {
                "access_token": JWTAuthenticator.dump_access_token(Config.auth_secret_key,
                                                                   Identity(data.name, Role.ADMIN),
                                                                   Config.auth_token_exp)
            }
        if data.name in Config.auth_users and data.password == Config.auth_users[data.name]:
            return {
                "access_token": JWTAuthenticator.dump_access_token(Config.auth_secret_key,
                                                                   Identity(data.name, Role.USER),
                                                                   Config.auth_token_exp)
            }
        raise cls.Errors.INVALID_PARAM("User or password mismatch")

