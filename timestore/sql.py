import re
import warnings
import psycopg2
from psycopg2.extras import Json, execute_values

from timestore import _TABLE_NAME, SQLTypes, to_snake_case
from timestore.config import DEFAULT_CONFIG_FILE, postgres_db


def _execute(query,
             data=None,
             config_file=DEFAULT_CONFIG_FILE):
    """Execute SQL query on a postgres db"""
    # Connect to an existing database.
    postgres_db_credentials = postgres_db(config_file)
    conn = psycopg2.connect(dbname=postgres_db_credentials["dbname"],
                            user=postgres_db_credentials["user"],
                            password=postgres_db_credentials["password"],
                            host=postgres_db_credentials["host"],
                            port=postgres_db_credentials["port"])

    # Open a cursor to perform database operations.
    cur = conn.cursor()

    if data is None:
        cur.execute(query)

    elif isinstance(data, list):
        execute_values(cur, query, data, template=None, page_size=100)

    else:
        cur.execute(query, data)

    conn.commit()

    if cur.description is None:
        result = None
    elif len(cur.description) == 1:
        result, = cur.fetchone()
    else:
        result = cur.fetchall()

    cur.close()
    conn.close()

    return result


def _to_dict(obj):
    """Serialize dataclass into SQL insertable dictionary"""
    return {k: Json(v) if isinstance(v, dict) else v for k, v in obj.__dict__.items()}


def _to_tuple(obj):
    """Serialize dataclass into SQL insertable tuple"""
    return tuple(Json(v) if isinstance(v, dict) else v for _, v in obj.__dict__.items())


def _insert(obj):
    """Insert dataclass into SQL table"""
    name = getattr(obj.__class__, _TABLE_NAME)
    types = ", ".join([f"%({field})s" for field in obj.__annotations__])
    fields = ", ".join(obj.__annotations__)
    sql = f"INSERT INTO {name}({fields}) VALUES ({types});"

    return sql


def _batch_insert(objs):
    """Batch insert a list of dataclass instances into corresponding SQL table"""
    name = getattr(objs[0].__class__, _TABLE_NAME)
    fields = ", ".join(objs[0].__annotations__)
    sql = f"INSERT INTO {name}({fields}) VALUES %s;"

    return sql


def _sql_type(ptype):
    """Convert python type to SQL type"""
    if "Union" in ptype.__class__.__name__:
        assert len(ptype.__args__) == 2, "Cannot create sql column with more than one type."
        assert type(None) in ptype.__args__, "Cannot create sql column with more than one type."

        return f"{ptype.__args__[0].__name__} NULL"

    elif ptype in SQLTypes.__dict__.values() and hasattr(ptype, "__name__"):
        return f"{ptype.__name__} NOT NULL"

    else:
        raise ValueError(f"Cannot parse type {ptype}.")


def _create(dcls, partition_col="time", hyper_table=True):
    """Returns SQL query to create a SQL table associated with a dataclass"""
    # Check if it is a modified dataclass with a table name
    if hasattr(dcls, _TABLE_NAME):
        name = getattr(dcls, _TABLE_NAME)

    else:
        # Regular dataclass
        name = to_snake_case(dcls.__name__)
        setattr(dcls, _TABLE_NAME, name)

    columns = [f"{k} {_sql_type(v)}" for k, v in dcls.__annotations__.items()]
    columns = ", ".join(columns)
    sql = "CREATE TABLE %s (%s); " % (name, columns)
    sql += "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"

    if hyper_table is True and hasattr(dcls, partition_col):
        sql += "SELECT create_hypertable('%s', '%s');" % (name, partition_col)
    else:
        warnings.warn(f"Cannot create hypertable: column {partition_col} does not exist.")
    return sql


def _exists(dcls):
    """Returns SQL query to check if a table exists"""
    name = getattr(dcls, _TABLE_NAME)
    sql = f"SELECT EXISTS ( SELECT 1 FROM pg_tables WHERE tablename = '{name}' );"
    return sql


def _drop(dcls):
    """Drop SQL table associated with the dataclass"""
    name = getattr(dcls, _TABLE_NAME)
    sql = f"DROP TABLE {name};"
    return sql


def _query(dcls, limit=100, order="DESC", order_by="time"):
    """Query SQL table associated with dataclass"""
    if order is not None:
        assert order in ["DESC", "ASC"]

    name = getattr(dcls, _TABLE_NAME)
    sql = f"SELECT * FROM {name}"

    if order_by is not None and order is not None:
        sql += f" ORDER BY {order_by} {order}"
    if limit is not None:
        sql += f" LIMIT {limit}"

    sql += ";"
    return sql


def create(dcls, partition_col="time", hyper_table=True):
    """Create a SQL table from a dataclass with (optional) a time series column"""
    sql = _create(dcls, partition_col, hyper_table)
    _execute(sql)


def drop(dcls):
    """Drop a SQL table from a dataclass"""
    sql = _drop(dcls)
    _execute(sql)


def insert(obj):
    """Insert a dataclass instance into a SQL table"""
    sql = _insert(obj)
    data = _to_dict(obj)
    _execute(sql, data)


def batch_insert(objs):
    """Batch insert a list of dataclass instances into a SQL table"""
    sql = _batch_insert(objs)
    data = [_to_tuple(obj) for obj in objs]
    _execute(sql, data)


def exists(dcls):
    """Returns True if a SQL table exists for the dataclass, otherwise False"""
    sql = _exists(dcls)
    return _execute(sql)


def query(dcls, limit=100, order="DESC"):
    """Query the SQL table associated with a dataclass"""
    sql = _query(dcls, limit, order)
    return _execute(sql)
