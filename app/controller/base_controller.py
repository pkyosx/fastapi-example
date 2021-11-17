import abc
import logging

from pydantic import Field
from starlette.responses import JSONResponse
from starlette.responses import Response
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBearer
from fastapi import Depends

from util.auth_util import JWTAuthenticator
from util.auth_util import Identity
from util.config_util import Config
from util.enum_util import EnumBase
from util.http_error_util import HttpErrors
from util.http_error_util import gen_error_responses


logger = logging.getLogger(__name__)


DEFAULT_MODULE_ARGS = {
    "response_model_exclude_unset": True,
}

def recursive_merge_dict(to_dict, from_dict):
    for k, v in from_dict.items():
        if isinstance(v, dict):
            to_dict[k] = recursive_merge_dict(to_dict.get(k, {}), v)
        else:
            to_dict[k] = v
    return to_dict

class ControllerBase(abc.ABC):
    class Errors(EnumBase):
        INVALID_PARAM = HttpErrors.INVALID_PARAM
        INTERNAL_SERVER_ERROR = HttpErrors.INTERNAL_SERVER_ERROR

    @classmethod
    @abc.abstractmethod
    async def _run(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def _module_args(cls):
        raise NotImplementedError

    @classmethod
    def module_args(cls):
        assert "responses" not in cls._module_args(), "responses should be defined via Errors class"
        # [Q2] How to generate error response for openapi in a clean way
        # Error responses will be generated automatically according to Errors
        # You can check gen_error_responses for detail
        return recursive_merge_dict(to_dict=dict(responses=gen_error_responses(name=cls.__name__,
                                                                               http_errors=cls.Errors.values()),
                                                 **DEFAULT_MODULE_ARGS),
                                    from_dict=cls._module_args() or {})

    @classmethod
    async def run(cls, *args, **kwargs):
        return await cls._run(*args, **kwargs)


class AuthenticateControllerBase(ControllerBase):
    class Errors(ControllerBase.Errors):
        UNAUTHENTICATED = HttpErrors.UNAUTHENTICATED

    @classmethod
    def authenticate(cls, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))) -> Identity:
        if not credentials:
            logger.error("Access JWT is missing")
            raise cls.Errors.UNAUTHENTICATED("JWT is missing")

        access_jwt = credentials.credentials
        try:
            return JWTAuthenticator.load_access_token(key=Config.auth_secret_key, access_token=access_jwt)
        except:
            # [Q7] How to print the entire exception chain when wanted
            raise cls.Errors.UNAUTHENTICATED("Invalid JWT", show_stack=True)


class UserControllerBase(AuthenticateControllerBase):
    class Errors(AuthenticateControllerBase.Errors):
        UNAUTHORIZED = HttpErrors.UNAUTHORIZED

    @classmethod
    async def run(cls, identity: Identity, payload):
        if not identity.is_user():
            raise cls.Errors.UNAUTHORIZED("Is not user")
        return await cls._run(payload)


class AdminControllerBase(AuthenticateControllerBase):
    class Errors(AuthenticateControllerBase.Errors):
        UNAUTHORIZED = HttpErrors.UNAUTHORIZED

    @classmethod
    async def run(cls, identity: Identity, payload):
        if not identity.is_admin():
            raise cls.Errors.UNAUTHORIZED("Is not admin")
        return await cls._run(payload)

