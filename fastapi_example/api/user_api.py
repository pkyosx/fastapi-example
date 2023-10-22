from controller.read_msgs_controller import ReadMsgsController
from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from sqlalchemy.orm.session import Session
from util.auth_util import Identity
from util.fastapi_util import CommonAPIRoute
from util.fastapi_util import get_session

user_api_router = APIRouter(tags=["USER"], route_class=CommonAPIRoute)


@user_api_router.post("/api/user/read_msgs", **ReadMsgsController.module_args())
def login(
    session: Session = Depends(get_session),
    identity: Identity = Depends(ReadMsgsController.authenticate),
    payload: ReadMsgsController.request_model = Body(...),
):
    return ReadMsgsController.run(session, identity, payload)
