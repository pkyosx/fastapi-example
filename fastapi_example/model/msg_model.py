# A very simple in-memory storage just for demo
class MsgModel:
    db = []

    @classmethod
    def leave_msg(cls, msg: str):
        cls.db.append(msg)

    @classmethod
    def read_msgs(cls, limit):
        return cls.db[:limit]

    @classmethod
    def clear(cls):
        cls.db = []
