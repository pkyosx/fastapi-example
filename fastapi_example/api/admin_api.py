from controller.leave_msg_controller import LeaveMsgController
from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from sqlalchemy.orm.session import Session
from util.auth_util import Identity
from util.fastapi_util import CommonAPIRoute
from util.fastapi_util import get_session

admin_api_router = APIRouter(tags=["ADMIN"], route_class=CommonAPIRoute)


@admin_api_router.post("/api/admin/leave_msg", **LeaveMsgController.module_args())
def login(
    session: Session = Depends(get_session),
    identity: Identity = Depends(LeaveMsgController.authenticate),
    payload: LeaveMsgController.request_model = Body(...),
):
    return LeaveMsgController.run(session, identity, payload)
