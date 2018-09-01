import re
from datetime import datetime

import pytz
from dataclasses import field, _PARAMS, _FIELDS, dataclass

from timestore.types import SQLTypes


_TABLE_NAME = "__table_name__"


def utcnow():
    return datetime.now(pytz.utc)


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def to_snake_case(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def timeseries(_dcls=None, *, table_name=None):
    """
    Add a "time" field to an existing class of type TIMESTAMP and turn it into a dataclass.
    """

    def wrap(dcls):
        assert not hasattr(dcls, _PARAMS) and not hasattr(dcls, _FIELDS), \
            "Cannot wrap an existing dataclass with the timeseries decorator."

        cls_annotations = dcls.__dict__.get('__annotations__', {})
        cls_annotations["time"] = SQLTypes.TIMESTAMPTZ

        dcls.time = field(default_factory=utcnow)
        dcls = dataclass(dcls)
        setattr(dcls, _TABLE_NAME, to_snake_case(dcls.__name__) if not table_name else table_name)

        return dcls

    # See if we're being called as @timeseries or @timeseries().
    if _dcls is None:
        # We're called with parens.
        return wrap

    return wrap(_dcls)
