import abc
import logging

from fastapi import Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBearer

from util.auth_util import Identity
from util.auth_util import JWTAuthenticator
from util.auth_util import Perm
from util.config_util import Config
from util.enum_util import EnumBase
from util.fastapi_util import BaseSchema
from util.http_error_util import HttpErrors
from util.http_error_util import gen_error_responses

logger = logging.getLogger(__name__)


DEFAULT_MODULE_ARGS = {
    "response_model_exclude_unset": True,
}


class ControllerBase(abc.ABC):

    request_schema = BaseSchema
    response_schema = BaseSchema

    class Errors(EnumBase):
        INVALID_PARAM = HttpErrors.INVALID_PARAM
        INTERNAL_SERVER_ERROR = HttpErrors.INTERNAL_SERVER_ERROR

    @abc.abstractclassmethod
    def run(cls, payload: request_schema) -> response_schema:
        raise NotImplementedError()

    @classmethod
    def module_args(cls):
        # [Q2] How to generate error response for openapi in a clean way
        # Error responses will be generated automatically according to Errors
        # You can check gen_error_responses for detail
        return DEFAULT_MODULE_ARGS | {
            "responses": gen_error_responses(cls.__name__, cls.Errors.values())
        }


class RbacControllerBase(abc.ABC):
    request_schema = BaseSchema
    response_schema = BaseSchema
    perm = Perm.NONE

    class Errors(EnumBase):
        UNAUTHENTICATED = HttpErrors.UNAUTHENTICATED
        INVALID_PARAM = HttpErrors.INVALID_PARAM
        INTERNAL_SERVER_ERROR = HttpErrors.INTERNAL_SERVER_ERROR
        UNAUTHORIZED = HttpErrors.UNAUTHORIZED

    @classmethod
    def module_args(cls):
        # [Q2] How to generate error response for openapi in a clean way
        # Error responses will be generated automatically according to Errors
        # You can check gen_error_responses for detail
        return DEFAULT_MODULE_ARGS | {
            "responses": gen_error_responses(cls.__name__, cls.Errors.values())
        }

    @classmethod
    def authenticate(
        cls,
        credentials: HTTPAuthorizationCredentials = Depends(
            HTTPBearer(auto_error=False)
        ),
    ) -> Identity:
        if not credentials:
            logger.error("Access JWT is missing")
            raise cls.Errors.UNAUTHENTICATED("JWT is missing")

        access_jwt = credentials.credentials
        try:
            identity = JWTAuthenticator.load_access_token(
                key=Config.auth_secret_key, access_token=access_jwt
            )
        except:
            # [Q7] How to print the entire exception chain when wanted
            raise cls.Errors.UNAUTHENTICATED("Invalid JWT", show_stack=True)

        if not identity.has_permission(cls.perm):
            raise cls.Errors.UNAUTHORIZED(f"{identity.role} does not have {cls.perm}")
        return identity

    @abc.abstractclassmethod
    def rbac_checker(cls, identity: Identity) -> None:
        raise NotImplementedError()

    @abc.abstractclassmethod
    def run(cls, identity: Identity, payload: request_schema) -> response_schema:
        raise NotImplementedError()
