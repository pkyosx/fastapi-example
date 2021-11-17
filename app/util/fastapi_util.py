import logging
from typing import Callable

from pydantic import BaseModel

from fastapi import Request
from fastapi import Response
from fastapi import Depends

from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBearer

from util.http_error_util import HttpErrors
from util.http_error_util import WebAppException

logger = logging.getLogger(__name__)


class CommonAPIRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except RequestValidationError as exc:
                # await request.body() might get RuntimeError("Stream consumed")
                # if body is presented, it will cached in request._body
                logger.error(f"RequestValidationError Request body: {getattr(request, '_body', '')}")
                logger.error(f"RequestValidationError: {exc.errors()}")
                # [{'loc': ('query', 'page'), 'msg': 'value is not a valid integer', 'type': 'type_error.integer'}]
                location = exc.errors()[0]["loc"][0]
                param = ".".join(str(x) for x in exc.errors()[0]["loc"][1:])
                return JSONResponse(
                    status_code=HttpErrors.INVALID_PARAM.status_code,
                    content={"msg": f"Invalid {location} param: {param}",
                             "code": HttpErrors.INVALID_PARAM.code},
                )
            except WebAppException as exc:
                # await request.body() might get RuntimeError("Stream consumed")
                # if body is presented, it will cached in request._body
                logger.error(f"WebAppException Request body: {getattr(request, '_body', '')}")
                if exc.show_stack:
                    logger.exception(f"WebAppException: {exc}")
                else:
                    logger.error(f"WebAppException: {exc}")
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"msg": exc.msg, "code": exc.code},
                )
            except Exception as exc:
                # await request.body() might get RuntimeError("Stream consumed")
                # if body is presented, it will cached in request._body
                logger.error(f"Interal Server Error Request body: {getattr(request, '_body', '')}")
                logger.exception(f"Interal Server Error: {exc}")
                return JSONResponse(
                    status_code=HttpErrors.INTERNAL_SERVER_ERROR.status_code,
                    content={"code": HttpErrors.INTERNAL_SERVER_ERROR.code,
                             "msg": str(exc)},
                )

        return custom_route_handler


class DisableFieldOverwrite(type(BaseModel)):
    def __new__(mcls, name, bases, class_dict):
        defined_fields = set()
        for base in bases:
            for key in base.__fields__:
                if key in defined_fields:
                    raise RuntimeError(f"overwrite of {key} is not allowed")
                defined_fields.add(key)
        for key in class_dict.get("__annotations__", []):
            if key in defined_fields:
                raise RuntimeError(f"overwrite of {key} is not allowed")
            defined_fields.add(key)
        return super().__new__(mcls, name, bases, class_dict)


class BaseSchema(BaseModel, metaclass=DisableFieldOverwrite):
    class Config:
        extra = 'forbid'

        @staticmethod
        def schema_extra(schema, model):
            # Patch for field that allows None
            # We use openapi 3.1 spec: https://stackoverflow.com/questions/48111459/how-to-define-a-property-that-can-be-string-or-null-in-openapi-swagger
            # Some discussion on pydantic hook: https://github.com/samuelcolvin/pydantic/issues/1270
            for prop, value in schema.get('properties', {}).items():
                # retrieve right field from alias or name
                field = [x for x in model.__fields__.values() if x.alias == prop][0]
                if field.allow_none:
                    # only one type e.g. {'type': 'integer'}
                    if 'type' in value:
                        value['anyOf'] = [{'type': value.pop('type')}]
                    # only one $ref e.g. from other model
                    elif '$ref' in value:
                        if issubclass(field.type_, BaseModel):
                            # add 'title' in schema to have the exact same behaviour as the rest
                            value['title'] = field.type_.__config__.title or field.type_.__name__
                        value['anyOf'] = [{'$ref': value.pop('$ref')}]
                    elif 'allOf' in value:
                        value['anyOf'] = [{'allOf': value.pop('allOf')}]
                    elif 'oneOf' in value:
                        value['anyOf'] = [{'oneOf': value.pop('oneOf')}]
                    elif 'anyOf' in value:
                        value['anyOf'].append({'type': 'null'})


