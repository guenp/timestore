from datetime import datetime


class SQLTypes(object):
    TIMESTAMPTZ = type("TIMESTAMPTZ", (datetime,), {})
    DOUBLE_PRECISION = type("DOUBLE PRECISION", (float,), {})
    TEXT = type("TEXT", (str,), {})
    JSONB = type("JSONB", (dict,), {})
