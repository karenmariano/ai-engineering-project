def test_app_imports() -> None:
    from src import app as app_mod  # noqa: F401

    assert app_mod is not None
