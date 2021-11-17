import contextvars

log_ctx_holder = contextvars.ContextVar('log_ctx')


class AddLogCtx(object):
    def filter(self, record):
        log_ctx = log_ctx_holder.get({})
        record.log_ctx = " ".join([f"[{k}={log_ctx[k]}]" for k in sorted(log_ctx.keys())]) or "[]"
        return True


def update_log_ctx(k, v):
    log_ctx_holder.set({**log_ctx_holder.get({}), **{k: v}})


def clear_log_ctx():
    log_ctx_holder.set({})
