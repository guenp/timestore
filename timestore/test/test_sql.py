import os
import numpy as np
import pytest
import pytz

from datetime import datetime, timedelta
from typing import Optional, Union
from dataclasses import dataclass

from timestore import timeseries, _TABLE_NAME
from timestore.config import DEFAULT_CONFIG_FILE, get_config
from timestore.sql import SQLTypes, insert, create, exists, query, batch_insert, drop


@pytest.yield_fixture(autouse=True)
def config():
    assert not os.path.isfile(DEFAULT_CONFIG_FILE)
    get_config()
    yield
    assert os.path.isfile(DEFAULT_CONFIG_FILE)
    os.remove(DEFAULT_CONFIG_FILE)


@timeseries
class Foo():
    value: SQLTypes.DOUBLE_PRECISION
    location: Optional[SQLTypes.TEXT]
    metadata: SQLTypes.JSONB


@pytest.yield_fixture()
def create_and_drop_foo():
    assert not exists(Foo)
    create(Foo)
    yield exists(Foo)
    drop(Foo)
    assert not exists(Foo)


def test_dclass():
    @dataclass
    class FooTest():
        bar: SQLTypes.TEXT

    create(FooTest)
    assert getattr(FooTest, _TABLE_NAME) == "foo_test"
    foo_dc = FooTest(bar="baz")
    insert(foo_dc)
    drop(FooTest)


def test_gen(create_and_drop_foo):
    assert create_and_drop_foo
    assert getattr(Foo, _TABLE_NAME) == "foo"

    foo = Foo(value=np.random.rand(), location="Berkeley", metadata={"bar": "baz"})
    assert hasattr(foo, "time")
    assert isinstance(foo.time, datetime)

    foo1 = Foo(value=np.random.rand(), location="Berkeley", metadata={"bar": "baz"},
               time=datetime.now(pytz.utc))
    assert foo1.time > foo.time

    def get_time(n, N):
        return datetime.now(pytz.utc) - timedelta(seconds=N) + timedelta(seconds=n)

    N = 100000
    foo_data = [
        Foo(value=f,
            location="Berkeley",
            metadata={"bar": "baz"},
            time=get_time(n, N))
        for n, f in enumerate(np.random.rand(N))]
    insert(foo_data[0])
    batch_insert(foo_data[1:])

    foo2 = Foo(*query(Foo, limit=1)[0])
    assert np.isclose(foo_data[-1].value, foo2.value)
    assert foo_data[-1].location == foo2.location
    assert foo_data[-1].metadata == foo2.metadata
    assert str(foo_data[-1].time) == str(foo2.time)


def test_union_assert():
    @timeseries
    class FooBad():
        bar: Union[str, float, int]

    with pytest.raises(AssertionError):
        create(FooBad)


def test_ptype():
    @dataclass
    class FooBad():
        bar: str

    with pytest.raises(ValueError):
        create(FooBad)
