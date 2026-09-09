"""Smoke test : vérifie que le package afrosite_agents s'importe sans erreur."""


def test_package_importable() -> None:
    """Le package afrosite_agents doit s'importer sans lever d'exception."""
    import afrosite_agents  # noqa: F401

    assert afrosite_agents.__version__ == "0.1.0"
