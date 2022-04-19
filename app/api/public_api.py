from controller.login_controller import LoginController
from fastapi import APIRouter, Body
from fastapi.param_functions import Body
from util.fastapi_util import CommonAPIRoute

public_api_router = APIRouter(tags=["PUBLIC"], route_class=CommonAPIRoute)


@public_api_router.post("/api/public/login", **LoginController.module_args())
def login(payload: LoginController.request_model = Body(...)):
    return LoginController.run(payload)
