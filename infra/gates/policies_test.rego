# Gate policy tests (OPA). Run with: opa test infra/gates -v

package afrosite.gates

test_g1_blocks_invalid_blueprint if {
	deny["G1: Blueprint JSON schema validation failed"] with input as {
		"gate": "g1_schema",
		"blueprint_valid": false,
	}
}

test_g2_blocks_when_ci_red if {
	deny["G2: CI quality checks are not green"] with input as {
		"gate": "g2_quality",
		"ci_green": false,
	}
}

test_g3_blocks_security_findings if {
	deny["G3: Security scan reported findings"] with input as {
		"gate": "g3_security",
		"security_scan_clean": false,
	}
}

test_g4_blocks_unverified_payment_sandbox if {
	deny["G4: Payment sandbox checks incomplete"] with input as {
		"gate": "g4_payment",
		"payment_sandbox_verified": false,
	}
}

test_g5_blocks_unhealthy_preview if {
	deny["G5: Preview environment unhealthy"] with input as {
		"gate": "g5_preview",
		"preview_healthy": false,
	}
}

test_g6_requires_audit if {
	deny["G6: External security audit not passed"] with input as {
		"gate": "g6_production",
		"audit_passed": false,
		"human_approval": true,
	}
}

test_g6_requires_human_approval if {
	deny["G6: Explicit human approval required for production"] with input as {
		"gate": "g6_production",
		"audit_passed": true,
		"human_approval": false,
	}
}

test_allow_when_clean if {
	allow with input as {"gate": "g2_quality", "ci_green": true}
}
