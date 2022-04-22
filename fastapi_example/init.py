import logging
from functools import partial

import prometheus_client
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from api.admin_api import admin_api_router
from api.public_api import public_api_router
from api.user_api import user_api_router
from util.config_util import Config
from util.fastapi_util import create_openapi_schema
from util.fastapi_util import init_fastapi_app

logger = logging.getLogger(__name__)


def init_app():
    doc_opt = {
        "docs_url": "/api_doc/swagger",
        "redoc_url": "/api_doc/redoc",
        "openapi_url": "/api_doc/openapi.json",
    }

    app = FastAPI(
        title=Config.app_title,
        description=Config.app_description,
        version=Config.app_version,
        **doc_opt
    )

    # setup default and customized plugins
    init_fastapi_app(app)

    # add all routes here
    app.include_router(public_api_router)
    app.include_router(user_api_router)
    app.include_router(admin_api_router)

    # customize api doc
    app.openapi = partial(
        create_openapi_schema,
        title=Config.app_title,
        description=Config.app_description,
        version=Config.app_version,
        routes=app.routes,
    )

    @app.get("/", include_in_schema=False)
    def health_check():
        return PlainTextResponse("This page is for health check.")

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        from util.metrics_util import update_latest

        update_latest(version=Config.app_version)
        return PlainTextResponse(prometheus_client.generate_latest())

    return app
