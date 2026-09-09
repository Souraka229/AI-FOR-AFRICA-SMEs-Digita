"""Smoke test : vérifie que le package afrosite_workflows s'importe sans erreur."""


def test_package_importable() -> None:
    """Le package afrosite_workflows doit s'importer sans lever d'exception."""
    import afrosite_workflows  # noqa: F401

    assert afrosite_workflows.__version__ == "0.1.0"
