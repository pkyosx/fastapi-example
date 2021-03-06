from enum import Enum

from pydantic import create_model

from util.enum_util import EnumBase


class HttpStatusCode(EnumBase):
    OK = 200
    GENERAL_ERROR = 400
    AUTHENTICATION_ERROR = 401
    AUTHORIZATION_ERROR = 403
    UNEXPECTED_ERROR = 500


class WebAppException(Exception):
    def __init__(self, status_code, code, msg="", show_stack=False):
        self.status_code = status_code
        self.code = code
        self.msg = msg
        self.show_stack = show_stack

    def __str__(self):
        return self.msg


class HttpError:
    def __init__(self, status_code: int, code: str):
        self.status_code = status_code
        self.code = code

    def __call__(self, msg="", show_stack=False):
        return WebAppException(
            status_code=self.status_code, code=self.code, msg=msg, show_stack=show_stack
        )


class HttpErrors(EnumBase):
    # GENERAL_ERROR (400)
    # I suggest centralize all other application errors to status_code=400.
    # We could create different 'code' in string format to distinguish them.
    INVALID_PARAM = HttpError(
        status_code=HttpStatusCode.GENERAL_ERROR, code="INVALID_PARAM"
    )
    # OTHER_APP_ERROR = HttpError(status_code=HttpErrorStatusCode.GENERAL_ERROR, code='OTHER_APP_ERROR')

    # AUTHENTICATION_ERROR (401)
    UNAUTHENTICATED = HttpError(
        status_code=HttpStatusCode.AUTHENTICATION_ERROR, code="UNAUTHENTICATED"
    )

    # AUTHORIZATION_ERROR (403)
    UNAUTHORIZED = HttpError(
        status_code=HttpStatusCode.AUTHORIZATION_ERROR, code="UNAUTHORIZED"
    )

    # UNEXPECTED_ERROR (500)
    INTERNAL_SERVER_ERROR = HttpError(
        status_code=HttpStatusCode.UNEXPECTED_ERROR, code="INTERNAL_SERVER_ERROR"
    )


# [Q2] How to generate error response for openapi in a clean way
def gen_error_responses(prefix: str, http_errors: list[HttpError]):
    http_status_to_name = {v: k for v, k in HttpStatusCode.value_to_key().items()}
    status_to_codes = {}
    responses = {}

    for http_error in http_errors:
        status_to_codes.setdefault(http_error.status_code, set()).add(http_error.code)

    for status_code, codes in status_to_codes.items():
        model_name = f"{prefix}_{http_status_to_name[status_code]}"
        responses[status_code] = {
            "model": ResponsesGenerator.gen_error_model(model_name, codes)
        }
    return responses


class ResponsesGenerator(object):
    cache_instances = {}

    @classmethod
    def gen_enum(cls, model_name: str, codes: set):
        enum_name = f"{model_name}_CODE"
        if enum_name not in cls.cache_instances:
            cls.cache_instances[enum_name] = {
                "codes": set(codes),
                "model": Enum(enum_name, [(str(c), c) for c in codes], type=str),
            }
        assert (
            cls.cache_instances[enum_name]["codes"] == codes
        ), f'Same name({enum_name}) with different codes({codes}) is not allowed: in cache({cls.cache_instances[enum_name]["codes"]})'
        return cls.cache_instances[enum_name]["model"]

    @classmethod
    def gen_error_model(cls, model_name: str, codes: set):
        error_model_name = f"{model_name}_RESPONSE"
        if error_model_name not in cls.cache_instances:
            enum_cls = cls.gen_enum(model_name, codes)
            cls.cache_instances[error_model_name] = {
                "codes": set(codes),
                "model": create_model(
                    error_model_name, msg=(str, ...), code=(enum_cls, ...)
                ),
            }
        assert (
            cls.cache_instances[error_model_name]["codes"] == codes
        ), f'Same name({error_model_name}) with different codes({codes}) is not allowed: in cache({cls.cache_instances[error_model_name]["codes"]})'
        return cls.cache_instances[error_model_name]["model"]
