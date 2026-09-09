# Gate policies (OPA/Rego) — Afrosite 6 gates
# Evaluated by CI / Security Agent; Rego is the source of truth for gate rules.

package afrosite.gates

# G1 — Schema / contract validation must pass before generation merges.
deny[msg] if {
	input.gate == "g1_schema"
	not input.blueprint_valid
	msg := "G1: Blueprint JSON schema validation failed"
}

# G2 — Lint, typecheck, unit tests, build, no secrets.
deny[msg] if {
	input.gate == "g2_quality"
	not input.ci_green
	msg := "G2: CI quality checks are not green"
}

# G3 — SAST / deps / secrets / RBAC checks.
deny[msg] if {
	input.gate == "g3_security"
	not input.security_scan_clean
	msg := "G3: Security scan reported findings"
}

# G4 — Payment sandbox: signed webhooks, idempotency, server amounts.
deny[msg] if {
	input.gate == "g4_payment"
	not input.payment_sandbox_verified
	msg := "G4: Payment sandbox checks incomplete"
}

# G5 — Preview environment healthy.
deny[msg] if {
	input.gate == "g5_preview"
	not input.preview_healthy
	msg := "G5: Preview environment unhealthy"
}

# G6 — Production release requires explicit approval + audit.
deny[msg] if {
	input.gate == "g6_production"
	not input.audit_passed
	msg := "G6: External security audit not passed"
}

deny[msg] if {
	input.gate == "g6_production"
	not input.human_approval
	msg := "G6: Explicit human approval required for production"
}

allow if {
	count(deny) == 0
}
