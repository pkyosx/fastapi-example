# Because Enum does not allow inheritance, we created a util here and .to_enum() could be used to convert it to Enum.

from enum import Enum


class EnumBase(object):
    # All upper_case member will be treated as Enum variable
    @classmethod
    def __is_enum(cls, attr):
        return attr[0].isupper()

    @classmethod
    def keys(cls):
        return [i for i in dir(cls) if cls.__is_enum(i)]

    @classmethod
    def values(cls):
        return [getattr(cls, i) for i in dir(cls) if cls.__is_enum(i)]

    @classmethod
    def items(cls):
        return [(i, getattr(cls, i)) for i in dir(cls) if cls.__is_enum(i)]

    @classmethod
    def has_key(cls, k):
        return k in cls.keys()

    @classmethod
    def has_value(cls, v):
        return v in cls.values()

    @classmethod
    def get_field(cls, name):
        for field in cls.values():
            if field == name:
                return field

    @classmethod
    def value_to_key(cls):
        return {v: k for k, v in cls.items()}

    @classmethod
    def to_enum(cls) -> Enum:
        if not hasattr(cls, "__enum_instance__"):
            cls.__enum_instance__ = Enum(cls.__name__, [(k, v) for k, v in cls.items()], type=str)
        return cls.__enum_instance__

