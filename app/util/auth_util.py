import logging
import time
from util.enum_util import EnumBase
from dataclasses import dataclass

import jwt

logger = logging.getLogger(__name__)


class Role(EnumBase):
    USER = "USER"
    ADMIN = "ADMIN"


@dataclass
class Identity(object):
    user: str
    role: Role.to_enum()

    def is_user(self):
        return self.role in [Role.USER, Role.ADMIN]

    def is_admin(self):
        return self.role == Role.ADMIN


class JWTAuthenticator(object):
    ACCESS_JWT_ALGORITHM = "HS256"

    @classmethod
    def dump_access_token(cls, key: str, identity: Identity, exp: int) -> str:
        current_ts = int(time.time())
        return jwt.encode(payload=dict(user=identity.user,
                                       role=identity.role,
                                       nbf=current_ts - 300, # not before
                                       exp=current_ts + exp),
                          key=key,
                          algorithm=cls.ACCESS_JWT_ALGORITHM)

    @classmethod
    def load_access_token(cls, key: str, access_token: str) -> Identity:
        payload = jwt.decode(jwt=access_token, key=key, algorithms=[cls.ACCESS_JWT_ALGORITHM])
        return Identity(user=payload['user'], role=payload['role'])