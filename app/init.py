import logging
import time
import uuid
import os

from fastapi import FastAPI
from fastapi import Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.responses import PlainTextResponse

from api.public_api import public_api_router
from api.user_api import user_api_router
from api.admin_api import admin_api_router

from util.http_error_util import HttpErrors
from util.log_util import clear_log_ctx
from util.log_util import update_log_ctx

logger = logging.getLogger(__name__)


def init_app():
    doc_opt = {"docs_url": "/api_doc/swagger",
               "redoc_url": "/api_doc/redoc",
               "openapi_url": "/api_doc/openapi.json"}

    app = FastAPI(**doc_opt)

    # initialize API path mapping for metrics
    app.endpoint_to_path = None

    # Add url mappings.
    app.include_router(public_api_router)
    app.include_router(user_api_router)
    app.include_router(admin_api_router)

    def _app_before_request(request):
        app_ctx = {}
        request.state.start = time.time()

        trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
        request.state.trace_id = trace_id

        clear_log_ctx()
        update_log_ctx("TRACE_ID", trace_id)

        logger.info(f"[IN] [{request.method}] {request.url.path} {request.query_params}")
        logger.info(f'Remote: {request.client.host}, {request.url._url}, {request.headers}')
        return app_ctx


    def _app_after_request(endpoint_to_path, request, response):
        exec_time = time.time() - request.state.start
        logger.info(f"[OUT] ({response.status_code}) [{request.method}] {request.url.path} ({int(exec_time * 1000)} ms)")

        response.headers["x-trace-id"] = request.state.trace_id
        if 'endpoint' in request.scope:
            method = request.method
            alias = endpoint_to_path.get(request.scope['endpoint'])
            status_code = response.status_code
            # [Q5] How to get '/path/{param}' in the middleware for metrics
            logger.info(f"[Metrics] {method=} {alias=} {status_code=}")
        return response


    @app.middleware("http")
    async def app_middleware(request: Request, call_next):
        # we set endpoint_to_path during the first call
        if request.app.endpoint_to_path is None:
            request.app.endpoint_to_path = {route.endpoint: route.path for route in request.app.routes}

        _app_before_request(request)

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.exception("Should not reach here, CommonAPIRoute should catch all exceptions")
            response = JSONResponse(
                    status_code=HttpErrors.INTERNAL_SERVER_ERROR.status_code,
                    content={"code": HttpErrors.INTERNAL_SERVER_ERROR.code,
                             "msg": str(exc)},
                )

        _app_after_request(request.app.endpoint_to_path, request, response)
        return response


    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(title="Sample FastAPI service",
                                     version="1.0",
                                     description="Sample FastAPI service",
                                     routes=app.routes)

        # [Q1] How to customize our input schema error (status_code=422)
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

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app