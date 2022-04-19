from controller.read_msgs_controller import ReadMsgsController
from fastapi import APIRouter, Body, Depends
from util.auth_util import Identity
from util.fastapi_util import CommonAPIRoute

user_api_router = APIRouter(tags=["USER"], route_class=CommonAPIRoute)


@user_api_router.post("/api/user/read_msgs", **ReadMsgsController.module_args())
def login(
    identity: Identity = Depends(ReadMsgsController.authenticate),
    payload: ReadMsgsController.request_model = Body(...),
):
    return ReadMsgsController.run(identity, payload)
