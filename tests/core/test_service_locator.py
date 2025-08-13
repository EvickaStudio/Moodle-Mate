import pytest

from src.core.service_locator import ServiceLocator


class Foo:
    pass


def test_register_and_get():
    f = Foo()
    ServiceLocator.register("foo", f)
    got = ServiceLocator.get("foo", Foo)
    assert got is f


def test_get_missing_raises():
    with pytest.raises(KeyError):
        ServiceLocator.get("nope", Foo)


def test_type_mismatch_raises():
    ServiceLocator.register("foo2", object())
    with pytest.raises(TypeError):
        ServiceLocator.get("foo2", Foo)
