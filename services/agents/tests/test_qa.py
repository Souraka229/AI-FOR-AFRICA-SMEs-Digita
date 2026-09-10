from runtime.qa import run_qa_agent


def test_qa_passes_complete_artifact() -> None:
    report = run_qa_agent(
        {
            "branch": "feature/generated-wax",
            "unit_passed": True,
            "e2e": {
                "studio": True,
                "storefront": True,
                "desktop": True,
                "mobile": True,
            },
            "gate5": {
                "migrationOnCopy": True,
                "backupVerified": True,
                "rollbackReady": True,
            },
        }
    )
    assert report["passed"] is True
    assert report["gate"] == "g5"


def test_qa_blocks_production_and_missing_playwright() -> None:
    report = run_qa_agent(
        {
            "branch": "feature/generated-wax",
            "unit_passed": True,
            "production": True,
            "e2e": {"studio": False},
        }
    )
    assert report["passed"] is False
    assert any("production" in error for error in report["errors"])
    assert any("studio" in error for error in report["errors"])
