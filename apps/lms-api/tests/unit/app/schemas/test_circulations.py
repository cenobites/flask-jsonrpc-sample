from __future__ import annotations


def test_circulations_module_exists() -> None:
    from lms.app.schemas import circulations  # noqa: F401

    # Module exists but contains no schemas yet
    assert True
