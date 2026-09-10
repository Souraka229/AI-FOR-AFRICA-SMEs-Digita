"""Compatibilité des quatre paquets OpenHands et du contrat Docker."""

from importlib.metadata import version

from openhands.workspace import DockerWorkspace

from runtime.code_agent import OPENHANDS_IMAGE


for package in (
    "openhands-sdk",
    "openhands-tools",
    "openhands-workspace",
    "openhands-agent-server",
):
    assert version(package) == "1.44.1", (package, version(package))

fields = DockerWorkspace.model_fields
assert {"server_image", "volumes", "forward_env"} <= fields.keys()
assert "@sha256:" in OPENHANDS_IMAGE and ":latest" not in OPENHANDS_IMAGE

print("check:openhands OK · versions assorties · Docker · digest · volumes")
