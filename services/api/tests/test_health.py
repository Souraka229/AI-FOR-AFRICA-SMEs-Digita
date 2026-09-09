"""Smoke test : vérifie que le package afrosite_api s'importe sans erreur.

Ce fichier est un placeholder minimal dont le seul rôle est de garantir
qu'il existe au moins un test collecté par pytest (exit code 0 au lieu de 5).
Il sera complété avec des tests fonctionnels lors des sprints suivants.
"""


def test_package_importable() -> None:
    """Le package afrosite_api doit s'importer sans lever d'exception."""
    import afrosite_api  # noqa: F401

    assert afrosite_api.__version__ == "0.1.0"
