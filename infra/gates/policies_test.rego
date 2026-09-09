# Gate policy tests (OPA). Run with: opa test infra/gates -v

package afrosite.gates

test_g2_blocks_when_ci_red if {
	deny["G2: CI quality checks are not green"] with input as {
		"gate": "g2_quality",
		"ci_green": false,
	}
}

test_g6_requires_audit if {
	deny["G6: External security audit not passed"] with input as {
		"gate": "g6_production",
		"audit_passed": false,
		"human_approval": true,
	}
}

test_allow_when_clean if {
	allow with input as {"gate": "g2_quality", "ci_green": true}
}
