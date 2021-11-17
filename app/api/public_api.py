from fastapi import Body
from fastapi import APIRouter
from fastapi.param_functions import Body
from util.fastapi_util import CommonAPIRoute
from controller.login_controller import LoginController

public_api_router = APIRouter(tags=["PUBLIC"], route_class=CommonAPIRoute)

@public_api_router.post("/api/public/login", **LoginController.module_args())
async def login(payload: LoginController.request_model = Body(...)):
    return await LoginController.run(payload)