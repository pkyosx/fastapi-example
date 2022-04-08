from functools import partial
import logging
import time
import uuid
import os
import prometheus_client

from fastapi import FastAPI
from fastapi import Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.responses import PlainTextResponse

from api.public_api import public_api_router
from api.user_api import user_api_router
from api.admin_api import admin_api_router
from app.util.config_util import Config
from app.util.fastapi_util import create_openapi_schema, init_fastapi_app
from app.util.http_error_util import WebAppException

from util.http_error_util import HttpErrors
from util.log_util import clear_log_ctx
from util.log_util import update_log_ctx

logger = logging.getLogger(__name__)


def init_app():
    doc_opt = {"docs_url": "/api_doc/swagger",
               "redoc_url": "/api_doc/redoc",
               "openapi_url": "/api_doc/openapi.json"}

    app = FastAPI(title=Config.app_title,
                  description= Config.app_description,
                  version=Config.app_version,
                  **doc_opt)

    # setup default and customized plugins
    init_fastapi_app(app)

    # add all routes here
    app.include_router(public_api_router)
    app.include_router(user_api_router)
    app.include_router(admin_api_router)

    # customize api doc
    app.openapi = partial(create_openapi_schema,
                          title=Config.app_title,
                          description=Config.app_description,
                          version=Config.app_version,
                          routes=app.routes)

    @app.get('/', include_in_schema=False)
    def health_check():
        return PlainTextResponse("This page is for health check.")

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        from app.util.metrics_util import update_latest
        update_latest(version=Config.app_version)
        return PlainTextResponse(prometheus_client.generate_latest())

    return app
