import logging
import contextvars

# [Q8] How to create log context and add trace id into it
# We use contextvars under fastapi for request context.
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


def init_log():
    # [Q8] How to create log context and add trace id into it
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "add_log_ctx": {
                "()": AddLogCtx
            }
        },
        "formatters": {
            "console": {
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "%(asctime)s,%(msecs)03d %(levelname)-5.5s %(log_ctx)s %(message)s (%(filename)s:%(lineno)d)"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
                "filters": ["add_log_ctx"]
            }
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO"
        }
    })
