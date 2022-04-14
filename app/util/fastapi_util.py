import contextvars
import logging
import time
from typing import Callable, Protocol
import uuid

from pydantic import BaseModel

from fastapi import FastAPI, Request
from fastapi import Response
from fastapi import Depends

from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBearer
from util.log_util import clear_log_ctx, update_log_ctx
from util.metrics_util import Metrics

from util.http_error_util import HttpErrors
from util.http_error_util import WebAppException

logger = logging.getLogger(__name__)

class WrappedRequestValidationError(Exception):
    def __init__(self, exc: RequestValidationError):
        self.exc = exc

class CommonAPIRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except RequestValidationError as e:
                logger.error(f"Error request body: {getattr(request, '_body', '')}")
                raise WrappedRequestValidationError(e)
            except Exception:
                # await request.body() might get RuntimeError("Stream consumed")
                # if body is presented, it will cached in request._body
                logger.error(f"Error request body: {getattr(request, '_body', '')}")
                raise

        return custom_route_handler

# [Q4] How to do if I want schema to be inheritable but don't want child class to overwrite parent's any attributes
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
            # [Q3] How to define a property that can be string or null in openapi
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


class FastAPIPlugin(Protocol):
    def on_before(self, request):
        pass

    def on_after(self, request, response, exec_time, alias):
        pass

class RequestCtx:
    x_trace_id = contextvars.ContextVar('x_trace_id')
    x_task_id = contextvars.ContextVar('x_task_id')

    @classmethod
    def get_x_trace_id(cls):
        return cls.x_trace_id.get("NA")

    @classmethod
    def set_x_trace_id(cls, value):
        return cls.x_trace_id.set(value)

    @classmethod
    def get_x_task_id(cls):
        return cls.x_trace_id.get("NA")

    @classmethod
    def set_x_task_id(cls, value):
        return cls.x_trace_id.set(value)

class RequestCtxPlugin:
    def on_before(self, request):
        RequestCtx.set_x_task_id(request.headers.get("x-trace-id", str(uuid.uuid4())))
        RequestCtx.set_x_task_id(request.headers.get("x-task-id", str(uuid.uuid4())))


    def on_after(self, request, response, exec_time, alias):
        response.headers["x-trace-id"] = RequestCtx.get_x_trace_id()
        response.headers["x-task-id"] = RequestCtx.get_x_task_id()

class LoggerPlugging:
    def on_before(self, request):
        clear_log_ctx()
        update_log_ctx("X_TRACE_ID", RequestCtx.get_x_trace_id())
        update_log_ctx("X_TASK_ID", RequestCtx.get_x_task_id())

        logger.info(f"[IN] [{request.method}] {request.url.path} {request.query_params}")
        logger.info(f'Remote: {request.client.host}, {request.url._url}, {request.headers}')

    def on_after(self, request, response, exec_time, alias):
        if response.status_code == 200:
            logger.info(f"[OUT] ({response.status_code}) [{request.method}] {request.url.path} ({int(exec_time * 1000)} ms)")
        else:
            logger.error(f"[OUT] ({response.status_code}) [{request.method}] {request.url.path} ({int(exec_time * 1000)} ms)")

class MetricsPlugging:
    def on_before(self, request):
        Metrics.app_api_connection_total.inc()

    def on_after(self, request, response, exec_time, alias):
        Metrics.app_api_connection_total.dec()
        if alias:
            Metrics.app_api_latency_seconds.labels(method=request.method,
                                                   alias=alias,
                                                   status_code=response.status_code).observe(exec_time)
class AliasFinder:
    def __init__(self):
        self.endpoint_to_path = None
        self.num_routes = None

    def get_alias(self, request):
        if len(request.app.routes) != self.num_routes:
            self.num_routes = len(request.app.routes)
            self.endpoint_to_path = {route.endpoint: route.path for route in request.app.routes}
            logger.info(f"Initialize alias finder for {self.num_routes} routes")
        if 'endpoint' in request.scope:
            return self.endpoint_to_path.get(request.scope['endpoint'])

def init_fastapi_app(
    app: FastAPI,
    plugins: list[FastAPIPlugin] = [],
) -> None:

    alias_finder = AliasFinder()
    fastapi_plugins = plugins + [RequestCtxPlugin(), LoggerPlugging(), MetricsPlugging()]

    @app.middleware("http")
    async def app_middleware(request: Request, call_next):
        start = time.time()

        for plugin in fastapi_plugins:
            plugin.on_before(request)

        try:
            response = await call_next(request)
        except WrappedRequestValidationError as exc:
            location = exc.exc.errors()[0]["loc"][0]
            param = ".".join(str(x) for x in exc.exc.errors()[0]["loc"][1:])
            response = JSONResponse(
                status_code=HttpErrors.INVALID_PARAM.status_code,
                content={"msg": f"Invalid {location} param: {param}", "code": HttpErrors.INVALID_PARAM.code},
            )
        except WebAppException as exc:
            if exc.show_stack:
                logger.exception(f"WebAppException: {exc}")
            else:
                logger.error(f"WebAppException: {exc}")
            response = JSONResponse(
                status_code=exc.status_code,
                content={"msg": exc.msg, "code": exc.code},
            )
        except Exception as exc:
            logger.exception(f"Interal Server Error: {exc}")
            response = JSONResponse(
                    status_code=HttpErrors.INTERNAL_SERVER_ERROR.status_code,
                    content={"code": HttpErrors.INTERNAL_SERVER_ERROR.code,
                             "msg": "Internal Server Error"},
                )

        exec_time = time.time() - start

        for plugin in fastapi_plugins:
            plugin.on_after(request, response, exec_time, alias_finder.get_alias(request))

        return response

def create_openapi_schema(
    title,
    description,
    version,
    routes,
) -> dict:
    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(title=title,
                                 description=description,
                                 version=version,
                                 routes=routes)

    # look for the error 422 and removes it
    for url in openapi_schema["paths"]:
        for method in openapi_schema["paths"][url]:
            tags = openapi_schema["paths"][url][method].get("tags")
            if tags and len(tags) != len(set(tags)):
                raise Exception(f"Duplicated tags found [{method}] {url=}: {tags=}")
            try:
                del openapi_schema["paths"][url][method]["responses"]["422"]
            except KeyError:
                pass
    return openapi_schema