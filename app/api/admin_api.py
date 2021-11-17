from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from util.fastapi_util import CommonAPIRoute
from util.auth_util import Identity
from controller.leave_msg_controller import LeaveMsgController

admin_api_router = APIRouter(tags=["ADMIN"], route_class=CommonAPIRoute)


@admin_api_router.post("/api/admin/leave_msg", **LeaveMsgController.module_args())
def login(
    admin: Identity = Depends(LeaveMsgController.authenticate),
    payload: LeaveMsgController.request_model = Body(...)
):
    return LeaveMsgController.run(admin, payload)