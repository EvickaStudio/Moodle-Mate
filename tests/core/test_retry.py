import pytest

from moodlemate.core.utils.retry import with_retry


def test_with_retry_raises_after_max_retries():
    calls = {"count": 0}

    @with_retry(max_retries=2, base_delay=0.0, max_delay=0.0, exceptions=(ValueError,))
    def always_fail():
        calls["count"] += 1
        raise ValueError("boom")

    with pytest.raises(ValueError):
        always_fail()

    assert calls["count"] == 3


def test_with_retry_on_failure_callback():
    @with_retry(
        max_retries=1,
        base_delay=0.0,
        max_delay=0.0,
        exceptions=(RuntimeError,),
        on_failure=lambda: "fallback",
    )
    def always_fail():
        raise RuntimeError("boom")

    assert always_fail() == "fallback"
